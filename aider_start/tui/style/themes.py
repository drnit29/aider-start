
# themes.py: Theme definitions and helpers for Aider-Start TUI.

from prompt_toolkit.styles import Style
from .colors import COLORS
from .functions import get_button_style, get_input_style, get_label_style, get_list_item_style

default_style = Style.from_dict(
    {
        # Base UI elements
        "title": f"bold {COLORS['accent_primary']}",
        "status": f"bg:{COLORS['bg_component']} {COLORS['text_primary']}",
        "selected": f"bg:{COLORS['accent_primary']} {COLORS['text_primary']} bold",
        "description": f"{COLORS['text_secondary']}",
        "key": f"bold {COLORS['accent_secondary']}",
        # Frame and border elements
        "frame": f"border:{COLORS['bg_highlight']}",  # Default style for a frame (e.g., border color)
        "frame.focused": f"border:{COLORS['accent_secondary']}",  # Style for a frame when its content is focused
        "frame.border": f"{COLORS['bg_highlight']}",  # Existing, can be kept or merged
        "frame.label": f"bg:{COLORS['bg_component']} {COLORS['accent_primary']} bold",
        "frame.corner": f"{COLORS['bg_highlight']}",  # For corners if using specific characters
        # Dialog elements
        "dialog": f"bg:{COLORS['bg_secondary']}",
        "dialog.body": f"bg:{COLORS['bg_component']} {COLORS['text_primary']}",
        "dialog frame.border": f"{COLORS['accent_primary']}",
        "dialog frame.label": f"bg:{COLORS['accent_primary']} {COLORS['bg_primary']} bold",
        "dialog frame.corner": f"{COLORS['accent_primary']}",
        # Buttons
        "button": get_button_style("normal"),
        "button.focused": get_button_style("focus"),
        "button.hover": get_button_style("hover"),
        "button.active": get_button_style("active"),
        "button.disabled": get_button_style("disabled"),
        "button.selected": f"bg:{COLORS['success']} {COLORS['bg_primary']} bold",
        # Inputs
        "text-area": f"bg:{COLORS['bg_component']} {COLORS['text_primary']}",
        "text-area.cursor": f"{COLORS['accent_primary']}",
        "text-area.cursor-line": f"bg:{COLORS['bg_highlight']}",
        "text-area.selection": f"bg:{COLORS['accent_tertiary']} {COLORS['text_primary']}",
        # Form elements
        "input": get_input_style("normal"),
        "input.focused": get_input_style("focus"),
        "input.invalid": get_input_style("normal", "error"),
        "input.disabled": get_input_style("disabled"),
        "label": get_label_style(),
        "label.header": get_label_style("header"),
        "label.subheader": get_label_style("subheader"),
        "label.muted": get_label_style("muted"),
        "label.error": f"{COLORS['error']} bold",
        "checkbox": f"{COLORS['text_primary']}",
        "checkbox.checked": f"{COLORS['success']} bold",
        "checkbox.focused": f"bg:{COLORS['bg_highlight']} {COLORS['text_primary']}",
        "radio": f"{COLORS['text_primary']}",
        "radio.selected": f"{COLORS['success']} bold",
        "radio.focused": f"bg:{COLORS['bg_highlight']} {COLORS['text_primary']}",
        # List and menus
        "list-item": get_list_item_style(),
        "list-item.selected": get_list_item_style(selected=True),
        "list-item.focused": get_list_item_style(focused=True),
        "list-item.highlighted": get_list_item_style(highlighted=True),
        "list-item.selected.focused": get_list_item_style(selected=True, focused=True),
        # Scrollbars
        "scrollbar.background": f"bg:{COLORS['bg_component']}",
        "scrollbar.button": f"bg:{COLORS['bg_highlight']}",
        "scrollbar.arrow": f"{COLORS['text_secondary']}",
        "scrollbar.handle": f"bg:{COLORS['accent_tertiary']}",
        # Additional elements
        "search-match": f"bg:{COLORS['warning']} {COLORS['bg_primary']} bold",
        "separator": f"{COLORS['bg_highlight']}",
        "help-key": f"bg:{COLORS['accent_tertiary']} {COLORS['text_primary']} bold",
        "help-text": f"{COLORS['text_secondary']}",
        "notification.info": f"bg:{COLORS['info']} {COLORS['bg_primary']} bold",
        "notification.warning": f"bg:{COLORS['warning']} {COLORS['bg_primary']} bold",
        "notification.error": f"bg:{COLORS['error']} {COLORS['bg_primary']} bold",
        "notification.success": f"bg:{COLORS['success']} {COLORS['bg_primary']} bold",
        # Filter bar styles
        "filter-bar": f"bg:{COLORS['bg_component']}",  # Background for the TextArea itself
        "filter-bar.prompt": f"{COLORS['text_muted']}",  # Prompt style when not focused
        "filter-bar.prompt.focused": f"bold {COLORS['accent_secondary']}",  # Prompt style when focused
        # Styles for the main list body area
        "list-body": f"bg:{COLORS['bg_primary']}",  # Default background for the list area
        "list-body.focused": f"bg:{COLORS['bg_secondary']}",  # Slightly different background when list area is focused
    }
)

THEMES = {
    "default": default_style,
    # Other themes can be added here
}

def get_theme(name="default"):
    """Get a theme by name"""
    return THEMES.get(name, default_style)
