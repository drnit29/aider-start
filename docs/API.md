# API Interna do aider-start

Este documento descreve as principais classes e interfaces programáticas do aider-start para desenvolvedores que desejam estender ou integrar a ferramenta.

## Visão Geral da Arquitetura

O aider-start é composto por vários componentes principais que trabalham juntos:

```
ConfigManager <---> SecureConfigManager
       ^                  ^
       |                  |
       v                  v
ProfileBuilder <------> ParameterDatabase
       ^
       |
       v
      TUI <------------> CommandExecutor
```

## Classes Principais

### ConfigManager

A classe `ConfigManager` gerencia o arquivo de configuração do aider-start, manipulando perfis, provedores e endpoints personalizados.

```python
from aider_start.config_manager import ConfigManager

# Inicializar com caminho de configuração padrão
config = ConfigManager()

# Ou com caminho personalizado
config = ConfigManager(config_path="/caminho/para/config.json")

# Obter todos os perfis
perfis = config.get_profiles()

# Adicionar um novo perfil
config.add_profile("meu_perfil", {
    "name": "meu_perfil",
    "model": "gpt-4",
    "temperature": 0.7
})

# Obter um perfil específico
perfil = config.get_profile("meu_perfil")

# Remover um perfil
config.remove_profile("meu_perfil")

# Definir perfil padrão
config.set_default_profile("meu_perfil")

# Obter perfil padrão
perfil_padrao = config.get_default_profile()

# Trabalhar com provedores
provedores = config.get_providers()
config.add_provider("openai", {"models": ["gpt-4", "gpt-3.5-turbo"]})
config.update_provider_models("openai", ["gpt-4o", "gpt-4", "gpt-3.5-turbo"])

# Trabalhar com endpoints personalizados
endpoints = config.get_custom_endpoints()
config.add_custom_endpoint("meu_endpoint", {
    "api_url": "https://meu-servidor/v1",
    "models": ["local-model"]
})
```

### SecureConfigManager

A classe `SecureConfigManager` estende o `ConfigManager` para fornecer armazenamento seguro de chaves API usando o keyring do sistema.

```python
from aider_start.secure_config import SecureConfigManager

# Inicializar com caminho de configuração padrão
secure_config = SecureConfigManager()

# Definir uma chave API
secure_config.set_api_key("openai", "sk-sua-chave-aqui")

# Obter uma chave API
key = secure_config.get_api_key("openai")

# Verificar se uma chave API existe
tem_chave = secure_config.has_api_key("openai")

# Remover uma chave API
secure_config.delete_api_key("openai")
```

### ParameterDatabase

A classe `ParameterDatabase` gerencia informações sobre todos os parâmetros disponíveis para o aider, suas descrições, tipos e valores padrão.

```python
from aider_start.param_db import ParameterDatabase

# Inicializar o banco de dados de parâmetros
params = ParameterDatabase()

# Obter todas as categorias disponíveis
categorias = params.get_categories()

# Obter todos os parâmetros de uma categoria
api_opcoes = params.get_category("api_options")

# Obter um parâmetro específico
modelo_param = params.get_parameter("model_options", "model")

# Formatar o tipo de um parâmetro para exibição
tipo_formatado = params.format_parameter_type(modelo_param)
```

### ProfileBuilder

A classe `ProfileBuilder` ajuda a construir perfis de configuração para o aider interativamente.

```python
from aider_start.profile_builder import ProfileBuilder
from aider_start.config_manager import ConfigManager
from aider_start.param_db import ParameterDatabase

# Inicializar o construtor de perfis
config = ConfigManager()
params = ParameterDatabase()
builder = ProfileBuilder(config_manager=config, param_db=params)

# Iniciar um novo perfil
builder.start_new_profile()

# Configurar parâmetros
builder.set_parameter("name", "meu_perfil")
builder.set_parameter("model", "gpt-4")
builder.set_parameter("temperature", 0.7)

# Obter valor atual de um parâmetro
temp = builder.get_parameter_value("temperature")

# Obter descrição de ajuda para um parâmetro
ajuda = builder.get_parameter_help("model_options", "model")

# Verificar se um parâmetro é secreto (como uma chave API)
e_secreto = builder.is_parameter_secret("api_options", "openai_api_key")

# Validar o perfil atual
valido, mensagem = builder.validate_profile()

# Salvar o perfil
if valido:
    builder.save_profile()
```

### TUI

A classe `TUI` implementa a interface de terminal interativa.

```python
from aider_start.tui import TUI
from aider_start.config_manager import ConfigManager
from aider_start.profile_builder import ProfileBuilder
from aider_start.command_executor import CommandExecutor

# Inicializar os componentes
config = ConfigManager()
builder = ProfileBuilder(config_manager=config)
executor = CommandExecutor(config_manager=config)

# Inicializar a TUI
tui = TUI(config_manager=config, profile_builder=builder, command_executor=executor)

# Iniciar a interface
tui.start()
```

### CommandExecutor

A classe `CommandExecutor` é responsável por construir e executar os comandos aider com base nos perfis.

```python
from aider_start.command_executor import CommandExecutor
from aider_start.config_manager import ConfigManager

# Inicializar o executor
config = ConfigManager()
executor = CommandExecutor(config_manager=config)

# Executar o aider com um perfil específico
executor.run_aider("meu_perfil")

# Construir um comando sem executá-lo
cmd = executor.build_command("meu_perfil")
print(f"Comando que seria executado: {cmd}")
```

## Eventos e Interfaces de Extensão

O aider-start suporta um sistema simples de eventos que permite que extensões sejam adicionadas sem modificar o código principal.

### Sistema de Eventos

```python
from aider_start.events import EventManager

# Registrar um manipulador de evento
def on_profile_created(profile_name, profile_data):
    print(f"Perfil criado: {profile_name}")

EventManager.register("profile_created", on_profile_created)

# Disparar um evento
EventManager.trigger("profile_created", "meu_perfil", {})
```

### Extensões

Para criar uma extensão para o aider-start:

1. Crie um pacote Python com a convenção de nomenclatura `aider_start_extension_*`
2. Implemente uma função `setup()` que registra manipuladores de eventos

Exemplo:

```python
# Pacote: aider_start_extension_github

from aider_start.events import EventManager

def setup():
    """Configurar a extensão."""
    EventManager.register("profile_created", on_profile_created)
    EventManager.register("before_aider_run", add_github_args)

def on_profile_created(profile_name, profile_data):
    """Manipular a criação de perfil."""
    print(f"Extensão GitHub: Perfil {profile_name} criado")

def add_github_args(profile_name, args_list):
    """Adicionar argumentos relacionados ao GitHub."""
    # Modificar a lista de argumentos antes de executar o aider
    args_list.extend(["--github-repo", "user/repo"])
```

## Integração com Aplicações Externas

Para integrar o aider-start em uma aplicação externa:

```python
from aider_start.config_manager import ConfigManager
from aider_start.command_executor import CommandExecutor

# Inicializar os componentes necessários
config = ConfigManager()
executor = CommandExecutor(config_manager=config)

# Criar uma função para obter e executar um perfil
def executar_aider_com_perfil(nome_perfil):
    """Executa o aider com um perfil específico e retorna o código de saída."""
    try:
        return executor.run_aider(nome_perfil)
    except Exception as e:
        print(f"Erro ao executar o aider: {str(e)}")
        return 1

# Função para obter todos os perfis
def listar_perfis_disponiveis():
    """Retorna uma lista de perfis disponíveis."""
    return config.get_profiles()
```

## Arquivos de Configuração

### Formato do arquivo config.json

```json
{
  "default_profile": "meu_perfil",
  "profiles": {
    "meu_perfil": {
      "name": "meu_perfil",
      "model": "gpt-4",
      "temperature": 0.7
    }
  },
  "providers": {
    "openai": {
      "description": "OpenAI API",
      "models": ["gpt-4", "gpt-3.5-turbo"]
    },
    "anthropic": {
      "description": "Anthropic API",
      "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"]
    }
  },
  "custom_endpoints": {
    "local_endpoint": {
      "api_url": "http://localhost:8000/v1",
      "models": ["local-model-1", "local-model-2"]
    }
  }
}
```

## Personalização e Hooks

O aider-start permite personalização através de hooks em locais específicos:

### Personalização do Comportamento do CommandExecutor

```python
from aider_start.command_executor import CommandExecutor

class CustomCommandExecutor(CommandExecutor):
    """Executor de comando personalizado com funcionalidade adicional."""
    
    def run_aider(self, profile_name):
        """Sobrescreve o método run_aider com funcionalidade personalizada."""
        print(f"Executando o aider com perfil {profile_name}")
        
        # Adicionar lógica adicional antes de executar
        self._before_run_hook(profile_name)
        
        # Chamar a implementação original
        result = super().run_aider(profile_name)
        
        # Adicionar lógica adicional após a execução
        self._after_run_hook(profile_name, result)
        
        return result
    
    def _before_run_hook(self, profile_name):
        """Código a ser executado antes de iniciar o aider."""
        print("Preparando ambiente...")
    
    def _after_run_hook(self, profile_name, result):
        """Código a ser executado após a conclusão do aider."""
        print(f"Aider concluído com código de saída: {result}")
```

## Conclusão

Esta documentação de API fornece uma visão geral das principais classes e interfaces do aider-start. Desenvolvedores podem usar essas interfaces para estender ou integrar o aider-start em suas próprias aplicações ou workflows.

Para questões específicas ou recursos avançados, consulte o código-fonte diretamente. Cada componente possui docstrings detalhadas que fornecem informações adicionais sobre sua funcionalidade. 