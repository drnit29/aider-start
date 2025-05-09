import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from aider_start.config_manager import ConfigManager
from aider_start.profile_builder import ProfileBuilder
from aider_start.command_executor import CommandExecutor

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for config files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)
        self.config_file = self.config_dir / 'config.json'
        
        # Patch the CONFIG_DIR and CONFIG_FILE constants
        self.patcher1 = patch('aider_start.config_manager.CONFIG_DIR', self.config_dir)
        self.patcher2 = patch('aider_start.config_manager.CONFIG_FILE', self.config_file)
        self.patcher_prev = patch('aider_start.config_manager.CONFIG_PREV_FILE', self.config_dir / 'config.json.prev')
        self.patcher_lastgood = patch('aider_start.config_manager.CONFIG_LASTGOOD_FILE', self.config_dir / 'config.json.lastgood')
        self.patcher_backup = patch('aider_start.config_manager.CONFIG_BACKUP_FILE', self.config_dir / 'config.json.bak')

        self.patcher1.start()
        self.patcher2.start()
        self.patcher_prev.start()
        self.patcher_lastgood.start()
        self.patcher_backup.start()
        
        # Mock keyring
        self.keyring_patcher = patch('aider_start.config_manager.keyring')
        self.mock_keyring = self.keyring_patcher.start()
        
        # Mock logger in modules to prevent console output during tests
        self.logger_config_patcher = patch('aider_start.config_manager.logger', MagicMock())
        self.logger_utils_patcher = patch('aider_start.utils.logger', MagicMock())
        self.logger_executor_patcher = patch('aider_start.command_executor.logger', MagicMock())
        # No logger to patch in profile_builder module level or directly in class for now

        self.mock_logger_config = self.logger_config_patcher.start()
        self.mock_logger_utils = self.logger_utils_patcher.start()
        self.mock_logger_executor = self.logger_executor_patcher.start()

        # Create components
        self.config_manager = ConfigManager() 
        self.profile_builder = ProfileBuilder(self.config_manager)
        self.command_executor = CommandExecutor(self.config_manager)
    
    def tearDown(self):
        # Stop the patchers
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher_prev.stop()
        self.patcher_lastgood.stop()
        self.patcher_backup.stop()
        self.keyring_patcher.stop()
        self.logger_config_patcher.stop()
        self.logger_utils_patcher.stop()
        self.logger_executor_patcher.stop()
        # No logger patcher for profile_builder to stop
        
        # Clean up the temporary directory
        self.temp_dir.cleanup()
    
    def test_create_profile_and_execute(self):
        """Test creating a profile and executing a command"""
        # Set up the profile builder
        self.profile_builder.start_new_profile()
        self.profile_builder.set_parameter('name', 'test_profile')
        self.profile_builder.set_parameter('model', 'gpt-4')
        self.profile_builder.set_parameter('temperatura', 0.7)
        
        # Save the profile
        self.profile_builder.save_profile()
        
        # Verify the profile was saved in ConfigManager
        saved_profile = self.config_manager.get_profile('test_profile')
        self.assertIsNotNone(saved_profile)
        self.assertEqual(saved_profile.get('model'), 'gpt-4')
        self.assertEqual(saved_profile.get('temperatura'), 0.7)
        self.assertNotIn('name', saved_profile)
        
        # Build and Execute a command from the profile
        with patch('aider_start.command_executor.subprocess.run') as mock_run:
            with patch('aider_start.command_executor.CommandExecutor.check_aider_installed', return_value=True):
                # Set up the mock to return a successful result
                mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
                
                # Execute the command using patch.dict to handle os.environ
                with patch.dict(os.environ, {}, clear=True):
                    with patch('aider_start.command_executor.sys.platform', 'win32'): # Simulate Windows for subprocess.run
                        result = self.command_executor.execute_command('test_profile')
                        self.assertTrue(result)
                
                # Verify the command was executed correctly
                mock_run.assert_called_once()
                called_cmd = mock_run.call_args[0][0]
                self.assertIn('aider', called_cmd)
                self.assertIn('--model', called_cmd)
                self.assertIn('gpt-4', called_cmd)
                self.assertIn('--temperatura', called_cmd)
                self.assertIn('0.7', called_cmd)
    
    def test_provider_integration(self):
        """Test provider integration with profiles and command execution"""
        # Add a provider
        provider_data = {
            'description': 'Test OpenAI Provider',
            'api_url': 'https://api.openai.com/v1',
            'api_key': 'test-api-key',
            'models': ['gpt-4', 'gpt-3.5-turbo'],
            'api_key_env_var': 'OPENAI_API_KEY',
            'params': {
                'api_type': {'value': 'openai', 'cli_arg': '--api-type'}
            }
        }
        self.config_manager.add_provider('openai_test_provider', provider_data)
        
        # Set up the mock keyring to return the API key when get_api_key is called
        self.mock_keyring.get_password.return_value = 'test-api-key'
        
        # Create a profile that uses the provider
        self.profile_builder.start_new_profile()
        self.profile_builder.set_parameter('name', 'provider_profile')
        self.profile_builder.set_parameter('model', 'gpt-4')
        self.profile_builder.set_parameter('provider', 'openai_test_provider')
        
        # Save the profile
        self.profile_builder.save_profile()
        
        # Build and Execute a command from the profile
        with patch('aider_start.command_executor.subprocess.run') as mock_run:
            with patch('aider_start.command_executor.CommandExecutor.check_aider_installed', return_value=True):
                mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
                
                # Execute the command using patch.dict to handle os.environ
                with patch.dict(os.environ, {}, clear=True):
                    with patch('aider_start.command_executor.sys.platform', 'win32'): 
                        result = self.command_executor.execute_command('provider_profile')
                        self.assertTrue(result)
                
                    # Verificar o ambiente passado para subprocess.run
                    called_kwargs = mock_run.call_args[1] # Acessa o dicionário de kwargs
                    self.assertIn('env', called_kwargs)
                    self.assertIsNotNone(called_kwargs['env'], "O argumento 'env' para subprocess.run não deveria ser None.")
                    self.assertEqual(called_kwargs['env'].get('OPENAI_API_KEY'), 'test-api-key')

                mock_run.assert_called_once()
                cmd_args = mock_run.call_args[0][0]
                self.assertIn('aider', cmd_args)
                self.assertIn('--model', cmd_args)
                self.assertIn('gpt-4', cmd_args)
                self.assertIn('--api-type', cmd_args)
                self.assertIn('openai', cmd_args)

if __name__ == '__main__':
    unittest.main() 