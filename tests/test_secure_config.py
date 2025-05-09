"""
Testes para o módulo de configuração segura.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from aider_start.secure_config import SecureConfigManager
from aider_start.exceptions import ValidationError, ConfigError, ProviderNotFoundError, EndpointNotFoundError


class TestSecureConfigManager:
    """Testes para a classe SecureConfigManager."""
    
    @pytest.fixture
    def mock_keyring(self):
        """Fixture para simular o keyring."""
        with patch('aider_start.secure_config.keyring') as mock:
            # Armazenar chaves de API em um dicionário para simular o comportamento do keyring
            keys_store = {}
            
            def mock_set_password(service_name, key, value):
                keys_store[f"{service_name}:{key}"] = value
                return True
            
            def mock_get_password(service_name, key):
                return keys_store.get(f"{service_name}:{key}")
            
            def mock_delete_password(service_name, key):
                if f"{service_name}:{key}" in keys_store:
                    del keys_store[f"{service_name}:{key}"]
                    return True
                return False
            
            mock.set_password.side_effect = mock_set_password
            mock.get_password.side_effect = mock_get_password
            mock.delete_password.side_effect = mock_delete_password
            yield mock
    
    @pytest.fixture
    def secure_config(self, mock_keyring, tmp_path):
        """Fixture para criar um objeto SecureConfigManager com mock de arquivos e keyring."""
        config_dir = tmp_path / '.aider-start'
        config_file = config_dir / 'config.json'
        
        # Mock do caminho do arquivo de configuração
        with patch('aider_start.config_manager.CONFIG_DIR', config_dir), \
             patch('aider_start.config_manager.CONFIG_FILE', config_file):
            
            # Criar diretório de configuração
            os.makedirs(config_dir, exist_ok=True)
            
            # Inicializar com configuração padrão
            default_config = {
                'profiles': {},
                'providers': {},
                'custom_endpoints': {}
            }
            
            # Criar arquivo de configuração
            with open(config_file, 'w') as f:
                json.dump(default_config, f)
            
            yield SecureConfigManager()
    
    def test_initialization(self, secure_config):
        """Testa a inicialização da classe SecureConfigManager."""
        assert secure_config.service_name == 'aider-start'
        assert isinstance(secure_config.config, dict)
        assert 'profiles' in secure_config.config
        assert 'providers' in secure_config.config
        assert 'custom_endpoints' in secure_config.config
    
    def test_store_api_key(self, secure_config, mock_keyring):
        """Testa o armazenamento de chaves de API."""
        # Armazenar chave de API
        result = secure_config.store_api_key('openai', 'sk-test-key')
        assert result is True
        mock_keyring.set_password.assert_called_once_with(
            'aider-start', 'openai_api_key', 'sk-test-key'
        )
        
        # Testar validação de parâmetros
        with pytest.raises(ValidationError):
            secure_config.store_api_key('', 'sk-test-key')
        with pytest.raises(ValidationError):
            secure_config.store_api_key('openai', '')
    
    def test_get_api_key(self, secure_config, mock_keyring):
        """Testa a recuperação de chaves de API."""
        # Substituir a implementação simulada pelo retorno fixo,
        # já que precisamos garantir que o mock retorne o valor esperado
        mock_keyring.get_password = MagicMock(return_value='sk-test-key')
        
        # Recuperar chave de API
        key = secure_config.get_api_key('openai')
        assert key == 'sk-test-key'
        mock_keyring.get_password.assert_called_with(
            'aider-start', 'openai_api_key'
        )
        
        # Testar validação de parâmetros
        with pytest.raises(ValidationError):
            secure_config.get_api_key('')
    
    def test_get_api_key_not_found(self, secure_config, mock_keyring):
        """Testa a recuperação de chaves de API não encontradas."""
        # Substituir a implementação simulada pelo retorno fixo
        mock_keyring.get_password = MagicMock(return_value=None)
        
        # Recuperar chave de API sem prompt
        key = secure_config.get_api_key('openai', prompt_if_missing=False)
        assert key is None
        
        # Recuperar chave de API com prompt (simulamos que não há entrada do usuário)
        with patch('aider_start.secure_config.getpass.getpass', return_value=''):
            key = secure_config.get_api_key('openai', prompt_if_missing=True)
            assert key is None
    
    def test_get_api_key_with_prompt(self, secure_config, mock_keyring):
        """Testa a recuperação de chaves de API com prompt ao usuário."""
        # Configurar mock para retornar None (chave não encontrada)
        mock_keyring.get_password.return_value = None
        
        # Simular entrada do usuário
        with patch('aider_start.secure_config.getpass.getpass', return_value='sk-user-input'):
            key = secure_config.get_api_key('openai', prompt_if_missing=True)
            assert key == 'sk-user-input'
            
            # Verificar se armazenou a chave fornecida pelo usuário
            mock_keyring.set_password.assert_called_once_with(
                'aider-start', 'openai_api_key', 'sk-user-input'
            )
    
    def test_delete_api_key(self, secure_config, mock_keyring):
        """Testa a remoção de chaves de API."""
        # Configurar mock para indicar sucesso na exclusão
        mock_keyring.delete_password.return_value = True
        
        # Remover chave de API
        result = secure_config.delete_api_key('openai')
        assert result is True
        mock_keyring.delete_password.assert_called_once_with(
            'aider-start', 'openai_api_key'
        )
        
        # Testar validação de parâmetros
        with pytest.raises(ValidationError):
            secure_config.delete_api_key('')
    
    def test_delete_api_key_error(self, secure_config, mock_keyring):
        """Testa a remoção de chaves de API com erro."""
        # Configurar mock para lançar exceção
        mock_keyring.delete_password.side_effect = Exception("Erro ao excluir")
        
        # Remover chave de API
        result = secure_config.delete_api_key('openai')
        assert result is False
    
    def test_add_provider_with_api_key(self, secure_config):
        """Testa a adição de um provedor com chave de API."""
        provider_data = {
            'api_url': 'https://api.openai.com/v1',
            'models': ['gpt-4', 'gpt-3.5-turbo'],
            'api_key': 'sk-test-key',
            'description': 'Provedor OpenAI'
        }
        
        # Adicionar provedor
        with patch.object(secure_config, 'store_api_key') as mock_store:
            mock_store.return_value = True
            result = secure_config.add_provider('openai', provider_data.copy())
            assert result is True
            
            # Verificar se a chave de API foi extraída e armazenada separadamente
            mock_store.assert_called_once_with('openai', 'sk-test-key')
            
            # Verificar se a chave de API foi removida dos dados do provedor
            saved_provider = secure_config.get_provider('openai')
            assert 'api_key' not in saved_provider
            assert saved_provider['api_url'] == 'https://api.openai.com/v1'
    
    def test_get_provider_with_api_key(self, secure_config):
        """Testa a obtenção de um provedor com chave de API."""
        # Adicionar provedor sem chave de API
        provider_data = {
            'api_url': 'https://api.openai.com/v1',
            'models': ['gpt-4', 'gpt-3.5-turbo'],
            'description': 'Provedor OpenAI'
        }
        secure_config.add_provider('openai', provider_data)
        
        # Obter provedor sem chave de API
        provider = secure_config.get_provider('openai')
        assert 'api_key' not in provider
        
        # Obter provedor com chave de API
        with patch.object(secure_config, 'get_api_key', return_value='sk-test-key'):
            provider = secure_config.get_provider('openai', include_api_key=True)
            assert provider['api_key'] == 'sk-test-key'
    
    def test_delete_provider_with_api_key(self, secure_config):
        """Testa a exclusão de um provedor e sua chave de API."""
        # Adicionar provedor
        provider_data = {
            'api_url': 'https://api.openai.com/v1',
            'models': ['gpt-4', 'gpt-3.5-turbo'],
            'description': 'Provedor OpenAI'
        }
        secure_config.add_provider('openai', provider_data)
        
        # Excluir provedor
        with patch.object(secure_config, 'delete_api_key') as mock_delete:
            mock_delete.return_value = True
            result = secure_config.delete_provider('openai')
            assert result is True
            
            # Verificar se a chave de API foi removida
            mock_delete.assert_called_once_with('openai')
            
            # Verificar se o provedor foi removido
            with pytest.raises(ProviderNotFoundError):
                secure_config.get_provider('openai')
    
    def test_add_endpoint_with_api_key(self, secure_config):
        """Testa a adição de um endpoint com chave de API."""
        endpoint_data = {
            'api_url': 'https://custom-endpoint.com/v1',
            'models': ['custom-model'],
            'api_key': 'sk-endpoint-key',
            'description': 'Endpoint personalizado'
        }
        
        # Adicionar endpoint
        with patch.object(secure_config, 'store_api_key') as mock_store:
            mock_store.return_value = True
            result = secure_config.add_endpoint('custom', endpoint_data.copy())
            assert result is True
            
            # Verificar se a chave de API foi extraída e armazenada separadamente
            mock_store.assert_called_once_with('endpoint_custom', 'sk-endpoint-key')
            
            # Verificar se a chave de API foi removida dos dados do endpoint
            saved_endpoint = secure_config.get_endpoint('custom')
            assert 'api_key' not in saved_endpoint
            assert saved_endpoint['api_url'] == 'https://custom-endpoint.com/v1'
    
    def test_get_endpoint_with_api_key(self, secure_config):
        """Testa a obtenção de um endpoint com chave de API."""
        # Adicionar endpoint sem chave de API
        endpoint_data = {
            'api_url': 'https://custom-endpoint.com/v1',
            'models': ['custom-model'],
            'description': 'Endpoint personalizado'
        }
        secure_config.add_endpoint('custom', endpoint_data)
        
        # Obter endpoint sem chave de API
        endpoint = secure_config.get_endpoint('custom')
        assert 'api_key' not in endpoint
        
        # Obter endpoint com chave de API
        with patch.object(secure_config, 'get_api_key', return_value='sk-endpoint-key'):
            endpoint = secure_config.get_endpoint('custom', include_api_key=True)
            assert endpoint['api_key'] == 'sk-endpoint-key'
    
    def test_delete_endpoint_with_api_key(self, secure_config):
        """Testa a exclusão de um endpoint e sua chave de API."""
        # Adicionar endpoint
        endpoint_data = {
            'api_url': 'https://custom-endpoint.com/v1',
            'models': ['custom-model'],
            'description': 'Endpoint personalizado'
        }
        secure_config.add_endpoint('custom', endpoint_data)
        
        # Excluir endpoint
        with patch.object(secure_config, 'delete_api_key') as mock_delete:
            mock_delete.return_value = True
            result = secure_config.delete_endpoint('custom')
            assert result is True
            
            # Verificar se a chave de API foi removida
            mock_delete.assert_called_once_with('endpoint_custom')
            
            # Verificar se o endpoint foi removido
            with pytest.raises(EndpointNotFoundError):
                secure_config.get_endpoint('custom')
    
    def test_delete_endpoint_without_api_key(self, secure_config):
        """Testa a exclusão de um endpoint sem chave de API."""
        # Adicionar endpoint
        endpoint_data = {
            'api_url': 'https://custom-endpoint.com/v1',
            'models': ['custom-model'],
            'description': 'Endpoint personalizado'
        }
        secure_config.add_endpoint('custom', endpoint_data)
        
        # Excluir endpoint
        with patch.object(secure_config, 'delete_api_key') as mock_delete:
            mock_delete.return_value = True
            result = secure_config.delete_endpoint('custom')
            assert result is True
            
            # Verificar se a chave de API foi removida
            mock_delete.assert_called_once_with('endpoint_custom')
            
            # Verificar se o endpoint foi removido
            with pytest.raises(EndpointNotFoundError):
                secure_config.get_endpoint('custom') 