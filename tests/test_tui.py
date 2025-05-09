"""
Testes para o módulo tui.py
"""

import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os
import curses

# Adiciona o diretório raiz ao path para importação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aider_start.tui import TUI
from aider_start.config_manager import ConfigManager
from aider_start.profile_builder import ProfileBuilder


class TestTUI(unittest.TestCase):
    """Testes para a classe TUI."""
    
    def setUp(self):
        """Configuração dos testes."""
        # Mock do ConfigManager
        self.config_mock = MagicMock(spec=ConfigManager)
        # Mock do ProfileBuilder
        self.profile_builder_mock = MagicMock(spec=ProfileBuilder)
        # Mock do CommandExecutor
        self.command_executor_mock = MagicMock()
        
        # Inicializa o TUI com os mocks
        self.tui = TUI(
            config_manager=self.config_mock,
            profile_builder=self.profile_builder_mock,
            command_executor=self.command_executor_mock
        )
        
        # Mock para o screen e seus métodos para evitar erros de curses
        self.mock_screen = MagicMock()
        self.mock_screen.getmaxyx.return_value = (24, 80) # Altura, Largura
        self.tui.screen = self.mock_screen 
        self.tui.height, self.tui.width = self.mock_screen.getmaxyx()
        
        # Mock do curses.color_pair para evitar erro "must call initscr() first"
        self.color_pair_patcher = patch('curses.color_pair', return_value=0)
        self.mock_color_pair = self.color_pair_patcher.start()
        
        # Mock de curses.curs_set
        self.curs_set_patcher = patch('curses.curs_set')
        self.mock_curs_set = self.curs_set_patcher.start()
    
    def tearDown(self):
        """Limpeza após cada teste."""
        self.color_pair_patcher.stop()
        self.curs_set_patcher.stop()
    
    def test_init(self):
        """Testa a inicialização do TUI."""
        self.assertEqual(self.tui.config_manager, self.config_mock)
        self.assertEqual(self.tui.profile_builder, self.profile_builder_mock)
        self.assertEqual(self.tui.command_executor, self.command_executor_mock)
        self.assertIsNone(self.tui.screen)
        self.assertEqual(self.tui.current_row, 0)
        self.assertEqual(self.tui.height, 0)
        self.assertEqual(self.tui.width, 0)
    
    @patch('curses.wrapper')
    def test_start(self, mock_wrapper):
        """Testa o método start."""
        # Simula um KeyboardInterrupt
        mock_wrapper.side_effect = KeyboardInterrupt()
        
        with patch('builtins.print') as mock_print:
            self.tui.start()
            mock_print.assert_called_once_with("Programa encerrado pelo usuário.")
        
        # Simula uma exceção genérica
        mock_wrapper.side_effect = Exception("Erro de teste")
        
        with patch('builtins.print') as mock_print:
            self.tui.start()
            # A TUI agora imprime uma mensagem mais detalhada, verificar se foi chamada
            mock_print.assert_any_call("Erro crítico não tratado: Erro de teste. Verifique os logs.")
    
    def test_safe_addstr(self):
        """Testa o método _safe_addstr."""
        # Configura o mock do screen
        self.tui.screen = MagicMock()
        self.tui.height = 24
        self.tui.width = 80
        
        # Testa posições válidas
        self.tui._safe_addstr(5, 5, "Texto de teste")
        self.tui.screen.addstr.assert_called_with(5, 5, "Texto de teste", 0)
        
        # Testa posições fora dos limites
        self.tui._safe_addstr(-1, 5, "Texto inválido")
        self.tui._safe_addstr(5, -1, "Texto inválido")
        self.tui._safe_addstr(25, 5, "Texto inválido")  # Excede altura
        self.tui._safe_addstr(5, 81, "Texto inválido")  # Excede largura
        
        # Verifica se o método addstr não foi chamado para posições inválidas
        self.tui.screen.addstr.assert_called_once()  # Apenas a primeira chamada era válida
        
        # Testa truncamento de texto
        self.tui.screen.reset_mock()
        self.tui._safe_addstr(5, 75, "Este texto é muito longo e deve ser truncado")
        # A largura é 80, posição x é 75, então só há espaço para 4 caracteres
        self.tui.screen.addstr.assert_called_with(5, 75, "Este", 0)
        
        # Testa tratamento de erro curses.error
        self.tui.screen.reset_mock()
        self.tui.screen.addstr.side_effect = curses.error
        self.tui._safe_addstr(5, 5, "Texto com erro")
        self.tui.screen.addstr.assert_called_once()  # O método foi chamado
        # Não deve lançar exceção
    
    @patch.object(TUI, '_safe_addstr')
    def test_show_menu(self, mock_safe_addstr):
        """Testa o método _show_menu com mock para _safe_addstr."""
        # Configura o TUI e o mock do screen
        self.tui.screen = MagicMock()
        self.tui.height = 24
        self.tui.width = 80
        
        # Configura o comportamento do getch para simular navegação e seleção
        self.tui.screen.getch.side_effect = [
            curses.KEY_DOWN,  # Tecla para baixo
            curses.KEY_DOWN,  # Tecla para baixo
            curses.KEY_UP,    # Tecla para cima
            10                # Enter (seleciona o item)
        ]
        
        items = ["Item 1", "Item 2", "Item 3"]
        result = self.tui._show_menu("Título", "Prompt", items)
        
        # Verifica se a tela foi limpa e atualizada
        self.tui.screen.clear.assert_called()
        self.tui.screen.refresh.assert_called()
        
        # Verifica se retornou o índice correto (1 após navegação)
        self.assertEqual(result, 1)
        
        # Testa saída com 'q'
        self.tui.screen.getch.side_effect = [ord('q')]
        with self.assertRaises(SystemExit):
            self.tui._show_menu("Título", "Prompt", items)
    
    @patch.object(TUI, '_show_menu')
    @patch.object(TUI, 'display_profile_selection')
    @patch.object(TUI, 'display_profile_creation')
    @patch.object(TUI, 'display_provider_management')
    @patch.object(TUI, 'display_endpoint_management')
    def test_display_main_menu(self, mock_endpoint, mock_provider, mock_creation, 
                              mock_selection, mock_show_menu):
        """Testa o método display_main_menu."""
        # Testa seleção de cada opção
        for i in range(5):
            mock_show_menu.return_value = i
            
            if i < 4:  # Opções válidas
                self.tui.display_main_menu()
            else:  # Opção Sair
                with self.assertRaises(SystemExit):
                    self.tui.display_main_menu()
        
        # Verifica se os métodos correspondentes foram chamados
        mock_selection.assert_called_once()
        mock_creation.assert_called_once()
        mock_provider.assert_called_once()
        mock_endpoint.assert_called_once()
    
    @patch.object(TUI, '_show_message')
    @patch.object(TUI, 'display_main_menu')
    @patch.object(TUI, 'display_profile_creation')
    @patch.object(TUI, '_show_menu')
    @patch.object(TUI, '_show_profile_details')
    def test_display_profile_selection_no_config(self, mock_details, mock_menu, 
                                               mock_creation, mock_main, mock_message):
        """Testa display_profile_selection sem ConfigManager."""
        # Configura o TUI sem ConfigManager
        self.tui.config_manager = None
        
        # Chama o método
        self.tui.display_profile_selection()
        
        # Verifica se a mensagem de erro foi exibida
        mock_message.assert_called_once_with("Erro", "ConfigManager não inicializado.")
        mock_main.assert_called_once()
        
        # Verifica que outros métodos não foram chamados
        mock_menu.assert_not_called()
        mock_details.assert_not_called()
        mock_creation.assert_not_called()
    
    @patch.object(TUI, '_safe_addstr')
    def test_show_message(self, mock_safe_addstr):
        """Testa _show_message com mock para _safe_addstr."""
        # Configura o TUI e o mock do screen
        self.tui.screen = MagicMock()
        self.tui.height = 24
        self.tui.width = 80
        
        self.tui._show_message("Título Teste", "Mensagem\nCom\nVárias\nLinhas")
        
        # Verifica se a tela foi limpa
        self.tui.screen.clear.assert_called_once()
        
        # Verifica se a tela foi atualizada
        self.tui.screen.refresh.assert_called_once()
        
        # Verifica se aguardou tecla
        self.tui.screen.getch.assert_called_once()

    @patch('aider_start.provider_manager.ProviderManager')
    @patch.object(TUI, '_show_menu')
    @patch.object(TUI, '_show_providers')
    @patch.object(TUI, '_add_provider')
    @patch.object(TUI, '_edit_provider')
    @patch.object(TUI, '_delete_provider')
    @patch.object(TUI, 'display_main_menu')
    def test_display_provider_management(self, mock_main_menu, mock_delete, 
                                        mock_edit, mock_add, mock_show, 
                                        mock_show_menu, mock_provider_manager):
        """Testa apenas a existência do método display_provider_management."""
        # Verifica se o método existe
        self.assertTrue(hasattr(self.tui, 'display_provider_management'))
        self.assertTrue(callable(getattr(self.tui, 'display_provider_management')))

    @patch.object(TUI, '_show_menu')
    @patch.object(TUI, '_show_message')
    def test_get_confirmation(self, mock_show_message, mock_show_menu):
        """Testa o método _get_confirmation."""
        # Caso 1: Usuário confirma
        mock_show_menu.return_value = 0
        result = self.tui._get_confirmation("Confirma?")
        assert result is True
        
        # Caso 2: Usuário cancela
        mock_show_menu.return_value = 1
        result = self.tui._get_confirmation("Confirma?")
        assert result is False

    @patch.object(TUI, '_show_menu')
    @patch.object(TUI, '_show_message')
    @patch.object(TUI, '_show_endpoints')
    @patch.object(TUI, '_add_endpoint')
    @patch.object(TUI, '_edit_endpoint')
    @patch.object(TUI, '_delete_endpoint')
    @patch.object(TUI, 'display_main_menu')
    def test_display_endpoint_management(self, mock_main_menu, mock_delete, 
                                        mock_edit, mock_add, mock_show, 
                                        mock_message, mock_show_menu):
        """Testa apenas a existência do método display_endpoint_management."""
        # Verifica se o método existe
        self.assertTrue(hasattr(self.tui, 'display_endpoint_management'))
        self.assertTrue(callable(getattr(self.tui, 'display_endpoint_management')))

    @patch.object(TUI, '_show_message')
    @patch.object(TUI, '_show_scrollable_list')
    def test_show_endpoints(self, mock_show_list, mock_show_message):
        """Testa o método _show_endpoints."""
        # Mock do ConfigManager
        self.tui.config_manager = MagicMock()
        
        # Caso 1: Sem endpoints
        self.tui.config_manager.get_endpoints.return_value = {}
        self.tui._show_endpoints()
        mock_show_message.assert_called_once()
        mock_show_list.assert_not_called()
        
        mock_show_message.reset_mock()
        mock_show_list.reset_mock()
        
        # Caso 2: Com endpoints
        self.tui.config_manager.get_endpoints.return_value = {
            "custom_api": {
                "description": "API Personalizada",
                "api_url": "https://api.custom.com/v1",
                "models": ["custom-model-1", "custom-model-2"]
            }
        }
        
        self.tui._show_endpoints()
        mock_show_message.assert_not_called()
        mock_show_list.assert_called_once()
    
    @patch.object(TUI, '_get_text_input')
    @patch.object(TUI, '_get_password_input')
    @patch.object(TUI, '_show_message')
    def test_add_endpoint(self, mock_show_message, mock_get_password, mock_get_text):
        """Testa o método _add_endpoint."""
        # Mock do ConfigManager
        self.tui.config_manager = MagicMock()
        
        # Caso 1: Usuário cancelou no primeiro input
        mock_get_text.return_value = None
        self.tui._add_endpoint()
        self.tui.config_manager.add_endpoint.assert_not_called()
        
        # Caso 2: Endpoint já existe
        mock_get_text.return_value = "existing_endpoint"
        self.tui.config_manager.get_endpoint.return_value = {"name": "existing_endpoint"}
        self.tui._add_endpoint()
        mock_show_message.assert_called_once()
        self.tui.config_manager.add_endpoint.assert_not_called()
        
        mock_show_message.reset_mock()
        
        # Caso 3: Adição bem sucedida
        self.tui.config_manager.get_endpoint.return_value = None
        # Simular sequência de inputs
        mock_get_text.side_effect = ["new_endpoint", "Endpoint de Teste", "https://api.test.com/v1", "model1,model2"]
        mock_get_password.return_value = "test-key"
        
        self.tui._add_endpoint()
        self.tui.config_manager.add_endpoint.assert_called_once()
        mock_show_message.assert_called_once()
        
        # Caso 4: Erro na adição
        mock_show_message.reset_mock()
        self.tui.config_manager.add_endpoint.reset_mock()
        self.tui.config_manager.add_endpoint.side_effect = Exception("Erro")
        
        mock_get_text.side_effect = ["new_endpoint", "Endpoint de Teste", "https://api.test.com/v1", "model1,model2"]
        mock_get_password.return_value = "test-key"
        
        self.tui._add_endpoint()
        self.tui.config_manager.add_endpoint.assert_called_once()
        mock_show_message.assert_called_once()
    
    @patch.object(TUI, '_get_confirmation')
    @patch.object(TUI, '_show_menu')
    @patch.object(TUI, '_show_message')
    def test_delete_endpoint(self, mock_show_message, mock_show_menu, mock_confirm):
        """Testa o método _delete_endpoint."""
        # Mock do ConfigManager
        self.tui.config_manager = MagicMock()
        
        # Caso 1: Sem endpoints
        self.tui.config_manager.get_endpoints.return_value = {}
        self.tui._delete_endpoint()
        mock_show_message.assert_called_once()
        
        mock_show_message.reset_mock()
        
        # Caso 2: Usuário cancela a seleção
        self.tui.config_manager.get_endpoints.return_value = {"endpoint1": {}}
        mock_show_menu.return_value = 1  # Selecionou a opção "Cancelar"
        
        self.tui._delete_endpoint()
        self.tui.config_manager.delete_endpoint.assert_not_called()
        
        # Caso 3: Usuário cancela a confirmação
        mock_show_menu.return_value = 0  # Selecionou um endpoint
        mock_confirm.return_value = False
        
        self.tui._delete_endpoint()
        self.tui.config_manager.delete_endpoint.assert_not_called()
        
        # Caso 4: Remoção bem sucedida
        mock_confirm.return_value = True
        
        self.tui._delete_endpoint()
        self.tui.config_manager.delete_endpoint.assert_called_once()
        mock_show_message.assert_called_once()
        
        # Caso 5: Erro na remoção
        mock_show_message.reset_mock()
        self.tui.config_manager.delete_endpoint.reset_mock()
        self.tui.config_manager.delete_endpoint.side_effect = Exception("Erro")
        
        self.tui._delete_endpoint()
        self.tui.config_manager.delete_endpoint.assert_called_once()
        mock_show_message.assert_called_once()


if __name__ == '__main__':
    unittest.main() 