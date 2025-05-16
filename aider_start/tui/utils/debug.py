"""
Debugging utilities for Aider-Start TUI.
"""

import sys
import traceback
import logging
from prompt_toolkit.application.current import get_app
from prompt_toolkit.formatted_text import HTML

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="aider_start_tui.log",
    filemode="w",
)

logger = logging.getLogger("aider_start.tui")


def log_exception(exc_type, exc_value, exc_traceback):
    """
    Log an exception and display error message.

    Args:
        exc_type: Exception type
        exc_value: Exception value
        exc_traceback: Exception traceback
    """
    # Log the exception
    logger.error("Exception occurred", exc_info=(exc_type, exc_value, exc_traceback))

    # Format traceback as string
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = "".join(tb_lines)

    # Try to display error message in application
    try:
        app = get_app()
        show_error_message(
            app,
            f"An error occurred: {exc_value}\n\nSee aider_start_tui.log for details.",
        )
    except Exception:
        # If showing error in app fails, print to stderr
        print(f"Error: {exc_value}", file=sys.stderr)
        print(f"Traceback:\n{tb_text}", file=sys.stderr)


def show_error_message(app, message):
    """
    Show error message in application.

    Args:
        app: Application instance
        message (str): Error message
    """
    from prompt_toolkit.layout import HSplit, Window, FormattedTextControl
    from prompt_toolkit.layout.dimension import D
    from prompt_toolkit.widgets import Frame, Box, Shadow
    from prompt_toolkit.layout import Float, FloatContainer

    # Create error dialog
    error_text = FormattedTextControl(
        HTML(f"<b>Error</b>\n\n{message}\n\nPress Escape to continue")
    )

    error_window = Window(
        error_text, style="class:error-dialog", dont_extend_height=True
    )

    error_box = Box(error_window, padding=1, style="class:error-dialog")

    error_frame = Frame(error_box, title="Error", style="class:error-dialog.frame")

    error_dialog = Shadow(error_frame)

    # Add to floats
    if isinstance(app.layout.container, FloatContainer):
        app.layout.container.floats.append(Float(content=error_dialog, top=5, left=10))

    # Force redraw
    app.invalidate()


def install_exception_handler():
    """Install global exception handler"""
    sys.excepthook = log_exception


def log_debug(message):
    """Log debug message"""
    logger.debug(message)


def log_info(message):
    """Log info message"""
    logger.info(message)


def log_warning(message):
    """Log warning message"""
    logger.warning(message)


def log_error(message):
    """Log error message"""
    logger.error(message)
