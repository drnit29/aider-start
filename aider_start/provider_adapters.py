"""
Módulo com adaptadores para diferentes provedores de API de LLM.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import requests
import json

from .logger import get_logger

# Obter logger para este módulo
logger = get_logger("provider_adapters")


class BaseProviderAdapter(ABC):
    """Classe base para adaptadores de provedores de LLM."""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Inicializa o adaptador base.
        
        Args:
            api_key: Chave de API do provedor.
            api_url: URL base da API do provedor.
        """
        self.api_key = api_key
        self.api_url = api_url
        self.name = "base"  # Nome do provedor, deve ser sobrescrito nas subclasses
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """
        Valida se a chave de API é válida.
        
        Returns:
            bool: True se a chave for válida.
        """
        pass
    
    @abstractmethod
    def get_models(self) -> List[str]:
        """
        Retorna a lista de modelos disponíveis para este provedor.
        
        Returns:
            List[str]: Lista de nomes de modelos.
        """
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida e normaliza os parâmetros para uso com este provedor.
        
        Args:
            parameters: Dicionário de parâmetros.
            
        Returns:
            Dict[str, Any]: Parâmetros validados e normalizados.
        """
        pass


class OpenAIAdapter(BaseProviderAdapter):
    """Adaptador para a API da OpenAI."""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Inicializa o adaptador da OpenAI.
        
        Args:
            api_key: Chave de API da OpenAI.
            api_url: URL base da API da OpenAI (padrão: https://api.openai.com/v1).
        """
        super().__init__(api_key, api_url or "https://api.openai.com/v1")
        self.name = "openai"
        logger.debug("Adaptador OpenAI inicializado")
    
    def validate_api_key(self) -> bool:
        """
        Valida se a chave de API da OpenAI é válida.
        
        Returns:
            bool: True se a chave for válida.
        """
        if not self.api_key:
            logger.warning("Chave de API da OpenAI não fornecida")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.api_url}/models", headers=headers)
            
            if response.status_code == 200:
                logger.info("Chave de API da OpenAI validada com sucesso")
                return True
            else:
                logger.warning(f"Falha na validação da chave de API da OpenAI: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Erro ao validar chave de API da OpenAI: {e}")
            return False
    
    def get_models(self) -> List[str]:
        """
        Retorna a lista de modelos disponíveis na API da OpenAI.
        
        Returns:
            List[str]: Lista de nomes de modelos.
        """
        if not self.api_key:
            logger.warning("Chave de API da OpenAI não fornecida")
            return []
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.api_url}/models", headers=headers)
            
            if response.status_code == 200:
                models_data = response.json()
                models = [model["id"] for model in models_data["data"] 
                          if model["id"].startswith(("gpt-", "text-embedding-"))]
                logger.info(f"Recuperados {len(models)} modelos da OpenAI")
                return models
            else:
                logger.warning(f"Falha ao obter modelos da OpenAI: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Erro ao obter modelos da OpenAI: {e}")
            return []
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida e normaliza os parâmetros para uso com a API da OpenAI.
        
        Args:
            parameters: Dicionário de parâmetros do aider.
            
        Returns:
            Dict[str, Any]: Parâmetros validados e normalizados.
        """
        validated = parameters.copy()
        
        # Mapeamento de parâmetros do aider para a OpenAI
        param_map = {
            "temperatura": "temperature",
            "max_tokens": "max_tokens",
            "top_p": "top_p",
            "frequency_penalty": "frequency_penalty",
            "presence_penalty": "presence_penalty"
        }
        
        # Renomear parâmetros conforme necessário
        for aider_param, openai_param in param_map.items():
            if aider_param in validated:
                validated[openai_param] = validated.pop(aider_param)
        
        # Ajustar valores de temperatura
        if "temperature" in validated and validated["temperature"] > 2.0:
            logger.warning("Temperatura ajustada para o máximo permitido (2.0)")
            validated["temperature"] = 2.0
        
        if "model" in validated:
            # Garantir que o modelo é válido para a OpenAI
            if not validated["model"].startswith(("gpt-", "text-embedding-")):
                logger.warning(f"Modelo {validated['model']} pode não ser compatível com a OpenAI")
        
        return validated


class AnthropicAdapter(BaseProviderAdapter):
    """Adaptador para a API da Anthropic."""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Inicializa o adaptador da Anthropic.
        
        Args:
            api_key: Chave de API da Anthropic.
            api_url: URL base da API da Anthropic (padrão: https://api.anthropic.com/v1).
        """
        super().__init__(api_key, api_url or "https://api.anthropic.com/v1")
        self.name = "anthropic"
        logger.debug("Adaptador Anthropic inicializado")
    
    def validate_api_key(self) -> bool:
        """
        Valida se a chave de API da Anthropic é válida.
        
        Returns:
            bool: True se a chave for válida.
        """
        if not self.api_key:
            logger.warning("Chave de API da Anthropic não fornecida")
            return False
        
        try:
            # A Anthropic não tem um endpoint específico para validação de chave
            # Verificamos se a chave parece ser válida
            if not self.api_key.startswith(("sk-ant-", "sk-")):
                logger.warning("Formato da chave de API da Anthropic parece inválido")
                return False
                
            # Poderíamos fazer uma chamada para um endpoint como "messages" com
            # um payload mínimo, mas isso pode gerar custos desnecessários
            
            # Por enquanto, apenas verificamos o formato da chave
            logger.info("Formato da chave de API da Anthropic parece válido")
            return True
        except Exception as e:
            logger.error(f"Erro ao validar chave de API da Anthropic: {e}")
            return False
    
    def get_models(self) -> List[str]:
        """
        Retorna a lista de modelos disponíveis na API da Anthropic.
        
        Como a Anthropic não tem um endpoint para listar modelos publicamente,
        retornamos uma lista estática dos modelos conhecidos.
        
        Returns:
            List[str]: Lista de nomes de modelos.
        """
        # A Anthropic não tem um endpoint para listar modelos publicamente
        # Retornamos uma lista estática dos modelos conhecidos
        models = [
            "claude-1",
            "claude-2",
            "claude-instant-1",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku"
        ]
        
        logger.info(f"Usando lista estática de {len(models)} modelos da Anthropic")
        return models
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida e normaliza os parâmetros para uso com a API da Anthropic.
        
        Args:
            parameters: Dicionário de parâmetros do aider.
            
        Returns:
            Dict[str, Any]: Parâmetros validados e normalizados.
        """
        validated = parameters.copy()
        
        # Mapeamento de parâmetros do aider para a Anthropic
        param_map = {
            "temperatura": "temperature",
            "max_tokens": "max_tokens_to_sample",
            "top_p": "top_p"
        }
        
        # Renomear parâmetros conforme necessário
        for aider_param, anthropic_param in param_map.items():
            if aider_param in validated:
                validated[anthropic_param] = validated.pop(aider_param)
        
        # Ajustar valores de temperatura
        if "temperature" in validated and validated["temperature"] > 1.0:
            logger.warning("Temperatura ajustada para o máximo permitido (1.0)")
            validated["temperature"] = 1.0
        
        # A Anthropic usa "model" em vez de "engine"
        if "engine" in validated:
            validated["model"] = validated.pop("engine")
        
        # Verificar se o modelo é válido para a Anthropic
        if "model" in validated:
            valid_prefix = ("claude-1", "claude-2", "claude-instant", "claude-3")
            if not any(validated["model"].startswith(prefix) for prefix in valid_prefix):
                logger.warning(f"Modelo {validated['model']} pode não ser compatível com a Anthropic")
        
        return validated


class MistralAdapter(BaseProviderAdapter):
    """Adaptador para a API da Mistral AI."""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Inicializa o adaptador da Mistral AI.
        
        Args:
            api_key: Chave de API da Mistral AI.
            api_url: URL base da API da Mistral AI (padrão: https://api.mistral.ai/v1).
        """
        super().__init__(api_key, api_url or "https://api.mistral.ai/v1")
        self.name = "mistral"
        logger.debug("Adaptador Mistral AI inicializado")
    
    def validate_api_key(self) -> bool:
        """
        Valida se a chave de API da Mistral AI é válida.
        
        Returns:
            bool: True se a chave for válida.
        """
        if not self.api_key:
            logger.warning("Chave de API da Mistral AI não fornecida")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.api_url}/models", headers=headers)
            
            if response.status_code == 200:
                logger.info("Chave de API da Mistral AI validada com sucesso")
                return True
            else:
                logger.warning(f"Falha na validação da chave de API da Mistral AI: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Erro ao validar chave de API da Mistral AI: {e}")
            return False
    
    def get_models(self) -> List[str]:
        """
        Retorna a lista de modelos disponíveis na API da Mistral AI.
        
        Returns:
            List[str]: Lista de nomes de modelos.
        """
        if not self.api_key:
            logger.warning("Chave de API da Mistral AI não fornecida")
            return []
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.api_url}/models", headers=headers)
            
            if response.status_code == 200:
                models_data = response.json()
                models = [model["id"] for model in models_data["data"]]
                logger.info(f"Recuperados {len(models)} modelos da Mistral AI")
                return models
            else:
                logger.warning(f"Falha ao obter modelos da Mistral AI: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Erro ao obter modelos da Mistral AI: {e}")
            return []
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida e normaliza os parâmetros para uso com a API da Mistral AI.
        
        Args:
            parameters: Dicionário de parâmetros do aider.
            
        Returns:
            Dict[str, Any]: Parâmetros validados e normalizados.
        """
        validated = parameters.copy()
        
        # Mapeamento de parâmetros do aider para a Mistral AI
        param_map = {
            "temperatura": "temperature",
            "max_tokens": "max_tokens",
            "top_p": "top_p"
        }
        
        # Renomear parâmetros conforme necessário
        for aider_param, mistral_param in param_map.items():
            if aider_param in validated:
                validated[mistral_param] = validated.pop(aider_param)
        
        # Ajustar valores de temperatura
        if "temperature" in validated and validated["temperature"] > 1.0:
            logger.warning("Temperatura ajustada para o máximo permitido (1.0)")
            validated["temperature"] = 1.0
        
        # Verificar se o modelo é válido para a Mistral AI
        if "model" in validated:
            valid_prefix = ("mistral-", "open-")
            if not any(validated["model"].startswith(prefix) for prefix in valid_prefix):
                logger.warning(f"Modelo {validated['model']} pode não ser compatível com a Mistral AI")
        
        return validated


# Função factory para obter o adaptador correto para um provedor
def get_provider_adapter(provider_name: str, api_key: Optional[str] = None, api_url: Optional[str] = None) -> Optional[BaseProviderAdapter]:
    """
    Retorna o adaptador adequado para o provedor especificado.
    
    Args:
        provider_name: Nome do provedor.
        api_key: Chave de API (opcional).
        api_url: URL base da API (opcional).
        
    Returns:
        BaseProviderAdapter: Instância do adaptador correspondente ou None se o provedor não for suportado.
    """
    adapters = {
        "openai": OpenAIAdapter,
        "anthropic": AnthropicAdapter,
        "mistral": MistralAdapter
    }
    
    adapter_class = adapters.get(provider_name.lower())
    if not adapter_class:
        logger.warning(f"Provedor não suportado: {provider_name}")
        return None
    
    return adapter_class(api_key, api_url) 