"""
Theme definitions and management for Aider-Start TUI.
Supports multiple themes and terminal compatibility detection.
"""

from prompt_toolkit.styles import Style
from .style import COLORS, COLOR_STATES, BASIC_COLORS


def create_theme(colors, name="custom"):
    """
    Create a custom theme based on provided color dictionary

    Args:
        colors (dict): Dictionary of color values
        name (str): Theme name

    Returns:
        dict: Theme configuration dictionary
    """
    return {
        "name": name,
        "colors": colors,
        "style": create_style_from_colors(colors),
    }


def create_style_from_colors(colors):
    """
    Create a prompt_toolkit Style from a color dictionary

    Args:
        colors (dict): Dictionary of color values

    Returns:
        Style: prompt_toolkit Style object
    """
    # Merge with default colors for any missing values
    merged_colors = {**COLORS, **colors}

    # Generate state variations if not provided
    if "accent_primary_hover" not in merged_colors:
        # Check if colors are in hex format
        if is_hex_color(merged_colors["accent_primary"]):
            # Simple algorithm to create lighter versions for hover state
            merged_colors["accent_primary_hover"] = lighten_color(
                merged_colors["accent_primary"], 0.1
            )
            merged_colors["accent_secondary_hover"] = lighten_color(
                merged_colors["accent_secondary"], 0.1
            )
            merged_colors["accent_tertiary_hover"] = lighten_color(
                merged_colors["accent_tertiary"], 0.1
            )
        else:
            # For named colors, just use the same color for variations
            merged_colors["accent_primary_hover"] = merged_colors["accent_primary"]
            merged_colors["accent_secondary_hover"] = merged_colors["accent_secondary"]
            merged_colors["accent_tertiary_hover"] = merged_colors["accent_tertiary"]

    if "accent_primary_active" not in merged_colors:
        if is_hex_color(merged_colors["accent_primary"]):
            # Simple algorithm to create darker versions for active state
            merged_colors["accent_primary_active"] = darken_color(
                merged_colors["accent_primary"], 0.1
            )
            merged_colors["accent_secondary_active"] = darken_color(
                merged_colors["accent_secondary"], 0.1
            )
            merged_colors["accent_tertiary_active"] = darken_color(
                merged_colors["accent_tertiary"], 0.1
            )
        else:
            # For named colors, just use the same color for variations
            merged_colors["accent_primary_active"] = merged_colors["accent_primary"]
            merged_colors["accent_secondary_active"] = merged_colors["accent_secondary"]
            merged_colors["accent_tertiary_active"] = merged_colors["accent_tertiary"]

    # Create style dictionary (simplified version - full styling in style.py)
    style_dict = {
        # Base UI elements
        "title": f"bold {merged_colors['accent_primary']}",
        "status": f"bg:{merged_colors['bg_component']} {merged_colors['text_primary']}",
        "selected": f"bg:{merged_colors['accent_primary']} {merged_colors['text_primary']} bold",
        "description": f"{merged_colors['text_secondary']}",
        "key": f"bold {merged_colors['accent_secondary']}",
        # Basic component styles
        "button": f"bg:{merged_colors['accent_primary']} {merged_colors['text_primary']}",
        "button.focused": f"bg:{merged_colors['accent_primary_hover']} {merged_colors['text_primary']} bold",
        "text-area": f"bg:{merged_colors['bg_component']} {merged_colors['text_primary']}",
        # List styles
        "list-item.selected": f"bg:{merged_colors['accent_primary']} {merged_colors['text_primary']}",
        "list-item.focused": f"bg:{merged_colors['bg_highlight']} {merged_colors['text_primary']}",
        # Form styles
        "checkbox.checked": f"{merged_colors['success']} bold",
        "radio.selected": f"{merged_colors['success']} bold",
        # Additional elements
        "search-match": f"bg:{merged_colors['warning']} {merged_colors['bg_primary']} bold",
        "notification.error": f"bg:{merged_colors['error']} {merged_colors['bg_primary']} bold",
        "notification.success": f"bg:{merged_colors['success']} {merged_colors['bg_primary']} bold",
    }

    return Style.from_dict(style_dict)


def is_hex_color(color):
    """Check if a color string is in hex format (#RRGGBB)"""
    if not isinstance(color, str):
        return False
    if not color.startswith("#"):
        return False
    if len(color) != 7:  # #RRGGBB format has 7 characters
        return False
    try:
        # Check if the hex part is valid
        int(color[1:], 16)
        return True
    except ValueError:
        return False


def hex_to_rgb(hex_color):
    """Convert hex color (#RRGGBB) to RGB tuple"""
    if not is_hex_color(hex_color):
        # Return a default color for non-hex values
        return (128, 128, 128)  # Gray as fallback

    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color (#RRGGBB)"""
    r, g, b = rgb
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return f"#{r:02x}{g:02x}{b:02x}"


def lighten_color(hex_color, amount=0.1):
    """
    Lighten a color by a certain amount

    Args:
        hex_color (str): Color in hex format (#RRGGBB)
        amount (float): Amount to lighten (0-1)

    Returns:
        str: Lightened color in hex format
    """
    if not is_hex_color(hex_color):
        return hex_color  # Return original if not hex

    r, g, b = hex_to_rgb(hex_color)
    r = r + (255 - r) * amount
    g = g + (255 - g) * amount
    b = b + (255 - b) * amount
    return rgb_to_hex((r, g, b))


def darken_color(hex_color, amount=0.1):
    """
    Darken a color by a certain amount

    Args:
        hex_color (str): Color in hex format (#RRGGBB)
        amount (float): Amount to darken (0-1)

    Returns:
        str: Darkened color in hex format
    """
    if not is_hex_color(hex_color):
        return hex_color  # Return original if not hex

    r, g, b = hex_to_rgb(hex_color)
    r = r * (1 - amount)
    g = g * (1 - amount)
    b = b * (1 - amount)
    return rgb_to_hex((r, g, b))


# Convert basic named colors to hex for better compatibility
BASIC_COLORS_HEX = {
    "bg_primary": "#000000",  # black
    "bg_secondary": "#111111",  # dark gray
    "bg_component": "#000033",  # darkblue
    "bg_highlight": "#000066",  # blue
    "accent_primary": "#cc00cc",  # magenta
    "accent_secondary": "#ff00ff",  # bright magenta
    "accent_tertiary": "#aa00aa",  # dark magenta
    "success": "#00cc00",  # green
    "warning": "#cccc00",  # yellow
    "error": "#cc0000",  # red
    "info": "#00cccc",  # cyan
    "text_primary": "#ffffff",  # white
    "text_secondary": "#aaaaaa",  # gray
    "text_muted": "#666666",  # darkgray
}

# Predefined themes
DEFAULT_THEME = create_theme(COLORS, "default")

# Purple theme based on the default colors in DESIGN.md
PURPLE_THEME = create_theme(
    {
        "bg_primary": "#121212",
        "bg_secondary": "#1e1e2e",
        "bg_component": "#2a2a40",
        "bg_highlight": "#3a3a5a",
        "accent_primary": "#9d7cd8",
        "accent_secondary": "#c7a0f1",
        "accent_tertiary": "#a162de",
        "success": "#a2e1a2",
        "warning": "#f0c38e",
        "error": "#f07178",
        "info": "#89ddff",
        "text_primary": "#f8f8f2",
        "text_secondary": "#c0c0cc",
        "text_muted": "#727288",
    },
    "purple",
)

# Blue theme based on a softer blue palette
BLUE_THEME = create_theme(
    {
        "bg_primary": "#0d1117",
        "bg_secondary": "#161b22",
        "bg_component": "#21262d",
        "bg_highlight": "#30363d",
        "accent_primary": "#58a6ff",
        "accent_secondary": "#79c0ff",
        "accent_tertiary": "#388bfd",
        "success": "#56d364",
        "warning": "#e3b341",
        "error": "#f85149",
        "info": "#79c0ff",
        "text_primary": "#f0f6fc",
        "text_secondary": "#c9d1d9",
        "text_muted": "#8b949e",
    },
    "blue",
)

# High contrast theme for accessibility
HIGH_CONTRAST_THEME = create_theme(
    {
        "bg_primary": "#000000",
        "bg_secondary": "#121212",
        "bg_component": "#1a1a1a",
        "bg_highlight": "#2c2c2c",
        "accent_primary": "#ffcc00",
        "accent_secondary": "#ffdd55",
        "accent_tertiary": "#ffd700",
        "success": "#00ff00",
        "warning": "#ffcc00",
        "error": "#ff0000",
        "info": "#00ccff",
        "text_primary": "#ffffff",
        "text_secondary": "#e0e0e0",
        "text_muted": "#a0a0a0",
    },
    "high_contrast",
)

# Terminal-friendly theme for basic terminals
BASIC_TERMINAL_THEME = create_theme(BASIC_COLORS_HEX, "basic_terminal")

# All available themes
AVAILABLE_THEMES = {
    "default": DEFAULT_THEME,
    "purple": PURPLE_THEME,
    "blue": BLUE_THEME,
    "high_contrast": HIGH_CONTRAST_THEME,
    "basic_terminal": BASIC_TERMINAL_THEME,
}


def get_theme(name="default"):
    """Get a theme by name"""
    return AVAILABLE_THEMES.get(name, DEFAULT_THEME)


def get_all_theme_names():
    """Get list of all available theme names"""
    return list(AVAILABLE_THEMES.keys())


def detect_terminal_color_support():
    """
    Detect the level of color support in the current terminal

    Returns:
        str: Theme name recommendation based on terminal capabilities
    """
    import os
    import shutil

    # Check if COLORTERM environment variable is set to truecolor or 24bit
    colorterm = os.environ.get("COLORTERM", "").lower()
    if "truecolor" in colorterm or "24bit" in colorterm:
        return "default"  # Full RGB color support

    # Check if terminal supports 256 colors
    if os.environ.get("TERM", "").endswith("-256color"):
        return "default"  # 256 color support should handle our themes

    # Check terminal size as a heuristic (larger terminals often have better support)
    try:
        width, height = shutil.get_terminal_size()
        if width >= 80 and height >= 24:
            return "default"  # Assume decent color support
    except (AttributeError, OSError):
        pass

    # Fall back to basic terminal theme
    return "basic_terminal"
