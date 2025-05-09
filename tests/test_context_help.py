"""
Testes para o módulo de ajuda contextual.
"""

import pytest
from unittest.mock import MagicMock, patch

from aider_start.context_help import ContextHelp
from aider_start.param_db import ParameterDatabase


class TestContextHelp:
    """Testes para a classe ContextHelp."""
    
    @pytest.fixture
    def param_db(self):
        """Fixture para criar uma instância do ParameterDatabase."""
        return ParameterDatabase()
    
    @pytest.fixture
    def context_help(self, param_db):
        """Fixture para criar uma instância do ContextHelp."""
        return ContextHelp(param_db)
    
    def test_initialization(self, context_help, param_db):
        """Testa a inicialização correta da classe ContextHelp."""
        assert context_help.param_db == param_db
        assert isinstance(context_help.parameter_dependencies, dict)
    
    def test_get_parameter_help(self, context_help):
        """Testa a obtenção de texto de ajuda para um parâmetro."""
        # Testar com um parâmetro que existe
        help_text = context_help.get_parameter_help('model', 'model_options')
        assert "PARÂMETRO: model" in help_text
        assert "Categoria: model_options" in help_text
        assert "Modelo a ser usado" in help_text
        
        # Testar com um parâmetro que não existe
        help_text = context_help.get_parameter_help('parâmetro_inexistente')
        assert "Parâmetro não encontrado" in help_text
    
    def test_get_parameter_help_without_category(self, context_help):
        """Testa a obtenção de texto de ajuda sem especificar categoria."""
        help_text = context_help.get_parameter_help('model')
        assert "PARÂMETRO: model" in help_text
        assert "Categoria: model_options" in help_text
    
    def test_get_parameter_help_without_param_db(self):
        """Testa a obtenção de texto de ajuda sem param_db inicializado."""
        context_help = ContextHelp(None)
        help_text = context_help.get_parameter_help('model')
        assert "Informação detalhada não disponível" in help_text
    
    def test_should_show_parameter(self, context_help):
        """Testa a lógica de exibição progressiva de parâmetros."""
        # Parâmetro que deve ser mostrado quando architect=True
        profile = {'architect': True}
        assert context_help.should_show_parameter('auto-accept-architect', profile)
        
        # Parâmetro que deve ser escondido quando architect=True
        assert not context_help.should_show_parameter('edit-format', profile)
        
        # Parâmetro que deve ser mostrado quando architect=False
        profile = {'architect': False}
        assert context_help.should_show_parameter('edit-format', profile)
    
    def test_should_show_parameter_with_lambda(self, context_help):
        """Testa a lógica de exibição com condições lambda."""
        # Teste para o parâmetro editor-edit-format com editor-model definido
        profile = {'editor-model': 'gpt-4'}
        assert context_help.should_show_parameter('editor-edit-format', profile)
        
        # Teste para o parâmetro editor-edit-format com editor-model não definido
        profile = {'editor-model': None}
        assert not context_help.should_show_parameter('editor-edit-format', profile)
        
        # Teste para o parâmetro editor-edit-format com editor-model como string vazia
        profile = {'editor-model': ''}
        assert not context_help.should_show_parameter('editor-edit-format', profile)
    
    def test_get_required_parameters(self, context_help):
        """Testa a identificação de parâmetros obrigatórios."""
        mock_param_db = MagicMock()
        mock_param_db.get_category.return_value = {
            'param1': {'type': 'string'},  # Sem default, deveria ser obrigatório
            'param2': {'type': 'string', 'default': 'valor'},  # Com default, não é obrigatório
            'param3': {'type': 'string', 'secret': True},  # Secreto, não é obrigatório mesmo sem default
        }
        context_help.param_db = mock_param_db
        
        required = context_help.get_required_parameters('test_category')
        assert 'param1' in required
        assert 'param2' not in required
        assert 'param3' not in required
    
    def test_get_parameter_examples(self, context_help):
        """Testa a obtenção de exemplos para parâmetros."""
        # Teste para modelo
        examples = context_help.get_parameter_examples('model', 'model_options')
        assert "gpt-4o" in examples
        assert "claude-3-sonnet" in examples
        
        # Teste para booleano
        examples = context_help.get_parameter_examples('architect', 'model_options')
        assert "True" in examples
        assert "False" in examples
        
        # Teste para timeout (inteiro)
        examples = context_help.get_parameter_examples('timeout', 'model_options')
        assert "30" in examples
        assert "60" in examples
        
        # Teste para parâmetro inexistente
        examples = context_help.get_parameter_examples('inexistente')
        assert len(examples) == 0
        
    def test_find_parameter_category(self, context_help):
        """Testa a identificação da categoria de um parâmetro."""
        category = context_help._find_parameter_category('model')
        assert category == 'model_options'
        
        category = context_help._find_parameter_category('git')
        assert category == 'git_options'
        
        category = context_help._find_parameter_category('parâmetro_inexistente')
        assert category is None
    
    def test_get_related_parameters(self, context_help):
        """Testa a identificação de parâmetros relacionados."""
        # architect afeta edit-format e auto-accept-architect
        related = context_help._get_related_parameters('architect')
        assert 'edit-format' in related
        assert 'auto-accept-architect' in related
        
        # edit-format é afetado por architect
        related = context_help._get_related_parameters('edit-format')
        assert 'architect' in related 