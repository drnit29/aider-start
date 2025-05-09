#!/usr/bin/env python3
"""
Ponto de entrada principal para o aider-start.
"""

import sys
import argparse
from pathlib import Path

from .config_manager import ConfigManager
from .secure_config import SecureConfigManager
from .tui import TUI
from .profile_builder import ProfileBuilder
from .command_executor import CommandExecutor
from .logger import get_logger

# Obter logger para este módulo
logger = get_logger("main")

def parse_args():
    """Processar argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description="Gerenciador de perfis para o aider"
    )
    parser.add_argument(
        "--config", "-c", action="store_true", 
        help="Iniciar no modo de configuração"
    )
    parser.add_argument(
        "--profile", "-p", 
        help="Iniciar o aider com o perfil especificado"
    )
    parser.add_argument(
        "--list", "-l", action="store_true", 
        help="Listar perfis disponíveis"
    )
    parser.add_argument(
        "--version", "-v", action="store_true", 
        help="Mostrar informação de versão"
    )
    
    return parser.parse_args()


def main():
    """Função principal da aplicação"""
    args = parse_args()
    
    # Mostrar versão e sair se solicitado
    if args.version:
        print("aider-start v0.1.0")
        return 0
    
    # Inicializa componentes
    logger.debug("Inicializando componentes principais")
    try:
        config_manager = SecureConfigManager()
        profile_builder = ProfileBuilder(config_manager=config_manager)
        command_executor = CommandExecutor(config_manager=config_manager)
        
        # Adiciona alguns dados de teste durante o desenvolvimento
        if not config_manager.get_profiles():
            logger.debug("Nenhum perfil encontrado, usando modo de teste")
            config_manager = SecureConfigManager(use_test_data=True)
            profile_builder = ProfileBuilder(config_manager=config_manager)
            command_executor = CommandExecutor(config_manager=config_manager)
    except Exception as e:
        logger.error(f"Erro inicializando componentes: {e}")
        print(f"Erro inicializando a aplicação: {e}")
        return 1
    
    # Listar perfis e sair se solicitado
    if args.list:
        profiles = config_manager.get_profiles()
        if not profiles:
            print("Nenhum perfil encontrado.")
        else:
            print("Perfis disponíveis:")
            for name in profiles.keys():
                print(f"  {name}")
        return 0
    
    # Iniciar com perfil específico se fornecido
    if args.profile:
        profile_name = args.profile
        profiles = config_manager.get_profiles()
        
        if profile_name in profiles:
            logger.info(f"Iniciando aider com perfil: {profile_name}")
            print(f"Iniciando aider com perfil: {profile_name}")
            try:
                success = command_executor.execute_command(profile_name)
                return 0 if success else 1
            except Exception as e:
                logger.error(f"Erro executando aider com perfil {profile_name}: {e}")
                print(f"Erro executando aider: {e}")
                return 1
        else:
            logger.error(f"Perfil não encontrado: {profile_name}")
            print(f"Erro: Perfil '{profile_name}' não encontrado.")
            print("Use --list para ver os perfis disponíveis.")
            return 1
    
    # Iniciar no modo de configuração (não implementado ainda)
    if args.config:
        print("Modo de configuração via CLI ainda não implementado.")
        print("Iniciando a interface TUI para configuração...")
    
    # Caso contrário, iniciar a TUI
    logger.info("Iniciando interface TUI")
    try:
        tui = TUI(config_manager=config_manager, 
                 profile_builder=profile_builder, 
                 command_executor=command_executor)
        tui.start()
    except Exception as e:
        logger.error(f"Erro na execução da TUI: {e}")
        print(f"Erro na interface gráfica: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 