
"""
Main app module for Aider-Start TUI.
Contains the main application class AiderStartTUI.
"""

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import merge_styles

from ..style import default_style
from ..themes import get_theme, detect_terminal_color_support
from ..utils.terminal import get_terminal_capabilities
from ..utils.responsive import adapt_layout_to_terminal
from ..utils.accessibility import (
    global_accessibility_options,
    get_accessibility_style_mods,
)
from ..screens import PresetListScreen
from .layout import create_help_dialog, create_layout
from .keybindings import setup_global_key_bindings

class AiderStartTUI:
    """Main TUI application class"""

    def __init__(self, config=None):
        """
        Initialize TUI application.

        Args:
            config (dict, optional): Application configuration
        """
        self.config = config or {}
        self.theme_name = self.config.get("theme", detect_terminal_color_support())

        # Create key bindings
        self.key_bindings = KeyBindings()
        setup_global_key_bindings(self)

        # Set up terminal capabilities detection
        self.terminal_capabilities = get_terminal_capabilities()

        # Initialize the current screen
        self.current_screen = None

        # Setup help dialog
        self.show_help = False
        self.help_dialog = create_help_dialog(self)
        
        # Create application
        self.app = self._create_application()

    def _create_application(self):
        """
        Create the prompt_toolkit application.

        Returns:
            Application: The prompt_toolkit application
        """
        # Create layout
        layout = create_layout(self)

        # Create merged style with theme and accessibility modifications
        theme = get_theme(self.theme_name)
        accessibility_mods = get_accessibility_style_mods(global_accessibility_options)
        merged_style = merge_styles([theme, default_style])

        # Create application
        app = Application(
            layout=layout,
            key_bindings=self.key_bindings,
            style=merged_style,
            full_screen=True,
            mouse_support=True,
        )

        # Set up terminal size change handler
        app.on_resize = adapt_layout_to_terminal(
            layout, lambda w, h: self._on_terminal_resize(w, h)
        )

        return app

    def _on_terminal_resize(self, width, height):
        """
        Handle terminal resize event.

        Args:
            width (int): New terminal width
            height (int): New terminal height
        """
        # Update the layout as needed based on new dimensions
        # This method can be expanded if specific resize behavior is needed
        pass

    def _toggle_theme(self):
        """Toggle between available themes"""
        from ..themes import get_all_theme_names

        theme_names = get_all_theme_names()
        current_index = (
            theme_names.index(self.theme_name) if self.theme_name in theme_names else 0
        )
        next_index = (current_index + 1) % len(theme_names)
        self.theme_name = theme_names[next_index]

        # Update application style
        theme = get_theme(self.theme_name)
        accessibility_mods = get_accessibility_style_mods(global_accessibility_options)
        merged_style = merge_styles([theme, default_style])
        self.app.style = merged_style

    def set_presets(self, presets):
        """
        Set the presets list.

        Args:
            presets (list): List of presets
        """
        if hasattr(self, "preset_list_screen"):
            self.preset_list_screen.presets = presets
            self.preset_list_screen._refresh_list()

    def run(self):
        """Run the application"""
        return self.app.run()

    def _on_preset_select(self, preset):
        """
        Handle preset selection.

        Args:
            preset: The selected preset
        """
        # Placeholder - to be implemented
        pass

    def _on_preset_edit(self, preset):
        """
        Handle preset edit request.

        Args:
            preset: The preset to edit
        """
        # Placeholder - to be implemented
        pass

    def _on_preset_delete(self, preset):
        """
        Handle preset delete request.

        Args:
            preset: The preset to delete
        """
        # Placeholder - to be implemented
        pass

    def _on_preset_create(self):
        """Handle preset create request"""
        # Placeholder - to be implemented
        pass

    def _toggle_help(self):
        """Toggle help dialog visibility"""
        from prompt_toolkit.layout import FloatContainer, Float

        self.show_help = not self.show_help

        # Update floats in layout
        if isinstance(self.app.layout.container, FloatContainer):
            if self.show_help:
                self.app.layout.container.floats.append(
                    Float(content=self.help_dialog, top=5, left=10)
                )
            else:
                # Remove help dialog from floats
                self.app.layout.container.floats = [
                    f
                    for f in self.app.layout.container.floats
                    if f.content != self.help_dialog
                ]
