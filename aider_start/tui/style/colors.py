
# colors.py: Color palettes and color state constants for Aider-Start TUI.

COLORS = {
    # Background Colors
    "bg_primary": "#121212",  # very dark gray
    "bg_secondary": "#1e1e2e",  # slightly lighter dark gray
    "bg_component": "#2a2a40",  # dark blue-gray
    "bg_highlight": "#3a3a5a",  # medium blue-gray
    # Accent Colors
    "accent_primary": "#9d7cd8",  # medium purple
    "accent_secondary": "#c7a0f1",  # light purple
    "accent_tertiary": "#a162de",  # deep purple
    # Semantic Colors
    "success": "#a2e1a2",  # soft green
    "warning": "#f0c38e",  # soft orange
    "error": "#f07178",  # soft red
    "info": "#89ddff",  # light blue
    # Text Colors
    "text_primary": "#f8f8f2",  # off-white
    "text_secondary": "#c0c0cc",  # light gray
    "text_muted": "#727288",  # medium gray
}

COLOR_STATES = {
    # Hover variations (lighter)
    "accent_primary_hover": "#ae8de9",
    "accent_secondary_hover": "#d8b1ff",
    "accent_tertiary_hover": "#b273ef",
    # Active/pressed variations (darker)
    "accent_primary_active": "#8c6bc7",
    "accent_secondary_active": "#b691e0",
    "accent_tertiary_active": "#9051cd",
    # Disabled variations (desaturated)
    "accent_primary_disabled": "#6c6c86",
    "accent_secondary_disabled": "#7f7f99",
    "accent_tertiary_disabled": "#5d5d77",
    # Focus variations (brighter)
    "accent_primary_focus": "#ae8de9",
    "bg_component_focus": "#3a3a50",
}

BASIC_COLORS = {
    "bg_primary": "black",
    "bg_secondary": "black",
    "bg_component": "darkblue",
    "bg_highlight": "blue",
    "accent_primary": "magenta",
    "accent_secondary": "magenta",
    "accent_tertiary": "magenta",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "cyan",
    "text_primary": "white",
    "text_secondary": "gray",
    "text_muted": "darkgray",
}
