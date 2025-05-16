
"""
FadeAnimation for fading in/out text in the TUI.
"""

import time
from prompt_toolkit.application import get_app

from .base import Animation

class FadeAnimation(Animation):
    """Fade in/out animation for text"""

    def __init__(self, control, text, fade_in=True, duration=0.3, fps=30):
        """
        Initialize fade animation.

        Args:
            control: FormattedTextControl to animate
            text: Text content (string or formatted text)
            fade_in (bool): True for fade in, False for fade out
            duration (float): Animation duration in seconds
            fps (int): Frames per second
        """
        super().__init__(duration, fps)
        self.control = control
        self.text = text
        self.fade_in = fade_in
        self.original_text = None

    async def run(self):
        """Run the fade animation"""
        self.is_running = True
        self.start_time = time.time()
        self.original_text = self.control.text

        app = get_app()

        try:
            for i in range(self.frame_count + 1):
                if not self.is_running:
                    break

                progress = i / self.frame_count
                if not self.fade_in:
                    progress = 1.0 - progress

                self._update_opacity(progress)
                app.invalidate()

                await self._wait_frame()

            # Ensure final state
            progress = 1.0 if self.fade_in else 0.0
            self._update_opacity(progress)
            app.invalidate()

        finally:
            self.is_running = False

    def _update_opacity(self, opacity):
        """
        Update text opacity.

        Args:
            opacity (float): Opacity value (0.0 to 1.0)
        """
        if isinstance(self.text, str):
            # For plain text, adjust the color
            gray = int(opacity * 255)
            self.control.text = f"\x1b[38;2;{gray};{gray};{gray}m{self.text}\x1b[0m"
        else:
            # For formatted text, we need a different approach
            # This is a simplified implementation
            self.control.text = self.text
