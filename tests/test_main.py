"""
Testes para o módulo main.
"""
import sys
import pytest
from unittest.mock import patch, MagicMock

from aider_start.main import parse_args, main


class TestMain:
    """Testes para as funções do módulo main."""
    
    # Patch global para prevenir que a TUI real seja iniciada em qualquer teste
    @pytest.fixture(autouse=True)
    def prevent_real_tui(self):
        """Previne que a TUI real seja iniciada em qualquer teste."""
        with patch('aider_start.main.TUI', autospec=True) as mock_tui:
            mock_instance = MagicMock()
            mock_tui.return_value = mock_instance
            yield mock_tui, mock_instance
    
    def test_parse_args_default(self):
        """Testa o parse_args com argumentos padrão."""
        with patch('sys.argv', ['main.py']):
            args = parse_args()
            assert args.config is False
            assert args.profile is None
            assert args.list is False
            assert args.version is False
    
    def test_parse_args_config(self):
        """Testa o parse_args com a flag de configuração."""
        with patch('sys.argv', ['main.py', '--config']):
            args = parse_args()
            assert args.config is True
            
        with patch('sys.argv', ['main.py', '-c']):
            args = parse_args()
            assert args.config is True
    
    def test_parse_args_profile(self):
        """Testa o parse_args com a opção de perfil."""
        with patch('sys.argv', ['main.py', '--profile', 'test_profile']):
            args = parse_args()
            assert args.profile == 'test_profile'
            
        with patch('sys.argv', ['main.py', '-p', 'test_profile']):
            args = parse_args()
            assert args.profile == 'test_profile'
    
    def test_parse_args_list(self):
        """Testa o parse_args com a flag de listar."""
        with patch('sys.argv', ['main.py', '--list']):
            args = parse_args()
            assert args.list is True
            
        with patch('sys.argv', ['main.py', '-l']):
            args = parse_args()
            assert args.list is True
    
    def test_parse_args_version(self):
        """Testa o parse_args com a flag de versão."""
        with patch('sys.argv', ['main.py', '--version']):
            args = parse_args()
            assert args.version is True
            
        with patch('sys.argv', ['main.py', '-v']):
            args = parse_args()
            assert args.version is True
    
    def test_parse_args_combined(self):
        """Testa o parse_args com múltiplos argumentos."""
        with patch('sys.argv', ['main.py', '-l', '-v']):
            args = parse_args()
            assert args.list is True
            assert args.version is True
    
    @patch('aider_start.main.print')
    def test_main_version(self, mock_print):
        """Testa a exibição de versão."""
        with patch('sys.argv', ['main.py', '--version']):
            exit_code = main()
            assert exit_code == 0
            mock_print.assert_called_with("aider-start v0.1.0")
    
    @patch('aider_start.main.SecureConfigManager')
    @patch('aider_start.main.ProfileBuilder')
    @patch('aider_start.main.CommandExecutor')
    @patch('aider_start.main.print')
    def test_main_list_empty(self, mock_print, mock_cmd, mock_profile, mock_config):
        """Testa a listagem de perfis quando nenhum perfil existe."""
        # Configurar mock
        config_instance = MagicMock()
        config_instance.get_profiles.return_value = {}
        mock_config.return_value = config_instance
        
        with patch('sys.argv', ['main.py', '--list']):
            exit_code = main()
            assert exit_code == 0
            mock_print.assert_called_with("Nenhum perfil encontrado.")
    
    @patch('aider_start.main.SecureConfigManager')
    @patch('aider_start.main.ProfileBuilder')
    @patch('aider_start.main.CommandExecutor')
    @patch('aider_start.main.print')
    def test_main_list_with_profiles(self, mock_print, mock_cmd, mock_profile, mock_config):
        """Testa a listagem de perfis quando existem perfis."""
        # Configurar mock
        config_instance = MagicMock()
        config_instance.get_profiles.return_value = {'profile1': {}, 'profile2': {}}
        mock_config.return_value = config_instance
        
        with patch('sys.argv', ['main.py', '--list']):
            exit_code = main()
            assert exit_code == 0
            mock_print.assert_any_call("Perfis disponíveis:")
            mock_print.assert_any_call("  profile1")
            mock_print.assert_any_call("  profile2")
    
    @patch('aider_start.main.SecureConfigManager')
    @patch('aider_start.main.ProfileBuilder')
    @patch('aider_start.main.CommandExecutor')
    @patch('aider_start.main.print')
    def test_main_profile_not_found(self, mock_print, mock_cmd, mock_profile, mock_config):
        """Testa a execução com um perfil inexistente."""
        # Configurar mock
        config_instance = MagicMock()
        config_instance.get_profiles.return_value = {'profile1': {}}
        mock_config.return_value = config_instance
        
        with patch('sys.argv', ['main.py', '--profile', 'nonexistent']):
            exit_code = main()
            assert exit_code == 1
            mock_print.assert_any_call("Erro: Perfil 'nonexistent' não encontrado.")
    
    @patch('aider_start.main.SecureConfigManager')
    @patch('aider_start.main.ProfileBuilder')
    @patch('aider_start.main.CommandExecutor')
    @patch('aider_start.main.print')
    def test_main_profile_success(self, mock_print, mock_cmd, mock_profile, mock_config):
        """Testa a execução bem-sucedida com um perfil existente."""
        # Configurar mocks
        config_instance = MagicMock()
        config_instance.get_profiles.return_value = {'profile1': {}}
        mock_config.return_value = config_instance
        
        cmd_instance = MagicMock()
        cmd_instance.execute_command.return_value = True
        mock_cmd.return_value = cmd_instance
        
        with patch('sys.argv', ['main.py', '--profile', 'profile1']):
            exit_code = main()
            assert exit_code == 0
            cmd_instance.execute_command.assert_called_with('profile1')
    
    @patch('aider_start.main.SecureConfigManager')
    @patch('aider_start.main.ProfileBuilder')
    @patch('aider_start.main.CommandExecutor')
    @patch('aider_start.main.print')
    def test_main_profile_failure(self, mock_print, mock_cmd, mock_profile, mock_config):
        """Testa a execução com falha com um perfil existente."""
        # Configurar mocks
        config_instance = MagicMock()
        config_instance.get_profiles.return_value = {'profile1': {}}
        mock_config.return_value = config_instance
        
        cmd_instance = MagicMock()
        cmd_instance.execute_command.return_value = False
        mock_cmd.return_value = cmd_instance
        
        with patch('sys.argv', ['main.py', '--profile', 'profile1']):
            exit_code = main()
            assert exit_code == 1
            cmd_instance.execute_command.assert_called_with('profile1')
    
    @patch('aider_start.main.SecureConfigManager')
    @patch('aider_start.main.ProfileBuilder')
    @patch('aider_start.main.CommandExecutor')
    @patch('aider_start.main.print')
    def test_main_tui_start(self, mock_print, mock_cmd, mock_profile, mock_config, prevent_real_tui):
        """Testa o início da TUI."""
        # Obter os mocks da fixture
        mock_tui_class, mock_tui_instance = prevent_real_tui
        
        # Configurar mocks
        config_instance = MagicMock()
        mock_config.return_value = config_instance
        
        with patch('sys.argv', ['main.py']):
            exit_code = main()
            assert exit_code == 0
            mock_tui_class.assert_called_once()
            mock_tui_instance.start.assert_called_once()
    
    @patch('aider_start.main.SecureConfigManager')
    @patch('aider_start.main.ProfileBuilder')
    @patch('aider_start.main.CommandExecutor')
    @patch('aider_start.main.print')
    def test_main_tui_exception(self, mock_print, mock_cmd, mock_profile, mock_config, prevent_real_tui):
        """Testa exceção ao iniciar a TUI."""
        # Obter os mocks da fixture
        mock_tui_class, mock_tui_instance = prevent_real_tui
        
        # Configurar mocks
        config_instance = MagicMock()
        mock_config.return_value = config_instance
        
        # Configurar exceção
        mock_tui_instance.start.side_effect = Exception("TUI error")
        
        with patch('sys.argv', ['main.py']):
            exit_code = main()
            assert exit_code == 1
            mock_print.assert_any_call("Erro na interface gráfica: TUI error")
    
    @patch('aider_start.main.SecureConfigManager')
    @patch('aider_start.main.print')
    def test_main_config_initialization_exception(self, mock_print, mock_config):
        """Testa exceção ao inicializar componentes."""
        # Configurar mock para lançar exceção
        mock_config.side_effect = Exception("Init error")
        
        with patch('sys.argv', ['main.py']):
            exit_code = main()
            assert exit_code == 1
            mock_print.assert_called_with("Erro inicializando a aplicação: Init error")
    
    @patch('aider_start.main.SecureConfigManager')
    @patch('aider_start.main.ProfileBuilder')
    @patch('aider_start.main.CommandExecutor')
    @patch('aider_start.main.print')
    def test_main_config_mode(self, mock_print, mock_cmd, mock_profile, mock_config, prevent_real_tui):
        """Testa o modo de configuração."""
        # Configurar mocks
        config_instance = MagicMock()
        mock_config.return_value = config_instance
        
        with patch('sys.argv', ['main.py', '--config']):
            # Como o modo de configuração ainda não está implementado, deve cair na TUI
            main()
            mock_print.assert_any_call("Modo de configuração via CLI ainda não implementado.")
            mock_print.assert_any_call("Iniciando a interface TUI para configuração...") 