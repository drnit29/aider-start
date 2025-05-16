from typing import Callable, Optional, List, Dict, Any
from prompt_toolkit.widgets import Button
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType


class SelectableButton(Button):
    """
    A button that can be selected, with a different style when selected.
    """

    def __init__(
        self,
        text: str = "",
        handler: Optional[Callable[[], None]] = None,
        width: int = 12,  # Default width from Button class
        left_symbol: str = "<",
        right_symbol: str = ">",
        style: str = "",
        selected: bool = False,
        group: Optional[str] = None,
    ):
        super().__init__(
            text=text,
            handler=handler,
            width=width,
            left_symbol=left_symbol,
            right_symbol=right_symbol,
        )
        self._custom_style = style
        self.selected = selected
        self.group = group

        # Store reference to all buttons in the same group
        if group is not None:
            if group not in SelectableButton._groups:
                SelectableButton._groups[group] = []
            SelectableButton._groups[group].append(self)

    # Class variable to track button groups
    _groups: Dict[str, List["SelectableButton"]] = {}

    def _get_text_fragments(self) -> StyleAndTextTuples:
        # Get the base text fragments from the parent class
        fragments = super()._get_text_fragments()

        # Apply custom style if provided
        if self._custom_style and not self.selected:
            return [
                (
                    (f"{self._custom_style} {fragment[0]}", fragment[1])
                    if fragment[0]
                    else (self._custom_style, fragment[1])
                )
                for fragment in fragments
            ]

        # If selected, modify the style to use button.selected
        elif self.selected:
            return [
                (
                    (f"class:button.selected {fragment[0]}", fragment[1])
                    if fragment[0]
                    else ("class:button.selected", fragment[1])
                )
                for fragment in fragments
            ]

        return fragments

    def _handle_click(self, mouse_event: MouseEvent) -> None:
        """Handle mouse click event."""
        if mouse_event.event_type == MouseEventType.MOUSE_UP:
            # Toggle selection state
            self.selected = not self.selected

            # If this button is part of a group and is now selected,
            # deselect all other buttons in the group
            if self.selected and self.group is not None:
                for btn in SelectableButton._groups.get(self.group, []):
                    if btn is not self and btn.selected:
                        btn.selected = False
                        if hasattr(btn, "window") and hasattr(btn.window, "app"):
                            btn.window.app.invalidate()

            # Call the handler if provided
            if self.handler is not None:
                self.handler()

            # Invalidate the UI to reflect the selection change
            if hasattr(self, "window") and hasattr(self.window, "app"):
                self.window.app.invalidate()
