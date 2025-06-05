from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from .config_manager import load_presets, save_presets
import subprocess

def main_flow():
    while True:
        action = inquirer.select(
            message="Selecione uma ação:",
            choices=[
                Choice("run", name="Executar Preset"),
                Choice("config", name="Configurar Preset"),
                Choice("exit", name="Sair"),
            ]
        ).execute()
        
        if action == "run":
            run_preset()
        elif action == "config":
            configure_presets()
        else:
            break

def run_preset():
    presets = load_presets()
    if not presets:
        print("Nenhum preset configurado!\n")
        return
        
    choices = [Choice(name=name, value=cmd) for name, cmd in presets.items()]
    choices.append(Choice(value=None, name="Voltar"))
    
    selected_cmd = inquirer.select(
        message="Selecione um preset:",
        choices=choices
    ).execute()
    
    if selected_cmd:
        subprocess.run(selected_cmd, shell=True)

def configure_presets():
    while True:
        action = inquirer.select(
            message="Gerenciar presets:",
            choices=[
                Choice("add", name="Adicionar novo preset"),
                Choice("edit", name="Editar preset existente"),
                Choice("remove", name="Remover preset"),
                Choice("back", name="Voltar"),
            ]
        ).execute()
        
        if action == "add":
            add_preset()
        elif action == "edit":
            edit_preset()
        elif action == "remove":
            remove_preset()
        else:
            break

def add_preset():
    name = inquirer.text(message="Nome do preset:").execute()
    command = inquirer.text(message="Comando (ex: aider --model openai/gpt-4.1):").execute()
    presets = load_presets()
    presets[name] = command
    save_presets(presets)

def edit_preset():
    presets = load_presets()
    if not presets:
        print("Nenhum preset disponível!\n")
        return
        
    name = inquirer.select(
        message="Selecione para editar:",
        choices=list(presets.keys()) + ["Voltar"]
    ).execute()
    
    if name != "Voltar":
        new_command = inquirer.text(
            message=f"Novo comando para '{name}':", 
            default=presets[name]
        ).execute()
        presets[name] = new_command
        save_presets(presets)

def remove_preset():
    presets = load_presets()
    if not presets:
        print("Nenhum preset disponível!\n")
        return
        
    name = inquirer.select(
        message="Selecione para remover:",
        choices=list(presets.keys()) + ["Voltar"]
    ).execute()
    
    if name != "Voltar":
        del presets[name]
        save_presets(presets)
