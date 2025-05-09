"""
Módulo para fornecer ajuda contextual e disclosure progressivo para a TUI.
"""

from typing import Dict, List, Any, Optional


class ContextHelp:
    """Classe para gerenciar ajuda contextual e disclosure progressivo de parâmetros."""
    
    def __init__(self, param_db=None):
        """
        Inicializa o gerenciador de ajuda contextual.
        
        Args:
            param_db: Instância do ParameterDatabase para acessar informações de parâmetros.
        """
        self.param_db = param_db
        self.parameter_dependencies = self._initialize_dependencies()
        
    def _initialize_dependencies(self) -> Dict[str, List[str]]:
        """
        Inicializa o mapeamento de dependências entre parâmetros.
        Define quais parâmetros devem ser mostrados/escondidos com base nos valores de outros.
        
        Returns:
            Dicionário mapeando parâmetros para listas de parâmetros dependentes.
        """
        # Mapeamento de dependências: {param_nome: [(param_dependente, valor_condicional)]}
        # Se param_nome for definido como valor_condicional, param_dependente deve ser mostrado
        dependencies = {
            # Parâmetros relacionados ao architect
            'architect': [
                ('edit-format', False),            # Mostra apenas edit-format quando não estiver usando architect
                ('auto-accept-architect', True)    # Mostra auto-accept-architect apenas se architect estiver habilitado
            ],
            # Mostra editor-edit-format apenas se editor-model estiver definido
            'editor-model': [
                ('editor-edit-format', lambda x: x is not None and x != '')
            ],
            # Mostra weak-model apenas se max-chat-history-tokens estiver definido
            'max-chat-history-tokens': [
                ('weak-model', lambda x: x is not None and x > 0)
            ],
            # Mostra configurações específicas da API apenas quando o provedor correspondente for usado
            'model': [
                ('anthropic-api-key', lambda x: x and ('claude' in x.lower())),
                ('openai-api-key', lambda x: x and ('gpt' in x.lower() or 'openai' in x.lower()))
            ]
        }
        return dependencies
    
    def get_parameter_help(self, param_name: str, category: str = None) -> str:
        """
        Obtém texto de ajuda detalhado para um parâmetro específico.
        
        Args:
            param_name: Nome do parâmetro.
            category: Categoria do parâmetro (opcional, se já souber).
            
        Returns:
            Texto de ajuda formatado para o parâmetro.
        """
        if not self.param_db:
            return "Informação detalhada não disponível."
            
        # Localizar o parâmetro em todas as categorias, se categoria não for fornecida
        param_data = None
        if category:
            param_data = self.param_db.get_parameter(category, param_name)
        else:
            for cat in self.param_db.get_categories():
                param_data = self.param_db.get_parameter(cat, param_name)
                if param_data:
                    category = cat
                    break
        
        if not param_data:
            return "Parâmetro não encontrado."
            
        # Formatar informações do parâmetro
        help_text = []
        
        # Título e descrição
        help_text.append(f"PARÂMETRO: {param_name}")
        help_text.append(f"Categoria: {category}")
        help_text.append("")
        
        if 'description' in param_data:
            help_text.append(param_data['description'])
            help_text.append("")
            
        # Tipo e valores default
        param_type = self.param_db.format_parameter_type(param_data)
        help_text.append(f"Tipo: {param_type}")
        
        if 'default' in param_data:
            default_val = param_data['default']
            default_str = str(default_val) if default_val is not None else "não definido"
            help_text.append(f"Valor padrão: {default_str}")
            
        # Variável de ambiente associada
        if 'env_var' in param_data:
            help_text.append(f"Variável de ambiente: {param_data['env_var']}")
            
        # Informação sobre parâmetros relacionados
        related = self._get_related_parameters(param_name)
        if related:
            help_text.append("")
            help_text.append("Parâmetros relacionados:")
            for rel_param in related:
                rel_category = self._find_parameter_category(rel_param)
                if rel_category:
                    rel_data = self.param_db.get_parameter(rel_category, rel_param)
                    if rel_data and 'description' in rel_data:
                        desc = rel_data['description']
                        if len(desc) > 60:
                            desc = desc[:57] + "..."
                        help_text.append(f"- {rel_param}: {desc}")
            
        return "\n".join(help_text)
    
    def _get_related_parameters(self, param_name: str) -> List[str]:
        """
        Encontra parâmetros relacionados a um parâmetro específico.
        
        Args:
            param_name: Nome do parâmetro.
            
        Returns:
            Lista de parâmetros relacionados.
        """
        related = []
        
        # Parâmetros que este parâmetro afeta
        if param_name in self.parameter_dependencies:
            for dep_param, _ in self.parameter_dependencies[param_name]:
                if dep_param not in related:
                    related.append(dep_param)
        
        # Parâmetros que afetam este parâmetro
        for parent_param, deps in self.parameter_dependencies.items():
            for dep_param, _ in deps:
                if dep_param == param_name and parent_param not in related:
                    related.append(parent_param)
        
        return related
    
    def _find_parameter_category(self, param_name: str) -> Optional[str]:
        """
        Encontra a categoria de um parâmetro pelo nome.
        
        Args:
            param_name: Nome do parâmetro.
            
        Returns:
            Nome da categoria ou None se não encontrado.
        """
        if not self.param_db:
            return None
            
        for category in self.param_db.get_categories():
            category_params = self.param_db.get_category(category)
            if param_name in category_params:
                return category
        return None
        
    def should_show_parameter(self, param_name: str, profile_data: Dict[str, Any]) -> bool:
        """
        Determina se um parâmetro deve ser mostrado com base nos valores atuais do perfil.
        Implementa lógica de disclosure progressivo.
        
        Args:
            param_name: Nome do parâmetro.
            profile_data: Dados atuais do perfil.
            
        Returns:
            True se o parâmetro deve ser mostrado, False caso contrário.
        """
        # Parâmetros que são dependentes de outros
        for parent_param, deps in self.parameter_dependencies.items():
            for dep_param, condition in deps:
                if dep_param == param_name and parent_param in profile_data:
                    parent_value = profile_data[parent_param]
                    
                    # Verificar a condição
                    if callable(condition):
                        # Condição é uma função lambda
                        should_show = condition(parent_value)
                    else:
                        # Condição é um valor direto
                        should_show = (parent_value == condition)
                    
                    # Se a condição não for atendida, não mostrar o parâmetro
                    if not should_show:
                        return False
        
        # Por padrão, mostra o parâmetro
        return True
    
    def get_required_parameters(self, category: str) -> List[str]:
        """
        Retorna uma lista de parâmetros obrigatórios para uma categoria.
        
        Args:
            category: Nome da categoria.
            
        Returns:
            Lista de nomes de parâmetros obrigatórios.
        """
        if not self.param_db:
            return []
            
        required_params = []
        category_params = self.param_db.get_category(category)
        
        for param_name, param_data in category_params.items():
            # Considerar obrigatórios aqueles sem valor padrão e não secretos
            if 'default' not in param_data and not param_data.get('secret', False):
                required_params.append(param_name)
                
        return required_params
    
    def get_parameter_examples(self, param_name: str, category: str = None) -> List[str]:
        """
        Obtém exemplos de uso para um parâmetro específico.
        
        Args:
            param_name: Nome do parâmetro.
            category: Categoria do parâmetro (opcional).
            
        Returns:
            Lista de exemplos de uso.
        """
        if not self.param_db:
            return []
            
        param_data = None
        if category:
            param_data = self.param_db.get_parameter(category, param_name)
        else:
            for cat in self.param_db.get_categories():
                param_data = self.param_db.get_parameter(cat, param_name)
                if param_data:
                    break
        
        if not param_data:
            return []
            
        # Exemplos específicos para tipos de parâmetros
        param_type = param_data.get('type', 'string')
        
        if param_type == 'string':
            if 'model' in param_name:
                return ["gpt-4o", "claude-3-sonnet", "gpt-3.5-turbo"]
            elif 'api-key' in param_name:
                return ["sk-xxxxxxxxxxxxx"]
            elif 'file' in param_name:
                return [".aider.chat.history", "/caminho/para/arquivo.txt"]
        elif param_type == 'boolean':
            return ["True", "False"]
        elif param_type == 'integer':
            if 'tokens' in param_name:
                return ["1000", "2000", "4000"]
            elif 'timeout' in param_name:
                return ["30", "60", "120"]
        elif param_type == 'float':
            if 'temperatura' in param_name or 'temperature' in param_name:
                return ["0.7", "1.0", "0.5"]
        
        # Se não tivermos exemplos específicos, retornar lista vazia
        return [] 