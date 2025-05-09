"""
Testes para o módulo profile_builder.py
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Adiciona o diretório raiz ao path para importação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aider_start.profile_builder import ProfileBuilder
from aider_start.param_db import ParameterDatabase
from aider_start.config_manager import ConfigManager


class TestProfileBuilder(unittest.TestCase):
    """Testes para a classe ProfileBuilder."""
    
    def setUp(self):
        """Configuração dos testes."""
        # Mock do ConfigManager
        self.config_mock = MagicMock(spec=ConfigManager)
        self.config_mock.add_profile = MagicMock(return_value=True)
        
        # Mock do ParameterDatabase
        self.param_db_mock = MagicMock(spec=ParameterDatabase)
        self.param_db_mock.get_categories.return_value = ['model_options', 'api_options', 'execution_options', 'prompt_options', 'general']
        
        # Configurar side_effect para get_category para retornar dados mais específicos
        def get_category_side_effect(category_name):
            if category_name == 'model_options':
                return {
                    'model': {'description': 'Modelo a ser usado', 'type': 'string', 'default': 'gpt-4'},
                    'timeout': {'description': 'Timeout em segundos', 'type': 'integer', 'default': 60}
                }
            elif category_name == 'execution_options':
                return {
                    'fnames': {'description': 'Arquivos a serem processados', 'type': 'array', 'items': {'type': 'string'}}
                }
            # Adicione mais categorias conforme necessário para outros testes
            return {}
        self.param_db_mock.get_category.side_effect = get_category_side_effect
        
        # Configurar side_effect para get_parameter
        def get_parameter_side_effect(category, param_name):
            if category == 'model_options' and param_name == 'model':
                return {'description': 'Modelo a ser usado', 'type': 'string', 'default': 'gpt-4'}
            elif category == 'execution_options' and param_name == 'fnames':
                return {'description': 'Arquivos para processar', 'type': 'array', 'items': {'type': 'string'}}
            elif category == 'prompt_options' and param_name == 'main_prompt_template':
                # Simular um parâmetro que pode ser string ou null, ou apenas string
                return {'description': 'Template de prompt principal', 'type': ['string', 'null']} # ou apenas 'string'
            elif category == 'general' and param_name == 'provider':
                return {'description': 'Provedor de API', 'type': 'string'}
            elif category == 'api_options' and param_name == 'api-key':
                 return {'description': 'Chave API', 'type': 'string', 'secret': True}
            # Adicione mais casos conforme necessário
            return None # Retorna None para parâmetros não encontrados
        self.param_db_mock.get_parameter.side_effect = get_parameter_side_effect
        
        self.param_db_mock.format_parameter_type.return_value = 'string' # Pode precisar de side_effect também se tipos formatados variados são testados
        
        # Inicializa o ProfileBuilder com os mocks
        self.builder = ProfileBuilder(
            config_manager=self.config_mock,
            param_db=self.param_db_mock
        )
        
    def test_init(self):
        """Testa a inicialização do ProfileBuilder."""
        self.assertEqual(self.builder.config_manager, self.config_mock)
        self.assertEqual(self.builder.param_db, self.param_db_mock)
        self.assertEqual(self.builder.current_profile, {})
        
        # Testa inicialização sem passar param_db
        with patch('aider_start.profile_builder.ParameterDatabase') as param_db_class_mock:
            builder = ProfileBuilder(config_manager=self.config_mock)
            param_db_class_mock.assert_called_once()
            
    def test_start_new_profile(self):
        """Testa o método start_new_profile."""
        # Define alguns valores no perfil atual
        self.builder.current_profile = {'model': 'gpt-4', 'timeout': 60}
        
        # Chama o método
        self.builder.start_new_profile()
        
        # Verifica se o perfil foi limpo
        self.assertEqual(self.builder.current_profile, {})
    
    def test_get_categories(self):
        """Testa o método get_categories."""
        categories = self.builder.get_categories()
        self.param_db_mock.get_categories.assert_called_once()
        self.assertEqual(categories, ['model_options', 'api_options', 'execution_options', 'prompt_options', 'general'])
    
    def test_get_category_parameters(self):
        """Testa o método get_category_parameters."""
        params = self.builder.get_category_parameters('model_options')
        self.param_db_mock.get_category.assert_called_once_with('model_options')
        self.assertEqual(len(params), 2)
        self.assertIn('model', params)
        self.assertIn('timeout', params)
    
    def test_set_parameter(self):
        """Testa o método set_parameter."""
        # Verifica que o perfil está vazio inicialmente
        self.assertEqual(self.builder.current_profile, {})
        
        # Define um parâmetro
        self.builder.set_parameter('model', 'gpt-4')
        
        # Verifica se o parâmetro foi definido
        self.assertEqual(self.builder.current_profile, {'model': 'gpt-4'})
        
        # Define mais um parâmetro
        self.builder.set_parameter('timeout', 120)
        
        # Verifica se ambos os parâmetros estão definidos
        self.assertEqual(self.builder.current_profile, {'model': 'gpt-4', 'timeout': 120})
    
    def test_get_parameter_value(self):
        """Testa o método get_parameter_value."""
        # Perfil vazio
        self.assertEqual(self.builder.get_parameter_value('model'), None)
        
        # Define um parâmetro
        self.builder.current_profile = {'model': 'gpt-4'}
        
        # Verifica se o valor pode ser recuperado
        self.assertEqual(self.builder.get_parameter_value('model'), 'gpt-4')
        
        # Parâmetro inexistente
        self.assertEqual(self.builder.get_parameter_value('inexistente'), None)
    
    def test_get_current_profile(self):
        """Testa o método get_current_profile."""
        # Perfil vazio
        self.assertEqual(self.builder.get_current_profile(), {})
        
        # Define alguns valores
        self.builder.current_profile = {'name': 'Teste', 'model': 'gpt-4'}
        
        # Verifica se os valores são retornados corretamente
        self.assertEqual(self.builder.get_current_profile(), {'name': 'Teste', 'model': 'gpt-4'})
        
        # Verifica se o retorno é uma cópia (não uma referência)
        profile = self.builder.get_current_profile()
        profile['new_key'] = 'new_value'
        self.assertNotIn('new_key', self.builder.current_profile)
    
    def test_get_parameter_help(self):
        """Testa o método get_parameter_help."""
        # Parâmetro existente
        help_text = self.builder.get_parameter_help('model_options', 'model')
        self.param_db_mock.get_parameter.assert_called_with('model_options', 'model')
        self.assertEqual(help_text, 'Modelo a ser usado')
        
        # Parâmetro inexistente
        self.param_db_mock.get_parameter.return_value = None
        help_text = self.builder.get_parameter_help('model_options', 'inexistente')
        self.assertEqual(help_text, '')
    
    def test_get_parameter_default(self):
        """Testa o método get_parameter_default."""
        # Parâmetro com valor padrão
        default = self.builder.get_parameter_default('model_options', 'model')
        self.param_db_mock.get_parameter.assert_called_with('model_options', 'model')
        self.assertEqual(default, 'gpt-4')
        
        # Parâmetro sem valor padrão
        self.param_db_mock.get_parameter.return_value = {'description': 'Descrição', 'type': 'string'}
        default = self.builder.get_parameter_default('model_options', 'outro')
        self.assertIsNone(default)
        
        # Parâmetro inexistente
        self.param_db_mock.get_parameter.return_value = None
        default = self.builder.get_parameter_default('model_options', 'inexistente')
        self.assertIsNone(default)
    
    def test_get_parameter_type(self):
        """Testa o método get_parameter_type."""
        # Parâmetro existente
        param_type = self.builder.get_parameter_type('model_options', 'model')
        self.param_db_mock.get_parameter.assert_called_with('model_options', 'model')
        self.param_db_mock.format_parameter_type.assert_called_once()
        self.assertEqual(param_type, 'string')
        
        # Parâmetro inexistente
        self.param_db_mock.get_parameter.return_value = None
        param_type = self.builder.get_parameter_type('model_options', 'inexistente')
        self.assertEqual(param_type, 'desconhecido')
    
    def test_is_parameter_secret(self):
        """Testa o método is_parameter_secret."""
        # Parâmetro não secreto
        self.param_db_mock.get_parameter.return_value = {'description': 'Descrição', 'type': 'string'}
        is_secret = self.builder.is_parameter_secret('model_options', 'model')
        self.param_db_mock.get_parameter.assert_called_with('model_options', 'model')
        self.assertFalse(is_secret)
        
        # Parâmetro secreto
        self.param_db_mock.get_parameter.return_value = {'description': 'Descrição', 'type': 'string', 'secret': True}
        is_secret = self.builder.is_parameter_secret('api_options', 'api-key')
        self.assertTrue(is_secret)
        
        # Parâmetro inexistente
        self.param_db_mock.get_parameter.return_value = None
        is_secret = self.builder.is_parameter_secret('model_options', 'inexistente')
        self.assertFalse(is_secret)
    
    def test_reset_profile(self):
        """Testa o método reset_profile."""
        # Define alguns valores no perfil atual
        self.builder.current_profile = {'model': 'gpt-4', 'timeout': 60}
        
        # Chama o método
        self.builder.reset_profile()
        
        # Verifica se o perfil foi limpo
        self.assertEqual(self.builder.current_profile, {})
    
    def test_create_profile(self):
        """Testa o método create_profile."""
        # Cria um perfil sem nome
        profile = self.builder.create_profile()
        self.assertEqual(profile, {})
        
        # Cria um perfil com nome
        profile = self.builder.create_profile(name='Meu Perfil')
        self.assertEqual(profile, {'name': 'Meu Perfil'})
    
    def test_edit_profile(self):
        """Testa o método edit_profile."""
        # Define um perfil de exemplo
        example_profile = {'name': 'Perfil Existente', 'model': 'gpt-4', 'timeout': 60}
        
        # Edita o perfil
        result = self.builder.edit_profile(example_profile)
        
        # Verifica se o perfil atual foi atualizado
        self.assertEqual(self.builder.current_profile, example_profile)
        
        # Verifica se o retorno é correto
        self.assertEqual(result, example_profile)
        
        # Verifica se é uma cópia (não uma referência)
        example_profile['modified'] = True
        self.assertNotIn('modified', self.builder.current_profile)
    
    def test_validate_profile_empty(self):
        """Testa o método validate_profile com perfil vazio."""
        # Perfil vazio
        valid, message = self.builder.validate_profile({})
        self.assertFalse(valid)
        self.assertEqual(message, "O perfil está vazio.")
    
    def test_validate_profile_no_name(self):
        """Testa o método validate_profile com perfil sem nome."""
        # Perfil sem nome
        valid, message = self.builder.validate_profile({'model': 'gpt-4'})
        self.assertFalse(valid)
        self.assertEqual(message, "O perfil precisa ter um nome.")
    
    def test_validate_profile_valid(self):
        """Testa o método validate_profile com perfil válido."""
        # Perfil válido
        valid, message = self.builder.validate_profile({'name': 'Meu Perfil', 'model': 'gpt-4'})
        self.assertTrue(valid)
        self.assertEqual(message, "Perfil válido.")
        
        # Teste passando o perfil atual
        self.builder.current_profile = {'name': 'Perfil Atual', 'timeout': 60}
        valid, message = self.builder.validate_profile()
        self.assertTrue(valid)
    
    def test_save_profile_no_config_manager(self):
        """Testa o método save_profile sem config_manager."""
        # Configura o builder sem config_manager
        self.builder.config_manager = None
        
        # Tenta salvar um perfil
        result = self.builder.save_profile()
        
        # Verifica que o resultado é None
        self.assertIsNone(result)
    
    def test_save_profile_invalid(self):
        """Testa o método save_profile com perfil inválido."""
        # Perfil sem nome
        self.builder.current_profile = {'model': 'gpt-4'}
        
        # Tenta salvar um perfil inválido
        with self.assertRaises(ValueError) as context:
            self.builder.save_profile()
        
        self.assertIn("O perfil precisa ter um nome", str(context.exception))
    
    def test_save_profile_success(self):
        """Testa o método save_profile com sucesso."""
        # Configura um perfil válido
        self.builder.current_profile = {'name': 'Meu Perfil', 'model': 'gpt-4'}
        
        # Salva o perfil
        result = self.builder.save_profile()
        
        # Verifica que o método add_profile do config_manager foi chamado
        # com o dicionário de dados do perfil SEM a chave 'name'
        expected_profile_data = {'model': 'gpt-4'}
        self.config_mock.add_profile.assert_called_once_with('Meu Perfil', expected_profile_data)
        
        # Verifica que o resultado é uma cópia do perfil (que ainda inclui 'name')
        self.assertEqual(result, self.builder.current_profile)
        self.assertIsNot(result, self.builder.current_profile)
    
    def test_save_profile_with_name(self):
        """Testa o método save_profile passando um nome."""
        # Configura um perfil
        self.builder.current_profile = {'model': 'gpt-4'}
        
        # Salva o perfil com um nome
        result = self.builder.save_profile(name='Novo Perfil')
        
        # Verifica que o nome foi adicionado ao perfil
        self.assertEqual(self.builder.current_profile['name'], 'Novo Perfil')
        
        # Verifica que o método add_profile do config_manager foi chamado
        # com o dicionário de dados do perfil SEM a chave 'name'
        expected_profile_data_with_name = {'model': 'gpt-4'}
        self.config_mock.add_profile.assert_called_once_with('Novo Perfil', expected_profile_data_with_name)

    def test_get_parameter_raw_type(self):
        """Testa a obtenção do tipo raw de um parâmetro."""
        # Assume que param_db.json tem estas entradas e tipos
        # Categoria: model_options, Parâmetro: model, Tipo: string
        raw_type_model = self.builder.get_parameter_raw_type('model_options', 'model')
        self.assertEqual(raw_type_model, 'string')

        # Categoria: execution_options, Parâmetro: fnames, Tipo: array
        raw_type_fnames = self.builder.get_parameter_raw_type('execution_options', 'fnames')
        self.assertEqual(raw_type_fnames, 'array')

        # Parâmetro que pode ser string ou null (Exemplo: prompt_options.main_prompt_template)
        # Ajuste esta parte se o param_db.json tiver um exemplo melhor ou diferente
        # Supondo que 'main_prompt_template' em 'prompt_options' pode ser ["string", "null"]
        raw_type_nullable = self.builder.get_parameter_raw_type('prompt_options', 'main_prompt_template')
        # O tipo exato depende do param_db.json. Se for apenas "string", o teste falhará.
        # Se for ["string", "null"], o teste abaixo é apropriado.
        # Se param_db.json tiver 'main_prompt_template' como apenas 'string', use self.assertEqual(raw_type_nullable, 'string')
        self.assertIn(raw_type_nullable, ['string', ["string", "null"]]) # Flexível para string ou string/null
        
        # Categoria: general, Parâmetro: provider, Tipo: string
        raw_type_provider = self.builder.get_parameter_raw_type('general', 'provider')
        self.assertEqual(raw_type_provider, 'string')

        # Parâmetro inexistente
        raw_type_non_existent = self.builder.get_parameter_raw_type('model_options', 'parametro_fantasma')
        self.assertIsNone(raw_type_non_existent)

        # Categoria inexistente
        raw_type_bad_category = self.builder.get_parameter_raw_type('categoria_fantasma', 'model')
        self.assertIsNone(raw_type_bad_category)


if __name__ == '__main__':
    unittest.main() 