
"""
TypewriterAnimation for typewriter-style text effects in the TUI.
"""

import time
from prompt_toolkit.application import get_app

from .base import Animation

class TypewriterAnimation(Animation):
    """Typewriter text animation"""

    def __init__(self, control, text, duration=1.0, fps=30):
        """
        Initialize typewriter animation.

        Args:
            control: FormattedTextControl to animate
            text (str): Text to type
            duration (float): Animation duration in seconds
            fps (int): Frames per second
        """
        super().__init__(duration, fps)
        self.control = control
        self.text = text

    async def run(self):
        """Run the typewriter animation"""
        self.is_running = True
        self.start_time = time.time()

        app = get_app()

        try:
            for i in range(self.frame_count + 1):
                if not self.is_running:
                    break

                progress = i / self.frame_count
                typed_length = int(len(self.text) * progress)
                self.control.text = self.text[:typed_length]
                app.invalidate()

                await self._wait_frame()

            # Ensure final state
            self.control.text = self.text
            app.invalidate()

        finally:
            self.is_running = False
