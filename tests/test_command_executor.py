"""
Testes unitários para o módulo CommandExecutor.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import subprocess

from aider_start.command_executor import CommandExecutor
from aider_start.exceptions import ConfigError, ProfileNotFoundError, ProviderNotFoundError, EndpointNotFoundError, CommandBuildError, CommandExecutionError

class TestCommandExecutor(unittest.TestCase):
    """Testes para a classe CommandExecutor."""
    
    def setUp(self):
        """Configuração antes de cada teste."""
        # Criar um mock ConfigManager
        self.mock_config_manager = MagicMock()
        
        # Configurar dados de perfil mock
        self.mock_config_manager.get_profile.side_effect = lambda name: {
            'simple': {'model': 'gpt-4', 'temperature': 0.7},
            'with_provider': {'model': 'gpt-4', 'provider': 'openai'},
            'with_endpoint': {'model': 'llama-2', 'endpoint': 'local-llm'},
            'bool_params': {'model': 'gpt-4', 'stream': True, 'verbose': False},
            'empty_params': {'model': 'gpt-4', 'temperature': '', 'prompt': None},
            'profile_no_provider': {'model': 'gpt-4', 'provider': 'non_existent_provider'},
            'profile_no_endpoint': {'model': 'gpt-4', 'endpoint': 'non_existent_endpoint'}
        }.get(name)
        
        # Configurar dados de provedor mock
        self.mock_config_manager.get_provider.side_effect = lambda name: {
            'openai': {'api_type': 'openai', 'models': ['gpt-4', 'gpt-3.5-turbo']}
        }.get(name)
        
        # Configurar dados de endpoint mock
        self.mock_config_manager.get_endpoint.side_effect = lambda name: {
            'local-llm': {'api_url': 'http://localhost:8000/v1', 'api_type': 'openai', 'models': ['llama-2']}
        }.get(name)
        
        # Configurar recuperação de chaves API mock
        self.mock_config_manager.get_api_key.side_effect = lambda name: {
            'openai': 'openai-api-key',
            'endpoint_local-llm': 'local-api-key'
        }.get(name)
        
        # Criar um CommandExecutor com o ConfigManager mock
        self.executor = CommandExecutor(self.mock_config_manager)
    
    def test_init_without_config_manager(self):
        """Testa inicialização sem ConfigManager."""
        executor = CommandExecutor()
        self.assertIsNone(executor.config_manager)
    
    @patch('aider_start.command_executor.subprocess.run')
    def test_check_aider_installed_success(self, mock_run):
        """Testa verificação bem-sucedida de instalação do aider."""
        # Configura o mock para retornar um código de saída 0 (sucesso)
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.executor.check_aider_installed()
        
        # Verifica se o comando foi executado corretamente
        mock_run.assert_called_once_with(
            ["aider", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=False,
            text=True
        )
        
        # Verifica o resultado
        self.assertTrue(result)
    
    @patch('aider_start.command_executor.subprocess.run')
    def test_check_aider_installed_error_code(self, mock_run):
        """Testa verificação de instalação do aider com código de erro."""
        # Configura o mock para retornar um código de saída 1 (erro)
        mock_run.return_value = MagicMock(returncode=1)
        
        result = self.executor.check_aider_installed()
        
        # Verifica o resultado
        self.assertFalse(result)
    
    @patch('aider_start.command_executor.subprocess.run')
    def test_check_aider_installed_not_found(self, mock_run):
        """Testa verificação de instalação do aider quando não encontrado."""
        # Configura o mock para lançar FileNotFoundError
        mock_run.side_effect = FileNotFoundError()
        
        result = self.executor.check_aider_installed()
        
        # Verifica o resultado
        self.assertFalse(result)
    
    def test_build_command_simple(self):
        """Testa construção de um comando simples."""
        cmd = self.executor.build_command('simple')
        
        # Verifica o comando
        self.assertEqual(cmd, ['aider', '--model', 'gpt-4', '--temperature', '0.7'])
    
    def test_build_command_with_provider(self):
        """Testa construção de um comando com provedor."""
        cmd = self.executor.build_command('with_provider')
        
        # Verifica o comando
        # O modelo do provider também é adicionado ao comando
        expected_cmd = [
            'aider', 
            '--model', 'gpt-4', 
            '--api-type', 'openai'
        ]
        self.assertEqual(cmd, expected_cmd)
    
    def test_build_command_with_endpoint(self):
        """Testa construção de um comando com endpoint personalizado."""
        cmd = self.executor.build_command('with_endpoint')
        
        # Verifica o comando
        self.assertEqual(cmd, [
            'aider',
            '--model', 'llama-2',
            '--api-base', 'http://localhost:8000/v1',
            '--api-type', 'openai'
        ])
    
    def test_build_command_boolean_params(self):
        """Testa construção de um comando com parâmetros booleanos."""
        cmd = self.executor.build_command('bool_params')
        
        # Verifica o comando
        self.assertIn('--stream', cmd)
        self.assertIn('--no-verbose', cmd)
    
    def test_build_command_empty_params(self):
        """Testa construção de um comando com parâmetros vazios ou nulos."""
        cmd = self.executor.build_command('empty_params')
        
        # Verifica o comando
        self.assertEqual(cmd, ['aider', '--model', 'gpt-4'])
        self.assertNotIn('--temperature', cmd)
        self.assertNotIn('--prompt', cmd)
    
    def test_build_command_no_config_manager(self):
        """Testa construção de um comando sem ConfigManager."""
        executor = CommandExecutor()  # Sem ConfigManager
        
        with self.assertRaises(CommandBuildError) as context:
            executor.build_command('simple')
        
        self.assertIn("ConfigManager não inicializado", str(context.exception))
    
    def test_build_command_profile_not_found(self):
        """Testa construção de um comando com perfil inexistente."""
        # Configurar mock para levantar ProfileNotFoundError
        self.mock_config_manager.get_profile.side_effect = ProfileNotFoundError("Perfil mock não encontrado")
        
        with self.assertRaises(CommandBuildError) as context:
            self.executor.build_command('non_existent')
        
        self.assertTrue("Erro de configuração para perfil 'non_existent'" in str(context.exception) or 
                        "Perfil mock não encontrado" in str(context.exception.args[0]))

    def test_build_command_provider_not_found(self):
        """Testa construção com perfil que aponta para provedor inexistente."""
        self.mock_config_manager.get_provider.side_effect = ProviderNotFoundError("Provedor mock não encontrado")
        with self.assertRaises(CommandBuildError) as context:
            self.executor.build_command('profile_no_provider')
        self.assertTrue("Provedor 'non_existent_provider' não encontrado" in str(context.exception))

    def test_build_command_endpoint_not_found(self):
        """Testa construção com perfil que aponta para endpoint inexistente."""
        self.mock_config_manager.get_endpoint.side_effect = EndpointNotFoundError("Endpoint mock não encontrado")
        with self.assertRaises(CommandBuildError) as context:
            self.executor.build_command('profile_no_endpoint')
        self.assertTrue("Endpoint 'non_existent_endpoint' não encontrado" in str(context.exception))

    @patch('aider_start.command_executor.subprocess.run')
    def test_execute_command_windows(self, mock_run):
        """Testa execução de um comando no Windows."""
        # Configura o mock para retornar sucesso
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        # Patch para check_aider_installed
        with patch.object(self.executor, 'check_aider_installed', return_value=True):
            # Patch para _prepare_env_for_profile
            with patch.object(self.executor, '_prepare_env_for_profile', return_value={'TEST_ENV': 'value'}) as mock_prepare_env:
                # Patch para verificar se estamos no Windows
                with patch('aider_start.command_executor.sys.platform', 'win32'):
                    # Executa o comando
                    self.executor.execute_command('simple') 
                    
                    # Verifica se o comando foi executado com os parâmetros corretos
                    mock_run.assert_called_once_with(
                        ['aider', '--model', 'gpt-4', '--temperature', '0.7'],
                        check=False, text=True, capture_output=True, env={'TEST_ENV': 'value'}
                    )
                    
                    # Verifica se _prepare_env_for_profile foi chamado com o perfil correto
                    mock_prepare_env.assert_called_once_with('simple')
    
    @patch('aider_start.command_executor.os.execvpe')
    def test_execute_command_unix(self, mock_execvpe):
        """Testa execução de um comando no Unix."""
        # Pular este teste no Windows
        if sys.platform == 'win32':
            self.skipTest("Teste específico para sistemas Unix")
            
        # Patch para check_aider_installed
        with patch.object(self.executor, 'check_aider_installed', return_value=True):
            # Patch para _prepare_env_for_profile
            with patch.object(self.executor, '_prepare_env_for_profile', return_value={'TEST_ENV': 'value'}) as mock_prepare_env:
                # Patch para verificar se estamos no Unix
                with patch('aider_start.command_executor.sys.platform', 'linux'):
                    # Executa o comando
                    self.executor.execute_command('simple')
                    
                    # Verifica se o comando foi executado com execvpe
                    mock_execvpe.assert_called_once_with('aider', 
                                                       ['aider', '--model', 'gpt-4', '--temperature', '0.7'],
                                                       {'TEST_ENV': 'value'})
                    
                    # Verifica se _prepare_env_for_profile foi chamado com o perfil correto
                    mock_prepare_env.assert_called_once_with('simple')
    
    def test_execute_command_aider_not_installed(self):
        """Testa execução de um comando quando o aider não está instalado."""
        # Patch para check_aider_installed retornar False
        with patch.object(self.executor, 'check_aider_installed', return_value=False):
            with self.assertRaises(CommandExecutionError) as context:
                self.executor.execute_command('simple')
            self.assertIn("aider não está instalado", str(context.exception))
    
    @patch('aider_start.command_executor.subprocess.run')
    @patch('aider_start.command_executor.logger') # Mock o logger do módulo
    def test_execute_command_subprocess_error_windows(self, mock_logger, mock_run):
        """Testa CommandExecutionError quando subprocess.run falha no Windows."""
        # Configura o mock para simular falha de subprocesso
        mock_run.return_value = MagicMock(returncode=1, stderr="Falha simulada no subprocesso")
        
        with patch.object(self.executor, 'check_aider_installed', return_value=True):
            with patch('aider_start.command_executor.sys.platform', 'win32'):
                with self.assertRaises(CommandExecutionError) as context:
                    self.executor.execute_command('simple')
                
                self.assertIn("Comando aider falhou (código: 1)", str(context.exception))
                self.assertIn("Falha simulada no subprocesso", str(context.exception))
                mock_logger.error.assert_called_once() # Verifica se o logger.error foi chamado

                self.assertIn("Comando aider falhou (código: 1). Detalhes: Falha simulada no subprocesso", mock_logger.error.call_args[0][0])

    @patch('aider_start.command_executor.os.execvpe')
    @patch('aider_start.command_executor.logger') # Mock o logger
    def test_execute_command_os_error_unix(self, mock_logger, mock_execvpe):
        """Testa CommandExecutionError quando os.execvpe falha no Unix."""
        # Pular este teste no Windows
        if sys.platform == 'win32':
            self.skipTest("Teste específico para sistemas Unix")
            
        mock_execvpe.side_effect = OSError("Erro simulado no os.execvpe")
        
        with patch.object(self.executor, 'check_aider_installed', return_value=True):
            with patch('aider_start.command_executor.sys.platform', 'linux'): # Simula Unix
                with self.assertRaises(CommandExecutionError) as context:
                    self.executor.execute_command('simple')
                self.assertIn("Erro de Sistema Operacional", str(context.exception))
                self.assertIn("Erro simulado no os.execvpe", str(context.exception))
                mock_logger.error.assert_called_once()
                self.assertIn("Erro de Sistema Operacional ao tentar executar", mock_logger.error.call_args[0][0])

    @patch('aider_start.command_executor.logger')
    def test_execute_command_build_error_propagates(self, mock_logger):
        """Testa se CommandBuildError de build_command é propagado por execute_command."""
        self.mock_config_manager.get_profile.side_effect = ProfileNotFoundError("Perfil de teste não existe")
        
        with self.assertRaises(CommandBuildError) as context:
            self.executor.execute_command('non_existent_profile')
        self.assertTrue("Erro de configuração para perfil 'non_existent_profile'" in str(context.exception) or
                        "Perfil de teste não existe" in str(context.exception.args[0]))
        # Verifica se o logger.error foi chamado dentro de build_command E se o print ocorreu em execute_command.
        # O logger em build_command é o que queremos confirmar aqui.
        mock_logger.error.assert_called() # Chamado em build_command

    def test_run_aider_calls_execute_command(self):
        """Testa se run_aider chama execute_command."""
        # Patch para execute_command
        with patch.object(self.executor, 'execute_command', return_value=True) as mock_execute:
            result = self.executor.run_aider('simple')
            
            # Verifica se execute_command foi chamado
            mock_execute.assert_called_once_with('simple')
            
            # Verifica o resultado
            self.assertTrue(result)

if __name__ == '__main__':
    unittest.main() 