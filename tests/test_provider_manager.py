"""
Testes para o módulo provider_manager.py
"""

import unittest
import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Adiciona o diretório raiz ao path para importação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aider_start.provider_manager import ProviderManager
from aider_start.secure_config import SecureConfigManager
from aider_start.exceptions import ProviderNotFoundError, ValidationError


class TestProviderManager:
    """Testes para a classe ProviderManager."""
    
    @pytest.fixture
    def mock_secure_config(self):
        """Fixture para mock do SecureConfigManager."""
        with patch('aider_start.provider_manager.SecureConfigManager') as mock:
            config_mock = MagicMock(spec=SecureConfigManager)
            
            # Configurar comportamento do mock
            config_mock.get_providers.return_value = {
                "openai": {
                    "description": "OpenAI API",
                    "api_url": "https://api.openai.com/v1",
                    "models": ["gpt-3.5-turbo", "gpt-4"]
                },
                "anthropic": {
                    "description": "Anthropic API",
                    "api_url": "https://api.anthropic.com/v1",
                    "models": ["claude-1", "claude-2"]
                }
            }
            
            config_mock.get_provider.side_effect = lambda name, include_api_key=False: (
                {
                    "description": "OpenAI API",
                    "api_url": "https://api.openai.com/v1",
                    "models": ["gpt-3.5-turbo", "gpt-4"],
                    **({"api_key": "test-key"} if include_api_key else {})
                } if name == "openai" else
                {
                    "description": "Anthropic API",
                    "api_url": "https://api.anthropic.com/v1",
                    "models": ["claude-1", "claude-2"],
                    **({"api_key": "test-key"} if include_api_key else {})
                } if name == "anthropic" else
                None
            )
            
            config_mock.add_provider.return_value = True
            config_mock.delete_provider.return_value = True
            config_mock.get_api_key.return_value = "test-key"
            config_mock.store_api_key.return_value = True
            
            # Retornar o mock configurado como instância
            mock.return_value = config_mock
            yield config_mock
    
    @pytest.fixture
    def provider_manager(self, mock_secure_config):
        """Fixture para o ProviderManager com mock do config manager."""
        # Impedir que _ensure_default_providers seja chamado durante os testes
        with patch('aider_start.provider_manager.ProviderManager._ensure_default_providers'):
            return ProviderManager(mock_secure_config)
    
    def test_init(self, mock_secure_config):
        """Testa a inicialização do ProviderManager."""
        # Caso 1: Com config_manager fornecido
        with patch('aider_start.provider_manager.ProviderManager._ensure_default_providers'):
            manager = ProviderManager(mock_secure_config)
            assert manager.config_manager == mock_secure_config
        
        # Caso 2: Sem config_manager (deve criar um novo)
        with patch('aider_start.provider_manager.SecureConfigManager') as mock_config_class:
            with patch('aider_start.provider_manager.ProviderManager._ensure_default_providers'):
                mock_config_instance = MagicMock()
                mock_config_class.return_value = mock_config_instance
                
                manager = ProviderManager()
                assert manager.config_manager == mock_config_instance
    
    def test_ensure_default_providers(self, mock_secure_config):
        """Testa a adição de provedores padrão quando necessário."""
        # Caso 1: Não há provedores configurados
        mock_secure_config.get_providers.return_value = {}
        
        manager = ProviderManager(mock_secure_config)
        
        # Verifica se add_provider foi chamado para cada provedor padrão
        assert mock_secure_config.add_provider.call_count >= 1
        
        # Caso 2: Já existem provedores configurados
        mock_secure_config.reset_mock()
        mock_secure_config.get_providers.return_value = {"openai": {}}
        
        with patch('aider_start.provider_manager.ProviderManager._ensure_default_providers'):
            manager = ProviderManager(mock_secure_config)
            # Reaplica o patch apenas para o método específico
            manager._ensure_default_providers()
        
        # Verifica que nenhum provedor foi adicionado
        assert mock_secure_config.add_provider.call_count == 0
    
    def test_get_providers(self, provider_manager, mock_secure_config):
        """Testa a obtenção de todos os provedores."""
        result = provider_manager.get_providers()
        
        # Verifica se o método correto do config_manager foi chamado
        mock_secure_config.get_providers.assert_called_once()
        
        # Verifica se retornou o valor correto
        assert result == mock_secure_config.get_providers.return_value
    
    def test_get_provider(self, provider_manager, mock_secure_config):
        """Testa a obtenção de um provedor específico."""
        # Caso 1: Sem incluir a chave de API
        result = provider_manager.get_provider("openai")
        
        # Verifica se o método correto do config_manager foi chamado
        mock_secure_config.get_provider.assert_called_with("openai", False)
        
        # Caso 2: Incluindo a chave de API
        result = provider_manager.get_provider("openai", include_api_key=True)
        
        # Verifica se o método correto do config_manager foi chamado
        mock_secure_config.get_provider.assert_called_with("openai", True)
        
        # Caso 3: Provedor inexistente
        mock_secure_config.get_provider.return_value = None
        result = provider_manager.get_provider("inexistente")
        
        # Verifica se retornou None
        assert result is None
    
    def test_add_provider(self, provider_manager, mock_secure_config):
        """Testa a adição de um provedor."""
        provider_data = {
            "description": "Provedor Teste",
            "api_url": "https://api.teste.com",
            "models": ["modelo1", "modelo2"]
        }
        
        # Adicionar provedor válido
        result = provider_manager.add_provider("teste", provider_data)
        
        # Verifica se o método correto do config_manager foi chamado
        mock_secure_config.add_provider.assert_called_with("teste", provider_data)
        
        # Verifica se retornou o valor correto
        assert result is True
        
        # Tentar adicionar com dados inválidos
        with pytest.raises(ValidationError):
            # Nome inválido
            provider_manager.add_provider("", provider_data)
    
    def test_delete_provider(self, provider_manager, mock_secure_config):
        """Testa a remoção de um provedor."""
        # Configurar mock para simular provedor existente
        mock_secure_config.get_provider.return_value = {"name": "openai"}
        
        # Remover provedor existente
        result = provider_manager.delete_provider("openai")
        
        # Verifica se o método correto do config_manager foi chamado
        mock_secure_config.delete_provider.assert_called_with("openai")
        
        # Verifica se retornou o valor correto
        assert result is True
        
        # Tentar remover provedor inexistente
        mock_secure_config.get_provider.return_value = None
        
        with pytest.raises(ProviderNotFoundError):
            provider_manager.delete_provider("inexistente")
    
    def test_set_api_key(self, provider_manager, mock_secure_config):
        """Testa a definição de uma chave de API."""
        # Configurar mock para simular provedor existente
        mock_secure_config.get_provider.return_value = {"name": "openai"}
        
        # Definir chave de API para provedor existente
        result = provider_manager.set_api_key("openai", "sk-test-key")
        
        # Verifica se o método correto do config_manager foi chamado
        mock_secure_config.store_api_key.assert_called_with("openai", "sk-test-key")
        
        # Verifica se retornou o valor correto
        assert result is True
        
        # Tentar definir chave para provedor inexistente
        mock_secure_config.get_provider.return_value = None
        
        with pytest.raises(ProviderNotFoundError):
            provider_manager.set_api_key("inexistente", "sk-test-key")
        
        # Tentar definir chave inválida
        mock_secure_config.get_provider.return_value = {"name": "openai"}
        
        with pytest.raises(ValidationError):
            provider_manager.set_api_key("openai", "")
    
    def test_get_api_key(self, provider_manager, mock_secure_config):
        """Testa a obtenção de uma chave de API."""
        # Configurar mock para simular provedor existente
        mock_secure_config.get_provider.return_value = {"name": "openai"}
        mock_secure_config.get_api_key.return_value = "sk-test-key"
        
        # Obter chave de API de provedor existente
        result = provider_manager.get_api_key("openai")
        
        # Verifica se o método correto do config_manager foi chamado
        mock_secure_config.get_api_key.assert_called_with("openai", False)
        
        # Verifica se retornou o valor correto
        assert result == "sk-test-key"
        
        # Tentar obter chave de provedor inexistente
        mock_secure_config.get_provider.return_value = None
        
        result = provider_manager.get_api_key("inexistente")
        
        # Verifica se retornou None
        assert result is None
    
    def test_get_provider_models(self, provider_manager, mock_secure_config):
        """Testa a obtenção de modelos de um provedor."""
        # Configurar mock para simular provedor existente
        mock_secure_config.get_provider.return_value = {
            "name": "openai",
            "models": ["gpt-3.5-turbo", "gpt-4"]
        }

        # Obter modelos de provedor existente
        result = provider_manager.get_provider_models("openai")

        # Verifica se retornou o valor correto
        assert result == ["gpt-3.5-turbo", "gpt-4"]

        # Tentar obter modelos de provedor inexistente
        mock_secure_config.get_provider.side_effect = lambda name, include_api_key=False: None

        with pytest.raises(ProviderNotFoundError):
            provider_manager.get_provider_models("inexistente")

        # Provedor sem modelos definidos
        mock_secure_config.get_provider.side_effect = lambda name, include_api_key=False: {"name": "openai"} if name == "openai" else None

        result = provider_manager.get_provider_models("openai")

        # Verifica se retornou uma lista vazia
        assert result == []
    
    def test_add_provider_model(self, provider_manager, mock_secure_config):
        """Testa a adição de um modelo a um provedor."""
        # Configurar mock para simular provedor existente
        mock_secure_config.get_provider.return_value = {
            "name": "openai",
            "models": ["gpt-3.5-turbo"]
        }
        
        # Configurar o mock para simular o comportamento do método add_provider_model
        mock_secure_config.add_provider_model.return_value = True
        
        # Adicionar modelo a provedor existente
        result = provider_manager.add_provider_model("openai", "gpt-4")
        
        # Verifica se o método correto do config_manager foi chamado
        mock_secure_config.add_provider_model.assert_called_with("openai", "gpt-4")
        
        # Verifica se retornou o valor correto
        assert result is True
        
        # Tentar adicionar modelo a provedor inexistente
        mock_secure_config.get_provider.return_value = None
        
        with pytest.raises(ProviderNotFoundError):
            provider_manager.add_provider_model("inexistente", "modelo")
        
        # Tentar adicionar modelo com nome inválido
        mock_secure_config.get_provider.return_value = {"name": "openai", "models": []}
        
        with pytest.raises(ValidationError):
            provider_manager.add_provider_model("openai", "")
    
    def test_remove_provider_model(self, provider_manager, mock_secure_config):
        """Testa a remoção de um modelo de um provedor."""
        # Configurar mock para simular provedor existente
        mock_secure_config.get_provider.return_value = {
            "name": "openai",
            "models": ["gpt-3.5-turbo", "gpt-4"]
        }
        
        # Configurar o mock para simular o comportamento do método remove_provider_model
        mock_secure_config.remove_provider_model.return_value = True
        
        # Remover modelo de provedor existente
        result = provider_manager.remove_provider_model("openai", "gpt-4")
        
        # Verifica se o método correto do config_manager foi chamado
        mock_secure_config.remove_provider_model.assert_called_with("openai", "gpt-4")
        
        # Verifica se retornou o valor correto
        assert result is True
        
        # Tentar remover modelo de provedor inexistente
        mock_secure_config.get_provider.return_value = None
        
        with pytest.raises(ProviderNotFoundError):
            provider_manager.remove_provider_model("inexistente", "modelo")
    
    def test_has_api_key(self, provider_manager, mock_secure_config):
        """Testa a verificação de existência de chave de API."""
        # Configurar mock para simular provedor com chave de API
        mock_secure_config.get_provider.return_value = {"name": "openai"}
        mock_secure_config.get_api_key.return_value = "sk-test-key"
        
        # Verificar provedor com chave
        result = provider_manager.has_api_key("openai")
        
        # Verifica se retornou True
        assert result is True
        
        # Provedor sem chave
        mock_secure_config.get_api_key.return_value = None
        
        result = provider_manager.has_api_key("openai")
        
        # Verifica se retornou False
        assert result is False
        
        # Provedor com chave vazia
        mock_secure_config.get_api_key.return_value = ""
        
        result = provider_manager.has_api_key("openai")
        
        # Verifica se retornou False
        assert result is False 