"""
Configuração de logging para o aider-start.
"""

import logging
import os
import sys
from pathlib import Path


def setup_logger(name="aider_start", level=logging.INFO, log_file=None, enable_console=True):
    """Configura e retorna um logger."""
    logger = logging.getLogger(name)
    
    # Evitar configurar o mesmo logger duas vezes
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Formato para logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para console
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Handler para arquivo se especificado
    if log_file:
        log_dir = Path(log_file).parent
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Logger padrão para o módulo - desabilitando saída no console para testes
logger = setup_logger(enable_console=False)


def get_logger(module_name=None):
    """Retorna um logger para o módulo especificado."""
    if module_name:
        return logging.getLogger(f"aider_start.{module_name}")
    return logger 