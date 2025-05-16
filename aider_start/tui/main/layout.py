
"""
Layout and help dialog utilities for Aider-Start TUI.
"""

from prompt_toolkit.layout import Layout, Window, HSplit, FloatContainer, Float, FormattedTextControl
from prompt_toolkit.widgets import Frame, Box, Shadow
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.layout.dimension import D

from ..screens import PresetListScreen

def create_layout(app):
    """
    Create the application layout.

    Args:
        app (AiderStartTUI): The TUI app instance

    Returns:
        Container: The application layout container
    """
    # Set initial screen (preset list)
    app.preset_list_screen = PresetListScreen(
        [],
        on_select=app._on_preset_select,
        on_edit=app._on_preset_edit,
        on_delete=app._on_preset_delete,
        on_create=app._on_preset_create,
    )

    app.current_screen = app.preset_list_screen

    # Create float container for dialogs
    float_container = FloatContainer(content=app.current_screen, floats=[])

    # Add help dialog float when visible
    if app.show_help:
        float_container.floats.append(
            Float(content=app.help_dialog, top=5, left=10)
        )

    # Return the float container
    return float_container

def create_help_dialog(app):
    """
    Create the help dialog.

    Args:
        app (AiderStartTUI): The TUI app instance

    Returns:
        Container: The help dialog container
    """
    help_text = HSplit(
        [
            Window(
                FormattedTextControl(HTML("<b>Keyboard Shortcuts</b>")),
                height=D.exact(1),
                style="class:help.title",
            ),
            Window(height=D.exact(1)),  # Spacer
            Window(
                FormattedTextControl(
                    [
                        ("class:help.content", "F1 or ? - Show/hide this help\n"),
                        ("class:help.content", "F2 - Toggle theme\n"),
                        ("class:help.content", "Tab / Shift+Tab - Navigate between elements\n"),
                        ("class:help.content", "Arrow keys - Navigate within element\n"),
                        ("class:help.content", "Enter / Space - Activate selected item\n"),
                        ("class:help.content", "Escape - Close dialog / Go back\n"),
                        ("class:help.content", "Ctrl+C - Exit application\n"),
                        ("class:help.content", "\n"),
                        ("class:help.content.bold", "Preset List Screen\n"),
                        ("class:help.content", "c - Create new preset\n"),
                        ("class:help.content", "e - Edit selected preset\n"),
                        ("class:help.content", "d - Delete selected preset\n"),
                        ("class:help.content", "/ - Focus search filter\n"),
                    ]
                ),
                style="class:help.content",
            ),
            Window(height=D.exact(1)),  # Spacer
            Window(
                FormattedTextControl("Press Escape to close"),
                height=D.exact(1),
                style="class:help.footer",
            ),
        ]
    )

    help_box = Box(help_text, padding=1, style="class:help")

    help_frame = Frame(help_box, title="Aider-Start Help", style="class:help.frame")

    return Shadow(help_frame)
