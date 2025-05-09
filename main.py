#!/usr/bin/env python
"""
Script principal para iniciar o aider-start.
"""

from aider_start.tui import TUI
from aider_start.config_manager import ConfigManager
from aider_start.param_db import ParameterDatabase
from aider_start.profile_builder import ProfileBuilder

def main():
    """Função principal que inicia a aplicação."""
    # Inicializa componentes com dados de teste para desenvolvimento
    config_manager = ConfigManager(use_test_data=True)
    param_db = ParameterDatabase()
    profile_builder = ProfileBuilder(
        config_manager=config_manager,
        param_db=param_db
    )
    
    # Inicializa e inicia a interface TUI
    tui = TUI(
        config_manager=config_manager,
        profile_builder=profile_builder
    )
    
    print("Iniciando aider-start...")
    tui.start()

if __name__ == "__main__":
    main() 