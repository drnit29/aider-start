"""
Módulo com funções utilitárias para o aider-start.
"""

import os
import sys
import json
from pathlib import Path
import re
from urllib.parse import urlparse

from .logger import get_logger
from .exceptions import FileAccessError, JSONParseError

# Obter logger para este módulo
logger = get_logger("utils")


def get_version():
    """Retorna a versão atual do aider-start."""
    from . import __version__
    return __version__


def ensure_dir(directory):
    """Garante que um diretório existe, criando-o se necessário."""
    path = Path(directory)
    try:
        if not path.exists():
            logger.debug(f"Criando diretório: {path}")
            path.mkdir(parents=True, exist_ok=True)
        return path
    except PermissionError as e:
        logger.error(f"Erro de permissão ao criar diretório {path}: {e}")
        raise FileAccessError(f"Sem permissão para criar diretório {path}: {e}")
    except OSError as e:
        logger.error(f"Erro ao criar diretório {path}: {e}")
        raise FileAccessError(f"Erro ao criar diretório {path}: {e}")


def safe_json_read(file_path):
    """Lê um arquivo JSON com tratamento de erros."""
    try:
        logger.debug(f"Lendo arquivo JSON: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        error_msg = f"Erro ao decodificar JSON do arquivo {file_path}: {e}"
        logger.error(error_msg)
        return None, error_msg
    except FileNotFoundError as e:
        error_msg = f"Arquivo não encontrado: {file_path}"
        logger.debug(error_msg)  # Não é um erro crítico, apenas um aviso
        return None, error_msg
    except PermissionError as e:
        error_msg = f"Sem permissão para ler o arquivo {file_path}: {e}"
        logger.error(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Erro desconhecido ao ler arquivo {file_path}: {e}"
        logger.error(error_msg)
        return None, error_msg


def safe_json_write(file_path, data):
    """Escreve dados em um arquivo JSON com tratamento de erros."""
    try:
        logger.debug(f"Escrevendo no arquivo JSON: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True, None
    except PermissionError as e:
        error_msg = f"Sem permissão para escrever no arquivo {file_path}: {e}"
        logger.error(error_msg)
        return False, error_msg
    except OSError as e:
        error_msg = f"Erro de sistema ao escrever no arquivo {file_path}: {e}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Erro desconhecido ao escrever no arquivo {file_path}: {e}"
        logger.error(error_msg)
        return False, error_msg


def validate_dict_structure(data, required_keys=None, optional_keys=None):
    """Valida a estrutura de um dicionário.
    
    Args:
        data (dict): Dicionário a ser validado
        required_keys (list): Lista de chaves que devem estar presentes
        optional_keys (list): Lista de chaves opcionais
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Os dados devem ser um dicionário"
    
    if required_keys:
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            return False, f"Chaves obrigatórias ausentes: {', '.join(missing_keys)}"
    
    if required_keys or optional_keys:
        all_allowed_keys = set()
        if required_keys:
            all_allowed_keys.update(required_keys)
        if optional_keys:
            all_allowed_keys.update(optional_keys)
        
        unknown_keys = [key for key in data if key not in all_allowed_keys]
        if unknown_keys:
            return False, f"Chaves desconhecidas encontradas: {', '.join(unknown_keys)}"
    
    return True, None


def is_valid_url(url_string: str) -> bool:
    """Verifica se a string é uma URL bem formada."""
    if not url_string or not isinstance(url_string, str):
        return False
    try:
        result = urlparse(url_string)
        # Verifica se tem scheme (http, https) e netloc (domain)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except ValueError:
        return False


def is_valid_api_key(api_key_string: str, min_length: int = 10) -> bool:
    """Verifica se a chave API não está vazia, nula e tem um comprimento mínimo."""
    if not api_key_string or not isinstance(api_key_string, str):
        return False
    return len(api_key_string) >= min_length


def is_valid_name(name_string: str, max_length: int = 50, allowed_chars_pattern: str = r"^[a-zA-Z0-9_.-]+$") -> bool:
    """
    Valida nomes (para perfis, modelos, etc.).
    Verifica se não está vazio, tem comprimento máximo e segue um padrão de caracteres.
    O padrão default permite alfanuméricos, underscore, ponto e hífen.
    """
    if not name_string or not isinstance(name_string, str):
        return False
    if len(name_string) > max_length:
        return False
    if not re.match(allowed_chars_pattern, name_string):
        return False
    return True


def is_valid_file_path(path_string: str) -> bool:
    """Verifica se uma string é um caminho de arquivo sintaticamente válido (não verifica existência)."""
    if not path_string or not isinstance(path_string, str):
        return False
    # Verifica se o caminho não contém caracteres nulos, que são problemáticos
    if '\0' in path_string:
        return False
    # Verifica se o comprimento do caminho não é excessivo (varia por OS, mas 260 é um limite comum no Windows para o caminho completo)
    if len(path_string) > 1024: # Um limite genérico razoável para um componente de caminho ou nome de arquivo
        return False
    # Tenta criar um objeto Path para ver se é sintaticamente válido
    try:
        Path(path_string)
        return True
    except (TypeError, ValueError):
        # TypeError pode ocorrer se o tipo não for compatível com operações de caminho
        # ValueError pode ocorrer para caminhos inválidos em algumas plataformas/cenários
        return False


if __name__ == '__main__':
    # Testes rápidos para as funções de validação
    print(f"is_valid_url('http://example.com'): {is_valid_url('http://example.com')}") # True
    print(f"is_valid_url('ftp://example'): {is_valid_url('ftp://example')}") # True (ftp é um scheme)
    print(f"is_valid_url('example.com'): {is_valid_url('example.com')}") # False (sem scheme)
    print(f"is_valid_url(None): {is_valid_url(None)}") # False
    print(f"is_valid_url(''): {is_valid_url('')}") # False
    print(f"is_valid_url(123): {is_valid_url(123)}") # False

    print(f"is_valid_api_key('1234567890'): {is_valid_api_key('1234567890')}") # True
    print(f"is_valid_api_key('12345'): {is_valid_api_key('12345')}") # False
    print(f"is_valid_api_key(None): {is_valid_api_key(None)}") # False
    print(f"is_valid_api_key(''): {is_valid_api_key('')}") # False

    print(f"is_valid_name('valid-name_1.0'): {is_valid_name('valid-name_1.0')}") # True
    print(f"is_valid_name('invalid name with spaces'): {is_valid_name('invalid name with spaces')}") # False
    print(f"is_valid_name('toolong'*20): {is_valid_name('toolong'*20, max_length=50)}") # False
    print(f"is_valid_name('invalid!'): {is_valid_name('invalid!')}") # False
    print(f"is_valid_name(None): {is_valid_name(None)}") # False
    print(f"is_valid_name(''): {is_valid_name('')}") # False

    print(f"is_valid_file_path('test/path.txt'): {is_valid_file_path('test/path.txt')}") # True
    print(f"is_valid_file_path('C:\\test\\path.txt'): {is_valid_file_path('C:\\test\\path.txt')}") # True
    print(f"is_valid_file_path('/usr/local/bin/script.sh'): {is_valid_file_path('/usr/local/bin/script.sh')}") # True
    print(f"is_valid_file_path('a/b*c.txt'): {is_valid_file_path('a/b*c.txt')}") # True (caracteres como * são permitidos em nomes de arquivo em alguns OS, Path() não os rejeita)
    print(f"is_valid_file_path('a/b\0c.txt'): {is_valid_file_path('a/b\0c.txt')}") # False (caractere nulo)
    print(f"is_valid_file_path(None): {is_valid_file_path(None)}") # False
    print(f"is_valid_file_path(''): {is_valid_file_path('')}") # False 