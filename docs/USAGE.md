# Guia de Uso do aider-start

Este documento fornece instruções detalhadas sobre como usar o aider-start no dia a dia.

## Começando com o aider-start

O aider-start foi projetado para simplificar a configuração e o gerenciamento de perfis para o aider, proporcionando uma experiência mais fluida de programação em par com IA.

## Instalação

Para instalar o aider-start:

```bash
pip install aider-start
```

Verifique se a instalação foi bem-sucedida:

```bash
aider-start --version
```

## Uso da Interface TUI

A maneira mais fácil de usar o aider-start é através da sua interface de texto:

```bash
aider-start
```

Isto abrirá a interface TUI (Text User Interface) com as seguintes opções principais:

### Menu Principal

- **Perfis**: Gerenciar perfis de configuração
- **Provedores**: Configurar provedores de API
- **Endpoints**: Gerenciar endpoints personalizados
- **Executar aider**: Iniciar o aider com um perfil selecionado
- **Sair**: Encerrar o programa

### Gerenciamento de Perfis

Navegar para a opção "Perfis" exibirá os perfis existentes e oferecerá opções para:

- **Criar novo perfil**: Iniciar um assistente interativo para criar um perfil
- **Editar perfil**: Modificar um perfil existente
- **Remover perfil**: Excluir um perfil existente
- **Definir perfil padrão**: Configurar o perfil a ser usado por padrão
- **Voltar**: Retornar ao menu principal

#### Criação de Perfil

Ao criar um perfil, você navegará por categorias de parâmetros:

1. Nome do perfil
2. Opções de modelo (modelo, temperatura, context, etc.)
3. Opções de API (provedor, chave API, etc.)
4. Opções de histórico de chat
5. Opções git
6. Opções de código
7. Opções diversas

Para cada parâmetro, você verá:
- Descrição
- Tipo esperado
- Valor padrão (se houver)
- Um campo para inserir seu valor desejado

### Gerenciamento de Provedores

Na seção "Provedores", você pode:

- **Configurar chave API**: Adicionar/atualizar sua chave API para um provedor
- **Ver provedores disponíveis**: Listar os provedores configurados
- **Atualizar modelos**: Atualizar a lista de modelos para um provedor

### Gerenciamento de Endpoints

Na seção "Endpoints", você pode:

- **Adicionar endpoint**: Configurar um novo endpoint personalizado
- **Editar endpoint**: Modificar um endpoint existente
- **Remover endpoint**: Excluir um endpoint
- **Testar endpoint**: Verificar a conectividade de um endpoint

## Uso via Linha de Comando

O aider-start também pode ser usado diretamente via linha de comando.

### Listar Perfis

```bash
aider-start --list
```

Exibe todos os perfis configurados, incluindo o perfil padrão.

### Usar Perfil Específico

```bash
aider-start --profile meu_perfil
```

Inicia o aider com as configurações do perfil especificado.

### Editar Perfil via Linha de Comando

```bash
aider-start --edit-profile meu_perfil
```

Abre a interface TUI diretamente na edição do perfil especificado.

### Gerenciar Chaves API

```bash
aider-start --set-api-key openai SUACHAVEAPI
```

Define uma chave API para um provedor específico.

```bash
aider-start --delete-api-key openai
```

Remove a chave API associada a um provedor.

### Criar Perfil via Template

```bash
aider-start --create-profile novo_perfil --from-template gpt4_base
```

Cria um novo perfil baseado em um modelo pré-definido.

## Exemplos de Uso Comuns

### Alternar entre diferentes modelos

Crie perfis diferentes para modelos diferentes:

```bash
# Criar perfil para GPT-4
aider-start --create-profile gpt4_profile --model gpt-4

# Criar perfil para Claude
aider-start --create-profile claude_profile --model claude-3-opus-20240229

# Usar o perfil Claude
aider-start --profile claude_profile
```

### Configurar parâmetros de projeto específicos

```bash
# Criar perfil para trabalhar com Python
aider-start --create-profile python_proj --model gpt-4 --map-open-file-types "py,md,txt" --edit-format autopep8

# Usar o perfil para projeto Python
aider-start --profile python_proj
```

### Usar um endpoint local com modelos locais

```bash
# Primeiro, adicione um endpoint personalizado via TUI ou:
aider-start --add-custom-endpoint ollama http://localhost:11434/v1 --models "mistral:latest,codellama:latest"

# Criar perfil usando este endpoint
aider-start --create-profile local_coding --model codellama:latest --custom-endpoint ollama

# Usar o modelo local
aider-start --profile local_coding
```

## Solução de Problemas

### O aider não está sendo encontrado

Certifique-se de que o aider está instalado e disponível no PATH. O aider-start não instala o aider automaticamente.

```bash
pip install aider-ai
```

### Problemas com chaves API

Se você encontrar erros relacionados a chaves API, verifique:

1. A chave foi configurada corretamente: `aider-start --set-api-key <provider> <key>`
2. O keyring do sistema está funcionando adequadamente
3. O provedor está disponível e a chave é válida

### Problemas na Interface TUI

Em caso de problemas com a interface TUI:

1. Verifique se sua versão do Python é 3.8 ou superior
2. No Windows, certifique-se de que o pacote `windows-curses` está instalado
3. Em terminais com suporte limitado, tente usar a interface de linha de comando

## Avançado: Migração de Perfis

Para migrar perfis entre máquinas, você pode copiar o arquivo de configuração:

```bash
# Na máquina de origem
cp ~/.aider-start/config.json config_backup.json

# Na máquina de destino
mkdir -p ~/.aider-start/
cp config_backup.json ~/.aider-start/config.json
```

Nota: As chaves API não são exportadas e devem ser configuradas novamente na nova máquina.

## Conclusão

O aider-start torna o uso do aider mais conveniente, permitindo alternar facilmente entre diferentes configurações e armazenar chaves API de forma segura. Com estes comandos e a interface TUI, você pode personalizar completamente sua experiência de programação em par com IA. 