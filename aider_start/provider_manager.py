"""
Módulo para gerenciamento de provedores de API de LLM.
"""

from typing import Dict, List, Optional, Any
import keyring

from .secure_config import SecureConfigManager
from .logger import get_logger
from .exceptions import (
    ProviderError, ProviderNotFoundError, ValidationError,
    ConfigError
)

# Obter logger para este módulo
logger = get_logger("provider_manager")


class ProviderManager:
    """
    Gerencia os provedores de LLM e suas configurações.
    
    Esta classe é responsável por gerenciar os provedores de API de LLM,
    incluindo armazenamento seguro de chaves de API, configuração de modelos,
    e operações CRUD para provedores.
    """
    
    def __init__(self, config_manager: Optional[SecureConfigManager] = None):
        """
        Inicializa o gerenciador de provedores.
        
        Args:
            config_manager: Instância de SecureConfigManager para armazenamento de configurações.
                Se None, uma nova instância será criada.
        """
        logger.debug("Inicializando ProviderManager")
        self.config_manager = config_manager or SecureConfigManager()
        
        # Define provedores padrão conhecidos se não existirem na configuração
        self._ensure_default_providers()
    
    def _ensure_default_providers(self) -> None:
        """
        Garante que os provedores padrão conhecidos estejam registrados na configuração.
        Se não existirem provedores na configuração, adiciona os provedores padrão.
        """
        providers = self.config_manager.get_providers()
        
        # Se não há provedores configurados, adiciona os padrões
        if not providers:
            logger.info("Adicionando provedores padrão")
            default_providers = {
                "openai": {
                    "description": "OpenAI API (GPT-3.5, GPT-4, etc.)",
                    "api_url": "https://api.openai.com/v1",
                    "models": [
                        "gpt-3.5-turbo", 
                        "gpt-4", 
                        "gpt-4-turbo",
                        "gpt-4-vision"
                    ]
                },
                "anthropic": {
                    "description": "Anthropic API (Claude)",
                    "api_url": "https://api.anthropic.com/v1",
                    "models": [
                        "claude-1", 
                        "claude-2", 
                        "claude-instant-1",
                        "claude-3-opus",
                        "claude-3-sonnet",
                        "claude-3-haiku"
                    ]
                },
                "mistral": {
                    "description": "Mistral AI API",
                    "api_url": "https://api.mistral.ai/v1",
                    "models": [
                        "mistral-tiny", 
                        "mistral-small", 
                        "mistral-medium",
                        "mistral-large"
                    ]
                }
            }
            
            for name, provider_data in default_providers.items():
                try:
                    self.config_manager.add_provider(name, provider_data)
                    logger.info(f"Provedor padrão adicionado: {name}")
                except Exception as e:
                    logger.error(f"Erro ao adicionar provedor padrão {name}: {e}")
    
    def get_providers(self) -> Dict[str, Any]:
        """
        Retorna todos os provedores configurados.
        
        Returns:
            Dict[str, Any]: Dicionário com todos os provedores
        """
        return self.config_manager.get_providers()
    
    def get_provider(self, name: str, include_api_key: bool = False) -> Optional[Dict[str, Any]]:
        """
        Retorna um provedor específico pelo nome.
        
        Args:
            name: Nome do provedor
            include_api_key: Se True, inclui a chave de API nos dados retornados
            
        Returns:
            Optional[Dict[str, Any]]: Dados do provedor ou None se não for encontrado
        """
        if hasattr(self.config_manager, 'get_provider') and callable(getattr(self.config_manager, 'get_provider')):
            return self.config_manager.get_provider(name, include_api_key)
        else:
            # Fallback para o caso do ConfigManager não ter o método especializado
            provider = self.config_manager.get_providers().get(name)
            
            if provider and include_api_key:
                provider_copy = provider.copy()
                api_key = self.config_manager.get_api_key(name)
                if api_key:
                    provider_copy['api_key'] = api_key
                return provider_copy
            
            return provider
    
    def add_provider(self, name: str, provider_data: Dict[str, Any]) -> bool:
        """
        Adiciona ou atualiza um provedor.
        
        Args:
            name: Nome do provedor
            provider_data: Dados do provedor
            
        Returns:
            bool: True se a operação foi bem sucedida
            
        Raises:
            ValidationError: Se os dados do provedor forem inválidos
        """
        # Validar nome do provedor
        if not name or not isinstance(name, str):
            error_msg = "Nome do provedor deve ser uma string não vazia"
            logger.error(error_msg)
            raise ValidationError(error_msg)
            
        # Validar dados do provedor
        required_keys = []
        optional_keys = ['api_url', 'models', 'api_key', 'description']
        
        missing_keys = [key for key in required_keys if key not in provider_data]
        if missing_keys:
            error_msg = f"Dados do provedor ausentes: {', '.join(missing_keys)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)
        
        # Filtra apenas as chaves válidas
        filtered_data = {k: v for k, v in provider_data.items() 
                        if k in required_keys + optional_keys}
        
        return self.config_manager.add_provider(name, filtered_data)
    
    def delete_provider(self, name: str) -> bool:
        """
        Remove um provedor.
        
        Args:
            name: Nome do provedor
            
        Returns:
            bool: True se a operação foi bem sucedida
            
        Raises:
            ProviderNotFoundError: Se o provedor não for encontrado
        """
        if not self.get_provider(name):
            error_msg = f"Provedor não encontrado: {name}"
            logger.error(error_msg)
            raise ProviderNotFoundError(error_msg)
            
        return self.config_manager.delete_provider(name)
    
    def set_api_key(self, provider_name: str, api_key: str) -> bool:
        """
        Define a chave de API para um provedor.
        
        Args:
            provider_name: Nome do provedor
            api_key: Chave de API
            
        Returns:
            bool: True se a operação foi bem sucedida
            
        Raises:
            ProviderNotFoundError: Se o provedor não for encontrado
            ValidationError: Se a chave de API for inválida
        """
        if not self.get_provider(provider_name):
            error_msg = f"Provedor não encontrado: {provider_name}"
            logger.error(error_msg)
            raise ProviderNotFoundError(error_msg)
            
        if not api_key or not isinstance(api_key, str):
            error_msg = "API key deve ser uma string não vazia"
            logger.error(error_msg)
            raise ValidationError(error_msg)
            
        return self.config_manager.store_api_key(provider_name, api_key)
    
    def get_api_key(self, provider_name: str, prompt_if_missing: bool = False) -> Optional[str]:
        """
        Recupera a chave de API de um provedor.
        
        Args:
            provider_name: Nome do provedor
            prompt_if_missing: Se True, solicita a chave ao usuário caso não seja encontrada
            
        Returns:
            Optional[str]: Chave de API ou None se não for encontrada
        """
        if not self.get_provider(provider_name):
            logger.warning(f"Provedor não encontrado: {provider_name}")
            return None
            
        return self.config_manager.get_api_key(provider_name, prompt_if_missing)
    
    def get_provider_models(self, provider_name: str) -> List[str]:
        """
        Retorna os modelos disponíveis para um provedor específico.
        
        Args:
            provider_name: Nome do provedor
            
        Returns:
            List[str]: Lista de nomes de modelos
            
        Raises:
            ProviderNotFoundError: Se o provedor não for encontrado
        """
        provider = self.get_provider(provider_name)
        if not provider:
            error_msg = f"Provedor não encontrado: {provider_name}"
            logger.error(error_msg)
            raise ProviderNotFoundError(error_msg)
            
        return provider.get('models', [])
    
    def add_provider_model(self, provider_name: str, model_name: str) -> bool:
        """
        Adiciona um modelo a um provedor.
        
        Args:
            provider_name: Nome do provedor
            model_name: Nome do modelo
            
        Returns:
            bool: True se a operação foi bem sucedida
            
        Raises:
            ProviderNotFoundError: Se o provedor não for encontrado
            ValidationError: Se o nome do modelo for inválido
        """
        if not model_name or not isinstance(model_name, str):
            error_msg = "Nome do modelo deve ser uma string não vazia"
            logger.error(error_msg)
            raise ValidationError(error_msg)
            
        # Verificar primeiro se o provedor existe, antes de qualquer outra operação
        provider = self.get_provider(provider_name)
        if not provider:
            error_msg = f"Provedor não encontrado: {provider_name}"
            logger.error(error_msg)
            raise ProviderNotFoundError(error_msg)
            
        if hasattr(self.config_manager, 'add_provider_model') and callable(getattr(self.config_manager, 'add_provider_model')):
            return self.config_manager.add_provider_model(provider_name, model_name)
        else:
            # Implementação manual caso o método não exista no ConfigManager                
            # Criar cópia para modificação
            provider_copy = provider.copy()
            models = provider_copy.get('models', [])
            
            if model_name not in models:
                models.append(model_name)
                provider_copy['models'] = models
                return self.config_manager.add_provider(provider_name, provider_copy)
            
            return True
    
    def remove_provider_model(self, provider_name: str, model_name: str) -> bool:
        """
        Remove um modelo de um provedor.
        
        Args:
            provider_name: Nome do provedor
            model_name: Nome do modelo
            
        Returns:
            bool: True se a operação foi bem sucedida
            
        Raises:
            ProviderNotFoundError: Se o provedor não for encontrado
        """
        # Verificar primeiro se o provedor existe, antes de qualquer outra operação
        provider = self.get_provider(provider_name)
        if not provider:
            error_msg = f"Provedor não encontrado: {provider_name}"
            logger.error(error_msg)
            raise ProviderNotFoundError(error_msg)
            
        if hasattr(self.config_manager, 'remove_provider_model') and callable(getattr(self.config_manager, 'remove_provider_model')):
            return self.config_manager.remove_provider_model(provider_name, model_name)
        else:
            # Implementação manual caso o método não exista no ConfigManager
            # Criar cópia para modificação
            provider_copy = provider.copy()
            models = provider_copy.get('models', [])
            
            if model_name in models:
                models.remove(model_name)
                provider_copy['models'] = models
                return self.config_manager.add_provider(provider_name, provider_copy)
            
            return True
    
    def has_api_key(self, provider_name: str) -> bool:
        """
        Verifica se um provedor tem uma chave de API configurada.
        
        Args:
            provider_name: Nome do provedor
            
        Returns:
            bool: True se o provedor tiver uma chave de API configurada
        """
        api_key = self.get_api_key(provider_name)
        return api_key is not None and len(api_key) > 0 