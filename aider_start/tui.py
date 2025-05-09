"""
Módulo para interface de terminal (TUI) do aider-start.
"""

import curses
import sys
from typing import List, Optional, Any, Dict, Tuple

from .context_help import ContextHelp
from .param_validator import ParamValidator
from .logger import get_logger
from .exceptions import ConfigError, CommandError, ValidationError, ProfileError, FileAccessError

# Obter logger para este módulo
tui_logger = get_logger("tui")

class TUI:
    """Classe principal para a interface de terminal."""
    
    def __init__(self, config_manager=None, profile_builder=None, command_executor=None):
        """Inicializa a interface TUI."""
        self.config_manager = config_manager
        self.profile_builder = profile_builder
        self.command_executor = command_executor
        self.screen = None
        self.current_row = 0
        self.height = 0
        self.width = 0
        
        # Inicializar o helper de contexto se o profile_builder tiver param_db
        self.context_help = None
        self.param_validator = None
        if self.profile_builder and hasattr(self.profile_builder, 'param_db'):
            self.context_help = ContextHelp(self.profile_builder.param_db)
            self.param_validator = ParamValidator(self.profile_builder.param_db)
        
        # Armazenar erros de validação dos parâmetros
        self.validation_errors = {}
        
    def start(self):
        """Inicia a interface TUI."""
        try:
            curses.wrapper(self._main)
        except KeyboardInterrupt:
            # Tratamento de interrupção pelo usuário (Ctrl+C)
            print("Programa encerrado pelo usuário.")
            tui_logger.info("Programa encerrado pelo usuário (KeyboardInterrupt).")
        except Exception as e:
            # Tratamento genérico de exceções
            tui_logger.critical(f"Erro não tratado na TUI: {e}", exc_info=True)
            print(f"Erro crítico não tratado: {str(e)}. Verifique os logs.")
        
    def _main(self, stdscr):
        """Loop principal da TUI."""
        self.screen = stdscr
        # Configuração inicial
        curses.curs_set(0)  # Oculta o cursor
        self.screen.clear()
        
        # Obtém as dimensões da tela
        self.height, self.width = self.screen.getmaxyx()
        
        # Configuração de cores
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Item selecionado
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Cabeçalho
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)    # Título de Erro
        
        # Mostra o menu principal
        self.display_main_menu()
    
    def display_main_menu(self):
        """Exibe o menu principal."""
        menu_items = [
            "Selecionar Perfil",
            "Criar Novo Perfil",
            "Gerenciar Provedores",
            "Gerenciar Endpoints",
            "Sair"
        ]
        
        selected = self._show_menu("aider-start", "Selecione uma opção:", menu_items)
        
        if selected == 0:
            self.display_profile_selection()
        elif selected == 1:
            self.display_profile_creation()
        elif selected == 2:
            self.display_provider_management()
        elif selected == 3:
            self.display_endpoint_management()
        elif selected == 4:
            sys.exit(0)
    
    def _safe_addstr(self, y: int, x: int, text: str, color_pair=0):
        """Adiciona texto com segurança, garantindo que não ultrapasse os limites da tela."""
        # Verifica se a posição está dentro dos limites da tela
        if y < 0 or y >= self.height or x < 0 or x >= self.width:
            return
        
        # Trunca o texto se necessário para caber na tela
        max_width = self.width - x - 1
        if max_width <= 0:
            return
        
        # Trunca o texto se for maior que o espaço disponível
        display_text = text[:max_width]
        
        try:
            self.screen.addstr(y, x, display_text, color_pair)
        except curses.error:
            # Ignora erros de posicionamento (pode ocorrer ao escrever no último caractere da tela)
            pass
    
    def _show_menu(self, title: str, prompt: str, items: List[str]) -> int:
        """Mostra um menu e retorna o índice selecionado."""
        current_item = 0
        
        while True:
            # Limpa a tela a cada atualização
            self.screen.clear()
            
            # Desenha o título
            title_text = title.center(self.width - 1)
            self._safe_addstr(0, 0, title_text, curses.color_pair(2))
            self._safe_addstr(2, 2, prompt)
            
            # Desenha os itens do menu
            for i, item in enumerate(items):
                y = i + 4
                if i == current_item:
                    self._safe_addstr(y, 4, f"> {item}", curses.color_pair(1))
                else:
                    self._safe_addstr(y, 4, f"  {item}")
            
            # Desenha o rodapé
            footer = "Use as setas para navegar, Enter para selecionar, q para sair"
            footer_text = footer.center(self.width - 1)
            self._safe_addstr(self.height-2, 0, footer_text)
            
            self.screen.refresh()
            
            # Processa entrada do usuário
            key = self.screen.getch()
            
            if key == ord('q'):
                # Sair com a tecla 'q'
                sys.exit(0)
            elif key == curses.KEY_UP and current_item > 0:
                current_item -= 1
            elif key == curses.KEY_DOWN and current_item < len(items) - 1:
                current_item += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:  # Tecla Enter
                return current_item
    
    def handle_input(self):
        """Processa a entrada do usuário."""
        # Esta função será implementada quando necessário
        pass
    
    def _display_error_dialog(self, title: str, message: str, details: Optional[str] = None):
        """Exibe um diálogo de erro formatado."""
        self.screen.clear()
        
        # Título do erro (vermelho)
        error_title = f"ERRO: {title}".center(self.width -1)
        self._safe_addstr(0, 0, error_title, curses.color_pair(3)) # Usa cor 3 para erro
        
        # Mensagem principal
        lines = message.split('\n')
        start_y = 2
        for i, line in enumerate(lines):
            self._safe_addstr(start_y + i, 2, line)
        
        current_y = start_y + len(lines) + 1
        
        # Opção para ver detalhes, se houver
        has_details_option = False
        if details:
            has_details_option = True
            self._safe_addstr(current_y, 2, "[D] Ver Detalhes")
            current_y += 2 # Espaço adicional para a opção de detalhes
            
        self._safe_addstr(current_y, 2, "Pressione qualquer tecla para continuar...")
        self.screen.refresh()
        
        key = self.screen.getch()
        
        if has_details_option and (key == ord('d') or key == ord('D')):
            # Chamar um método para mostrar o texto rolável dos detalhes
            self._show_scrollable_text_dialog(f"Detalhes do Erro: {title}", details)

    def _show_scrollable_text_dialog(self, title: str, text_content: str):
        """Mostra um diálogo com texto rolável (para detalhes de erro, ajuda, etc.)."""
        if not text_content:
            # Usar o novo diálogo de erro para erros internos da TUI
            self._display_error_dialog("Erro Interno da TUI", "Nenhum conteúdo para exibir no diálogo de texto.")
            return

        lines = text_content.split('\n')
        self.screen.clear()
        
        self._safe_addstr(0, 0, title.center(self.width - 1), curses.color_pair(2)) # Cor normal para título
        
        max_visible_lines = self.height - 4 # Espaço para título e rodapé
        current_top_line = 0
        
        while True:
            self.screen.clear() 
            self._safe_addstr(0, 0, title.center(self.width - 1), curses.color_pair(2))

            for i in range(max_visible_lines):
                line_idx = current_top_line + i
                if line_idx < len(lines):
                    self._safe_addstr(2 + i, 2, lines[line_idx])
                else:
                    break
            
            if current_top_line > 0:
                self._safe_addstr(1, self.width - 3, "↑")
            if current_top_line + max_visible_lines < len(lines):
                self._safe_addstr(self.height - 3, self.width - 3, "↓")

            self._safe_addstr(self.height - 2, 0, "Use ↑/↓ para rolar, 'q' ou ESC para fechar".center(self.width -1))
            self.screen.refresh()
            
            key = self.screen.getch()
            if key == ord('q') or key == ord('Q') or key == 27: # q, Q ou ESC
                break
            elif key == curses.KEY_UP and current_top_line > 0:
                current_top_line -= 1
            elif key == curses.KEY_DOWN and current_top_line + max_visible_lines < len(lines):
                current_top_line += 1
        self.screen.clear() # Limpar após fechar o diálogo rolável

    def _execute_safely(self, func_to_call, *args, **kwargs):
        """Executa uma função de forma segura, capturando e exibindo erros."""
        import traceback # Importar aqui para uso nos detalhes
        try:
            return func_to_call(*args, **kwargs)
        except (ConfigError, CommandError, ValidationError, ProfileError, FileAccessError) as e: # Nossas exceções esperadas
            tui_logger.error(f"Erro da aplicação tratado na TUI: {type(e).__name__} - {e}", exc_info=True)
            details_text = traceback.format_exc()
            self._display_error_dialog(f"Erro: {type(e).__name__}", str(e), details=details_text)
            return None # Indica falha
        except Exception as e_unexp: # Erros inesperados não previstos
            tui_logger.critical(f"Erro inesperado capturado na TUI: {e_unexp}", exc_info=True)
            details_text = traceback.format_exc()
            self._display_error_dialog("Erro Inesperado do Sistema", str(e_unexp), details=details_text)
            return None # Indica falha

    # Métodos placeholder para outras telas
    def display_profile_selection(self):
        """Exibe a tela de seleção de perfil."""
        if not self.config_manager:
            self._show_message("Erro", "ConfigManager não inicializado.")
            self.display_main_menu()
            return
            
        # Obtém perfis do config manager
        profiles = self.config_manager.get_profiles()
        
        if not profiles:
            self._show_message("Nenhum Perfil Encontrado", "Não existem perfis configurados.\nCrie um novo perfil primeiro.")
            self.display_profile_creation()
            return
        
        # Cria itens do menu a partir dos perfis
        profile_names = list(profiles.keys())
        menu_items = profile_names.copy()
        menu_items.append("Voltar ao Menu Principal")
        
        # Mostra o menu de seleção de perfil
        selected = self._show_menu("Seleção de Perfil", "Selecione um perfil para usar com o aider:", menu_items)
        
        if selected < len(profile_names):
            # Usuário selecionou um perfil
            selected_profile = profile_names[selected]
            profile_data = profiles.get(selected_profile, {})
            self._show_profile_details(selected_profile, profile_data)
        else:
            # Usuário selecionou "Voltar ao Menu Principal"
            self.display_main_menu()
    
    def _show_profile_details(self, profile_name: str, profile_data: dict):
        """Exibe os detalhes de um perfil e opções para ação."""
        self.screen.clear()
        
        # Desenha o título
        title_text = f"Perfil: {profile_name}".center(self.width - 1)
        self._safe_addstr(0, 0, title_text, curses.color_pair(2))
        
        # Exibe os dados do perfil
        self._safe_addstr(2, 2, "Detalhes do Perfil:")
        
        row = 3
        for key, value in profile_data.items():
            if key == "name":
                continue  # Nome já está no título
            
            # Ocultar valores de segurança (ex: api_key)
            display_value = "********" if "key" in key.lower() or "secret" in key.lower() else str(value)
            self._safe_addstr(row, 4, f"{key}: {display_value}")
            row += 1
        
        # Exibe opções
        options = [
            "1. Iniciar aider com este perfil",
            "2. Editar perfil",
            "3. Excluir perfil",
            "4. Voltar à seleção de perfil"
        ]
        
        row += 2
        self._safe_addstr(row, 2, "Opções:")
        row += 1
        
        for option in options:
            self._safe_addstr(row, 4, option)
            row += 1
        
        # Desenha o rodapé
        self._safe_addstr(self.height-2, 0, "Pressione o número da opção desejada...".center(self.width - 1))
        
        self.screen.refresh()
        
        # Processa a escolha do usuário
        while True:
            key = self.screen.getch()
            
            if key == ord('1'):
                # Iniciar aider com este perfil
                self._launch_aider_with_profile(profile_name)
                break
            elif key == ord('2'):
                # Editar perfil - implementação futura
                self._show_message("Funcionalidade Futura", "A edição de perfis será implementada em breve.")
                self.display_profile_selection()
                break
            elif key == ord('3'):
                # Excluir perfil - implementação futura
                self._show_message("Funcionalidade Futura", "A exclusão de perfis será implementada em breve.")
                self.display_profile_selection()
                break
            elif key == ord('4') or key == 27:  # 4 ou ESC
                # Voltar à seleção de perfil
                self.display_profile_selection()
                break
            
    def _launch_aider_with_profile(self, profile_name: str):
        """Inicia o aider com o perfil selecionado."""
        if not self.command_executor:
            self._display_error_dialog("Componente Ausente", "CommandExecutor não inicializado.")
            return
            
        # Usar o wrapper para executar o comando
        self._execute_safely(self.command_executor.run_aider, profile_name)
    
    def _get_text_input(self, title: str, prompt: str, default=None):
        """Obtém entrada de texto do usuário."""
        self.screen.clear()
        
        # Desenha o título
        self._safe_addstr(0, 0, title.center(self.width - 1), curses.color_pair(2))
        
        # Desenha o prompt com quebras de linha
        y = 2
        for line in prompt.split('\n'):
            self._safe_addstr(y, 2, line)
            y += 1
        
        # Mostra o valor padrão, se houver
        if default is not None:
            self._safe_addstr(y + 1, 2, f"Valor padrão: {default}")
            self._safe_addstr(y + 2, 2, "(Pressione Enter para usar o valor padrão)")
            y += 3
        else:
            y += 1
        
        # Desenha a caixa de entrada
        self._safe_addstr(y, 2, "Digite seu valor abaixo:")
        y += 1
        input_y = y
        input_x = 4
        input_width = self.width - 8
        self._safe_addstr(input_y, input_x - 2, "> ")
        
        # Desenha o rodapé
        self._safe_addstr(self.height-2, 0, "Pressione Enter para confirmar, Esc para cancelar".center(self.width - 1))
        
        # Habilita cursor e eco para entrada
        curses.curs_set(1)
        curses.echo()
        
        # Inicializa o buffer de entrada
        input_buffer = ""
        cursor_pos = 0
        
        # Loop de entrada
        while True:
            # Limpa a linha de entrada
            self._safe_addstr(input_y, input_x, " " * input_width)
            
            # Mostra o buffer atual
            # Limita a exibição à largura disponível
            display_start = max(0, cursor_pos - input_width + 10)
            display_text = input_buffer[display_start:display_start + input_width]
            self._safe_addstr(input_y, input_x, display_text)
            
            # Posiciona o cursor
            try:
                self.screen.move(input_y, input_x + min(cursor_pos - display_start, input_width - 1))
            except curses.error:
                # Ignora erros de posicionamento
                pass
            
            self.screen.refresh()
            
            # Obtém o próximo caractere
            try:
                key = self.screen.getch()
            except Exception:
                key = 27  # ESC
            
            if key == 27:  # ESC
                curses.curs_set(0)
                curses.noecho()
                return None
            elif key == curses.KEY_ENTER or key in [10, 13]:  # Enter
                curses.curs_set(0)
                curses.noecho()
                
                # Se o usuário não digitou nada e há um valor padrão, retorna o padrão
                if not input_buffer and default is not None:
                    return default
                
                return input_buffer
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:  # Backspace
                if cursor_pos > 0:
                    input_buffer = input_buffer[:cursor_pos-1] + input_buffer[cursor_pos:]
                    cursor_pos -= 1
            elif key == curses.KEY_DC:  # Delete
                if cursor_pos < len(input_buffer):
                    input_buffer = input_buffer[:cursor_pos] + input_buffer[cursor_pos+1:]
            elif key == curses.KEY_LEFT:  # Seta esquerda
                cursor_pos = max(0, cursor_pos - 1)
            elif key == curses.KEY_RIGHT:  # Seta direita
                cursor_pos = min(len(input_buffer), cursor_pos + 1)
            elif key == curses.KEY_HOME:  # Home
                cursor_pos = 0
            elif key == curses.KEY_END:  # End
                cursor_pos = len(input_buffer)
            elif 32 <= key <= 126:  # Caracteres ASCII imprimíveis
                input_buffer = input_buffer[:cursor_pos] + chr(key) + input_buffer[cursor_pos:]
                cursor_pos += 1
    
    def display_profile_creation(self):
        """Exibe a tela de criação de perfil."""
        if not self.profile_builder:
            self._show_message("Erro", "ProfileBuilder não inicializado.")
            self.display_main_menu()
            return
            
        # Inicializa um novo perfil
        self.profile_builder.start_new_profile()
        
        # Obtém nome do perfil
        profile_name = self._get_text_input("Novo Perfil", "Digite um nome para o novo perfil:")
        if not profile_name:
            self.display_main_menu()
            return
        
        # Define o nome do perfil
        self.profile_builder.set_parameter("name", profile_name)
        
        # Mostra seleção de categorias
        self._show_category_selection(profile_name)
    
    def _show_category_selection(self, profile_name):
        """Mostra seleção de categorias de parâmetros para configuração."""
        if not self.profile_builder:
            self._show_message("Erro", "ProfileBuilder não inicializado.")
            self.display_main_menu()
            return
            
        # Obtém categorias disponíveis
        categories = self.profile_builder.get_categories()
        menu_items = categories.copy()
        menu_items.append("Finalizar Criação do Perfil")
        
        while True:
            selected = self._show_menu(f"Criando Perfil: {profile_name}", 
                                      "Selecione uma categoria para configurar:", 
                                      menu_items)
            
            if selected < len(categories):
                # Usuário selecionou uma categoria
                self._configure_category(profile_name, categories[selected])
            else:
                # Usuário selecionou "Finalizar Criação do Perfil"
                self._finalize_profile_creation_action(profile_name)
    
    def _configure_category(self, profile_name, category):
        """Exibe a interface para configurar uma categoria específica de parâmetros."""
        if not self.profile_builder:
            self._show_message("Erro", "ProfileBuilder não inicializado.")
            return
        
        # Obter parâmetros da categoria
        category_params = self.profile_builder.get_category_parameters(category)
        if not category_params:
            self._show_message("Categoria Vazia", f"A categoria '{category}' não possui parâmetros.")
            return
        
        # Obter o perfil atual
        current_profile = self.profile_builder.get_current_profile()
        
        # Lista para armazenar os nomes dos parâmetros na ordem de exibição
        param_names = list(category_params.keys())
        
        # Filtrar parâmetros com base no disclosure progressivo, se disponível
        if self.context_help:
            param_names = [p for p in param_names if self.context_help.should_show_parameter(p, current_profile)]
            
            # Destacar parâmetros obrigatórios
            required_params = self.context_help.get_required_parameters(category)
        else:
            required_params = []
        
        # Inicializar erros de validação para esta categoria
        if self.param_validator:
            self.validation_errors = {}
        
        # Loop de configuração
        current_index = 0
        while current_index < len(param_names):
            param_name = param_names[current_index]
            param_data = category_params[param_name]
            
            # Obter o valor atual do parâmetro
            current_value = self.profile_builder.get_parameter_value(param_name)
            
            # Determinar o tipo de parâmetro usando get_parameter_raw_type
            param_type_info = self.profile_builder.get_parameter_raw_type(category, param_name)
            
            # Verificar se o parâmetro é um array
            is_array = False
            array_item_type = None
            
            if isinstance(param_type_info, list):
                # O tipo pode ser uma lista como ["array", "null"] indicando um array opcional
                is_array = "array" in param_type_info
            elif isinstance(param_type_info, str):
                is_array = param_type_info == "array"
            
            # Se for um array, tentar determinar o tipo dos itens
            if is_array and "items" in param_data:
                items_info = param_data.get("items", {})
                if isinstance(items_info, dict) and "type" in items_info:
                    array_item_type = items_info["type"]
            
            # Formatar a descrição com indicação visual para parâmetros obrigatórios
            description = param_data.get('description', '')
            
            # Adicionar indicador de erro se houver erro de validação
            error_message = self.validation_errors.get(param_name, "")
            error_indicator = " [ERRO]" if error_message else ""
            
            if param_name in required_params:
                prompt = f"[OBRIGATÓRIO{error_indicator}] {param_name}: {description}"
            else:
                prompt = f"{param_name}{error_indicator}: {description}"
            
            # Adicionar mensagem de erro à descrição se houver
            if error_message:
                prompt += f"\n\nErro: {error_message}"
            
            # Adicionar informações sobre o tipo do parâmetro ao prompt
            param_type_display = self.profile_builder.get_parameter_type(category, param_name)
            is_secret = self.profile_builder.is_parameter_secret(category, param_name)
            
            prompt += f"\n\nTipo: {param_type_display}"
            if is_secret:
                prompt += " (CONFIDENCIAL)"
            
            # Ajustar prompt para arrays
            if is_array:
                prompt += "\n(Insira múltiplos valores separados por vírgula)"
                if array_item_type:
                    prompt += f"\nCada item deve ser do tipo: {array_item_type}"
            
            # Obter dicas de formato do parâmetro
            format_hint = ""
            if self.param_validator:
                format_hint = self.param_validator.get_parameter_format_hint(param_name, category)
                if format_hint:
                    prompt += f"\n{format_hint}"
            
            # Obter exemplos para o parâmetro, se disponíveis
            examples = []
            if self.context_help:
                examples = self.context_help.get_parameter_examples(param_name, category)
            
            # Adicionar exemplos à mensagem de prompt
            if examples:
                examples_str = ", ".join(examples)
                prompt += f"\nExemplos: {examples_str}"
            
            # Adicionar valor atual/padrão ao prompt
            default_value = self.profile_builder.get_parameter_default(category, param_name)
            
            if current_value is not None:
                if is_array and isinstance(current_value, list):
                    current_value_str = ", ".join(str(item) for item in current_value)
                    prompt += f"\n\nValor atual: {current_value_str}"
                else:
                    # Ocultar valores confidenciais
                    if is_secret and current_value:
                        prompt += f"\n\nValor atual: {'*' * len(str(current_value))}"
                    else:
                        prompt += f"\n\nValor atual: {current_value}"
            elif default_value is not None:
                if is_array and isinstance(default_value, list):
                    default_value_str = ", ".join(str(item) for item in default_value)
                    prompt += f"\n\nValor padrão: {default_value_str}"
                else:
                    # Ocultar valores confidenciais
                    if is_secret and default_value:
                        prompt += f"\n\nValor padrão: {'*' * len(str(default_value))}"
                    else:
                        prompt += f"\n\nValor padrão: {default_value}"
            
            # Processar entrada com base no tipo
            if param_type_info == 'boolean' or (isinstance(param_type_info, list) and 'boolean' in param_type_info):
                new_value = self._get_boolean_input(
                    f"Configurar {param_name}", 
                    prompt, 
                    default=current_value
                )
            elif is_array:
                # Formatação especial para arrays
                if current_value and isinstance(current_value, list):
                    default_str = ", ".join(str(item) for item in current_value)
                else:
                    default_str = ""
                
                input_str = self._get_text_input(
                    f"Configurar {param_name}",
                    prompt,
                    default=default_str
                )
                
                if input_str is not None:
                    if input_str.strip():
                        # Converter string para lista
                        new_value = [item.strip() for item in input_str.split(',') if item.strip()]
                        
                        # Converter tipos de itens se necessário
                        if array_item_type == 'integer':
                            try:
                                new_value = [int(item) for item in new_value]
                            except ValueError:
                                self._show_message(
                                    "Erro de Formato", 
                                    f"Um ou mais valores não são inteiros válidos. Use apenas números inteiros separados por vírgula."
                                )
                                continue
                        elif array_item_type == 'number' or array_item_type == 'float':
                            try:
                                new_value = [float(item) for item in new_value]
                            except ValueError:
                                self._show_message(
                                    "Erro de Formato", 
                                    f"Um ou mais valores não são números válidos. Use apenas números separados por vírgula."
                                )
                                continue
                    else:
                        new_value = []
                else:
                    new_value = None # Usuário cancelou
            elif param_type_info == 'integer' or (isinstance(param_type_info, list) and 'integer' in param_type_info):
                new_value = self._get_integer_input(
                    f"Configurar {param_name}", 
                    prompt,
                    default=current_value
                )
            elif param_type_info == 'number' or (isinstance(param_type_info, list) and 'number' in param_type_info):
                new_value = self._get_float_input(
                    f"Configurar {param_name}", 
                    prompt,
                    default=current_value
                )
            elif is_secret:
                new_value = self._get_password_input(
                    f"Configurar {param_name}", 
                    prompt
                )
            else:
                # String ou outro tipo padrão
                if current_value is not None:
                    default = str(current_value)
                else:
                    default = None
                    
                new_value = self._get_text_input(
                    f"Configurar {param_name}", 
                    prompt,
                    default=default
                )
            
            # Se o usuário pressionar Escape (None), voltar para o parâmetro anterior
            if new_value is None:
                current_index = max(0, current_index - 1)
                continue
                
            # Se uma string vazia for fornecida para um parâmetro não-string, converter para None
            if new_value == "" and param_type_info != 'string' and not isinstance(param_type_info, list):
                new_value = None
                
            # Validar o valor antes de atualizar o parâmetro
            if self.param_validator:
                # Obter uma cópia do perfil para validação cruzada
                validation_profile = self.profile_builder.get_current_profile().copy()
                validation_profile[param_name] = new_value
                
                # Validar o parâmetro
                is_valid, error_message = self.param_validator.validate_parameter(
                    param_name, 
                    new_value, 
                    category, 
                    validation_profile
                )
                
                if not is_valid:
                    # Armazenar erro para este parâmetro
                    self.validation_errors[param_name] = error_message
                    
                    # Mostrar mensagem de erro e solicitar correção
                    self._show_message(
                        "Erro de Validação", 
                        f"O valor inserido para '{param_name}' é inválido:\n{error_message}\n\nPor favor, corrija o valor."
                    )
                    continue  # Manter no mesmo parâmetro
                else:
                    # Limpar erro se existia anteriormente
                    if param_name in self.validation_errors:
                        del self.validation_errors[param_name]
                
            # Atualizar o parâmetro no perfil
            self.profile_builder.set_parameter(param_name, new_value)
            
            # Mostrar mensagem de sucesso
            self._show_message(
                "Parâmetro Configurado", 
                f"O parâmetro '{param_name}' foi configurado com sucesso."
            )
            
            # Verificar se houve alteração no valor que afeta o disclosure progressivo
            if self.context_help and new_value != current_value:
                # Atualizar a lista de parâmetros visíveis
                updated_profile = self.profile_builder.get_current_profile()
                param_names = list(category_params.keys())
                param_names = [p for p in param_names if self.context_help.should_show_parameter(p, updated_profile)]
            
            # Perguntar se o usuário deseja ver ajuda detalhada sobre o parâmetro
            if self.context_help:
                # Mostrar opção de ajuda
                if self._get_confirmation(f"Deseja ver informações detalhadas sobre '{param_name}'?"):
                    help_text = self.context_help.get_parameter_help(param_name, category)
                    self._show_message(f"Ajuda: {param_name}", help_text)
            
            # Avançar para o próximo parâmetro
            current_index += 1
        
        # Validar todo o perfil antes de salvar
        if self.param_validator:
            complete_profile = self.profile_builder.get_current_profile()
            validation_errors = self.param_validator.get_validation_errors(complete_profile)
            
            if validation_errors:
                # Formatar mensagens de erro
                error_messages = [f"• {param}: {msg}" for param, msg in validation_errors.items()]
                error_text = "\n".join(error_messages)
                
                self._show_message(
                    "Erros de Validação",
                    f"Existem {len(validation_errors)} erros no perfil que precisam ser corrigidos:\n\n{error_text}"
                )
                self.validation_errors = validation_errors
                return
        
        # Salvar o perfil após configurar todos os parâmetros da categoria
        if self._get_confirmation(f"Salvar as configurações da categoria '{category}'?"):
            self._show_message("Sucesso", f"Configurações da categoria '{category}' salvas com sucesso!")
    
    def _finalize_profile_creation_action(self, profile_name: str):
        """Ação de finalização e salvamento de um novo perfil, com tratamento de erro."""
        tui_logger.debug(f"Finalizando criação do perfil: {profile_name}")

        def save_action():
            # Primeiro, validar o perfil construído até agora.
            is_profile_valid, validation_message = self.profile_builder.validate_profile()
            if not is_profile_valid:
                # Se a validação do ProfileBuilder falhar, mostrar como um erro da TUI
                # usando nosso diálogo. Isso é um erro antes de tentar salvar.
                self._display_error_dialog("Erro de Validação do Perfil", validation_message)
                return False # Indica falha na ação de salvar
            
            # Se a validação passou, tentar salvar.
            # profile_builder.save_profile() pode levantar FileAccessError, ValueError, ProfileError, ValidationError
            # que serão capturadas por _execute_safely.
            saved_profile_data = self.profile_builder.save_profile() # Não passar profile_name aqui
            
            if saved_profile_data: # Assume que save_profile retorna dados do perfil em sucesso
                self._show_message("Sucesso", f"Perfil '{profile_name}' criado/atualizado com sucesso.")
                return True # Indica sucesso da ação de salvar
            else:
                # Se save_profile retornou None/False (sem levantar exceção), é uma falha lógica interna.
                # Isso pode acontecer se, por exemplo, o perfil já existe e a lógica de save_profile
                # decide não sobrescrever sem um prompt explícito (hipotético).
                self._display_error_dialog(
                    "Falha ao Salvar Perfil", 
                    f"O perfil '{profile_name}' não pôde ser salvo. Verifique os logs para mais detalhes."
                )
                return False # Indica falha da ação de salvar

        # Envolver a função de ação de salvamento com _execute_safely.
        # _execute_safely cuidará de exceções levantadas por save_action (incluindo as de save_profile).
        self._execute_safely(save_action)
        
        # Após a tentativa de salvar (bem-sucedida ou não, com erro exibido), voltar ao menu principal.
        self.display_main_menu()

    def _get_help_for_parameter(self, param_name, category):
        """Exibe informações detalhadas de ajuda para um parâmetro."""
        if not self.context_help:
            self._show_message("Ajuda Indisponível", "Sistema de ajuda não inicializado.")
            return
            
        help_text = self.context_help.get_parameter_help(param_name, category)
        self._show_message(f"Ajuda: {param_name}", help_text)
    
    def _get_boolean_input(self, title, prompt, default=None):
        """Obtém entrada booleana (sim/não) do usuário."""
        options = ["Sim", "Não", "Cancelar"]
        
        # Define a opção padrão com base no valor padrão
        if default is not None:
            default_option = 0 if default else 1
        else:
            default_option = None
            
        # Formata o prompt com o valor padrão, se houver
        if default_option is not None:
            prompt_with_default = f"{prompt}\n\nValor padrão: {options[default_option]}"
        else:
            prompt_with_default = prompt
            
        selected = self._show_menu(title, prompt_with_default, options)
        
        if selected == 0:  # Sim
            return True
        elif selected == 1:  # Não
            return False
        else:  # Cancelar ou Escape
            return None
    
    def _get_float_input(self, title, prompt, default=None):
        """Obtém entrada de número de ponto flutuante do usuário."""
        while True:
            input_str = self._get_text_input(title, prompt, str(default) if default is not None else None)
            
            if input_str is None:  # Usuário cancelou
                return None
                
            # Tenta converter para float
            try:
                value = float(input_str)
                
                # Realizar validação específica para float, se disponível
                if self.param_validator and title.startswith("Configurar "):
                    param_name = title.replace("Configurar ", "")
                    is_valid, error_message = self.param_validator.validate_parameter(param_name, value)
                    
                    if not is_valid:
                        self._show_message("Erro de Validação", error_message)
                        continue
                        
                return value
            except ValueError:
                self._show_message("Erro", "Por favor, insira um número válido.")
                continue
    
    def _get_integer_input(self, title, prompt, default=None):
        """Obtém entrada de número inteiro do usuário."""
        while True:
            input_str = self._get_text_input(title, prompt, str(default) if default is not None else None)
            
            if input_str is None:  # Usuário cancelou
                return None
                
            # Tenta converter para inteiro
            try:
                value = int(input_str)
                
                # Realizar validação específica para inteiro, se disponível
                if self.param_validator and title.startswith("Configurar "):
                    param_name = title.replace("Configurar ", "")
                    is_valid, error_message = self.param_validator.validate_parameter(param_name, value)
                    
                    if not is_valid:
                        self._show_message("Erro de Validação", error_message)
                        continue
                        
                return value
            except ValueError:
                self._show_message("Erro", "Por favor, insira um número inteiro válido.")
                continue
    
    def display_provider_management(self):
        """Exibe a tela de gerenciamento de provedores."""
        if not self.config_manager:
            self._show_message("Erro", "ConfigManager não inicializado.")
            self.display_main_menu()
            return
        
        from .provider_manager import ProviderManager
        # Inicializa o gerenciador de provedores
        provider_manager = ProviderManager(self.config_manager)
        
        menu_items = [
            "Ver Provedores",
            "Adicionar Provedor",
            "Editar Provedor",
            "Remover Provedor",
            "Voltar ao Menu Principal"
        ]
        
        while True:
            selected = self._show_menu("Gerenciamento de Provedores", "Selecione uma opção:", menu_items)
            
            if selected == 0:
                self._show_providers(provider_manager)
            elif selected == 1:
                self._add_provider(provider_manager)
            elif selected == 2:
                self._edit_provider(provider_manager)
            elif selected == 3:
                self._delete_provider(provider_manager)
            elif selected == 4:
                self.display_main_menu()
                return
    
    def _show_providers(self, provider_manager):
        """Mostra todos os provedores configurados."""
        providers = provider_manager.get_providers()
        
        if not providers:
            self._show_message("Sem Provedores", "Não há provedores configurados.")
            return
        
        # Formata informações dos provedores
        provider_info = []
        for name, data in providers.items():
            description = data.get('description', 'Sem descrição')
            api_url = data.get('api_url', 'URL padrão')
            models = ", ".join(data.get('models', ['Nenhum modelo']))
            has_key = "Sim" if provider_manager.has_api_key(name) else "Não"
            
            provider_info.append(f"{name}")
            provider_info.append(f"  Descrição: {description}")
            provider_info.append(f"  URL da API: {api_url}")
            provider_info.append(f"  Chave API configurada: {has_key}")
            provider_info.append(f"  Modelos: {models}")
            provider_info.append("")
        
        self._show_scrollable_list("Provedores Configurados", "Lista de provedores:", provider_info)
    
    def _add_provider(self, provider_manager):
        """Adiciona um novo provedor."""
        # Obtém nome do provedor
        name = self._get_text_input("Adicionar Provedor", "Digite o nome do provedor (ex: OpenAI, Anthropic):")
        if not name:
            return
        
        # Verifica se já existe um provedor com esse nome
        if provider_manager.get_provider(name):
            self._show_message("Provedor Existente", f"Já existe um provedor com o nome '{name}'.")
            return
        
        # Obtém descrição
        description = self._get_text_input("Descrição", f"Digite uma descrição para o provedor '{name}':")
        if description is None:  # Usuário cancelou
            return
        
        # Obtém URL da API
        api_url = self._get_text_input("URL da API", 
                                      f"Digite a URL base da API para '{name}':", 
                                      "https://api.exemplo.com/v1")
        if api_url is None:  # Usuário cancelou
            return
        
        # Obtém API key
        api_key = self._get_password_input("Chave de API", f"Digite a chave de API para '{name}':")
        if api_key is None:  # Usuário cancelou
            return
        
        # Obtém modelos iniciais
        models_str = self._get_text_input("Modelos", "Digite uma lista de modelos separados por vírgula:")
        models = [m.strip() for m in models_str.split(',')] if models_str else []
        
        # Adiciona o provedor
        provider_data = {
            'description': description,
            'api_url': api_url,
            'api_key': api_key,
            'models': models
        }
        
        if api_key: # Só adiciona se não for vazia
            provider_data['api_key'] = api_key
        
        # Usar _execute_safely para a chamada de add_provider
        success = self._execute_safely(provider_manager.add_provider, name, provider_data)
        
        if success: # add_provider em ConfigManager retorna True em sucesso
            self._show_message("Sucesso", f"Provedor '{name}' adicionado.")
        # Se _execute_safely retornou None, o erro já foi exibido.
    
    def _edit_provider(self, provider_manager):
        """Edita um provedor existente."""
        providers = provider_manager.get_providers()
        
        if not providers:
            self._show_message("Sem Provedores", "Não há provedores configurados.")
            return
        
        # Lista os provedores para seleção
        provider_names = list(providers.keys())
        provider_names.append("Cancelar")
        
        selected = self._show_menu("Editar Provedor", "Selecione um provedor para editar:", provider_names)
        
        if selected < len(provider_names) - 1:
            provider_name = provider_names[selected]
            self._edit_provider_details(provider_manager, provider_name)
    
    def _edit_provider_details(self, provider_manager, provider_name):
        """Edita detalhes de um provedor específico."""
        provider = provider_manager.get_provider(provider_name)
        
        if not provider:
            self._show_message("Erro", f"Provedor '{provider_name}' não encontrado.")
            return
        
        menu_items = [
            "Editar Descrição",
            "Editar URL da API",
            "Alterar Chave de API",
            "Gerenciar Modelos",
            "Voltar"
        ]
        
        while True:
            selected = self._show_menu(f"Editando {provider_name}", "Selecione uma opção:", menu_items)
            
            if selected == 0:
                # Editar descrição
                current = provider.get('description', '')
                description = self._get_text_input("Descrição", f"Digite a nova descrição:", current)
                if description is not None:
                    provider_data = provider.copy()
                    provider_data['description'] = description
                    # add_provider aqui é usado para atualizar, _execute_safely tratará erros.
                    if self._execute_safely(provider_manager.add_provider, provider_name, provider_data):
                        self._show_message("Sucesso", "Descrição atualizada.")
            elif selected == 1:
                # Editar URL da API
                current = provider.get('api_url', '')
                api_url = self._get_text_input("URL da API", f"Digite a nova URL da API:", current)
                if api_url is not None:
                    provider_data = provider.copy()
                    provider_data['api_url'] = api_url
                    if self._execute_safely(provider_manager.add_provider, provider_name, provider_data):
                        self._show_message("Sucesso", "URL da API atualizada.")
            elif selected == 2:
                # Alterar chave de API
                api_key = self._get_password_input("Chave de API", f"Digite a nova Chave de API para '{provider_name}' (deixe em branco para remover):")
                if api_key is not None: # Checa se o usuário não cancelou a entrada
                    if api_key.strip() == "":
                        if self._execute_safely(provider_manager.delete_api_key, provider_name):
                            self._show_message("Sucesso", "Chave de API removida.")
                    else:
                        provider_data = provider.copy()
                        provider_data['api_key'] = api_key # add_provider lida com storing da key
                        if self._execute_safely(provider_manager.add_provider, provider_name, provider_data):
                            self._show_message("Sucesso", "Chave de API atualizada.")
            elif selected == 3:
                # Gerenciar modelos do provedor
                self._manage_provider_models(provider_manager, provider_name)
            elif selected == 4:
                return
    
    def _manage_provider_models(self, provider_manager, provider_name):
        """Permite ao usuário adicionar ou remover modelos de um provedor específico."""
        while True:
            current_provider_details = self._execute_safely(provider_manager.get_provider, provider_name)
            if not current_provider_details:
                return
            
            models = current_provider_details.get('models', [])
            options = ["Adicionar modelo", "Remover modelo", "Voltar"]
            choice_title = f"Modelos para '{provider_name}': {models if models else 'Nenhum'}"
            choice_prompt = "Escolha uma ação:"
            
            choice = self._select_option_dialog(choice_title, choice_prompt, options)

            if choice == "Adicionar modelo":
                model = self._get_text_input("Adicionar Modelo", f"Digite o nome do modelo para adicionar a '{provider_name}':")
                if model is not None and model.strip() != "":
                    if self._execute_safely(provider_manager.add_provider_model, provider_name, model):
                        self._show_message("Sucesso", f"Modelo '{model}' adicionado.")
            elif choice == "Remover modelo":
                if not models:
                    self._show_message("Aviso", "Nenhum modelo para remover.")
                    continue
                model_choice_idx = self._select_option_dialog("Remover Modelo", "Selecione o modelo para remover:", models)
                if model_choice_idx is not None:
                    model_to_remove = models[model_choice_idx]
                    if self._get_confirmation(f"Remover o modelo '{model_to_remove}' de '{provider_name}'?"):
                        if self._execute_safely(provider_manager.delete_provider_model, provider_name, model_to_remove):
                            self._show_message("Sucesso", f"Modelo '{model_to_remove}' removido.")
            elif choice == "Voltar" or choice is None:
                break
    
    def _delete_provider(self, provider_manager):
        """Remove um provedor existente."""
        providers = provider_manager.get_providers()
        
        if not providers:
            self._show_message("Sem Provedores", "Não há provedores configurados.")
            return
        
        # Lista os provedores para seleção
        provider_names = list(providers.keys())
        provider_names.append("Cancelar")
        
        selected = self._show_menu("Remover Provedor", "Selecione um provedor para remover:", provider_names)
        
        if selected < len(provider_names) - 1:
            provider_name = provider_names[selected]
            # Confirma a exclusão
            confirm = self._get_confirmation(f"Tem certeza que deseja remover o provedor '{provider_name}'?")
            if confirm:
                self._execute_safely(provider_manager.delete_provider, provider_name)
    
    def _get_password_input(self, title, prompt):
        """Obtém entrada de senha (mascarada) do usuário."""
        self.screen.clear()
        
        # Desenha o título
        self._safe_addstr(0, 0, title.center(self.width - 1), curses.color_pair(2))
        
        # Desenha o prompt
        y = 2
        for line in prompt.split('\n'):
            self._safe_addstr(y, 2, line)
            y += 1
        
        # Desenha a área de entrada
        y += 1
        input_y = y
        input_x = 4
        input_width = self.width - 8
        self._safe_addstr(input_y, input_x - 2, "> ")
        
        # Desenha o rodapé
        self._safe_addstr(self.height-2, 0, "Pressione Enter para confirmar, Esc para cancelar".center(self.width - 1))
        
        # Configuração para entrada de senha
        curses.curs_set(1)
        curses.noecho()
        
        password = ""
        
        while True:
            # Desenha asteriscos para representar a senha
            self._safe_addstr(input_y, input_x, " " * input_width)
            self._safe_addstr(input_y, input_x, "*" * len(password))
            
            # Posiciona o cursor
            try:
                self.screen.move(input_y, input_x + len(password))
            except curses.error:
                pass
            
            self.screen.refresh()
            
            # Obtém a próxima tecla
            key = self.screen.getch()
            
            if key == 27:  # ESC
                curses.curs_set(0)
                return None
            elif key == curses.KEY_ENTER or key in [10, 13]:  # Enter
                curses.curs_set(0)
                return password
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:  # Backspace
                if password:
                    password = password[:-1]
            elif 32 <= key <= 126:  # Caracteres ASCII imprimíveis
                password += chr(key)
    
    def _get_confirmation(self, message):
        """Obtém confirmação sim/não do usuário."""
        options = ["Sim", "Não"]
        selected = self._show_menu("Confirmação", message, options)
        return selected == 0
    
    def _show_scrollable_list(self, title, prompt, items):
        """Mostra uma lista com rolagem quando há muitos itens."""
        if not items:
            self._show_message(title, "Nenhum item para exibir.")
            return
        
        self.screen.clear()
        
        # Desenha o título
        self._safe_addstr(0, 0, title.center(self.width - 1), curses.color_pair(2))
        
        # Calcula área visível
        max_visible_items = self.height - 6  # Espaço para título, prompt e rodapé
        start_idx = 0
        
        while True:
            self.screen.clear()
            
            # Redesenha o título e o prompt
            self._safe_addstr(0, 0, title.center(self.width - 1), curses.color_pair(2))
            self._safe_addstr(2, 2, prompt)
            
            # Desenha os itens visíveis
            for i in range(start_idx, min(start_idx + max_visible_items, len(items))):
                item = items[i]
                self._safe_addstr(4 + i - start_idx, 2, item)
            
            # Indicadores de rolagem
            if start_idx > 0:
                self._safe_addstr(3, self.width - 3, "↑")
            if start_idx + max_visible_items < len(items):
                bottom_row = min(self.height - 3, 4 + min(max_visible_items, len(items) - start_idx) - 1)
                self._safe_addstr(bottom_row, self.width - 3, "↓")
            
            # Rodapé
            self._safe_addstr(self.height-2, 0, "Use as setas ↑↓ para rolar, qualquer outra tecla para voltar".center(self.width - 1))
            
            self.screen.refresh()
            
            # Processa teclas
            key = self.screen.getch()
            
            if key == curses.KEY_UP and start_idx > 0:
                start_idx -= 1
            elif key == curses.KEY_DOWN and start_idx + max_visible_items < len(items):
                start_idx += 1
            else:
                break
    
    def display_endpoint_management(self):
        """Exibe a tela de gerenciamento de endpoints."""
        if not self.config_manager:
            self._show_message("Erro", "ConfigManager não inicializado.")
            self.display_main_menu()
            return
        
        menu_items = [
            "Ver Endpoints",
            "Adicionar Endpoint",
            "Editar Endpoint",
            "Remover Endpoint",
            "Voltar ao Menu Principal"
        ]
        
        while True:
            selected = self._show_menu("Gerenciamento de Endpoints", "Selecione uma opção:", menu_items)
            
            if selected == 0:
                self._show_endpoints()
            elif selected == 1:
                self._add_endpoint()
            elif selected == 2:
                self._edit_endpoint()
            elif selected == 3:
                self._delete_endpoint()
            elif selected == 4:
                self.display_main_menu()
                return
    
    def _show_endpoints(self):
        """Mostra todos os endpoints configurados."""
        endpoints = self.config_manager.get_endpoints()
        
        if not endpoints:
            self._show_message("Sem Endpoints", "Não há endpoints personalizados configurados.")
            return
        
        # Formata informações dos endpoints
        endpoint_info = []
        for name, data in endpoints.items():
            description = data.get('description', 'Sem descrição')
            api_url = data.get('api_url', 'URL não definida')
            models = ", ".join(data.get('models', ['Nenhum modelo']))
            
            endpoint_info.append(f"{name}")
            endpoint_info.append(f"  Descrição: {description}")
            endpoint_info.append(f"  URL da API: {api_url}")
            endpoint_info.append(f"  Modelos: {models}")
            endpoint_info.append("")
        
        self._show_scrollable_list("Endpoints Configurados", "Lista de endpoints personalizados:", endpoint_info)
    
    def _add_endpoint(self):
        """Adiciona um novo endpoint personalizado."""
        # Obtém nome do endpoint
        name = self._get_text_input("Adicionar Endpoint", "Digite o nome do endpoint personalizado:")
        if not name:
            return
        
        # Verifica se já existe um endpoint com esse nome
        if self.config_manager.get_endpoint(name):
            self._show_message("Endpoint Existente", f"Já existe um endpoint com o nome '{name}'.")
            return
        
        # Obtém descrição
        description = self._get_text_input("Descrição", f"Digite uma descrição para o endpoint '{name}':")
        if description is None:  # Usuário cancelou
            return
        
        # Obtém URL da API
        api_url = self._get_text_input("URL da API", 
                                      f"Digite a URL base da API para '{name}':", 
                                      "https://api.exemplo.com/v1")
        if api_url is None:  # Usuário cancelou
            return
        
        # Obtém API key
        api_key = self._get_password_input("Chave de API", f"Digite a chave de API para '{name}' (opcional):")
        # Nota: api_key pode ser None, o que é válido (endpoint sem autenticação)
        
        # Obtém modelos iniciais
        models_str = self._get_text_input("Modelos", "Digite uma lista de modelos separados por vírgula (opcional):")
        models = [m.strip() for m in models_str.split(',')] if models_str else []
        
        # Adiciona o endpoint
        endpoint_data = {
            'description': description,
            'api_url': api_url,
            'models': models
        }
        
        # Adiciona api_key apenas se foi fornecida
        if api_key:
            endpoint_data['api_key'] = api_key
        
        # Agora, tentar adicionar o endpoint usando _execute_safely
        # que já trata erros de validação e outros.
        success_add = self._execute_safely(self.config_manager.add_endpoint, name, endpoint_data)

        if success_add is not None: # _execute_safely retorna None em caso de erro já tratado
            # Se a chave API foi fornecida, armazená-la
            if api_key:
                # Usar _execute_safely também para store_api_key para consistência no tratamento de erros
                self._execute_safely(self.config_manager.store_api_key, f"endpoint_{name}", api_key)
            
            # Mostrar mensagem de sucesso APÓS todas as operações críticas
            self._show_message("Sucesso", f"Endpoint '{name}' adicionado com sucesso.")
        
        # Retornar para o menu de gerenciamento de endpoints independentemente de pequenos erros no keyring
        # desde que a adição principal tenha ocorrido ou um erro tenha sido mostrado por _execute_safely.
        self.display_endpoint_management()

    def _edit_endpoint(self):
        """Edita um endpoint existente."""
        endpoints = self.config_manager.get_endpoints()
        
        if not endpoints:
            self._show_message("Sem Endpoints", "Não há endpoints personalizados configurados.")
            return
        
        # Lista os endpoints para seleção
        endpoint_names = list(endpoints.keys())
        endpoint_names.append("Cancelar")
        
        selected = self._show_menu("Editar Endpoint", "Selecione um endpoint para editar:", endpoint_names)
        
        if selected < len(endpoint_names) - 1:
            endpoint_name = endpoint_names[selected]
            self._edit_endpoint_details(endpoint_name)
    
    def _edit_endpoint_details(self, endpoint_name):
        """Edita detalhes de um endpoint específico."""
        endpoint = self.config_manager.get_endpoint(endpoint_name)
        
        if not endpoint:
            self._show_message("Erro", f"Endpoint '{endpoint_name}' não encontrado.")
            return
        
        menu_items = [
            "Editar Descrição",
            "Editar URL da API",
            "Alterar Chave de API",
            "Gerenciar Modelos",
            "Voltar"
        ]
        
        while True:
            selected = self._show_menu(f"Editando {endpoint_name}", "Selecione uma opção:", menu_items)
            
            if selected == 0:
                # Editar descrição
                current = endpoint.get('description', '')
                description = self._get_text_input("Descrição", f"Digite a nova descrição:", current)
                if description is not None:
                    endpoint_data = endpoint.copy()
                    endpoint_data['description'] = description
                    self._execute_safely(self.config_manager.add_endpoint, endpoint_name, endpoint_data)
            elif selected == 1:
                # Editar URL da API
                current = endpoint.get('api_url', '')
                api_url = self._get_text_input("URL da API", f"Digite a nova URL da API:", current)
                if api_url is not None:
                    endpoint_data = endpoint.copy()
                    endpoint_data['api_url'] = api_url
                    self._execute_safely(self.config_manager.add_endpoint, endpoint_name, endpoint_data)
            elif selected == 2:
                # Alterar chave de API
                api_key = self._get_password_input("Chave de API", f"Digite a nova chave de API para '{endpoint_name}' (deixe em branco para remover):")
                if api_key is not None:
                    try:
                        # Se a chave for vazia, remover a chave existente
                        if api_key.strip() == "":
                            self._execute_safely(self.config_manager.delete_api_key, f"endpoint_{endpoint_name}")
                        else:
                            endpoint_data = endpoint.copy()
                            endpoint_data['api_key'] = api_key
                            self._execute_safely(self.config_manager.add_endpoint, endpoint_name, endpoint_data)
                    except Exception as e:
                        self._show_message("Erro", f"Não foi possível atualizar a chave de API: {str(e)}")
            elif selected == 3:
                # Gerenciar modelos
                self._manage_endpoint_models(endpoint_name)
            elif selected == 4:
                return
    
    def _manage_endpoint_models(self, endpoint_name):
        """Gerencia modelos de um endpoint."""
        menu_items = [
            "Ver Modelos",
            "Adicionar Modelo",
            "Remover Modelo",
            "Voltar"
        ]
        
        while True:
            selected = self._show_menu(f"Modelos de {endpoint_name}", "Selecione uma opção:", menu_items)
            
            if selected == 0:
                # Ver modelos
                try:
                    models = self.config_manager.get_endpoint_models(endpoint_name)
                    if not models:
                        self._show_message("Sem Modelos", f"Não há modelos configurados para '{endpoint_name}'.")
                    else:
                        self._show_scrollable_list("Modelos", f"Modelos disponíveis para '{endpoint_name}':", models)
                except Exception as e:
                    self._show_message("Erro", f"Não foi possível obter os modelos: {str(e)}")
            elif selected == 1:
                # Adicionar modelo
                model = self._get_text_input("Adicionar Modelo", f"Digite o nome do modelo para adicionar a '{endpoint_name}':")
                if model is not None:
                    self._execute_safely(self.config_manager.add_endpoint_model, endpoint_name, model)
            elif selected == 2:
                # Remover modelo
                self._remove_endpoint_model(endpoint_name)
            elif selected == 3:
                return
    
    def _remove_endpoint_model(self, endpoint_name):
        """Remove um modelo de um endpoint."""
        try:
            models = self.config_manager.get_endpoint_models(endpoint_name)
            
            if not models:
                self._show_message("Sem Modelos", f"Não há modelos configurados para '{endpoint_name}'.")
                return
            
            # Adiciona opção para cancelar
            menu_items = models.copy()
            menu_items.append("Cancelar")
            
            selected = self._show_menu("Remover Modelo", f"Selecione o modelo que deseja remover de '{endpoint_name}':", menu_items)
            
            if selected < len(models):
                model = models[selected]
                try:
                    self.config_manager.remove_endpoint_model(endpoint_name, model)
                    self._show_message("Sucesso", f"Modelo '{model}' removido.")
                except Exception as e:
                    self._show_message("Erro", f"Não foi possível remover o modelo: {str(e)}")
        except Exception as e:
            self._show_message("Erro", f"Não foi possível listar os modelos: {str(e)}")
    
    def _delete_endpoint(self):
        """Remove um endpoint existente."""
        endpoints = self.config_manager.get_endpoints()
        
        if not endpoints:
            self._show_message("Sem Endpoints", "Não há endpoints personalizados configurados.")
            return
        
        # Lista os endpoints para seleção
        endpoint_names = list(endpoints.keys())
        endpoint_names.append("Cancelar")
        
        selected = self._show_menu("Remover Endpoint", "Selecione um endpoint para remover:", endpoint_names)
        
        if selected < len(endpoint_names) - 1:
            endpoint_name = endpoint_names[selected]
            # Confirma a exclusão
            confirm = self._get_confirmation(f"Tem certeza que deseja remover o endpoint '{endpoint_name}'?")
            if confirm:
                # Tentar remover o endpoint usando _execute_safely
                success_delete = self._execute_safely(self.config_manager.delete_endpoint, endpoint_name) # Corrigido para endpoint_name
                
                if success_delete is not None: # _execute_safely retorna None em caso de erro já tratado
                    # Adicionar mensagem de sucesso aqui
                    self._show_message("Sucesso", f"Endpoint '{endpoint_name}' removido com sucesso.") # Corrigido para endpoint_name
        
        # Retornar para o menu de gerenciamento de endpoints independentemente do resultado da deleção,
        # pois _execute_safely já terá mostrado qualquer erro.
        self.display_endpoint_management()

    def _show_message(self, title: str, message: str):
        """Exibe uma mensagem na tela."""
        self.screen.clear()
        
        # Desenha o título
        title_text = title.center(self.width - 1)
        self._safe_addstr(0, 0, title_text, curses.color_pair(2))
        
        # Desenha a mensagem
        lines = message.split('\n')
        for i, line in enumerate(lines):
            self._safe_addstr(i + 2, 2, line)
        
        # Desenha o rodapé
        footer = "Pressione qualquer tecla para continuar..."
        footer_text = footer.center(self.width - 1)
        self._safe_addstr(self.height-2, 0, footer_text)
        
        self.screen.refresh()
        self.screen.getch()  # Aguarda uma tecla 

    def _manage_providers(self, config_manager):
        """Gerencia provedores de API."""
        provider_manager = config_manager # Usar o config_manager diretamente

        options = ["Adicionar Novo Provedor", "Editar Provedor Existente", "Remover Provedor Existente", "Voltar"]
        choice = self._select_option_dialog("Gerenciar Provedores", "Escolha uma ação:", options)

        if choice == "Adicionar Novo Provedor":
            self._add_provider(provider_manager) 
        elif choice == "Editar Provedor Existente":
            self._edit_provider(provider_manager) 
        elif choice == "Remover Provedor Existente":
            self._delete_provider_interactive(provider_manager) # Esta função usará _execute_safely
        
        self.display_main_menu() 

    def _delete_provider_interactive(self, provider_manager):
        """Permite ao usuário selecionar e remover um provedor existente de forma interativa."""
        providers = self._execute_safely(provider_manager.get_providers)
        
        if providers is None: 
            return 
        if not providers: 
            self._show_message("Aviso", "Nenhum provedor configurado para remover.")
            return

        provider_names = list(providers.keys())
        # Adicionando opção de cancelar explicitamente para clareza
        menu_items = provider_names + ["Cancelar"]
        selected_idx = self._show_menu("Remover Provedor", "Selecione o provedor para remover:", menu_items)

        if selected_idx is not None and selected_idx < len(provider_names): # Certifica que não é "Cancelar"
            provider_name_to_delete = provider_names[selected_idx]
            if self._get_confirmation(f"Tem certeza que deseja remover o provedor '{provider_name_to_delete}'?"):
                if self._execute_safely(provider_manager.delete_provider, provider_name_to_delete):
                    self._show_message("Sucesso", f"Provedor '{provider_name_to_delete}' removido.")

    def _select_option_dialog(self, title, prompt, options):
        """
        Exibe um diálogo de seleção de opções e retorna a opção selecionada como string.
        
        Args:
            title: Título do diálogo
            prompt: Descrição explicativa
            options: Lista de opções a serem exibidas
            
        Returns:
            A string da opção selecionada ou None se cancelado
        """
        selected_idx = self._show_menu(title, prompt, options)
        
        if selected_idx is not None and 0 <= selected_idx < len(options):
            return options[selected_idx]
        return None
