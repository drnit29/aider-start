
# functions.py: Utility style functions for Aider-Start TUI.

from .colors import COLORS, COLOR_STATES

def get_button_style(state="normal"):
    """Get button style based on state (normal, hover, focus, active, disabled)"""
    if state == "normal":
        return f"bg:{COLORS['accent_primary']} {COLORS['text_primary']}"
    elif state == "hover":
        return f"bg:{COLOR_STATES['accent_primary_hover']} {COLORS['text_primary']}"
    elif state == "focus":
        # Usar uma cor de fundo bem distinta e/ou reverter para o foco
        # return f"bg:{COLORS['accent_secondary']} {COLORS['bg_primary']} bold reverse"
        # Ou, para manter o texto primário mas com fundo diferente e reverso:
        return f"bg:{COLORS['accent_secondary']} {COLORS['text_primary']} bold reverse"
    elif state == "active":
        return f"bg:{COLOR_STATES['accent_primary_active']} {COLORS['text_primary']}"
    elif state == "disabled":
        return f"bg:{COLOR_STATES['accent_primary_disabled']} {COLORS['text_muted']}"
    else:
        return f"bg:{COLORS['accent_primary']} {COLORS['text_primary']}"

def get_input_style(state="normal", validation="valid"):
    """Get input field style based on state and validation"""
    base_bg = COLORS["bg_component"]

    if validation == "error":
        border_color = COLORS["error"]
    elif validation == "warning":
        border_color = COLORS["warning"]
    else:
        border_color = (
            COLORS["accent_primary"]
            if state in ["focus", "hover"]
            else COLORS["bg_highlight"]
        )

    if state == "disabled":
        base_bg = COLORS["bg_secondary"]
        text_color = COLORS["text_muted"]
    else:
        text_color = COLORS["text_primary"]

    return f"bg:{base_bg} {text_color} border:{border_color}"

def get_list_item_style(selected=False, focused=False, highlighted=False):
    """Get style for list items based on state"""
    if selected and focused:
        return f"bg:{COLORS['accent_primary']} {COLORS['text_primary']} bold"
    elif selected:
        return f"bg:{COLORS['accent_tertiary']} {COLORS['text_primary']}"
    elif focused:
        return f"bg:{COLORS['bg_highlight']} {COLORS['text_primary']}"
    elif highlighted:
        return f"bg:{COLORS['bg_secondary']} {COLORS['accent_secondary']}"
    else:
        return f"{COLORS['text_primary']}"

def get_label_style(type="normal"):
    """Get style for different types of labels"""
    if type == "header":
        return f"bold {COLORS['accent_primary']}"
    elif type == "subheader":
        return f"{COLORS['accent_secondary']}"
    elif type == "muted":
        return f"{COLORS['text_muted']}"
    else:
        return f"{COLORS['text_primary']}"
