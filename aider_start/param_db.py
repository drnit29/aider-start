"""
Módulo para armazenamento e gerenciamento de parâmetros do aider.
"""


class ParameterDatabase:
    """Classe para gerenciamento do banco de dados de parâmetros do aider."""
    
    def __init__(self):
        """Inicializa o banco de dados de parâmetros."""
        self.parameters = {
            'model_options': {
                'model': {
                    'description': 'Modelo a ser usado (ex: gpt-4o, claude-3-sonnet)',
                    'type': 'string',
                    'default': None,
                    'env_var': 'AIDER_MODEL'
                },
                'reasoning-effort': {
                    'description': 'Define o parâmetro reasoning_effort da API',
                    'type': 'float',
                    'default': None,
                    'env_var': 'AIDER_REASONING_EFFORT'
                },
                'thinking-tokens': {
                    'description': 'Define o orçamento de tokens para pensamento em modelos que suportam',
                    'type': 'integer',
                    'default': None,
                    'env_var': 'AIDER_THINKING_TOKENS'
                },
                'edit-format': {
                    'description': 'Formato de edição que o LLM deve usar',
                    'type': 'string',
                    'default': None,
                    'env_var': 'AIDER_EDIT_FORMAT'
                },
                'architect': {
                    'description': 'Usar formato de edição architect para o chat principal',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_ARCHITECT'
                },
                'auto-accept-architect': {
                    'description': 'Aceitar automaticamente mudanças do architect',
                    'type': 'boolean',
                    'default': True,
                    'env_var': 'AIDER_AUTO_ACCEPT_ARCHITECT'
                },
                'verify-ssl': {
                    'description': 'Verificar certificado SSL ao conectar aos modelos',
                    'type': 'boolean',
                    'default': True,
                    'env_var': 'AIDER_VERIFY_SSL'
                },
                'timeout': {
                    'description': 'Timeout em segundos para chamadas de API',
                    'type': 'integer',
                    'default': None,
                    'env_var': 'AIDER_TIMEOUT'
                },
                'weak-model': {
                    'description': 'Modelo para mensagens de commit e sumarização do histórico de chat',
                    'type': 'string',
                    'default': None,
                    'env_var': 'AIDER_WEAK_MODEL'
                },
                'editor-model': {
                    'description': 'Modelo para tarefas de edição',
                    'type': 'string',
                    'default': None,
                    'env_var': 'AIDER_EDITOR_MODEL'
                },
                'editor-edit-format': {
                    'description': 'Formato de edição para o modelo de editor',
                    'type': 'string',
                    'default': None,
                    'env_var': 'AIDER_EDITOR_EDIT_FORMAT'
                },
                'show-model-warnings': {
                    'description': 'Mostrar avisos sobre modelos sem metadados disponíveis',
                    'type': 'boolean',
                    'default': True,
                    'env_var': 'AIDER_SHOW_MODEL_WARNINGS'
                },
                'max-chat-history-tokens': {
                    'description': 'Limite de tokens para histórico de chat antes da sumarização',
                    'type': 'integer',
                    'default': None,
                    'env_var': 'AIDER_MAX_CHAT_HISTORY_TOKENS'
                }
            },
            'api_options': {
                'openai-api-key': {
                    'description': 'Chave da API OpenAI',
                    'type': 'string',
                    'secret': True,
                    'env_var': 'AIDER_OPENAI_API_KEY'
                },
                'anthropic-api-key': {
                    'description': 'Chave da API Anthropic',
                    'type': 'string',
                    'secret': True,
                    'env_var': 'AIDER_ANTHROPIC_API_KEY'
                },
                'openai-api-base': {
                    'description': 'URL base da API',
                    'type': 'string',
                    'default': None,
                    'env_var': 'AIDER_OPENAI_API_BASE'
                },
                'api-key': {
                    'description': 'Define chave API para um provedor (ex: provider=xxx define PROVIDER_API_KEY=xxx)',
                    'type': 'string',
                    'secret': True,
                    'env_var': 'AIDER_API_KEY'
                },
                'set-env': {
                    'description': 'Define variável de ambiente para controlar configurações da API',
                    'type': 'string',
                    'default': [],
                    'env_var': 'AIDER_SET_ENV'
                }
            },
            'history_options': {
                'input-history-file': {
                    'description': 'Arquivo de histórico de entrada do chat',
                    'type': 'string',
                    'default': '.aider.input.history',
                    'env_var': 'AIDER_INPUT_HISTORY_FILE'
                },
                'chat-history-file': {
                    'description': 'Arquivo de histórico do chat',
                    'type': 'string',
                    'default': '.aider.chat.history.md',
                    'env_var': 'AIDER_CHAT_HISTORY_FILE'
                },
                'restore-chat-history': {
                    'description': 'Restaurar mensagens anteriores do histórico de chat',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_RESTORE_CHAT_HISTORY'
                },
                'llm-history-file': {
                    'description': 'Registrar conversa com o LLM neste arquivo',
                    'type': 'string',
                    'default': None,
                    'env_var': 'AIDER_LLM_HISTORY_FILE'
                }
            },
            'git_options': {
                'git': {
                    'description': 'Procurar por repositório git',
                    'type': 'boolean',
                    'default': True,
                    'env_var': 'AIDER_GIT'
                },
                'gitignore': {
                    'description': 'Adicionar .aider* ao .gitignore',
                    'type': 'boolean',
                    'default': True,
                    'env_var': 'AIDER_GITIGNORE'
                },
                'aiderignore': {
                    'description': 'Arquivo de ignorar do aider',
                    'type': 'string',
                    'default': '.aiderignore',
                    'env_var': 'AIDER_AIDERIGNORE'
                },
                'subtree-only': {
                    'description': 'Considerar apenas arquivos na subárvore atual do repositório git',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_SUBTREE_ONLY'
                },
                'auto-commits': {
                    'description': 'Commit automático de mudanças do LLM',
                    'type': 'boolean',
                    'default': True,
                    'env_var': 'AIDER_AUTO_COMMITS'
                },
                'dirty-commits': {
                    'description': 'Commit quando o repositório é encontrado sujo',
                    'type': 'boolean',
                    'default': True,
                    'env_var': 'AIDER_DIRTY_COMMITS'
                },
                'attribute-author': {
                    'description': 'Atribuir mudanças de código do aider no nome do autor do git',
                    'type': 'boolean',
                    'default': True,
                    'env_var': 'AIDER_ATTRIBUTE_AUTHOR'
                },
                'commit': {
                    'description': 'Commit de todas as mudanças pendentes e sair',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_COMMIT'
                },
                'commit-prompt': {
                    'description': 'Prompt personalizado para gerar mensagens de commit',
                    'type': 'string',
                    'default': None,
                    'env_var': 'AIDER_COMMIT_PROMPT'
                }
            },
            'input_output': {
                'file': {
                    'description': 'Especifica um arquivo para editar (pode ser usado múltiplas vezes)',
                    'type': 'array',
                    'default': [],
                    'env_var': 'AIDER_FILE'
                },
                'read': {
                    'description': 'Especifica um arquivo somente leitura (pode ser usado múltiplas vezes)',
                    'type': 'array',
                    'default': [],
                    'env_var': 'AIDER_READ'
                },
                'dark-mode': {
                    'description': 'Usar cores adequadas para terminal com fundo escuro',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_DARK_MODE'
                },
                'light-mode': {
                    'description': 'Usar cores adequadas para terminal com fundo claro',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_LIGHT_MODE'
                },
                'pretty': {
                    'description': 'Habilitar saída bonita e colorida',
                    'type': 'boolean',
                    'default': True,
                    'env_var': 'AIDER_PRETTY'
                },
                'stream': {
                    'description': 'Habilitar respostas em streaming',
                    'type': 'boolean',
                    'default': True,
                    'env_var': 'AIDER_STREAM'
                },
                'show-diffs': {
                    'description': 'Mostrar diffs ao fazer commit de mudanças',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_SHOW_DIFFS'
                }
            },
            'repomap_options': {
                'map-tokens': {
                    'description': 'Número sugerido de tokens para o mapa de repositório, use 0 para desabilitar',
                    'type': 'integer',
                    'default': None,
                    'env_var': 'AIDER_MAP_TOKENS'
                },
                'map-refresh': {
                    'description': 'Controla com que frequência o mapa de repositório é atualizado',
                    'type': 'string',
                    'default': 'auto',
                    'env_var': 'AIDER_MAP_REFRESH'
                },
                'map-multiplier-no-files': {
                    'description': 'Multiplicador para tokens de mapa quando nenhum arquivo é especificado',
                    'type': 'float',
                    'default': 2,
                    'env_var': 'AIDER_MAP_MULTIPLIER_NO_FILES'
                }
            },
            'fixing_options': {
                'lint': {
                    'description': 'Linting e correção de arquivos fornecidos ou sujos se nenhum fornecido',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_LINT'
                },
                'lint-cmd': {
                    'description': 'Especifica comandos de lint para diferentes linguagens',
                    'type': 'array',
                    'default': [],
                    'env_var': 'AIDER_LINT_CMD'
                },
                'auto-lint': {
                    'description': 'Linting automático após mudanças',
                    'type': 'boolean',
                    'default': True,
                    'env_var': 'AIDER_AUTO_LINT'
                },
                'test-cmd': {
                    'description': 'Especifica comando para executar testes',
                    'type': 'array',
                    'default': [],
                    'env_var': 'AIDER_TEST_CMD'
                },
                'auto-test': {
                    'description': 'Teste automático após mudanças',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_AUTO_TEST'
                },
                'test': {
                    'description': 'Executar testes, corrigir problemas encontrados e então sair',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_TEST'
                }
            },
            'voice_options': {
                'voice-format': {
                    'description': 'Formato de áudio para gravação de voz (wav, webm, mp3)',
                    'type': 'string',
                    'default': 'wav',
                    'env_var': 'AIDER_VOICE_FORMAT'
                },
                'voice-language': {
                    'description': 'Idioma para voz usando código ISO 639-1',
                    'type': 'string',
                    'default': 'en',
                    'env_var': 'AIDER_VOICE_LANGUAGE'
                },
                'voice-input-device': {
                    'description': 'Nome do dispositivo de entrada para gravação de voz',
                    'type': 'string',
                    'default': None,
                    'env_var': 'AIDER_VOICE_INPUT_DEVICE'
                }
            },
            'mode_options': {
                'message': {
                    'description': 'Mensagem única para enviar ao LLM, processar resposta e sair',
                    'type': 'string',
                    'default': None,
                    'env_var': 'AIDER_MESSAGE'
                },
                'message-file': {
                    'description': 'Arquivo contendo mensagem para enviar ao LLM, processar resposta e sair',
                    'type': 'string',
                    'default': None,
                    'env_var': 'AIDER_MESSAGE_FILE'
                },
                'gui': {
                    'description': 'Executar aider no navegador',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_GUI'
                },
                'copy-paste': {
                    'description': 'Habilitar copiar/colar automático do chat entre aider e UI web',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_COPY_PASTE'
                }
            },
            'misc_options': {
                'vim': {
                    'description': 'Usar modo de edição VI no terminal',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_VIM'
                },
                'chat-language': {
                    'description': 'Idioma a ser usado no chat',
                    'type': 'string',
                    'default': None,
                    'env_var': 'AIDER_CHAT_LANGUAGE'
                },
                'verbose': {
                    'description': 'Habilitar saída detalhada',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_VERBOSE'
                },
                'encoding': {
                    'description': 'Codificação para entrada e saída',
                    'type': 'string',
                    'default': 'utf-8',
                    'env_var': 'AIDER_ENCODING'
                },
                'line-endings': {
                    'description': 'Terminações de linha ao escrever arquivos',
                    'type': 'string',
                    'default': 'platform',
                    'env_var': 'AIDER_LINE_ENDINGS'
                },
                'config': {
                    'description': 'Arquivo de configuração',
                    'type': 'string',
                    'default': None,
                    'env_var': None
                },
                'env-file': {
                    'description': 'Arquivo .env para carregar',
                    'type': 'string',
                    'default': '.env',
                    'env_var': 'AIDER_ENV_FILE'
                },
                'yes-always': {
                    'description': 'Sempre dizer sim a cada confirmação',
                    'type': 'boolean',
                    'default': False,
                    'env_var': 'AIDER_YES_ALWAYS'
                }
            }
        }
        
    def get_all_parameters(self):
        """Retorna todos os parâmetros."""
        return self.parameters
        
    def get_category(self, category):
        """Retorna os parâmetros de uma categoria específica."""
        return self.parameters.get(category, {})
        
    def get_parameter(self, category, param_name):
        """Retorna um parâmetro específico de uma categoria."""
        return self.get_category(category).get(param_name)
    
    def get_categories(self):
        """Retorna a lista de todas as categorias disponíveis."""
        return list(self.parameters.keys())
    
    def format_parameter_type(self, param_data):
        """
        Formata o tipo de um parâmetro para exibição.
        
        Args:
            param_data: Dicionário de dados do parâmetro
            
        Returns:
            String com o tipo formatado
        """
        # Verifica se o dicionário de parâmetros é válido
        if not param_data:
            return 'desconhecido'
            
        param_type = param_data.get('type', 'desconhecido')
        
        # Traduz o tipo para português
        translations = {
            'string': 'string',
            'boolean': 'booleano',
            'integer': 'inteiro',
            'float': 'decimal',
            'array': 'lista',
            'list': 'lista'
        }
        
        # Verifica se é um parâmetro secreto
        if param_data.get('secret', False):
            return 'senha'
        
        # Adiciona informações adicionais para listas
        if param_type == 'array' or param_type == 'list':
            item_type = param_data.get('items', {}).get('type', 'item')
            return f"lista de {item_type}s"
        
        # Retorna a tradução ou o tipo original se não tiver tradução
        return translations.get(param_type, param_type)
    
    def get_parameters_by_filter(self, filter_func):
        """
        Retorna parâmetros que atendem a um critério específico.
        
        Args:
            filter_func: Função que recebe um parâmetro e retorna True/False
            
        Returns:
            Dict com parâmetros filtrados organizados por categoria
        """
        result = {}
        for category, params in self.parameters.items():
            filtered_params = {k: v for k, v in params.items() if filter_func(v)}
            if filtered_params:
                result[category] = filtered_params
        return result

# Código de teste quando executado diretamente
if __name__ == "__main__":
    db = ParameterDatabase()
    print("Categorias disponíveis:")
    categories = db.get_categories()
    print(categories)
    
    # Exemplo de acesso a parâmetros de uma categoria
    print("\nParâmetros da categoria 'model_options':")
    model_params = db.get_category("model_options")
    for name, param in model_params.items():
        print(f"- {name}: {param.get('description')} ({db.format_parameter_type(param)})")
        if param.get('default') is not None:
            print(f"  Valor padrão: {param.get('default')}") 