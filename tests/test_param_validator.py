"""
Testes para o módulo de validação de parâmetros.
"""

import pytest
from unittest.mock import MagicMock, patch

from aider_start.param_validator import ParamValidator
from aider_start.param_db import ParameterDatabase


class TestParamValidator:
    """Testes para a classe ParamValidator."""
    
    @pytest.fixture
    def param_db(self):
        """Fixture para criar uma instância do ParameterDatabase."""
        return ParameterDatabase()
    
    @pytest.fixture
    def validator(self, param_db):
        """Fixture para criar uma instância do ParamValidator."""
        return ParamValidator(param_db)
    
    def test_initialization(self, validator, param_db):
        """Testa a inicialização correta da classe ParamValidator."""
        assert validator.param_db == param_db
        assert isinstance(validator.validation_rules, dict)
        assert isinstance(validator.cross_validation_rules, dict)
    
    def test_validate_string(self, validator):
        """Testa a validação de valores do tipo string."""
        # Teste básico
        valid, message = validator._validate_string("teste", "nome")
        assert valid
        
        # Teste com valor não string
        valid, message = validator._validate_string(123, "nome")
        assert not valid
        assert "deve ser uma string" in message
        
    def test_validate_integer(self, validator):
        """Testa a validação de valores do tipo inteiro."""
        # Teste básico
        valid, message = validator._validate_integer(123, "idade")
        assert valid
        
        # Teste com string numérica (deve converter)
        valid, message = validator._validate_integer("456", "idade")
        assert valid
        
        # Teste com valor não inteiro
        valid, message = validator._validate_integer("abc", "idade")
        assert not valid
        assert "inteiro válido" in message
        
    def test_validate_float(self, validator):
        """Testa a validação de valores do tipo ponto flutuante."""
        # Teste básico
        valid, message = validator._validate_float(1.23, "temperatura")
        assert valid
        
        # Teste com string numérica (deve converter)
        valid, message = validator._validate_float("4.56", "temperatura")
        assert valid
        
        # Teste com valor não float
        valid, message = validator._validate_float("abc", "temperatura")
        assert not valid
        assert "decimal válido" in message
        
    def test_validate_boolean(self, validator):
        """Testa a validação de valores booleanos."""
        # Teste com booleano literal
        valid, message = validator._validate_boolean(True, "flag")
        assert valid
        
        # Teste com strings que representam booleanos
        valid, message = validator._validate_boolean("true", "flag")
        assert valid
        valid, message = validator._validate_boolean("yes", "flag")
        assert valid
        valid, message = validator._validate_boolean("false", "flag")
        assert valid
        
        # Teste com valor não booleano
        valid, message = validator._validate_boolean("talvez", "flag")
        assert not valid
        assert "verdadeiro ou falso" in message
        
    def test_validate_url(self, validator):
        """Testa a validação de URLs."""
        # Teste com URL válida
        valid, message = validator._validate_url("https://exemplo.com", "site")
        assert valid
        
        # Teste com URL inválida
        valid, message = validator._validate_url("exemplo", "site")
        assert not valid
        assert "formato válido" in message
        
    def test_validate_api_key(self, validator):
        """Testa a validação de chaves de API."""
        # Teste com chave OpenAI válida
        valid, message = validator._validate_api_key("sk-1234567890abcdef", "openai-api-key")
        assert valid
        
        # Teste com chave OpenAI inválida
        valid, message = validator._validate_api_key("key-123", "openai-api-key")
        assert not valid
        assert "deve começar com" in message
        
        # Teste com chave Anthropic válida
        valid, message = validator._validate_api_key("sk-ant-1234567890abcdef", "anthropic-api-key")
        assert valid
        
    def test_validate_email(self, validator):
        """Testa a validação de endereços de e-mail."""
        # Teste com e-mail válido
        valid, message = validator._validate_email("usuario@exemplo.com", "email")
        assert valid
        
        # Teste com e-mail inválido
        valid, message = validator._validate_email("usuario-exemplo.com", "email")
        assert not valid
        assert "formato do e-mail é inválido" in message
        
    def test_validate_model(self, validator):
        """Testa a validação de nomes de modelos."""
        # Teste com modelo OpenAI válido
        valid, message = validator._validate_model("gpt-4o", "model")
        assert valid
        
        # Teste com modelo Anthropic válido
        valid, message = validator._validate_model("claude-3-opus", "model")
        assert valid
        
        # Teste com modelo inválido
        valid, message = validator._validate_model("modelo-desconhecido", "model")
        assert not valid
        assert "não parece ter um formato conhecido" in message
        
    def test_cross_validate_model_provider(self, validator):
        """Testa a validação cruzada entre modelo e provedor."""
        # Teste com combinação válida
        valid, message = validator._cross_validate_model_provider("gpt-4o", "openai")
        assert valid
        
        # Teste com combinação inválida
        valid, message = validator._cross_validate_model_provider("claude-3", "openai")
        assert not valid
        assert "não parece ser compatível" in message
        
    def test_get_param_data(self, validator):
        """Testa a obtenção de dados de parâmetros."""
        # Teste com parâmetro existente
        param_data = validator._get_param_data("model", "model_options")
        assert param_data is not None
        assert "description" in param_data
        
        # Teste com parâmetro inexistente
        param_data = validator._get_param_data("parâmetro_inexistente")
        assert param_data is None
        
    def test_get_param_type(self, validator):
        """Testa a obtenção do tipo de um parâmetro."""
        # Teste com parâmetro string
        param_type = validator._get_param_type("model", "model_options")
        assert param_type == "string"
        
        # Teste com parâmetro booleano
        param_type = validator._get_param_type("architect", "model_options")
        assert param_type == "boolean"
        
    def test_validate_parameter(self, validator):
        """Testa a validação completa de um parâmetro."""
        # Teste com parâmetro válido
        valid, message = validator.validate_parameter("model", "gpt-4o", "model_options")
        assert valid
        
        # Teste com parâmetro inválido
        valid, message = validator.validate_parameter("model", 123, "model_options")
        assert not valid
        
        # Teste com validação cruzada
        profile_data = {"provider": "openai", "model": "claude-3"}
        valid, message = validator.validate_parameter("model", "claude-3", "model_options", profile_data)
        assert not valid
        assert "não parece ser compatível com OpenAI" in message
        
    def test_get_validation_errors(self, validator):
        """Testa a obtenção de erros de validação para um perfil."""
        # Perfil com erro
        profile_data = {
            "name": "teste",
            "model": 123,  # Erro: não é string
            "provider": "openai",
            "temperatura": -1  # Erro: temperatura negativa
        }
        
        errors = validator.get_validation_errors(profile_data)
        assert len(errors) == 3  # Três erros: modelo não é string, provider (erro de validação cruzada) e temperatura negativa
        assert "model" in errors
        assert "provider" in errors  # Erro de validação cruzada (provider → model)
        assert "temperatura" in errors
        
    def test_get_parameter_format_hint(self, validator):
        """Testa a obtenção de dicas de formato para parâmetros."""
        # Mock para _get_param_data e _get_param_type
        validator._get_param_data = MagicMock(return_value={
            'type': 'integer',
            'min_value': 0,
            'max_value': 100
        })
        validator._get_param_type = MagicMock(return_value='integer')
        
        # Teste para parâmetro inteiro
        hint = validator.get_parameter_format_hint("idade")
        assert "mín: 0" in hint
        assert "máx: 100" in hint
        
        # Teste para parâmetro URL
        validator._get_param_type = MagicMock(return_value='url')
        hint = validator.get_parameter_format_hint("site")
        assert "URL completa" in hint 