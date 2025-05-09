"""
Módulo para execução de comandos do aider.
"""

import subprocess
import shlex
import os
import sys
from pathlib import Path
from typing import List, Dict

from .exceptions import ProfileNotFoundError, ProviderNotFoundError, EndpointNotFoundError, CommandBuildError, CommandExecutionError
from .logger import get_logger

# Obter logger para este módulo
logger = get_logger("command_executor")

class CommandExecutor:
    """Classe para construção e execução de comandos do aider."""
    
    def __init__(self, config_manager=None):
        """Inicializa o executor de comandos."""
        self.config_manager = config_manager
    
    def check_aider_installed(self):
        """Verifica se o aider está instalado e acessível."""
        try:
            # Executa o comando 'aider --version' para verificar se o aider está instalado
            result = subprocess.run(["aider", "--version"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  check=False,
                                  text=True)
            
            # Se o comando for executado com sucesso, o aider está instalado
            return result.returncode == 0
        except FileNotFoundError:
            # Se o comando não for encontrado, o aider não está instalado
            return False
    
    def build_command(self, profile_name):
        """
        Constrói o comando aider a ser executado com base no perfil.
        
        Args:
            profile_name (str): Nome do perfil a ser usado
            
        Returns:
            list: Lista de strings com o comando e seus parâmetros
            
        Raises:
            ValueError: Se o perfil não for encontrado ou houver erro na construção.
        """
        if not self.config_manager:
            logger.error("Tentativa de construir comando sem ConfigManager inicializado.")
            raise CommandBuildError("ConfigManager não inicializado")
        
        try:
            logger.debug(f"Construindo comando para o perfil: {profile_name}")
            
            # Verificar se o perfil existe
            profile = self.config_manager.get_profile(profile_name) # Pode levantar ProfileNotFoundError
            if not profile:
                raise ProfileNotFoundError(f"Perfil '{profile_name}' não encontrado")
            
            # Usar o método _get_cli_args_from_profile para obter os argumentos CLI
            cmd = self._get_cli_args_from_profile(profile_name)
            
            # Log do comando final
            logger.info(f"Comando construído para perfil '{profile_name}': {' '.join(cmd)}")
            return cmd
            
        except (ProfileNotFoundError, ProviderNotFoundError, EndpointNotFoundError) as e_conf:
            logger.error(f"Erro de configuração ao construir comando para perfil '{profile_name}': {e_conf}")
            raise CommandBuildError(f"Erro de configuração para perfil '{profile_name}': {e_conf}") from e_conf
        except Exception as e_general:
            logger.error(f"Erro inesperado ao construir comando para perfil '{profile_name}': {e_general}")
            raise CommandBuildError(f"Erro inesperado ao construir comando para '{profile_name}': {e_general}") from e_general
    
    def execute_command(self, profile_name):
        """
        Executa o comando aider com o perfil especificado.
        
        Args:
            profile_name (str): Nome do perfil a ser usado
            
        Returns:
            bool: True se o comando for executado com sucesso, False caso contrário
            
        Raises:
            CommandBuildError: Se houver erro ao construir o comando.
            CommandExecutionError: Se houver erro ao executar o comando.
        """
        try:
            # Verifica se o aider está instalado
            if not self.check_aider_installed():
                error_msg = "aider não está instalado ou não está no PATH."
                logger.error(error_msg)
                # Para consistência, levantamos um erro aqui também, 
                # já que é uma pré-condição para a execução.
                raise CommandExecutionError(error_msg)
                
            # Constrói o comando
            logger.debug(f"Iniciando execução do comando para o perfil: {profile_name}")
            cmd = self.build_command(profile_name) # Pode levantar CommandBuildError
            
            # Prepara o ambiente ANTES de usá-lo
            prepared_env = self._prepare_env_for_profile(profile_name)
            
            # Exibe o comando que será executado
            logger.info(f"Executando: {' '.join(shlex.quote(c) for c in cmd)}")
            print(f"Executando: {' '.join(shlex.quote(c) for c in cmd)}") # Manter print para feedback ao usuário
            
            # Executa o comando
            if sys.platform == 'win32':
                # No Windows, usa subprocess.run
                result = subprocess.run(cmd, check=False, text=True, capture_output=True, env=prepared_env)
                if result.returncode != 0:
                    error_detail = result.stderr.strip() if result.stderr else (result.stdout.strip() if result.stdout else "Sem output de erro específico.")
                    logger.error(f"Comando aider falhou (código: {result.returncode}). Detalhes: {error_detail}")
                    raise CommandExecutionError(f"Comando aider falhou (código: {result.returncode}). Detalhes: {error_detail}")
            else:
                # No Unix, usa os.execvp para substituir o processo atual
                # Se execvp falhar (ex: comando não encontrado), ele levanta OSError
                # Precisa do ambiente preparado também
                os.execvpe(cmd[0], cmd, prepared_env)
                # O código abaixo de execvp não será alcançado se for bem-sucedido.
                
            logger.info(f"Comando para perfil '{profile_name}' executado.") # No Unix, isto não será logado se execvp suceder.
            return True
        except CommandBuildError: # Já logado em build_command
            print(f"Erro ao construir o comando para o perfil '{profile_name}'. Verifique os logs.")
            raise # Re-propaga o erro de construção.
        except FileNotFoundError as e_fnf: # Especificamente para falha de os.execvp
            command_name = cmd[0] if 'cmd' in locals() and cmd else 'aider'
            error_msg = f"Comando '{command_name}' não encontrado durante execvp: {e_fnf}"
            logger.error(error_msg)
            print(f"Erro: {error_msg}")
            raise CommandExecutionError(error_msg) from e_fnf
        except OSError as e_os: # Para outros erros de os.execvp ou problemas de permissão com subprocess.run
            command_name = cmd[0] if 'cmd' in locals() and cmd else 'aider'
            error_msg = f"Erro de Sistema Operacional ao tentar executar '{command_name}': {e_os}"
            logger.error(error_msg)
            print(f"Erro: {error_msg}")
            raise CommandExecutionError(error_msg) from e_os
        # A exceção CommandExecutionError levantada pelo returncode != 0 já foi logada e tratada.
        # Não precisamos de um except específico para ela aqui se ela for apenas re-propagada.
        except Exception as e_general: 
            # Se for uma das nossas exceções já tratadas e logadas, apenas re-propague.
            if isinstance(e_general, (CommandBuildError, CommandExecutionError)):
                raise
            
            # Caso contrário, é um erro verdadeiramente inesperado.
            command_str = ' '.join(shlex.quote(c) for c in cmd) if 'cmd' in locals() else "Comando não construído"
            logger.error(f"Erro verdadeiramente inesperado ao executar comando ({command_str}): {e_general}", exc_info=True)
            print(f"Erro inesperado ao executar o comando. Verifique os logs para detalhes completos.")
            raise CommandExecutionError(f"Erro inesperado: {e_general}") from e_general
            
    def run_aider(self, profile_name):
        """
        Método de conveniência para executar o aider.
        Equivalente a execute_command.
        
        Args:
            profile_name (str): Nome do perfil a ser usado
            
        Returns:
            bool: True se o comando for executado com sucesso, False caso contrário
        """
        return self.execute_command(profile_name) 

    def _prepare_env_for_profile(self, profile_name: str) -> Dict[str, str]:
        """Prepara o ambiente para executar o comando aider com base no perfil."""
        current_env = os.environ.copy() # Começa com uma cópia do ambiente atual
        
        try:
            profile_data = self.config_manager.get_profile(profile_name) 
        except ProfileNotFoundError:
            logger.error(f"Perfil '{profile_name}' não encontrado ao preparar o ambiente.")
            return current_env # Retorna o ambiente não modificado

        provider_name = profile_data.get('provider')
        if provider_name:
            logger.debug(f"Processando provedor: {provider_name} para variáveis de ambiente do perfil {profile_name}")
            try:
                provider_config_data = self.config_manager.get_provider(provider_name) 
                api_key_env_var = provider_config_data.get('api_key_env_var')
                api_key = self.config_manager.get_api_key(provider_name) 
                
                if api_key_env_var and api_key:
                    logger.debug(f"Definindo variável de ambiente {api_key_env_var} para o provedor {provider_name}")
                    current_env[api_key_env_var] = api_key
                elif api_key_env_var and not api_key:
                    logger.warning(f"Variável de ambiente {api_key_env_var} definida para provedor {provider_name}, mas nenhuma chave API encontrada no keyring.")
                else:
                    logger.debug(f"Nenhuma chave API ou nome de variável de ambiente para definir para provedor {provider_name}")
            except ProviderNotFoundError:
                logger.warning(f"Provedor '{provider_name}' especificado no perfil '{profile_name}' não encontrado. Variável de ambiente do provedor não será definida.")

        endpoint_name = profile_data.get('endpoint')
        if endpoint_name:
            logger.debug(f"Processando endpoint: {endpoint_name} para variáveis de ambiente do perfil {profile_name}")
            try:
                # get_endpoint não é necessário aqui se só precisamos da chave API
                # Aider espera OPENAI_API_KEY para endpoints com api_base customizada
                api_key = self.config_manager.get_api_key(f"endpoint_{endpoint_name}")
                if api_key:
                    logger.debug(f"Definindo variável de ambiente OPENAI_API_KEY para o endpoint {endpoint_name}")
                    current_env['OPENAI_API_KEY'] = api_key
                else:
                    logger.debug(f"Nenhuma chave API encontrada para endpoint {endpoint_name} para definir OPENAI_API_KEY.")
            except Exception as e: # Captura genérica para get_api_key ou outras falhas
                 logger.error(f"Erro ao processar API key para endpoint '{endpoint_name}': {e}")
        
        return current_env

    def _get_cli_args_from_profile(self, profile_name: str) -> List[str]:
        """ Obtém os argumentos de linha de comando a partir do perfil. """
        cmd = ["aider"]
        try:
            profile_data = self.config_manager.get_profile(profile_name)
        except ProfileNotFoundError:
            logger.error(f"Perfil '{profile_name}' não encontrado ao construir argumentos CLI.")
            # Retorna apenas "aider" para que build_command possa levantar CommandBuildError
            return cmd 

        param_db_instance = getattr(self.config_manager, 'param_db', None) # Acessa param_db se existir

        # Mapeamento preferencial de param_db para nomes de CLI args
        param_to_cli_map = {}
        if param_db_instance:
            for cat_data in param_db_instance.db.values():
                for p_name, p_details in cat_data.get('parameters', {}).items():
                    if 'cli_arg' in p_details:
                        param_to_cli_map[p_name] = p_details['cli_arg']
                    elif 'default_cli_arg' in p_details: # Para casos como 'model' que não tem cli_arg mas tem default
                         param_to_cli_map[p_name] = p_details['default_cli_arg']

        for key, value in profile_data.items():
            if key in ['name', 'provider', 'endpoint']: # Ignorar chaves de controle
                continue

            cli_arg = param_to_cli_map.get(key) # Tenta obter do param_db
            if not cli_arg:
                # Fallback se não estiver no param_db ou não tiver cli_arg definido ali
                # Alguns parâmetros são especiais e não seguem o padrão --key
                if key == "fnames" or key == "file": # Aider usa apenas o valor, sem --fnames
                    if isinstance(value, list):
                        cmd.extend(value)
                    elif isinstance(value, str) and value.strip():
                        cmd.append(value)
                    continue # Processado, pular para o próximo
                else:
                    cli_arg = f"--{key.replace('_', '-')}"
            
            if isinstance(value, bool):
                if value:
                    # Se o cli_arg já for "--no-something" e value é True, isso é uma contradição.
                    # A lógica aqui assume que cli_arg é a forma positiva da flag.
                    if cli_arg.startswith("--no-"):
                        logger.warning(f"Contradição de flag booleana para {key}: cli_arg é {cli_arg} mas valor é True.")
                        # Tentativa de usar a forma positiva
                        positive_flag = "--" + cli_arg[5:]
                        cmd.append(positive_flag)
                    else:
                        cmd.append(cli_arg)
                else:
                    # Valor é False. Precisamos do "--no-" prefixo.
                    if cli_arg.startswith("--no-"): # Já está no formato correto
                        cmd.append(cli_arg)
                    elif cli_arg.startswith("--"):
                        cmd.append(f"--no-{cli_arg[2:]}")
                    else:
                        logger.warning(f"Não foi possível determinar a flag negativa para {cli_arg} (chave: {key})")
            elif value is not None and str(value).strip() != "": # Checa se não é None ou string vazia
                cmd.extend([cli_arg, str(value)])

        # Lógica específica para provedor e endpoint (afeta CLI args, não env vars aqui)
        provider_name = profile_data.get('provider')
        if provider_name:
            try:
                provider_config = self.config_manager.get_provider(provider_name)
                # Garantir que o api_type seja incluído se disponível
                if provider_config.get('api_type'):
                    cmd.extend(['--api-type', provider_config['api_type']])
                
                # Adicionar params específicos do provedor que afetam CLI args
                # Exemplo: 'api_type' que tem mapeamento direto para um CLI arg do Aider
                if 'params' in provider_config:
                    for p_param_key, p_param_config in provider_config['params'].items():
                        if isinstance(p_param_config, dict) and p_param_config.get('cli_arg') and p_param_config.get('value') not in [None, "", False]:
                            cmd.extend([p_param_config['cli_arg'], str(p_param_config['value'])])
                # Se o modelo do provedor deve substituir o modelo do perfil, adicione aqui.
                # A lógica atual do param_db é que 'model' é um parâmetro de alto nível.
                # Se um provedor tem um modelo default, ele deve ser setado no perfil.
            except ProviderNotFoundError as pnf:
                # Levantar CommandBuildError em vez de apenas avisar
                error_msg = f"Provedor '{provider_name}' não encontrado ao construir argumentos CLI."
                logger.error(error_msg)
                raise CommandBuildError(error_msg) from pnf

        endpoint_name = profile_data.get('endpoint')
        if endpoint_name:
            try:
                endpoint_config = self.config_manager.get_endpoint(endpoint_name)
                if endpoint_config.get('api_url'):
                    # Verificar se --api-base já foi adicionado por um parâmetro 'api_base' no perfil
                    # para evitar duplicidade.
                    if "--api-base" not in cmd:
                        cmd.extend(["--api-base", endpoint_config['api_url']])
                    elif cmd[cmd.index("--api-base") + 1] != endpoint_config['api_url']:
                        logger.warning("Conflito de api_base: definido no perfil e no endpoint. Usando valor do perfil.")
                
                # Se o endpoint define um api_type específico (ex: 'openai', 'anthropic')
                if endpoint_config.get('api_type'):
                    if "--api-type" not in cmd:
                        cmd.extend(["--api-type", endpoint_config['api_type']])
                    elif cmd[cmd.index("--api-type") + 1] != endpoint_config['api_type']:
                        logger.warning("Conflito de api_type: definido no perfil e no endpoint. Usando valor do perfil.")

            except EndpointNotFoundError as enf:
                # Levantar CommandBuildError em vez de apenas avisar
                error_msg = f"Endpoint '{endpoint_name}' não encontrado ao construir argumentos CLI."
                logger.error(error_msg)
                raise CommandBuildError(error_msg) from enf
        
        return cmd 