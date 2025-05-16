
# symbols.py: Unicode and ASCII symbols for Aider-Start TUI.

SYMBOLS = {
    # Action icons
    "confirm": "✓",
    "cancel": "✗",
    "settings": "⚙",
    "up": "↑",
    "down": "↓",
    # Status icons
    "success": "✓",
    "warning": "⚠",
    "error": "✗",
    "info": "ℹ",
    # Navigation icons
    "back": "←",
    "forward": "→",
    "enter": "↵",
    # File/Item icons
    "file": "📄",
    "folder": "📁",
    "preset": "⚡",
    # Border elements
    "h_line": "─",
    "v_line": "│",
    "tl_corner": "╭",
    "tr_corner": "╮",
    "bl_corner": "╰",
    "br_corner": "╯",
    # Checkbox and toggles
    "checkbox_on": "☑",
    "checkbox_off": "☐",
    "radio_on": "●",
    "radio_off": "○",
    "toggle_on": "■",
    "toggle_off": "□",
}

ASCII_SYMBOLS = {
    "confirm": "+",
    "cancel": "x",
    "settings": "*",
    "up": "^",
    "down": "v",
    "success": "+",
    "warning": "!",
    "error": "x",
    "info": "i",
    "back": "<",
    "forward": ">",
    "enter": ">",
    "file": "F",
    "folder": "D",
    "preset": "#",
    "h_line": "-",
    "v_line": "|",
    "tl_corner": "+",
    "tr_corner": "+",
    "bl_corner": "+",
    "br_corner": "+",
    "checkbox_on": "[X]",
    "checkbox_off": "[ ]",
    "radio_on": "(X)",
    "radio_off": "( )",
    "toggle_on": "[#]",
    "toggle_off": "[ ]",
}

def get_symbol(name, use_unicode=True):
    """Get a symbol by name, with fallback to ASCII if unicode not supported"""
    if use_unicode:
        return SYMBOLS.get(name, "?")
    else:
        return ASCII_SYMBOLS.get(name, "?")
