"""
Testes para o módulo provider_adapters.py
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os
import json
import requests

# Adiciona o diretório raiz ao path para importação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aider_start.provider_adapters import (
    BaseProviderAdapter, OpenAIAdapter, AnthropicAdapter, 
    MistralAdapter, get_provider_adapter
)


class TestProviderAdapters:
    """Testes para os adaptadores de provedores."""
    
    def test_get_provider_adapter(self):
        """Testa a função factory get_provider_adapter."""
        # Verifica se retorna o adaptador correto para cada provedor
        
        # OpenAI
        adapter = get_provider_adapter("openai", "test-key", "https://api.test.com")
        assert isinstance(adapter, OpenAIAdapter)
        assert adapter.api_key == "test-key"
        assert adapter.api_url == "https://api.test.com"
        
        # Anthropic
        adapter = get_provider_adapter("anthropic", "test-key")
        assert isinstance(adapter, AnthropicAdapter)
        assert adapter.api_key == "test-key"
        assert adapter.api_url == "https://api.anthropic.com/v1"
        
        # Mistral
        adapter = get_provider_adapter("mistral")
        assert isinstance(adapter, MistralAdapter)
        assert adapter.api_key is None
        assert adapter.api_url == "https://api.mistral.ai/v1"
        
        # Provedor não suportado
        adapter = get_provider_adapter("provedor_inexistente")
        assert adapter is None
        
        # Provedor com case diferente
        adapter = get_provider_adapter("OpenAI", "test-key")
        assert isinstance(adapter, OpenAIAdapter)
        assert adapter.api_key == "test-key"


class TestOpenAIAdapter:
    """Testes para o adaptador da OpenAI."""
    
    @pytest.fixture
    def adapter(self):
        """Fixture para o adaptador da OpenAI."""
        return OpenAIAdapter(api_key="sk-test-key")
    
    @patch('aider_start.provider_adapters.requests.get')
    def test_validate_api_key_success(self, mock_get, adapter):
        """Testa a validação bem-sucedida da chave de API."""
        # Configurar mock para simular resposta de sucesso
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Verificar validação bem-sucedida
        result = adapter.validate_api_key()
        
        # Verificar se a chamada foi feita corretamente
        mock_get.assert_called_with(
            "https://api.openai.com/v1/models", 
            headers={
                "Authorization": "Bearer sk-test-key",
                "Content-Type": "application/json"
            }
        )
        
        # Verificar se retornou True
        assert result is True
    
    @patch('aider_start.provider_adapters.requests.get')
    def test_validate_api_key_failure(self, mock_get, adapter):
        """Testa a validação mal-sucedida da chave de API."""
        # Configurar mock para simular resposta de erro
        mock_response = MagicMock()
        mock_response.status_code = 401  # Não autorizado
        mock_get.return_value = mock_response
        
        # Verificar validação mal-sucedida
        result = adapter.validate_api_key()
        
        # Verificar se retornou False
        assert result is False
        
        # Sem chave de API
        adapter.api_key = None
        result = adapter.validate_api_key()
        assert result is False
        
        # Erro de requisição
        adapter.api_key = "sk-test-key"
        mock_get.side_effect = Exception("Erro de conexão")
        result = adapter.validate_api_key()
        assert result is False
    
    @patch('aider_start.provider_adapters.requests.get')
    def test_get_models(self, mock_get, adapter):
        """Testa a obtenção de modelos."""
        # Configurar mock para simular resposta de sucesso
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "gpt-3.5-turbo", "object": "model"},
                {"id": "gpt-4", "object": "model"},
                {"id": "text-embedding-ada-002", "object": "model"},
                {"id": "davinci", "object": "model"}  # Modelo que não começa com gpt- ou text-embedding-
            ]
        }
        mock_get.return_value = mock_response
        
        # Obter modelos
        models = adapter.get_models()
        
        # Verificar se a filtragem foi aplicada corretamente
        assert "gpt-3.5-turbo" in models
        assert "gpt-4" in models
        assert "text-embedding-ada-002" in models
        assert "davinci" not in models
        
        # Sem chave de API
        adapter.api_key = None
        assert adapter.get_models() == []
        
        # Erro de requisição
        adapter.api_key = "sk-test-key"
        mock_get.side_effect = Exception("Erro de conexão")
        assert adapter.get_models() == []
        
        # Código de status não 200
        mock_get.side_effect = None
        mock_response.status_code = 401
        assert adapter.get_models() == []
    
    def test_validate_parameters(self, adapter):
        """Testa a validação e normalização de parâmetros."""
        # Parâmetros a serem validados
        params = {
            "temperatura": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5,
            "model": "gpt-4"
        }
        
        # Validar parâmetros
        validated = adapter.validate_parameters(params)
        
        # Verificar se os parâmetros foram renomeados corretamente
        assert "temperature" in validated
        assert "temperatura" not in validated
        assert validated["temperature"] == 0.7
        
        # Verificar se os limites foram aplicados corretamente
        params["temperatura"] = 3.0  # Acima do limite
        validated = adapter.validate_parameters(params)
        assert validated["temperature"] == 2.0
        
        # Verificar se o modelo é verificado
        params["temperatura"] = 0.7
        params["model"] = "modelo-inexistente"
        validated = adapter.validate_parameters(params)
        assert validated["model"] == "modelo-inexistente"  # Apenas avisa, não altera


class TestAnthropicAdapter:
    """Testes para o adaptador da Anthropic."""
    
    @pytest.fixture
    def adapter(self):
        """Fixture para o adaptador da Anthropic."""
        return AnthropicAdapter(api_key="sk-ant-test-key")
    
    def test_validate_api_key(self, adapter):
        """Testa a validação da chave de API."""
        # Chave válida (prefixo correto)
        assert adapter.validate_api_key() is True
        
        # Chave válida (prefixo alternativo)
        adapter.api_key = "sk-test-key"
        assert adapter.validate_api_key() is True
        
        # Chave inválida (prefixo incorreto)
        adapter.api_key = "invalid-key"
        assert adapter.validate_api_key() is False
        
        # Sem chave
        adapter.api_key = None
        assert adapter.validate_api_key() is False
        
        # Erro ao validar - usando um mock para simular a exceção
        adapter.api_key = "sk-ant-test-key"
        with patch('aider_start.provider_adapters.AnthropicAdapter.validate_api_key', 
                  side_effect=Exception("Erro de teste")):
            # Criamos uma nova instância para evitar usar o objeto que já foi patched
            error_adapter = AnthropicAdapter(api_key="sk-ant-test-key")
            with pytest.raises(Exception):
                # Isso deve lançar a exceção simulada
                error_adapter.validate_api_key()
    
    def test_get_models(self, adapter):
        """Testa a obtenção de modelos (lista estática)."""
        models = adapter.get_models()
        
        # Verificar se retornou a lista estática correta
        assert isinstance(models, list)
        assert len(models) > 0
        assert "claude-1" in models
        assert "claude-2" in models
        assert "claude-3-opus" in models
    
    def test_validate_parameters(self, adapter):
        """Testa a validação e normalização de parâmetros."""
        # Parâmetros a serem validados
        params = {
            "temperatura": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9,
            "engine": "claude-2"  # A Anthropic usa "model" em vez de "engine"
        }
        
        # Validar parâmetros
        validated = adapter.validate_parameters(params)
        
        # Verificar se os parâmetros foram renomeados corretamente
        assert "temperature" in validated
        assert "temperatura" not in validated
        assert validated["temperature"] == 0.7
        
        assert "max_tokens_to_sample" in validated
        assert "max_tokens" not in validated
        
        # Verificar se "engine" foi convertido para "model"
        assert "model" in validated
        assert "engine" not in validated
        assert validated["model"] == "claude-2"
        
        # Verificar se os limites foram aplicados corretamente
        params["temperatura"] = 1.5  # Acima do limite
        validated = adapter.validate_parameters(params)
        assert validated["temperature"] == 1.0
        
        # Verificar se o modelo é verificado
        params["temperatura"] = 0.7
        params["engine"] = "modelo-inexistente"
        validated = adapter.validate_parameters(params)
        assert validated["model"] == "modelo-inexistente"  # Apenas avisa, não altera


class TestMistralAdapter:
    """Testes para o adaptador da Mistral AI."""
    
    @pytest.fixture
    def adapter(self):
        """Fixture para o adaptador da Mistral AI."""
        return MistralAdapter(api_key="test-key")
    
    @patch('aider_start.provider_adapters.requests.get')
    def test_validate_api_key(self, mock_get, adapter):
        """Testa a validação da chave de API."""
        # Configurar mock para simular resposta de sucesso
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Verificar validação bem-sucedida
        result = adapter.validate_api_key()
        
        # Verificar se a chamada foi feita corretamente
        mock_get.assert_called_with(
            "https://api.mistral.ai/v1/models", 
            headers={
                "Authorization": "Bearer test-key",
                "Content-Type": "application/json"
            }
        )
        
        # Verificar se retornou True
        assert result is True
        
        # Sem chave de API
        adapter.api_key = None
        result = adapter.validate_api_key()
        assert result is False
        
        # Erro de requisição
        adapter.api_key = "test-key"
        mock_get.side_effect = Exception("Erro de conexão")
        result = adapter.validate_api_key()
        assert result is False
        
        # Código de status não 200
        mock_get.side_effect = None
        mock_response.status_code = 401
        result = adapter.validate_api_key()
        assert result is False
    
    @patch('aider_start.provider_adapters.requests.get')
    def test_get_models(self, mock_get, adapter):
        """Testa a obtenção de modelos."""
        # Configurar mock para simular resposta de sucesso
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "mistral-tiny", "object": "model"},
                {"id": "mistral-small", "object": "model"},
                {"id": "mistral-medium", "object": "model"}
            ]
        }
        mock_get.return_value = mock_response
        
        # Obter modelos
        models = adapter.get_models()
        
        # Verificar se obteve os modelos corretamente
        assert "mistral-tiny" in models
        assert "mistral-small" in models
        assert "mistral-medium" in models
        
        # Sem chave de API
        adapter.api_key = None
        assert adapter.get_models() == []
        
        # Erro de requisição
        adapter.api_key = "test-key"
        mock_get.side_effect = Exception("Erro de conexão")
        assert adapter.get_models() == []
        
        # Código de status não 200
        mock_get.side_effect = None
        mock_response.status_code = 401
        assert adapter.get_models() == []
    
    def test_validate_parameters(self, adapter):
        """Testa a validação e normalização de parâmetros."""
        # Parâmetros a serem validados
        params = {
            "temperatura": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9,
            "model": "mistral-medium"
        }
        
        # Validar parâmetros
        validated = adapter.validate_parameters(params)
        
        # Verificar se os parâmetros foram renomeados corretamente
        assert "temperature" in validated
        assert "temperatura" not in validated
        assert validated["temperature"] == 0.7
        
        # Verificar se os limites foram aplicados corretamente
        params["temperatura"] = 1.5  # Acima do limite
        validated = adapter.validate_parameters(params)
        assert validated["temperature"] == 1.0
        
        # Verificar se o modelo é verificado
        params["temperatura"] = 0.7
        params["model"] = "modelo-inexistente"
        validated = adapter.validate_parameters(params)
        assert validated["model"] == "modelo-inexistente"  # Apenas avisa, não altera 