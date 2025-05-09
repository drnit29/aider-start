"""
Exceções personalizadas para o aider-start.
"""


class AiderStartError(Exception):
    """Classe base para todas as exceções do aider-start."""
    pass


class ConfigError(AiderStartError):
    """Classe base para erros relacionados à configuração."""
    pass


class FileAccessError(ConfigError):
    """Erro ao acessar arquivos de configuração."""
    pass


class JSONParseError(ConfigError):
    """Erro ao analisar JSON de configuração."""
    pass


class ValidationError(ConfigError):
    """Erro de validação de dados de configuração."""
    pass


class ConfigNotFoundError(ConfigError):
    """Erro quando um item de configuração não é encontrado."""
    pass


class ProfileError(ConfigError):
    """Classe base para erros relacionados a perfis."""
    pass


class ProfileNotFoundError(ProfileError):
    """Erro quando um perfil não é encontrado."""
    pass


class ProfileExistsError(ProfileError):
    """Erro quando se tenta criar um perfil que já existe."""
    pass


class ProviderError(ConfigError):
    """Classe base para erros relacionados a provedores."""
    pass


class ProviderNotFoundError(ProviderError):
    """Erro quando um provedor não é encontrado."""
    pass


class EndpointError(ConfigError):
    """Erro base para problemas relacionados a endpoints."""
    pass


class EndpointNotFoundError(EndpointError):
    """Endpoint não encontrado."""
    pass


# Novas exceções para CommandExecutor (Tarefa 22.3)
class CommandError(Exception):
    """Classe base para erros relacionados ao CommandExecutor."""
    pass


class CommandBuildError(CommandError):
    """Erro durante a construção de um comando."""
    pass


class CommandExecutionError(CommandError):
    """Erro durante a execução de um comando."""
    pass 