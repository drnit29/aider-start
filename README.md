# aider-start

Um gerenciador de perfis para o [aider](https://github.com/paul-gauthier/aider), ferramenta de programação em par com IA.

## Descrição

O aider-start é uma ferramenta de linha de comando projetada para simplificar o uso do aider. Ele oferece uma maneira interativa de gerenciar perfis de configuração, provedores de API e endpoints personalizados, permitindo que os usuários iniciem rapidamente o aider com configurações pré-definidas sem precisar memorizar argumentos complexos de linha de comando.

## Recursos Principais

- Gerenciamento de perfis de configuração do aider
- Gerenciamento de provedores e chaves de API
- Suporte para endpoints personalizados compatíveis com OpenAI
- Interface de terminal amigável (TUI)
- Assistente de configuração interativo
- Armazenamento seguro de chaves API no keyring do sistema
- Categorização de parâmetros para fácil navegação
- Validação de configurações para evitar erros

## Instalação

```bash
pip install aider-start
```

## Uso

### Interface Interativa

Para iniciar a interface interativa:

```bash
aider-start
```

A interface TUI permite gerenciar perfis, provedores e endpoints de forma intuitiva.

### Uso com Linha de Comando

Para iniciar o aider diretamente com um perfil específico:

```bash
aider-start --profile nome_do_perfil
```

Para listar os perfis disponíveis:

```bash
aider-start --list
```

Para obter ajuda sobre todos os comandos disponíveis:

```bash
aider-start --help
```

## Configuração

O aider-start armazena sua configuração em `~/.aider-start/config.json`. As chaves de API são armazenadas com segurança usando o sistema de keyring do sistema operacional.

### Estrutura do Arquivo de Configuração

O arquivo de configuração é organizado em três seções principais:

```json
{
  "profiles": {
    "meu_perfil": {
      "name": "meu_perfil",
      "model": "gpt-4o",
      "...": "..."
    }
  },
  "providers": {
    "openai": {
      "models": ["gpt-4o", "gpt-3.5-turbo"],
      "description": "OpenAI API"
    }
  },
  "custom_endpoints": {
    "meu_endpoint": {
      "api_url": "https://meu-servidor/v1",
      "models": ["local-model"]
    }
  }
}
```

### Estrutura de Perfis

Cada perfil pode conter qualquer parâmetro válido para o comando aider, organizados por categorias:

- **model_options**: opções relacionadas ao modelo utilizado
- **api_options**: configurações de API e autenticação
- **history_options**: opções de histórico de chat
- **git_options**: configurações relacionadas ao git
- **coding_options**: opções para o comportamento do código
- **map_options**: configurações de mapeamento do código
- **fixing_options**: opções para teste e linting de código
- **voice_options**: opções para entrada de voz
- **mode_options**: opções de modo de operação
- **misc_options**: opções diversas

### Configuração de Provedores

Os provedores representam serviços de API como OpenAI ou Anthropic. É possível configurar:
- Chaves de API (armazenadas com segurança)
- Modelos disponíveis
- Parâmetros específicos da API

### Endpoints Personalizados

É possível configurar endpoints de API personalizados que são compatíveis com o formato da API OpenAI:
- URL do endpoint
- Chave de API
- Modelos disponíveis
- Tipo de API/compatibilidade

## Arquitetura do Projeto

O aider-start é organizado em vários módulos:

- **ConfigManager**: gerencia a leitura/escrita do arquivo de configuração
- **SecureConfigManager**: estende o ConfigManager com suporte a armazenamento seguro de chaves
- **ParameterDatabase**: repositório de todos os parâmetros do aider com descrições e categorização
- **ProfileBuilder**: assistente para construção de perfis de comando do aider
- **TUI**: interface de terminal para interação com o usuário
- **CommandExecutor**: constrói e executa o comando aider com os parâmetros corretos

## Desenvolvimento

### Configuração do Ambiente de Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/aider-start.git
cd aider-start

# Crie um ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale o pacote em modo de desenvolvimento
pip install -e .

# Instale as dependências de desenvolvimento
pip install pytest pytest-cov
```

### Executando os Testes

```bash
# Executar todos os testes
python -m pytest

# Executar testes com cobertura
python -m pytest --cov=aider_start

# Executar testes de um módulo específico
python -m pytest tests/test_config_manager.py
```

### Estrutura de Diretórios

```
aider-start/
├── aider_start/            # Código-fonte principal
│   ├── __init__.py
│   ├── config_manager.py   # Gerenciamento de configuração
│   ├── secure_config.py    # Gerenciamento de chaves API
│   ├── param_db.py         # Banco de dados de parâmetros
│   ├── profile_builder.py  # Construtor de perfis
│   ├── tui.py              # Interface de terminal
│   ├── command_executor.py # Executor de comandos
│   ├── exceptions.py       # Exceções personalizadas
│   ├── logger.py           # Sistema de logging
│   └── utils.py            # Funções utilitárias
├── tests/                  # Testes automatizados
├── docs/                   # Documentação
├── setup.py                # Script de instalação
├── README.md               # Este arquivo
└── LICENSE                 # Licença do projeto
```

### Convenções de Código

O projeto segue as convenções PEP 8 para código Python. Principais diretrizes:

- Use 4 espaços para indentação
- Linhas limitadas a 100 caracteres
- Docstrings em todas as classes e funções
- Anotações de tipo em novas implementações
- Testes para todas as novas funcionalidades

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do repositório
2. Crie um branch para sua funcionalidade (`git checkout -b feature/nova-funcionalidade`)
3. Implemente sua mudança e adicione testes
4. Verifique se todos os testes passam
5. Faça commit de suas alterações (`git commit -am 'Adiciona nova funcionalidade'`)
6. Envie para o branch (`git push origin feature/nova-funcionalidade`)
7. Abra um Pull Request

## Requisitos

- Python 3.8 ou superior
- aider (instalado separadamente)
- curses (windows-curses no Windows)

## Problemas Conhecidos

- Em sistemas Windows, a interface TUI pode ter limitações visuais devido às restrições do terminal.
- O aider deve estar instalado separadamente e disponível no PATH.

## Licença

MIT

## Autor

[Seu Nome]

---

Projeto criado para simplificar o uso do aider, uma excelente ferramenta de programação em par com IA desenvolvida por [Paul Gauthier](https://github.com/paul-gauthier). 