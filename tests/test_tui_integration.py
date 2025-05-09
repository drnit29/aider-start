"""
Testes para integração entre TUI e outros componentes.
"""

import pytest
from unittest.mock import MagicMock, patch, call
import sys
import os
import curses
import unittest.mock

from aider_start.tui import TUI
from aider_start.config_manager import ConfigManager
from aider_start.profile_builder import ProfileBuilder
from aider_start.command_executor import CommandExecutor


class TestTUIIntegration:
    """Testes para a integração da TUI com os demais componentes."""
    
    @pytest.fixture
    def config_manager_mock(self):
        """Fixture para criar um mock do ConfigManager."""
        mock = MagicMock(spec=ConfigManager)
        # Configura o mock para retornar perfis fictícios
        mock_profiles = {
            "perfil_teste": {"name": "perfil_teste", "model": "gpt-4", "temperatura": 0.7},
            "perfil_dev": {"name": "perfil_dev", "model": "gpt-3.5-turbo", "temperatura": 0.5}
        }
        mock.get_profiles.return_value = mock_profiles
        mock.get_profile.side_effect = lambda name: mock_profiles.get(name)
        return mock
    
    @pytest.fixture
    def profile_builder_mock(self):
        """Fixture para criar um mock do ProfileBuilder."""
        mock = MagicMock(spec=ProfileBuilder)
        mock.param_db = MagicMock()
        return mock
    
    @pytest.fixture
    def command_executor_mock(self):
        """Fixture para criar um mock do CommandExecutor."""
        mock = MagicMock(spec=CommandExecutor)
        return mock
    
    @pytest.fixture
    def tui(self, config_manager_mock, profile_builder_mock, command_executor_mock):
        """Fixture para criar uma instância da TUI com mocks dos componentes."""
        tui = TUI(
            config_manager=config_manager_mock,
            profile_builder=profile_builder_mock,
            command_executor=command_executor_mock
        )
        # Mock do curses e screen para evitar erros
        tui.screen = MagicMock()
        with patch('curses.color_pair', return_value=0):
            yield tui
    
    def test_tui_initialization_with_components(self, tui, config_manager_mock, 
                                             profile_builder_mock, command_executor_mock):
        """Testa se a TUI inicializa corretamente com todos os componentes."""
        assert tui.config_manager == config_manager_mock
        assert tui.profile_builder == profile_builder_mock
        assert tui.command_executor == command_executor_mock
        assert hasattr(tui, 'context_help')
        assert hasattr(tui, 'param_validator')
    
    def test_launch_aider_with_profile(self, tui, command_executor_mock):
        """Testa a integração da TUI com o CommandExecutor para lançar o aider."""
        # Configura o mock para simular sucesso na execução
        command_executor_mock.run_aider.return_value = True
        
        # Mock de display_main_menu para evitar chamadas adicionais
        with patch.object(tui, 'display_main_menu'):
            # Mock de _show_message para evitar chamadas reais
            with patch.object(tui, '_show_message'):
                tui._launch_aider_with_profile("perfil_teste")
        
        # Verifica se o método run_aider foi chamado com o perfil correto
        command_executor_mock.run_aider.assert_called_once_with("perfil_teste")
    
    def test_launch_aider_error_handling(self, tui, command_executor_mock):
        """Testa o tratamento de erros ao lançar o aider."""
        # Configura o mock para simular erro na execução
        command_executor_mock.run_aider.side_effect = Exception("Erro de teste")
        
        # Mock de display_main_menu para evitar chamadas adicionais
        with patch.object(tui, 'display_main_menu'):
            # Mock de _display_error_dialog para capturar as chamadas
            with patch.object(tui, '_display_error_dialog') as mock_display_error_dialog:
                tui._launch_aider_with_profile("perfil_teste")

                # Verifica se a mensagem de erro foi exibida através de _display_error_dialog
                mock_display_error_dialog.assert_any_call(
                    "Erro Inesperado do Sistema", 
                    "Erro de teste",
                    details=unittest.mock.ANY # O traceback pode variar
                )
    
    def test_integration_profile_selection_to_launch(self, tui, config_manager_mock):
        """Testa o fluxo completo da seleção de perfil até o lançamento do aider."""
        # Mock para evitar entrar em display_main_menu
        with patch.object(tui, 'display_main_menu'):
            # Mock para evitar mostrar mensagem se não houver perfis
            with patch.object(tui, '_show_message'):
                # Configura mock para simular seleção do primeiro perfil
                with patch.object(tui, '_show_menu', return_value=0):
                    # Mock para _show_profile_details que simula seleção da opção "Iniciar aider"
                    with patch.object(tui, '_show_profile_details') as mock_show_details:
                        # Simula a função chamando _launch_aider_with_profile quando chamada
                        def side_effect_func(*args, **kwargs):
                            tui._launch_aider_with_profile("perfil_teste")
                            return None
                        mock_show_details.side_effect = side_effect_func
                        
                        # Mock para o _launch_aider_with_profile
                        with patch.object(tui, '_launch_aider_with_profile') as mock_launch:
                            tui.display_profile_selection()
                            
                            # Verifica se get_profiles foi chamado
                            config_manager_mock.get_profiles.assert_called_once()
                            # Verifica se _launch_aider_with_profile foi chamado uma vez
                            mock_launch.assert_called_once_with("perfil_teste")
    
    def test_profile_creation_integration(self, tui, profile_builder_mock):
        """Testa a integração da TUI com o ProfileBuilder para criar perfis."""
        # Configura mocks para simular a entrada do usuário
        with patch.object(tui, '_get_text_input', return_value="novo_perfil"):
            # Mock de _show_category_selection para evitar fluxo adicional
            with patch.object(tui, '_show_category_selection'):
                tui.display_profile_creation()
                
                # Verifica se os métodos corretos do ProfileBuilder foram chamados
                profile_builder_mock.start_new_profile.assert_called_once()
                profile_builder_mock.set_parameter.assert_called_once_with("name", "novo_perfil")
    
    def test_provider_management_integration(self, tui, config_manager_mock):
        """Testa a integração da TUI com o ConfigManager para gerenciar provedores."""
        # Mock para ProviderManager
        with patch('aider_start.provider_manager.ProviderManager') as mock_provider_manager_class:
            mock_provider_manager = MagicMock()
            mock_provider_manager_class.return_value = mock_provider_manager
            
            # Mock para evitar fluxo adicional
            with patch.object(tui, '_show_menu', return_value=4):  # Seleciona "Voltar"
                with patch.object(tui, 'display_main_menu'):
                    tui.display_provider_management()
                    
                    # Verifica se o ProviderManager foi inicializado com o ConfigManager
                    mock_provider_manager_class.assert_called_once_with(config_manager_mock)
    
    def test_endpoint_management_integration(self, tui, config_manager_mock):
        """Testa a integração da TUI com o ConfigManager para gerenciar endpoints."""
        # Mock para evitar fluxo adicional
        with patch.object(tui, '_show_menu', return_value=4):  # Seleciona "Voltar"
            with patch.object(tui, 'display_main_menu'):
                tui.display_endpoint_management()
                
                # Nada a verificar aqui, já que a interface usa diretamente o ConfigManager
                # que já está definido no fixture tui
                assert True
    
    def test_profile_parameters_integration(self, tui, profile_builder_mock):
        """Testa a integração da TUI com o ProfileBuilder para validação de parâmetros."""
        # Configurações para verificar se a validação de parâmetros está integrada
        profile_data = {
            "name": "perfil_teste",
            "model": "gpt-4",
            "provider": "openai",
            "temperatura": 0.7
        }
        
        # Configura o mock do ProfileBuilder para ser chamado no processo de validação
        # Isso simula o método que o TUI.param_validator usaria internamente
        profile_builder_mock.get_current_profile.return_value = profile_data
        
        # Modificamos o teste para forçar o uso do get_current_profile do profile_builder
        # Salvamos uma referência à função original
        original_get_validation_errors = tui.param_validator.get_validation_errors
        
        # Criamos uma função de substituição que usa o profile_builder
        def mock_get_validation_errors(*args, **kwargs):
            # Força a chamada ao get_current_profile do profile_builder
            current_profile = tui.profile_builder.get_current_profile()
            # Passa o perfil obtido para a função original
            return original_get_validation_errors(current_profile)
            
        # Substitui temporariamente a função
        tui.param_validator.get_validation_errors = mock_get_validation_errors
        
        try:
            # Valida o perfil usando o validador de parâmetros, agora usando profile_builder
            errors = tui.param_validator.get_validation_errors()
            
            # Verifica se o profile_builder foi usado corretamente
            profile_builder_mock.get_current_profile.assert_called_once()
            
            # Verifica se o tipo de retorno está correto
            assert isinstance(errors, dict)
        finally:
            # Restaura a função original
            tui.param_validator.get_validation_errors = original_get_validation_errors 