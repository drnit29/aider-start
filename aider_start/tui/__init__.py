"""
Terminal User Interface (TUI) package for Aider-Start.
Provides a modernized terminal interface for managing and running presets.
"""

from .main import run_tui, AiderStartTUI
from .style.themes import default_style
from .themes import get_theme, get_all_theme_names

__all__ = [
    "run_tui",
    "AiderStartTUI",
    "default_style",
    "get_theme",
    "get_all_theme_names",
]
