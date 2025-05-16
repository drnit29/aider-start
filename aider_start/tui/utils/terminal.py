"""
Terminal capability detection utilities for Aider-Start TUI.
"""

import os
import sys
import shutil


def get_terminal_size():
    """
    Get the current terminal size.

    Returns:
        tuple: (width, height) of the terminal
    """
    try:
        return shutil.get_terminal_size()
    except (AttributeError, OSError):
        # Fallback for environments where get_terminal_size is not available
        return (80, 24)


def supports_true_color():
    """
    Check if the terminal supports true color (24-bit color).

    Returns:
        bool: Whether the terminal supports true color
    """
    # Check if COLORTERM environment variable is set to truecolor or 24bit
    colorterm = os.environ.get("COLORTERM", "").lower()
    if "truecolor" in colorterm or "24bit" in colorterm:
        return True

    # Check specific terminals known to support true color
    term = os.environ.get("TERM", "").lower()
    if "truecolor" in term or "24bit" in term:
        return True

    # Some terminals support true color without advertising it
    if "kitty" in term or "iterm" in term:
        return True

    return False


def supports_256_color():
    """
    Check if the terminal supports 256 colors.

    Returns:
        bool: Whether the terminal supports 256 colors
    """
    term = os.environ.get("TERM", "").lower()
    if "-256color" in term or term == "xterm-256color":
        return True

    return False


def supports_unicode():
    """
    Check if the terminal supports Unicode characters.

    Returns:
        bool: Whether the terminal supports Unicode
    """
    # Check if the encoding supports Unicode
    encoding = sys.stdout.encoding or "ascii"
    if encoding.lower().startswith(("utf", "ucs")):
        return True

    # Check if the locale is set to a Unicode-compatible locale
    lang = os.environ.get("LANG", "").lower()
    if "utf" in lang:
        return True

    return False


def is_windows_terminal():
    """
    Check if running in a Windows terminal.

    Returns:
        bool: Whether running in a Windows terminal
    """
    return sys.platform.startswith("win")


def get_terminal_capabilities():
    """
    Get a dictionary of terminal capabilities.

    Returns:
        dict: Terminal capabilities
    """
    width, height = get_terminal_size()

    return {
        "width": width,
        "height": height,
        "true_color": supports_true_color(),
        "color_256": supports_256_color(),
        "unicode": supports_unicode(),
        "windows": is_windows_terminal(),
    }


def get_color_support_level():
    """
    Get the level of color support in the current terminal.

    Returns:
        str: "true_color", "256_color", "16_color", or "none"
    """
    if supports_true_color():
        return "true_color"
    elif supports_256_color():
        return "256_color"
    elif sys.stdout.isatty():
        return "16_color"
    else:
        return "none"
