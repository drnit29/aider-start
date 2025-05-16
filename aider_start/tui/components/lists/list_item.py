
from prompt_toolkit.layout import Window, FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.filters import has_focus
from prompt_toolkit.mouse_events import MouseEventType

from ..base import Component, ClickableComponent
from ..style import get_symbol

class ListItem(ClickableComponent):
    """Selectable list item component"""

    def __init__(self, text, data=None, style="class:list-item", selected=False):
        super().__init__()
        self.text = text
        self.data = data
        self.base_style = style
        self.selected = selected

        self._create_control()

    def _create_control(self):
        def get_formatted_text():
            if self.selected and self.has_focus():
                style = f"{self.base_style}.selected.focused"
            elif self.selected:
                style = f"{self.base_style}.selected"
            elif self.has_focus():
                style = f"{self.base_style}.focused"
            else:
                style = self.base_style

            if isinstance(self.text, str) and "<" in self.text and ">" in self.text:
                from prompt_toolkit.formatted_text import HTML
                html_text = self.text
                return HTML(f"<{style}>{html_text}</{style}>")
            else:
                return [(style, str(self.text))]

        self.control = FormattedTextControl(
            get_formatted_text,
            focusable=True,
            key_bindings=self.key_bindings,
            show_cursor=False,
            mouse_handlers=self._get_mouse_handlers(),
        )

        @self.key_bindings.add("enter", filter=has_focus(self))
        @self.key_bindings.add("space", filter=has_focus(self))
        def _(event):
            self.on_click()
            event.app.invalidate()

    def _get_mouse_handlers(self):
        mouse_handlers = {}

        def mouse_handler(mouse_event):
            if mouse_event.event_type == MouseEventType.MOUSE_UP:
                self.on_click()
                return None
            return NotImplemented

        mouse_handlers[MouseEventType.MOUSE_UP] = mouse_handler
        return mouse_handlers

    def set_text(self, text):
        self.text = text

    def set_selected(self, selected):
        self.selected = selected

    def __pt_container__(self):
        return Window(self.control, height=D.exact(1), dont_extend_height=True)

class ListSeparator(Component):
    """List separator component"""

    def __init__(self, label=None, style="class:list-separator"):
        super().__init__()
        self.label = label
        self.style = style

    def __pt_container__(self):
        if self.label:
            label_len = len(self.label) + 2

            def get_text():
                return [
                    (self.style, "─" * 2),
                    (f"{self.style}.label", f" {self.label} "),
                    (self.style, "─" * 10),
                ]

            return Window(
                FormattedTextControl(get_text), height=D.exact(1), style=self.style
            )
        else:
            return Window(height=D.exact(1), char="─", style=self.style)
