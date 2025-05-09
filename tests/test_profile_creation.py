"""
Teste para verificar a funcionalidade de criação de perfil sem depender da TUI.
"""

import unittest
from unittest.mock import MagicMock, patch

from aider_start.profile_builder import ProfileBuilder
from aider_start.param_db import ParameterDatabase
from aider_start.config_manager import ConfigManager

class TestProfileCreation(unittest.TestCase):
    """Testes para o fluxo de criação de perfil."""
    
    def setUp(self):
        """Configuração para cada teste."""
        # Mock para ConfigManager
        self.config_manager = MagicMock(spec=ConfigManager)
        self.config_manager.add_profile.return_value = True
        
        # Inicializar param_db real para ter acesso ao esquema JSON real
        self.param_db = ParameterDatabase()
        
        # Inicializar ProfileBuilder com configurações mocked
        self.profile_builder = ProfileBuilder(self.config_manager, self.param_db)
    
    def test_profile_building_flow(self):
        """Testa o fluxo de construção de um perfil completo."""
        # Iniciar novo perfil
        self.profile_builder.start_new_profile()
        
        # Definir nome do perfil
        profile_name = "Perfil de Teste"
        self.profile_builder.set_parameter("name", profile_name)
        
        # Verificar categorias disponíveis
        categories = self.profile_builder.get_categories()
        self.assertIsInstance(categories, list)
        self.assertTrue(len(categories) > 0)
        
        # Selecionar uma categoria (model_options) e configurar alguns parâmetros
        category = "model_options"
        
        # Obter parâmetros da categoria
        category_params = self.profile_builder.get_category_parameters(category)
        self.assertIsInstance(category_params, dict)
        self.assertTrue(len(category_params) > 0)
        
        # Configurar um parâmetro do tipo string
        param_name = "model"
        self.profile_builder.set_parameter(param_name, "gpt-4")
        
        # Verificar se o parâmetro foi configurado
        current_profile = self.profile_builder.get_current_profile()
        self.assertEqual(current_profile[param_name], "gpt-4")
        
        # Testar configuração de array
        param_name = "providers"
        if param_name in category_params:
            # Verificar o tipo do parâmetro
            param_type = self.profile_builder.get_parameter_raw_type(category, param_name)
            self.assertIn(param_type, ["array", ["array", "null"]])
            
            # Configurar lista de valores
            self.profile_builder.set_parameter(param_name, ["openai", "anthropic"])
            
            # Verificar se o parâmetro foi configurado
            current_profile = self.profile_builder.get_current_profile()
            self.assertEqual(current_profile[param_name], ["openai", "anthropic"])
        
        # Testar configuração de booleano
        param_name = "streaming"
        if param_name in category_params:
            param_type = self.profile_builder.get_parameter_raw_type(category, param_name)
            self.assertIn("boolean", param_type if isinstance(param_type, list) else [param_type])
            
            self.profile_builder.set_parameter(param_name, True)
            
            current_profile = self.profile_builder.get_current_profile()
            self.assertTrue(current_profile[param_name])
        
        # Testar configuração de inteiro
        param_name = "max_tokens"
        if param_name in category_params:
            param_type = self.profile_builder.get_parameter_raw_type(category, param_name)
            self.assertIn("integer", param_type if isinstance(param_type, list) else [param_type])
            
            self.profile_builder.set_parameter(param_name, 2048)
            
            current_profile = self.profile_builder.get_current_profile()
            self.assertEqual(current_profile[param_name], 2048)
        
        # Testar configuração de um parâmetro confidencial (API_KEY)
        category = "api_options"
        category_params = self.profile_builder.get_category_parameters(category)
        
        param_name = "api_key"
        if param_name in category_params:
            is_secret = self.profile_builder.is_parameter_secret(category, param_name)
            self.assertTrue(is_secret)
            
            self.profile_builder.set_parameter(param_name, "sk-1234567890")
            
            current_profile = self.profile_builder.get_current_profile()
            self.assertEqual(current_profile[param_name], "sk-1234567890")
        
        # Validar e salvar o perfil
        is_valid, _ = self.profile_builder.validate_profile()
        self.assertTrue(is_valid)
        
        # Salvar o perfil
        saved_profile = self.profile_builder.save_profile()
        
        # Verificar que o config_manager.add_profile foi chamado
        self.config_manager.add_profile.assert_called_once()
        
        # Verificar que o primeiro argumento foi o nome do perfil
        args, _ = self.config_manager.add_profile.call_args
        self.assertEqual(args[0], profile_name)
        
        # Verificar que o segundo argumento é um dicionário que NÃO contém a chave 'name'
        profile_data = args[1]
        self.assertIsInstance(profile_data, dict)
        self.assertNotIn('name', profile_data)
        
        # Verificar que o perfil retornado pelo save_profile inclui 'name'
        self.assertIn('name', saved_profile)
        self.assertEqual(saved_profile['name'], profile_name)


if __name__ == "__main__":
    unittest.main() 