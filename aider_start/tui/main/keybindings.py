
"""
Global key bindings setup for Aider-Start TUI.
"""

def setup_global_key_bindings(app):
    """
    Set up global application key bindings.

    Args:
        app (AiderStartTUI): The TUI app instance
    """
    @app.key_bindings.add("c-c")
    def _(event):
        """Exit the application on Ctrl+C"""
        event.app.exit()

    @app.key_bindings.add("f1")
    def _(event):
        """Show help on F1"""
        app._toggle_help()
        event.app.invalidate()

    @app.key_bindings.add("?")
    def _(event):
        """Show help on ?"""
        app._toggle_help()
        event.app.invalidate()

    @app.key_bindings.add("f2")
    def _(event):
        """Toggle theme on F2"""
        app._toggle_theme()
        event.app.invalidate()

    @app.key_bindings.add("escape")
    def _(event):
        """Handle escape key"""
        if app.show_help:
            app._toggle_help()
            event.app.invalidate()
