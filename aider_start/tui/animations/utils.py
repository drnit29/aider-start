
"""
Utility functions for animations in Aider-Start TUI.
"""

import asyncio
from prompt_toolkit.application import get_app

from .fade import FadeAnimation
from .spinner import SpinnerAnimation

async def animate_notification(message, duration=2.0):
    """
    Show a temporary notification with animation.

    Args:
        message (str): Notification message
        duration (float): Display duration in seconds
    """
    from prompt_toolkit.layout import Window
    from prompt_toolkit.layout.containers import Float
    from prompt_toolkit.layout.dimension import D
    from prompt_toolkit.layout.controls import FormattedTextControl

    app = get_app()
    if not hasattr(app, "_notification_float"):
        control = FormattedTextControl("")
        window = Window(
            content=control,
            width=D(preferred=40),
            height=D.exact(1),
            style="class:notification",
        )

        float_container = Float(window, right=1, top=1)

        app.layout.container.floats.append(float_container)
        app._notification_float = float_container
        app._notification_control = control

    # Update notification text
    app._notification_control.text = message
    app.invalidate()

    # Show for duration
    await asyncio.sleep(duration)

    # Fade out
    fade = FadeAnimation(
        app._notification_control, message, fade_in=False, duration=0.5
    )
    await fade.run()

    # Clear text
    app._notification_control.text = ""
    app.invalidate()


def create_loading_indicator():
    """
    Create a loading spinner control.

    Returns:
        tuple: (control, start_func, stop_func)
    """
    from prompt_toolkit.layout.controls import FormattedTextControl

    control = FormattedTextControl("")
    spinner = SpinnerAnimation(control)

    async def start():
        await spinner.run()

    def stop():
        spinner.stop()

    return control, start, stop
