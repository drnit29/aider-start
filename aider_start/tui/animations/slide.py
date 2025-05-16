
"""
SlideAnimation for sliding UI elements in/out in the TUI.
"""

import time
from prompt_toolkit.application import get_app

from .base import Animation

class SlideAnimation(Animation):
    """Slide in/out animation for UI elements"""

    def __init__(self, container, direction="left", duration=0.3, fps=30):
        """
        Initialize slide animation.

        Args:
            container: Container to animate
            direction (str): Slide direction ("left", "right", "up", "down")
            duration (float): Animation duration in seconds
            fps (int): Frames per second
        """
        super().__init__(duration, fps)
        self.container = container
        self.direction = direction
        self.original_width = None
        self.original_height = None

    async def run(self):
        """Run the slide animation"""
        self.is_running = True
        self.start_time = time.time()

        # Store original dimensions
        if hasattr(self.container, "width"):
            self.original_width = self.container.width
        if hasattr(self.container, "height"):
            self.original_height = self.container.height

        app = get_app()

        try:
            for i in range(self.frame_count + 1):
                if not self.is_running:
                    break

                progress = i / self.frame_count
                self._update_position(progress)
                app.invalidate()

                await self._wait_frame()

            # Ensure final state
            self._update_position(1.0)
            app.invalidate()

        finally:
            self.is_running = False
            # Restore original dimensions
            if hasattr(self.container, "width") and self.original_width:
                self.container.width = self.original_width
            if hasattr(self.container, "height") and self.original_height:
                self.container.height = self.original_height

    def _update_position(self, progress):
        """
        Update container position.

        Args:
            progress (float): Animation progress (0.0 to 1.0)
        """
        # This is a simplified implementation
        # Actual implementation would depend on how the container handles positioning
        pass
