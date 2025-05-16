from prompt_toolkit.shortcuts import yes_no_dialog
from .style.themes import default_style


def display_command_preview_screen(command_string: str) -> bool:
    """
    Displays the constructed command and asks for user confirmation.
    Returns True to execute, False to cancel.
    Uses a simple yes_no_dialog for now.
    """
    text_lines = ["Execute the following command?", "", command_string]
    dialog_text = "\n".join(text_lines)

    result = yes_no_dialog(
        title="Command Preview", text=dialog_text, style=default_style
    ).run()

    return result if result is not None else False
