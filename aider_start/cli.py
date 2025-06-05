from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from .config_manager import load_presets, save_presets
import subprocess

def main_flow():
    while True:
        action = inquirer.select(
            message="Select an action:",
            choices=[
                Choice("run", name="Run Preset"),
                Choice("config", name="Configure Preset"),
                Choice("exit", name="Exit"),
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
        print("No presets configured!\n")
        return
        
    choices = [Choice(name=name, value=cmd) for name, cmd in presets.items()]
    choices.append(Choice(value=None, name="Back"))
    
    selected_cmd = inquirer.select(
        message="Select a preset:",
        choices=choices
    ).execute()
    
    if selected_cmd:
        subprocess.run(selected_cmd, shell=True)

def configure_presets():
    while True:
        action = inquirer.select(
            message="Manage presets:",
            choices=[
                Choice("add", name="Add new preset"),
                Choice("edit", name="Edit existing preset"),
                Choice("remove", name="Remove preset"),
                Choice("back", name="Back"),
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
    name = inquirer.text(message="Preset name:").execute()
    command = inquirer.text(message="Command (e.g.: aider --model openai/gpt-4.1):").execute()
    presets = load_presets()
    presets[name] = command
    save_presets(presets)

def edit_preset():
    presets = load_presets()
    if not presets:
        print("No presets available!\n")
        return
        
    name = inquirer.select(
        message="Select to edit:",
        choices=list(presets.keys()) + ["Back"]
    ).execute()
    
    if name != "Back":
        new_command = inquirer.text(
            message=f"New command for '{name}':", 
            default=presets[name]
        ).execute()
        presets[name] = new_command
        save_presets(presets)

def remove_preset():
    presets = load_presets()
    if not presets:
        print("No presets available!\n")
        return
        
    name = inquirer.select(
        message="Select to remove:",
        choices=list(presets.keys()) + ["Back"]
    ).execute()
    
    if name != "Back":
        del presets[name]
        save_presets(presets)
