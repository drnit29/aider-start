"""
Módulo para gerenciamento seguro de configurações e chaves de API.
"""

import keyring
import getpass
from typing import Optional, Dict, Any

from .config_manager import ConfigManager
from .logger import get_logger
from .exceptions import ConfigError, ValidationError

# Obter logger para este módulo
logger = get_logger("secure_config")


class SecureConfigManager(ConfigManager):
    """
    Classe para gerenciamento seguro de configurações e chaves de API.
    
    Estende a classe ConfigManager para adicionar funcionalidades de
    armazenamento e recuperação segura de chaves de API e outras credenciais
    sensíveis usando o sistema keyring do sistema operacional.
    """
    
    def __init__(self, use_test_data=False):
        """
        Inicializa o gerenciador de configuração seguro.
        
        Args:
            use_test_data (bool): Se True, inicializa com dados de teste
        """
        super().__init__(use_test_data=use_test_data)
        self.service_name = 'aider-start'
        logger.debug("SecureConfigManager inicializado")
    
    def store_api_key(self, provider: str, api_key: str) -> bool:
        """
        Armazena uma chave de API de forma segura no keyring do sistema.
        
        Args:
            provider: Nome do provedor (ex: 'openai', 'anthropic')
            api_key: Chave de API a ser armazenada
            
        Returns:
            bool: True se a operação foi bem sucedida
            
        Raises:
            ConfigError: Se houver um erro ao armazenar a chave
        """
        if not provider or not isinstance(provider, str):
            raise ValidationError("Nome do provedor deve ser uma string não vazia")
        if not api_key or not isinstance(api_key, str):
            raise ValidationError("API key deve ser uma string não vazia")
            
        logger.debug(f"Armazenando chave de API para o provedor: {provider}")
        try:
            keyring.set_password(self.service_name, f"{provider}_api_key", api_key)
            logger.info(f"Chave de API para {provider} armazenada com sucesso")
            return True
        except Exception as e:
            error_msg = f"Erro ao armazenar chave de API para {provider}: {str(e)}"
            logger.error(error_msg)
            raise ConfigError(error_msg)
    
    def get_api_key(self, provider: str, prompt_if_missing: bool = False) -> Optional[str]:
        """
        Recupera uma chave de API do keyring do sistema.
        
        Args:
            provider: Nome do provedor (ex: 'openai', 'anthropic')
            prompt_if_missing: Se True, solicita a chave ao usuário caso não seja encontrada
            
        Returns:
            str: A chave de API ou None se não for encontrada
        """
        if not provider or not isinstance(provider, str):
            raise ValidationError("Nome do provedor deve ser uma string não vazia")
            
        logger.debug(f"Recuperando chave de API para o provedor: {provider}")
        try:
            key = keyring.get_password(self.service_name, f"{provider}_api_key")
            
            if not key and prompt_if_missing:
                logger.info(f"Chave de API para {provider} não encontrada, solicitando ao usuário")
                key = getpass.getpass(f"Digite a chave de API para {provider}: ")
                if key and key.strip():  # Verifica se a chave não é vazia ou apenas espaços
                    self.store_api_key(provider, key)
                else:
                    # Se o usuário forneceu uma string vazia, retornar None
                    return None
            
            return key
        except Exception as e:
            logger.error(f"Erro ao recuperar chave de API para {provider}: {str(e)}")
            return None
    
    def delete_api_key(self, provider: str) -> bool:
        """
        Remove uma chave de API do keyring do sistema.
        
        Args:
            provider: Nome do provedor
            
        Returns:
            bool: True se a operação foi bem sucedida
        """
        if not provider or not isinstance(provider, str):
            raise ValidationError("Nome do provedor deve ser uma string não vazia")
            
        logger.debug(f"Removendo chave de API para o provedor: {provider}")
        try:
            keyring.delete_password(self.service_name, f"{provider}_api_key")
            logger.info(f"Chave de API para {provider} removida com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover chave de API para {provider}: {str(e)}")
            return False
    
    def add_provider(self, name: str, provider_data: Dict[str, Any]) -> bool:
        """
        Adiciona ou atualiza um provedor, armazenando sua chave de API de forma segura.
        
        Args:
            name: Nome do provedor
            provider_data: Dados do provedor, incluindo a chave 'api_key' se disponível
            
        Returns:
            bool: True se a operação foi bem sucedida
        """
        # Extrair e armazenar a chave de API separadamente, se presente
        if 'api_key' in provider_data:
            api_key = provider_data.pop('api_key')
            self.store_api_key(name, api_key)
            logger.debug(f"Chave de API extraída e armazenada separadamente para {name}")
        
        # Continuar com a adição normal do provedor
        return super().add_provider(name, provider_data)
    
    def get_provider(self, name: str, include_api_key: bool = False) -> Optional[Dict[str, Any]]:
        """
        Retorna um provedor específico pelo nome, opcionalmente incluindo sua chave de API.
        
        Args:
            name: Nome do provedor
            include_api_key: Se True, inclui a chave de API nos dados retornados
            
        Returns:
            dict: Dados do provedor ou None se não for encontrado
        """
        provider = super().get_provider(name)
        
        if provider and include_api_key:
            # Criar uma cópia para não modificar o original
            provider_copy = provider.copy()
            api_key = self.get_api_key(name)
            if api_key:
                provider_copy['api_key'] = api_key
            return provider_copy
        
        return provider
    
    def delete_provider(self, name: str) -> bool:
        """
        Remove um provedor e sua chave de API.
        
        Args:
            name: Nome do provedor
            
        Returns:
            bool: True se a operação foi bem sucedida
        """
        # Tentar remover a chave de API primeiro, mas não falhar se não existir
        self.delete_api_key(name)
        
        # Continuar com a remoção normal do provedor
        return super().delete_provider(name)
    
    def add_endpoint(self, name: str, endpoint_data: Dict[str, Any]) -> bool:
        """
        Adiciona ou atualiza um endpoint, armazenando sua chave de API de forma segura.
        
        Args:
            name: Nome do endpoint
            endpoint_data: Dados do endpoint, incluindo a chave 'api_key' se disponível
            
        Returns:
            bool: True se a operação foi bem sucedida
        """
        # Extrair e armazenar a chave de API separadamente, se presente
        if 'api_key' in endpoint_data:
            api_key = endpoint_data.pop('api_key')
            self.store_api_key(f"endpoint_{name}", api_key)
            logger.debug(f"Chave de API extraída e armazenada separadamente para endpoint {name}")
        
        # Continuar com a adição normal do endpoint
        return super().add_endpoint(name, endpoint_data)
    
    def get_endpoint(self, name: str, include_api_key: bool = False) -> Optional[Dict[str, Any]]:
        """
        Retorna um endpoint específico pelo nome, opcionalmente incluindo sua chave de API.
        
        Args:
            name: Nome do endpoint
            include_api_key: Se True, inclui a chave de API nos dados retornados
            
        Returns:
            dict: Dados do endpoint ou None se não for encontrado
        """
        endpoint = super().get_endpoint(name)
        
        if endpoint and include_api_key:
            # Criar uma cópia para não modificar o original
            endpoint_copy = endpoint.copy()
            api_key = self.get_api_key(f"endpoint_{name}")
            if api_key:
                endpoint_copy['api_key'] = api_key
            return endpoint_copy
        
        return endpoint
    
    def delete_endpoint(self, name: str) -> bool:
        """
        Remove um endpoint e sua chave de API.
        
        Args:
            name: Nome do endpoint
            
        Returns:
            bool: True se a operação foi bem sucedida
        """
        # Tentar remover a chave de API primeiro, mas não falhar se não existir
        self.delete_api_key(f"endpoint_{name}")
        
        # Continuar com a remoção normal do endpoint
        return super().delete_endpoint(name) 