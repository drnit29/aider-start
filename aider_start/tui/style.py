
"""
Comprehensive style system for Aider-Start TUI.
Provides color palettes, style functions, and theme management.
This file acts as a façade for backward compatibility, reexporting the style API.
"""

from .tui.style.colors import COLORS, COLOR_STATES, BASIC_COLORS
from .tui.style.symbols import SYMBOLS, ASCII_SYMBOLS, get_symbol
from .tui.style.functions import (
    get_button_style,
    get_input_style,
    get_list_item_style,
    get_label_style,
)
from .tui.style.themes import default_style, THEMES, get_theme
