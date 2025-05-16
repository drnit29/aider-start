
"""
Base Animation class for terminal animations in Aider-Start TUI.
"""

import asyncio
import time

class Animation:
    """Base class for terminal animations"""

    def __init__(self, duration=0.3, fps=30):
        """
        Initialize animation.

        Args:
            duration (float): Animation duration in seconds
            fps (int): Frames per second
        """
        self.duration = duration
        self.fps = fps
        self.frame_count = int(duration * fps)
        self.interval = 1.0 / fps
        self.is_running = False
        self.start_time = None

    async def run(self):
        """
        Run the animation.

        This is an abstract method that should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def _get_progress(self):
        """
        Get animation progress (0.0 to 1.0).

        Returns:
            float: Animation progress
        """
        if self.start_time is None:
            return 0.0

        elapsed = time.time() - self.start_time
        progress = elapsed / self.duration
        return min(1.0, max(0.0, progress))

    async def _wait_frame(self):
        """Wait for next frame interval"""
        await asyncio.sleep(self.interval)
