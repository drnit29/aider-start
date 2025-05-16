import sqlite3
import time
from typing import Optional, Tuple, List, Any, Callable
from prompt_toolkit import Application
from prompt_toolkit.application.current import get_app  # Added get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    Window,
    HSplit,
    VSplit,
    ConditionalContainer,
    FloatContainer,
    Float,
)
from prompt_toolkit.layout.scrollable_pane import ScrollOffsets  # Added ScrollOffsets
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.shortcuts import message_dialog, yes_no_dialog
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.widgets import TextArea, Label, Button, Dialog, Frame
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.dimension import Dimension

from .style import default_style, COLORS
from .preset_list_filter import update_filtered_list, get_formatted_presets_text
from .preset_list_keybindings import make_preset_list_keybindings
from .preset_list_ui import (
    make_header,
    make_status_bar,
    make_filter_bar_section,
    make_conditional_filter_bar,
    make_main_layout,
    create_bordered_container,
)

try:
    from ..db import database
    from ..db.models import Preset
except ImportError:
    database = None
    Preset = None


def display_preset_list_screen(
    conn: sqlite3.Connection,
) -> Optional[Tuple[str, Optional[int]]]:
    """
    Displays a TUI screen to list available presets and allows selection or other actions.
    Returns a tuple: (action_string, optional_preset_id), e.g., ("select", 1), ("create", None), ("edit", 2)
    """
    if not database:
        message_dialog(
            title="Erro",
            text="Módulo de banco de dados não carregado. Não é possível exibir presets.",
            style=default_style,
        ).run()
        return None, None

    # Fetch presets from database
    all_presets_db: List[Preset] = database.list_presets(conn)
    CREATE_NEW_PRESET_MARKER = "[+] Criar Novo Preset"

    # Original lists for filtering
    original_display_items = [p.name for p in all_presets_db] + [
        CREATE_NEW_PRESET_MARKER
    ]
    original_descriptions = [p.description for p in all_presets_db] + [
        "Crie um novo preset de configuração personalizado."
    ]

    # Combined list of Preset objects + marker
    original_presets_plus_marker_obj: List[Any] = all_presets_db + [
        Preset(
            id=None,
            name=CREATE_NEW_PRESET_MARKER,
            description="Crie um novo preset de configuração personalizado.",
        )
    ]

    # Filtered lists (initially same as originals)
    filtered_display_items = list(original_display_items)
    filtered_descriptions = list(original_descriptions)
    filtered_presets_plus_marker_obj = list(original_presets_plus_marker_obj)

    selected_index_ref = [0]  # Use list for mutability
    app_ref = {"app": None}

    # Status message state
    status_message_state = {
        "message": None,
        "timestamp": 0,
        "duration": 0,
    }

    # Filter visibility state
    filter_active_state = [False]  # Use a list for mutable closure capture
    show_filter_bar_condition = Condition(lambda: filter_active_state[0])

    # Text filter field
    filter_text_area = TextArea(
        # prompt="🔍 Filtrar: ", # Original prompt string, replaced by dynamic one
        prompt=lambda: FormattedText(
            [
                (
                    (
                        "class:filter-bar.prompt.focused"
                        if get_app().layout.has_focus(filter_text_area)
                        else "class:filter-bar.prompt"
                    ),
                    "🔍 Filtrar: ",
                )
            ]
        ),
        multiline=False,
        height=1,
        style="class:filter-bar",  # Ensure 'filter-bar' style is defined in style.py
    )

    def _on_filter_text_changed(buff: Optional[Any] = None):
        """Update filtered lists when filter text changes"""
        update_filtered_list(
            filter_text_area,
            original_display_items,
            original_descriptions,
            original_presets_plus_marker_obj,
            CREATE_NEW_PRESET_MARKER,
            filtered_display_items,
            filtered_descriptions,
            filtered_presets_plus_marker_obj,
            selected_index_ref,
            app_ref,
        )

    filter_text_area.buffer.on_text_changed += _on_filter_text_changed

    def _get_formatted_presets_text() -> FormattedText:
        """Get formatted text for the preset list"""
        return get_formatted_presets_text(
            filtered_display_items,
            filtered_descriptions,
            filtered_presets_plus_marker_obj,
            selected_index_ref[0],
            filter_text_area,
            CREATE_NEW_PRESET_MARKER,
        )

    # List body control (focusable)
    list_body_control = FormattedTextControl(
        _get_formatted_presets_text, focusable=True
    )

    # Create a scrollable body with proper styling
    def get_body_style():
        try:
            if get_app().layout.has_focus(list_body_control):
                return "class:list-body.focused"
        except Exception:  # get_app() might fail if called too early or app not running
            pass
        return "class:list-body"

    body = Window(
        list_body_control,
        wrap_lines=False,
        allow_scroll_beyond_bottom=True,
        scroll_offsets=ScrollOffsets(top=1, bottom=1, left=0, right=0),
        style=get_body_style,  # Dynamic style based on focus
    )

    # Status message display
    def get_status_message() -> FormattedText:
        """Get the current status message if active"""
        if (
            status_message_state["message"]
            and time.time() - status_message_state["timestamp"]
            < status_message_state["duration"]
        ):
            return FormattedText(
                [("class:status", f" {status_message_state['message']} ")]
            )
        return FormattedText([])

    status_message_control = FormattedTextControl(get_status_message)
    status_message_window = ConditionalContainer(
        Window(status_message_control, height=1),
        filter=Condition(
            lambda: status_message_state["message"] is not None
            and time.time() - status_message_state["timestamp"]
            < status_message_state["duration"]
        ),
    )

    # Function to show status messages
    def show_status_message(message: str, duration: float = 1.0):
        """Display a temporary status message"""
        status_message_state["message"] = message
        status_message_state["timestamp"] = time.time()
        status_message_state["duration"] = duration
        if app_ref.get("app"):
            app_ref["app"].invalidate()

    # Global key bindings
    kb_global = make_preset_list_keybindings(
        filter_text_area=filter_text_area,
        list_body_control=list_body_control,
        filtered_display_items=filtered_display_items,
        filtered_presets_plus_marker_obj=filtered_presets_plus_marker_obj,
        selected_index_ref=selected_index_ref,
        app_ref=app_ref,
        CREATE_NEW_PRESET_MARKER=CREATE_NEW_PRESET_MARKER,
        filter_active_state=filter_active_state,
    )

    # Title and status bar text
    title_text = FormattedText(
        [("class:title", " Aider-Start: Selecione um Preset ou Ação ")]
    )

    status_formatted_text = FormattedText(
        [
            ("class:status", " "),
            ("class:key", "Up/Down"),
            ("class:status", ":Nav "),
            ("class:key", "Enter"),
            ("class:status", ":Sel "),
            ("class:key", "C"),
            ("class:status", ":Criar "),
            ("class:key", "E"),
            ("class:status", ":Editar "),
            ("class:key", "D"),
            ("class:status", ":Excluir "),
            ("class:key", "A"),
            ("class:status", ":Adv "),
            ("class:key", "Ctrl+F"),
            ("class:status", ":Filtrar "),
            ("class:key", "Ctrl+G"),  # Added
            ("class:status", ":CfgWiz "),  # Added
            ("class:key", "Esc"),
            ("class:status", ":Sair/Canc "),
            ("class:status", " "),
        ]
    )

    # Create UI components
    header = make_header(title_text)
    status_bar = make_status_bar(status_formatted_text)
    filter_bar_section = make_filter_bar_section(filter_text_area)
    conditional_filter_bar = make_conditional_filter_bar(
        filter_bar_section, show_filter_bar_condition
    )

    # Create main layout with status message
    main_container = make_main_layout(header, conditional_filter_bar, body, status_bar)

    # Add floating status message
    root_container = FloatContainer(
        content=main_container,
        floats=[
            Float(
                content=Window(
                    content=status_message_control,
                    height=1,
                    style="class:status",
                    width=40,
                ),
                bottom=0,  # Changed from top=1
                right=1,
                transparent=False,  # transparent=False can sometimes help with layout calculations too
            )
        ],
    )

    # Create layout and application
    layout = Layout(root_container)
    application = Application(
        layout=layout,
        key_bindings=kb_global,
        full_screen=True,
        style=default_style,
        mouse_support=True,
    )

    # Store application reference and add status message function
    app_ref["app"] = application
    application.show_message = show_status_message

    # Set initial focus to the list body if the filter is not active
    if not filter_active_state[0]:  # Should be true on initial launch
        application.layout.focus(list_body_control)

    # Run the application
    return application.run()
