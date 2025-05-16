
"""
Animation utilities for Aider-Start TUI.
Provides tools for creating smooth transitions and visual effects.

This is a façade module for backward compatibility.
"""

from .animations.base import Animation
from .animations.fade import FadeAnimation
from .animations.slide import SlideAnimation
from .animations.typewriter import TypewriterAnimation
from .animations.spinner import SpinnerAnimation
from .animations.progress import ProgressBarAnimation
from .animations.utils import animate_notification, create_loading_indicator

__all__ = [
    "Animation",
    "FadeAnimation",
    "SlideAnimation",
    "TypewriterAnimation",
    "SpinnerAnimation",
    "ProgressBarAnimation",
    "animate_notification",
    "create_loading_indicator",
]
