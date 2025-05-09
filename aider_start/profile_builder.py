"""
Módulo para construção e gerenciamento de perfis do aider.
"""

from typing import Dict, List, Any, Tuple, Optional
from .param_db import ParameterDatabase


class ProfileBuilder:
    """Classe para construção interativa de perfis do aider."""
    
    def __init__(self, config_manager=None, param_db=None):
        """Inicializa o construtor de perfis."""
        self.config_manager = config_manager
        self.param_db = param_db if param_db else ParameterDatabase()
        self.current_profile = {}
        
    def create_profile(self, name: str = None) -> Dict[str, Any]:
        """
        Cria um novo perfil interativamente.
        
        Args:
            name: Nome opcional para o perfil.
            
        Returns:
            Dicionário com os dados do perfil criado.
        """
        self.start_new_profile()
        
        if name:
            self.current_profile['name'] = name
            
        return self.current_profile
        
    def edit_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edita um perfil existente.
        
        Args:
            profile_data: Dados do perfil a ser editado.
            
        Returns:
            Dicionário com os dados do perfil editado.
        """
        self.current_profile = profile_data.copy()
        return self.current_profile
        
    def validate_profile(self, profile_data: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Valida os dados de um perfil.
        
        Args:
            profile_data: Dados do perfil a serem validados. Se None, usa o perfil atual.
            
        Returns:
            Tupla (válido, mensagem) indicando se o perfil é válido e uma mensagem explicativa.
        """
        data = profile_data if profile_data is not None else self.current_profile
        
        # Verifica se o perfil está vazio
        if not data:
            return False, "O perfil está vazio."
        
        # Verifica se o perfil tem um nome
        if 'name' not in data or not data['name']:
            return False, "O perfil precisa ter um nome."
        
        # Verificações adicionais podem ser adicionadas conforme necessário
        
        return True, "Perfil válido."
    
    def start_new_profile(self) -> None:
        """Inicializa um novo perfil vazio."""
        self.current_profile = {}
    
    def get_categories(self) -> List[str]:
        """
        Obtém todas as categorias de parâmetros disponíveis.
        
        Returns:
            Lista de categorias disponíveis.
        """
        return self.param_db.get_categories()
    
    def get_category_parameters(self, category: str) -> Dict[str, Any]:
        """
        Obtém todos os parâmetros de uma categoria.
        
        Args:
            category: Nome da categoria.
            
        Returns:
            Dicionário com os parâmetros da categoria.
        """
        return self.param_db.get_category(category)
    
    def set_parameter(self, param_name: str, value: Any) -> None:
        """
        Define um valor para um parâmetro no perfil atual.
        
        Args:
            param_name: Nome do parâmetro.
            value: Valor a ser definido.
        """
        self.current_profile[param_name] = value
    
    def get_parameter_value(self, param_name: str) -> Any:
        """
        Obtém o valor atual de um parâmetro no perfil atual.
        
        Args:
            param_name: Nome do parâmetro.
            
        Returns:
            Valor do parâmetro ou None se não existir.
        """
        return self.current_profile.get(param_name)
    
    def get_current_profile(self) -> Dict[str, Any]:
        """
        Obtém o perfil atual em construção.
        
        Returns:
            Dicionário com os dados do perfil atual.
        """
        return self.current_profile.copy()
    
    def get_parameter_help(self, category: str, param_name: str) -> str:
        """
        Obtém o texto de ajuda para um parâmetro específico.
        
        Args:
            category: Categoria do parâmetro.
            param_name: Nome do parâmetro.
            
        Returns:
            Texto de ajuda para o parâmetro.
        """
        param = self.param_db.get_parameter(category, param_name)
        if param:
            return param.get('description', '')
        return ''
    
    def get_parameter_default(self, category: str, param_name: str) -> Any:
        """
        Obtém o valor padrão para um parâmetro específico.
        
        Args:
            category: Categoria do parâmetro.
            param_name: Nome do parâmetro.
            
        Returns:
            Valor padrão para o parâmetro ou None se não existir.
        """
        param = self.param_db.get_parameter(category, param_name)
        if param and 'default' in param:
            return param['default']
        return None
    
    def get_parameter_type(self, category: str, param_name: str) -> str:
        """
        Obtém o tipo formatado de um parâmetro específico.
        
        Args:
            category: Categoria do parâmetro.
            param_name: Nome do parâmetro.
            
        Returns:
            Tipo formatado do parâmetro.
        """
        param = self.param_db.get_parameter(category, param_name)
        if param:
            return self.param_db.format_parameter_type(param)
        return 'desconhecido'
    
    def is_parameter_secret(self, category: str, param_name: str) -> bool:
        """
        Verifica se um parâmetro é secreto (como uma senha ou chave API).
        
        Args:
            category: Categoria do parâmetro.
            param_name: Nome do parâmetro.
            
        Returns:
            True se o parâmetro for secreto, False caso contrário.
        """
        param = self.param_db.get_parameter(category, param_name)
        if param:
            return param.get('secret', False)
        return False
    
    def get_parameter_raw_type(self, category: str, param_name: str) -> Any:
        """
        Obtém o tipo 'raw' (do JSON schema) de um parâmetro específico.
        
        Args:
            category: Categoria do parâmetro.
            param_name: Nome do parâmetro.
            
        Returns:
            Tipo raw do parâmetro (ex: "string", "array", ["array", "null"]) ou None.
        """
        param = self.param_db.get_parameter(category, param_name)
        if param:
            return param.get('type')
        return None
    
    def reset_profile(self) -> None:
        """Reinicia o perfil atual, limpando todos os valores definidos."""
        self.current_profile = {}
        
    def save_profile(self, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Salva o perfil atual no gerenciador de configuração.
        
        Args:
            name: Nome opcional para o perfil. Se fornecido, substitui o nome atual.
            
        Returns:
            Dados do perfil salvo ou None se não houver configuração.
        """
        if not self.config_manager:
            return None
            
        if name:
            self.current_profile['name'] = name
            
        # Valida antes de salvar
        valid, message = self.validate_profile()
        if not valid:
            raise ValueError(f"Não foi possível salvar o perfil: {message}")
            
        profile_name = self.current_profile.get('name')
        if not profile_name:
            raise ValueError("O perfil precisa ter um nome para ser salvo.")
            
        # Criar uma cópia do perfil sem a chave 'name' para passar ao ConfigManager
        profile_data_to_save = {k: v for k, v in self.current_profile.items() if k != 'name'}
        
        self.config_manager.add_profile(profile_name, profile_data_to_save)
        return self.current_profile.copy()
        
# Código de teste quando executado diretamente
if __name__ == "__main__":
    from .config_manager import ConfigManager
    from .param_db import ParameterDatabase
    
    # Criar dependências
    cm = ConfigManager(use_test_data=True)
    param_db = ParameterDatabase()
    
    # Criar instância do ProfileBuilder
    builder = ProfileBuilder(config_manager=cm, param_db=param_db)
    
    # Mostrar categorias disponíveis
    print("Categorias disponíveis:")
    categories = builder.get_categories()
    print(categories)
    
    # Exemplo de criação de perfil
    print("\nCriando perfil de exemplo:")
    builder.start_new_profile()
    builder.set_parameter("name", "teste")
    builder.set_parameter("model", "gpt-4o")
    builder.set_parameter("temperatura", 0.5)
    
    # Verificar perfil
    print("Perfil criado:")
    print(builder.get_current_profile())
    
    # Validar perfil
    valid, message = builder.validate_profile()
    print(f"\nPerfil válido: {valid}")
    print(f"Mensagem: {message}")
    
    # Exemplo de parâmetros de uma categoria
    print("\nParâmetros da categoria 'model_options':")
    model_params = builder.get_category_parameters("model_options")
    for name, param in list(model_params.items())[:3]:  # Mostrar só os 3 primeiros
        print(f"- {name}: {builder.get_parameter_help('model_options', name)}")
        print(f"  Tipo: {builder.get_parameter_type('model_options', name)}")
        default = builder.get_parameter_default('model_options', name)
        if default is not None:
            print(f"  Valor padrão: {default}") 