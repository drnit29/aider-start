"""
Testes para o módulo de banco de dados de parâmetros.
"""

import pytest
from aider_start.param_db import ParameterDatabase


class TestParameterDatabase:
    """Testes para a classe ParameterDatabase."""

    def setup_method(self):
        """Configuração antes de cada teste."""
        self.param_db = ParameterDatabase()

    def test_initialization(self):
        """Testa a inicialização do banco de dados de parâmetros."""
        # Verificar se as categorias foram carregadas corretamente
        assert len(self.param_db.get_categories()) > 0
        
        # Verificar se cada categoria tem parâmetros
        for category in self.param_db.get_categories():
            assert len(self.param_db.get_category(category)) > 0

    def test_get_all_parameters(self):
        """Testa a obtenção de todos os parâmetros."""
        params = self.param_db.get_all_parameters()
        assert params is not None
        assert isinstance(params, dict)
        assert len(params) > 0

    def test_get_category(self):
        """Testa a obtenção de uma categoria específica."""
        # Obter uma categoria existente
        model_options = self.param_db.get_category('model_options')
        assert model_options is not None
        assert isinstance(model_options, dict)
        assert len(model_options) > 0
        
        # Verificar se o parâmetro 'model' existe na categoria 'model_options'
        assert 'model' in model_options
        
        # Tentar obter uma categoria inexistente
        nonexistent = self.param_db.get_category('nonexistent')
        assert nonexistent == {}

    def test_get_parameter(self):
        """Testa a obtenção de um parâmetro específico."""
        # Obter um parâmetro existente
        model_param = self.param_db.get_parameter('model_options', 'model')
        assert model_param is not None
        assert isinstance(model_param, dict)
        assert 'description' in model_param
        assert 'type' in model_param
        assert 'env_var' in model_param
        
        # Tentar obter um parâmetro inexistente
        nonexistent = self.param_db.get_parameter('model_options', 'nonexistent')
        assert nonexistent is None
        
        # Tentar obter um parâmetro de uma categoria inexistente
        nonexistent = self.param_db.get_parameter('nonexistent', 'model')
        assert nonexistent is None

    def test_get_categories(self):
        """Testa a obtenção de todas as categorias."""
        categories = self.param_db.get_categories()
        assert categories is not None
        assert isinstance(categories, list)
        assert len(categories) > 0
        
        # Verificar se as categorias esperadas estão presentes
        expected_categories = [
            'model_options', 'api_options', 'git_options', 'input_output',
            'history_options', 'repomap_options', 'fixing_options',
            'voice_options', 'mode_options', 'misc_options'
        ]
        for category in expected_categories:
            assert category in categories

    def test_format_parameter_type(self):
        """Testa a formatação do tipo de parâmetro."""
        # Testar diferentes tipos de parâmetros
        assert self.param_db.format_parameter_type({'type': 'string'}) == 'string'
        assert self.param_db.format_parameter_type({'type': 'boolean'}) == 'booleano'
        assert self.param_db.format_parameter_type({'type': 'integer'}) == 'inteiro'
        assert self.param_db.format_parameter_type({'type': 'float'}) == 'decimal'
        assert self.param_db.format_parameter_type({'type': 'array'}) == 'lista de items'
        assert self.param_db.format_parameter_type({'type': 'string', 'secret': True}) == 'senha'
        
        # Testar array com items definidos
        assert self.param_db.format_parameter_type({
            'type': 'array', 
            'items': {'type': 'string'}
        }) == 'lista de strings'
        
        # Testar tipo não especificado (deveria retornar 'desconhecido')
        assert self.param_db.format_parameter_type({}) == 'desconhecido'

    def test_get_parameters_by_filter(self):
        """Testa a obtenção de parâmetros por filtro."""
        # Obter todos os parâmetros booleanos
        boolean_params = self.param_db.get_parameters_by_filter(lambda data: data.get('type') == 'boolean')
        assert boolean_params is not None
        assert isinstance(boolean_params, dict)
        assert len(boolean_params) > 0
        
        # Verificar se todos os parâmetros retornados são booleanos
        for category, params in boolean_params.items():
            for param_name, param_data in params.items():
                assert param_data.get('type') == 'boolean'
        
        # Obter todos os parâmetros com valor padrão True
        true_params = self.param_db.get_parameters_by_filter(lambda data: data.get('default') is True)
        assert true_params is not None
        assert isinstance(true_params, dict)
        
        # Verificar se todos os parâmetros retornados têm valor padrão True
        for category, params in true_params.items():
            for param_name, param_data in params.items():
                assert param_data.get('default') is True

    def test_parameter_structure(self):
        """Testa a estrutura dos parâmetros."""
        # Verificar a estrutura de um parâmetro de cada tipo
        types = ['string', 'boolean', 'integer', 'float', 'array']
        found_types = set()
        
        for category, params in self.param_db.get_all_parameters().items():
            for param_name, param_data in params.items():
                param_type = param_data.get('type')
                if param_type in types and param_type not in found_types:
                    found_types.add(param_type)
                    
                    # Verificar estrutura comum
                    assert 'description' in param_data
                    assert isinstance(param_data['description'], str)
                    
                    # Verificar variável de ambiente
                    if 'env_var' in param_data:
                        assert param_data['env_var'] is None or isinstance(param_data['env_var'], str)
        
        # Verificar que encontramos pelo menos um parâmetro de cada tipo
        for param_type in types:
            assert param_type in found_types, f"Nenhum parâmetro do tipo {param_type} encontrado" 