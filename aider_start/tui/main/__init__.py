
from .app import AiderStartTUI
from .layout import create_help_dialog, create_layout
from .keybindings import setup_global_key_bindings

def run_tui(config=None, presets=None):
    """
    Run the TUI application.

    Args:
        config (dict, optional): Application configuration
        presets (list, optional): List of presets

    Returns:
        Any: The result from the application
    """
    tui = AiderStartTUI(config)

    if presets:
        tui.set_presets(presets)

    return tui.run()

__all__ = [
    "AiderStartTUI",
    "create_help_dialog",
    "create_layout",
    "setup_global_key_bindings",
    "run_tui",
]
