
"""
SpinnerAnimation for loading spinner effects in the TUI.
"""

import time
from prompt_toolkit.application import get_app

from .base import Animation

class SpinnerAnimation(Animation):
    """Loading spinner animation"""

    def __init__(self, control, spinner_type="dots", fps=10):
        """
        Initialize spinner animation.

        Args:
            control: FormattedTextControl to animate
            spinner_type (str): Spinner type ("dots", "line", "braille")
            fps (int): Frames per second
        """
        super().__init__(duration=float("inf"), fps=fps)  # Infinite duration
        self.control = control
        self.frame = 0

        # Spinner frames
        self.spinners = {
            "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
            "line": ["-", "\\", "|", "/"],
            "braille": ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
            "basic": ["|", "/", "-", "\\"],
        }

        self.frames = self.spinners.get(spinner_type, self.spinners["dots"])

    async def run(self):
        """Run the spinner animation"""
        self.is_running = True
        self.start_time = time.time()

        app = get_app()

        try:
            while self.is_running:
                self.frame = (self.frame + 1) % len(self.frames)
                self.control.text = self.frames[self.frame]
                app.invalidate()

                await self._wait_frame()

        finally:
            self.is_running = False

    def stop(self):
        """Stop the spinner animation"""
        self.is_running = False
