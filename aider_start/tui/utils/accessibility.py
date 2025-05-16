"""
Accessibility utilities for Aider-Start TUI.
"""

from prompt_toolkit.layout import Window, FormattedTextControl
from prompt_toolkit.layout.dimension import D

from .terminal import supports_unicode, supports_true_color


class AccessibilityOptions:
    """Accessibility options for the application"""

    def __init__(self):
        """Initialize accessibility options with defaults"""
        # Automatically detect terminal capabilities
        self.use_unicode = supports_unicode()
        self.use_colors = supports_true_color()

        # Additional options with defaults
        self.high_contrast = False
        self.large_text = False
        self.reduce_animations = False
        self.simplified_ui = False
        self.keyboard_friendly = True
        self.screen_reader_mode = False

    def toggle_high_contrast(self):
        """Toggle high contrast mode"""
        self.high_contrast = not self.high_contrast

    def toggle_large_text(self):
        """Toggle large text mode"""
        self.large_text = not self.large_text

    def toggle_reduce_animations(self):
        """Toggle reduced animations mode"""
        self.reduce_animations = not self.reduce_animations

    def toggle_simplified_ui(self):
        """Toggle simplified UI mode"""
        self.simplified_ui = not self.simplified_ui

    def toggle_keyboard_friendly(self):
        """Toggle keyboard friendly mode"""
        self.keyboard_friendly = not self.keyboard_friendly

    def toggle_screen_reader_mode(self):
        """Toggle screen reader mode"""
        self.screen_reader_mode = not self.screen_reader_mode


# Global accessibility options that can be used throughout the application
global_accessibility_options = AccessibilityOptions()


def get_accessibility_style_mods(options=None):
    """
    Get style modifications based on accessibility options.

    Args:
        options (AccessibilityOptions, optional): Accessibility options

    Returns:
        dict: Style modifications
    """
    if options is None:
        options = global_accessibility_options

    style_mods = {}

    if options.high_contrast:
        # High contrast styles
        style_mods.update(
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
            }
        )

    if options.large_text:
        # Large text styles could be handled in the UI rendering
        # This is a placeholder for any style modifications needed
        pass

    return style_mods


def create_screen_reader_friendly_text(content, element_type="", role="", state=""):
    """
    Create screen reader friendly text with ARIA-like attributes.

    Args:
        content (str): The text content
        element_type (str): Element type (button, input, etc.)
        role (str): Element role
        state (str): Element state (selected, disabled, etc.)

    Returns:
        str: Screen reader friendly text
    """
    sr_text = content

    # Add element type if provided
    if element_type:
        sr_text = f"{element_type}: {sr_text}"

    # Add role if provided
    if role:
        sr_text = f"{sr_text} ({role})"

    # Add state if provided
    if state:
        sr_text = f"{sr_text}, {state}"

    return sr_text


def create_screenreader_only_container(text, visible=False):
    """
    Create a container with text only for screen readers.

    Args:
        text (str): Text content
        visible (bool): Whether the text should be visible

    Returns:
        Window: Screen reader only window
    """
    if visible:
        return Window(FormattedTextControl(text), height=D.exact(1))
    else:
        # Hidden visually but available to screen readers
        # This is a best effort approach for terminal screen readers
        return Window(FormattedTextControl(f"<!-- {text} -->"), height=D.exact(0))


def get_accessible_keybinding_hint(key, description):
    """
    Get an accessible keybinding hint.

    Args:
        key (str): Key combination
        description (str): Description of the action

    Returns:
        str: Accessible keybinding hint
    """
    # Make key names more readable
    key_display = (
        key.replace("-", "+")
        .replace("c-", "Ctrl+")
        .replace("s-", "Shift+")
        .replace("a-", "Alt+")
    )

    return f"{key_display}: {description}"


def get_accessible_symbol(name, use_unicode=None):
    """
    Get an accessible symbol based on accessibility settings.

    Args:
        name (str): Symbol name
        use_unicode (bool, optional): Whether to use Unicode

    Returns:
        str: Accessible symbol
    """
    from ..style import get_symbol

    if use_unicode is None:
        use_unicode = global_accessibility_options.use_unicode

    return get_symbol(name, use_unicode)


def create_keyboard_navigation_help():
    """
    Create keyboard navigation help text.

    Returns:
        str: Help text for keyboard navigation
    """
    return (
        "Keyboard Navigation:\n"
        "- Arrow keys: Navigate within a component\n"
        "- Tab / Shift+Tab: Move between components\n"
        "- Enter / Space: Activate selected item\n"
        "- Escape: Go back / Cancel\n"
        "- F1: Show this help\n"
    )
