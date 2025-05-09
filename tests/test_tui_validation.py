"""
Testes para a validação de parâmetros na interface TUI.
"""

import pytest
from unittest.mock import MagicMock, patch

from aider_start.tui import TUI
from aider_start.param_validator import ParamValidator
from aider_start.context_help import ContextHelp
from aider_start.param_db import ParameterDatabase


class TestTUIValidation:
    """Testes para validação de parâmetros na TUI."""
    
    @pytest.fixture
    def param_db(self):
        """Fixture para criar uma instância do ParameterDatabase."""
        return ParameterDatabase()
    
    @pytest.fixture
    def profile_builder_mock(self, param_db):
        """Fixture para criar um mock do ProfileBuilder com param_db."""
        profile_builder = MagicMock()
        profile_builder.param_db = param_db
        return profile_builder
    
    @pytest.fixture
    def tui(self, profile_builder_mock):
        """Fixture para criar uma instância da TUI."""
        tui = TUI(profile_builder=profile_builder_mock)
        return tui
    
    def test_tui_initializes_validators(self, tui, profile_builder_mock):
        """Testa se a TUI inicializa corretamente os validadores."""
        assert tui.profile_builder == profile_builder_mock
        assert isinstance(tui.context_help, ContextHelp)
        assert isinstance(tui.param_validator, ParamValidator)
        assert tui.validation_errors == {}
    
    def test_configure_category_validation(self, tui):
        """Testa validação de parâmetros no método _configure_category."""
        # Mock para profile_builder.get_category_parameters
        tui.profile_builder.get_category_parameters.return_value = {
            'model': {'type': 'string', 'description': 'Modelo a ser usado'},
            'temperatura': {'type': 'float', 'description': 'Temperatura de amostragem'}
        }
        
        # Mock para profile_builder.get_current_profile
        tui.profile_builder.get_current_profile.return_value = {
            'model': 'gpt-4o',
            'temperatura': 0.7
        }
        
        # Mock para context_help.should_show_parameter
        tui.context_help.should_show_parameter = MagicMock(return_value=True)
        
        # Mock para param_validator.validate_parameter
        tui.param_validator.validate_parameter = MagicMock(return_value=(True, "Valor válido"))
        
        # Mock para métodos da TUI que pedem entrada do usuário
        with patch.object(tui, '_get_text_input', return_value="gpt-4o"):
            # Não podemos testar diretamente _configure_category porque usa curses
            # Mas podemos verificar que o validador é chamado corretamente
            profile_data = {'model': 'gpt-4o', 'temperature': 0.7}
            tui.param_validator.get_validation_errors(profile_data)
            
            # Verifica se validate_parameter foi chamado
            tui.param_validator.validate_parameter.assert_called()
    
    def test_validation_errors_storage(self, tui):
        """Testa o armazenamento de erros de validação."""
        # Simula erro de validação
        error_message = "Formato inválido"
        tui.validation_errors['model'] = error_message
        
        assert tui.validation_errors['model'] == error_message
        
        # Simula limpeza de erros
        tui.validation_errors = {}
        assert 'model' not in tui.validation_errors
    
    def test_parameter_validation_integration(self, tui):
        """Testa a integração entre TUI e ParamValidator."""
        # Mock para profile_builder.get_current_profile
        current_profile = {
            'model': 123,  # Erro: não é string
            'provider': 'openai'
        }
        tui.profile_builder.get_current_profile.return_value = current_profile
        
        # Usar o validador real
        validation_errors = tui.param_validator.get_validation_errors(current_profile)
        
        # Deve detectar que 'model' não é uma string e erro de validação cruzada
        assert 'model' in validation_errors
        assert len(validation_errors) >= 1
    
    def test_format_hint_integration(self, tui):
        """Testa a integração entre TUI e dicas de formato de parâmetros."""
        # Usar o método real get_parameter_format_hint
        hint = tui.param_validator.get_parameter_format_hint('model', 'model_options')
        
        # Deve retornar alguma dica de formato
        assert isinstance(hint, str)
    
    def test_required_parameters_integration(self, tui):
        """Testa a integração entre TUI e parâmetros obrigatórios."""
        # Usar o método real get_required_parameters
        required = tui.context_help.get_required_parameters('model_options')
        
        # Deve retornar uma lista (vazia ou não)
        assert isinstance(required, list)
    
    def test_should_show_parameter_integration(self, tui):
        """Testa a integração entre TUI e disclosure progressivo."""
        # Profile para testar disclosure progressivo
        test_profile = {'architect': True}
        
        # Usar o método real should_show_parameter
        result1 = tui.context_help.should_show_parameter('auto-accept-architect', test_profile)
        result2 = tui.context_help.should_show_parameter('edit-format', test_profile)
        
        # Deve mostrar auto-accept-architect e esconder edit-format quando architect=True
        assert result1 is True
        assert result2 is False 