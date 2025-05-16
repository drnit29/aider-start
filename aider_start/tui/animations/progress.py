
"""
ProgressBarAnimation for animating progress bars in the TUI.
"""

from prompt_toolkit.application import get_app

from .base import Animation

class ProgressBarAnimation(Animation):
    """Progress bar animation"""

    def __init__(
        self, control, width=20, progress=0, animate=True, duration=0.3, fps=30
    ):
        """
        Initialize progress bar animation.

        Args:
            control: FormattedTextControl to animate
            width (int): Progress bar width in characters
            progress (float): Initial progress (0.0 to 1.0)
            animate (bool): Whether to animate progress changes
            duration (float): Animation duration in seconds
            fps (int): Frames per second
        """
        super().__init__(duration, fps)
        self.control = control
        self.width = width
        self.progress = progress
        self.target_progress = progress
        self.animate = animate

    async def set_progress(self, progress):
        """
        Set progress value with animation.

        Args:
            progress (float): New progress value (0.0 to 1.0)
        """
        old_progress = self.progress
        self.target_progress = min(1.0, max(0.0, progress))

        if self.animate:
            self.is_running = True
            self.start_time = None  # Reset start_time for progress animation

            app = get_app()

            try:
                for i in range(self.frame_count + 1):
                    if not self.is_running:
                        break

                    frame_progress = i / self.frame_count
                    current = (
                        old_progress
                        + (self.target_progress - old_progress) * frame_progress
                    )
                    self.progress = current
                    self._update_bar()
                    app.invalidate()

                    await self._wait_frame()

                # Ensure final state
                self.progress = self.target_progress
                self._update_bar()
                app.invalidate()

            finally:
                self.is_running = False
        else:
            # Immediate update without animation
            self.progress = self.target_progress
            self._update_bar()
            app = get_app()
            app.invalidate()

    def _update_bar(self):
        """Update progress bar visualization"""
        filled_width = int(self.width * self.progress)
        empty_width = self.width - filled_width

        bar = "█" * filled_width + "░" * empty_width
        percentage = int(self.progress * 100)

        self.control.text = f"{bar} {percentage}%"
