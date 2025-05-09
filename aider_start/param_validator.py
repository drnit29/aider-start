"""
Módulo para validação de parâmetros da interface TUI.
"""

from typing import Dict, Any, Tuple, Optional, List, Callable, Union
import re
from urllib.parse import urlparse


class ParamValidator:
    """Classe para validação de parâmetros da interface TUI."""
    
    def __init__(self, param_db=None):
        """
        Inicializa o validador de parâmetros.
        
        Args:
            param_db: Instância do ParameterDatabase para acessar informações de parâmetros.
        """
        self.param_db = param_db
        self.validation_rules = self._initialize_validation_rules()
        self.cross_validation_rules = self._initialize_cross_validation_rules()
        
    def _initialize_validation_rules(self) -> Dict[str, Callable]:
        """
        Inicializa regras de validação para tipos específicos de parâmetros.
        
        Returns:
            Dicionário mapeando tipos de parâmetros para funções de validação.
        """
        return {
            'string': self._validate_string,
            'integer': self._validate_integer,
            'float': self._validate_float,
            'boolean': self._validate_boolean,
            'url': self._validate_url,
            'api_key': self._validate_api_key,
            'email': self._validate_email,
            'file_path': self._validate_file_path,
            'directory_path': self._validate_directory_path,
            'model': self._validate_model,
        }
    
    def _initialize_cross_validation_rules(self) -> Dict[str, Dict[str, Callable]]:
        """
        Inicializa regras de validação cruzada entre parâmetros relacionados.
        
        Returns:
            Dicionário mapeando parâmetros para funções de validação cruzada.
        """
        return {
            'model': {
                'provider': self._cross_validate_model_provider,
            },
            'provider': {
                'model': self._cross_validate_provider_model,
            },
            'temperatura': {
                'model': self._cross_validate_temperature_model,
            },
            'endpoint': {
                'api_key': self._cross_validate_endpoint_api_key,
            }
        }
    
    def validate_parameter(self, param_name: str, value: Any, 
                          category: Optional[str] = None, 
                          profile_data: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Valida um valor de parâmetro conforme seu tipo e regras específicas.
        
        Args:
            param_name: Nome do parâmetro.
            value: Valor a ser validado.
            category: Categoria do parâmetro (opcional, para localizar o parâmetro no param_db).
            profile_data: Dados do perfil completo para validação cruzada.
            
        Returns:
            Tupla (bool, str) indicando se o valor é válido e mensagem de erro/sucesso.
        """
        if not self.param_db:
            return True, "Validação não disponível sem banco de parâmetros."
            
        # Se o valor for None ou string vazia, verificar se é obrigatório
        if value is None or (isinstance(value, str) and not value.strip()):
            param_data = self._get_param_data(param_name, category)
            if param_data and 'default' not in param_data:
                return False, "Este campo é obrigatório."
            return True, "Campo opcional."
        
        # Obter tipo do parâmetro
        param_type = self._get_param_type(param_name, category)
        
        # Validar conforme o tipo
        if param_type in self.validation_rules:
            valid, message = self.validation_rules[param_type](value, param_name, category)
            if not valid:
                return False, message
        
        # Validação cruzada com outros parâmetros (se profile_data fornecido)
        if profile_data and param_name in self.cross_validation_rules:
            for related_param, validation_func in self.cross_validation_rules[param_name].items():
                if related_param in profile_data:
                    related_value = profile_data[related_param]
                    valid, message = validation_func(value, related_value)
                    if not valid:
                        return False, message
        
        return True, "Valor válido."
    
    def _get_param_data(self, param_name: str, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Obtém os dados de um parâmetro.
        
        Args:
            param_name: Nome do parâmetro.
            category: Categoria do parâmetro (opcional).
            
        Returns:
            Dados do parâmetro ou None se não encontrado.
        """
        if not self.param_db:
            return None
            
        if category:
            return self.param_db.get_parameter(category, param_name)
        
        # Procurar em todas as categorias se a categoria não for especificada
        for cat in self.param_db.get_categories():
            param_data = self.param_db.get_parameter(cat, param_name)
            if param_data:
                return param_data
        
        return None
    
    def _get_param_type(self, param_name: str, category: Optional[str] = None) -> str:
        """
        Obtém o tipo de um parâmetro.
        
        Args:
            param_name: Nome do parâmetro.
            category: Categoria do parâmetro (opcional).
            
        Returns:
            Tipo do parâmetro (padrão: 'string').
        """
        param_data = self._get_param_data(param_name, category)
        if param_data:
            # Verificar se há um tipo de validação específico
            if 'validation_type' in param_data:
                return param_data['validation_type']
            
            # Caso contrário, usar o tipo básico
            return param_data.get('type', 'string')
        
        return 'string'  # tipo padrão
    
    # Métodos de validação para tipos específicos
    
    def _validate_string(self, value: Any, param_name: str, category: Optional[str] = None) -> Tuple[bool, str]:
        """Valida um valor de tipo string."""
        if not isinstance(value, str):
            return False, "O valor deve ser uma string."
        
        # Obter restrições específicas (se houver)
        param_data = self._get_param_data(param_name, category)
        if param_data:
            # Validar comprimento mínimo
            min_length = param_data.get('min_length')
            if min_length is not None and len(value) < min_length:
                return False, f"O valor deve ter pelo menos {min_length} caracteres."
            
            # Validar comprimento máximo
            max_length = param_data.get('max_length')
            if max_length is not None and len(value) > max_length:
                return False, f"O valor deve ter no máximo {max_length} caracteres."
            
            # Validar padrão regex (se definido)
            pattern = param_data.get('pattern')
            if pattern and not re.match(pattern, value):
                pattern_desc = param_data.get('pattern_description', 'o formato requerido')
                return False, f"O valor não corresponde a {pattern_desc}."
        
        return True, "Valor válido."
    
    def _validate_integer(self, value: Any, param_name: str, category: Optional[str] = None) -> Tuple[bool, str]:
        """Valida um valor de tipo inteiro."""
        # Tentar converter para inteiro
        try:
            if isinstance(value, str):
                value = int(value)
            elif not isinstance(value, int):
                return False, "O valor deve ser um número inteiro."
        except ValueError:
            return False, "O valor deve ser um número inteiro válido."
        
        # Obter restrições específicas (se houver)
        param_data = self._get_param_data(param_name, category)
        if param_data:
            # Validar valor mínimo
            min_value = param_data.get('min_value')
            if min_value is not None and value < min_value:
                return False, f"O valor deve ser no mínimo {min_value}."
            
            # Validar valor máximo
            max_value = param_data.get('max_value')
            if max_value is not None and value > max_value:
                return False, f"O valor deve ser no máximo {max_value}."
        
        return True, "Valor válido."
    
    def _validate_float(self, value: Any, param_name: str, category: Optional[str] = None) -> Tuple[bool, str]:
        """Valida um valor de tipo ponto flutuante."""
        # Tentar converter para float
        try:
            if isinstance(value, str):
                value = float(value)
            elif not isinstance(value, (int, float)):
                return False, "O valor deve ser um número decimal."
        except ValueError:
            return False, "O valor deve ser um número decimal válido."
        
        # Obter restrições específicas (se houver)
        param_data = self._get_param_data(param_name, category)
        if param_data:
            # Validar valor mínimo
            min_value = param_data.get('min_value')
            if min_value is not None and value < min_value:
                return False, f"O valor deve ser no mínimo {min_value}."
            
            # Validar valor máximo
            max_value = param_data.get('max_value')
            if max_value is not None and value > max_value:
                return False, f"O valor deve ser no máximo {max_value}."
        
        return True, "Valor válido."
    
    def _validate_boolean(self, value: Any, param_name: str, category: Optional[str] = None) -> Tuple[bool, str]:
        """Valida um valor de tipo booleano."""
        if not isinstance(value, bool):
            # Se for string, tentar converter
            if isinstance(value, str):
                value_lower = value.lower()
                if value_lower in ('true', 'yes', 'sim', '1', 'verdadeiro'):
                    return True, "Valor válido (verdadeiro)."
                elif value_lower in ('false', 'no', 'não', '0', 'falso'):
                    return True, "Valor válido (falso)."
            
            return False, "O valor deve ser verdadeiro ou falso."
        
        return True, "Valor válido."
    
    def _validate_url(self, value: Any, param_name: str, category: Optional[str] = None) -> Tuple[bool, str]:
        """Valida uma URL."""
        if not isinstance(value, str):
            return False, "A URL deve ser uma string."
        
        try:
            result = urlparse(value)
            if all([result.scheme, result.netloc]):
                return True, "URL válida."
            return False, "A URL deve ter um formato válido (ex: https://exemplo.com)."
        except Exception:
            return False, "URL inválida."
    
    def _validate_api_key(self, value: Any, param_name: str, category: Optional[str] = None) -> Tuple[bool, str]:
        """Valida uma chave de API."""
        if not isinstance(value, str):
            return False, "A chave de API deve ser uma string."
        
        # Verificar formato comum de chaves de API
        if 'openai' in param_name.lower() and not value.startswith(('sk-')):
            return False, "A chave da OpenAI deve começar com 'sk-'."
        
        if 'anthropic' in param_name.lower() and not value.startswith(('sk-ant-', 'sk-')):
            return False, "A chave da Anthropic deve começar com 'sk-ant-' ou 'sk-'."
        
        # Verificar comprimento mínimo para qualquer chave de API
        if len(value) < 8:
            return False, "A chave de API parece muito curta."
        
        return True, "Chave de API com formato válido."
    
    def _validate_email(self, value: Any, param_name: str, category: Optional[str] = None) -> Tuple[bool, str]:
        """Valida um endereço de e-mail."""
        if not isinstance(value, str):
            return False, "O e-mail deve ser uma string."
        
        # Regex básico para e-mail
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_pattern, value):
            return False, "O formato do e-mail é inválido."
        
        return True, "E-mail válido."
    
    def _validate_file_path(self, value: Any, param_name: str, category: Optional[str] = None) -> Tuple[bool, str]:
        """Valida um caminho de arquivo."""
        if not isinstance(value, str):
            return False, "O caminho do arquivo deve ser uma string."
        
        # Verificar caracteres inválidos em caminhos de arquivo
        invalid_chars = re.search(r'[<>"|?*]', value)
        if invalid_chars:
            return False, f"O caminho contém caracteres inválidos: {invalid_chars.group()}"
        
        return True, "Caminho de arquivo válido."
    
    def _validate_directory_path(self, value: Any, param_name: str, category: Optional[str] = None) -> Tuple[bool, str]:
        """Valida um caminho de diretório."""
        if not isinstance(value, str):
            return False, "O caminho do diretório deve ser uma string."
        
        # Verificar caracteres inválidos em caminhos de diretório
        invalid_chars = re.search(r'[<>"|?*]', value)
        if invalid_chars:
            return False, f"O caminho contém caracteres inválidos: {invalid_chars.group()}"
        
        return True, "Caminho de diretório válido."
    
    def _validate_model(self, value: Any, param_name: str, category: Optional[str] = None) -> Tuple[bool, str]:
        """Valida um nome de modelo de IA."""
        if not isinstance(value, str):
            return False, "O nome do modelo deve ser uma string."
        
        # Lista de prefixos de modelos conhecidos
        known_prefixes = ['gpt-', 'text-', 'claude-', 'llama-', 'mistral-', 'gemini-']
        
        # Verificar se o modelo tem um prefixo conhecido
        if not any(value.startswith(prefix) for prefix in known_prefixes):
            return False, "O modelo não parece ter um formato conhecido."
        
        return True, "Nome de modelo válido."
    
    # Métodos de validação cruzada entre parâmetros
    
    def _cross_validate_model_provider(self, model: str, provider: str) -> Tuple[bool, str]:
        """Valida se o modelo é compatível com o provedor."""
        if not model or not provider:
            return True, "Sem dados suficientes para validação cruzada."
        
        # Verificar se model é uma string antes de usar startswith
        if not isinstance(model, str):
            return False, f"O modelo deve ser uma string, mas é {type(model).__name__}."
            
        provider = provider.lower()
        
        # Verificar compatibilidade do modelo com o provedor
        if provider == 'openai' and not any(model.startswith(prefix) for prefix in ['gpt-', 'text-']):
            return False, f"O modelo '{model}' não parece ser compatível com OpenAI."
        
        if provider == 'anthropic' and not model.startswith('claude-'):
            return False, f"O modelo '{model}' não parece ser compatível com Anthropic."
        
        if provider == 'mistral' and not model.startswith('mistral-'):
            return False, f"O modelo '{model}' não parece ser compatível com Mistral."
        
        return True, "Modelo compatível com o provedor."
    
    def _cross_validate_provider_model(self, provider: str, model: str) -> Tuple[bool, str]:
        """Validação inversa de provider → model."""
        return self._cross_validate_model_provider(model, provider)
    
    def _cross_validate_temperature_model(self, temperature: float, model: str) -> Tuple[bool, str]:
        """Valida a temperatura conforme o modelo."""
        if not temperature or not model:
            return True, "Sem dados suficientes para validação cruzada."
        
        try:
            temp_value = float(temperature)
        except (ValueError, TypeError):
            return False, "Valor de temperatura inválido."
        
        # Verificar se model é uma string antes de usar startswith
        if not isinstance(model, str):
            return False, f"O modelo deve ser uma string, mas é {type(model).__name__}."
            
        # Limite específico para modelos da OpenAI
        if model.startswith('gpt-') and temp_value > 2.0:
            return False, "A OpenAI limita a temperatura a um máximo de 2.0."
        
        # Limites gerais para temperatura
        if temp_value < 0.0:
            return False, "A temperatura não deve ser negativa."
        
        if temp_value > 2.0:
            return False, "O valor de temperatura está muito alto (máx. recomendado: 2.0)."
        
        return True, "Temperatura válida para o modelo."
    
    def _cross_validate_endpoint_api_key(self, endpoint: str, api_key: str) -> Tuple[bool, str]:
        """Valida se a chave de API é necessária para um endpoint específico."""
        if not endpoint:
            return True, "Sem dados suficientes para validação cruzada."
        
        if not api_key and endpoint != 'default':
            return False, "Endpoints personalizados geralmente requerem uma chave de API."
        
        return True, "Configuração de endpoint válida."
    
    def get_validation_errors(self, profile_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Obtém erros de validação para todos os parâmetros em um perfil.
        
        Args:
            profile_data: Dados do perfil para validar.
            
        Returns:
            Dicionário de erros de validação (param_name: mensagem).
        """
        validation_errors = {}
        
        for param_name, value in profile_data.items():
            is_valid, message = self.validate_parameter(param_name, value, profile_data=profile_data)
            if not is_valid:
                validation_errors[param_name] = message
        
        return validation_errors
    
    def get_parameter_format_hint(self, param_name: str, category: Optional[str] = None) -> str:
        """
        Obtém uma dica de formato para um parâmetro.
        
        Args:
            param_name: Nome do parâmetro.
            category: Categoria do parâmetro (opcional).
            
        Returns:
            String com dica de formato para o parâmetro.
        """
        param_type = self._get_param_type(param_name, category)
        
        # Obter dados do parâmetro
        param_data = self._get_param_data(param_name, category)
        
        if not param_data:
            return ""
        
        hints = []
        
        # Adicionar dicas baseadas no tipo
        if param_type == 'integer':
            if 'min_value' in param_data:
                hints.append(f"mín: {param_data['min_value']}")
            if 'max_value' in param_data:
                hints.append(f"máx: {param_data['max_value']}")
        
        elif param_type == 'float':
            if 'min_value' in param_data:
                hints.append(f"mín: {param_data['min_value']}")
            if 'max_value' in param_data:
                hints.append(f"máx: {param_data['max_value']}")
        
        elif param_type == 'string':
            if 'min_length' in param_data:
                hints.append(f"mín chars: {param_data['min_length']}")
            if 'max_length' in param_data:
                hints.append(f"máx chars: {param_data['max_length']}")
            if 'pattern_description' in param_data:
                hints.append(param_data['pattern_description'])
        
        elif param_type == 'url':
            hints.append("URL completa (ex: https://exemplo.com)")
        
        elif param_type == 'api_key':
            if 'openai' in param_name.lower():
                hints.append("Começa com 'sk-'")
            elif 'anthropic' in param_name.lower():
                hints.append("Começa com 'sk-ant-'")
        
        if hints:
            return f"({', '.join(hints)})"
        
        return "" 