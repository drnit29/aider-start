
from prompt_toolkit.layout import Window
from prompt_toolkit.formatted_text import HTML, FormattedTextControl
from ..base import Component

class LabelComponent(Component):
    """Text label component"""

    def __init__(self, text, style="class:label"):
        super().__init__()
        self.text = text
        self.style = style
        self.formatted_text = None
        self._update_text()

    def set_text(self, text):
        self.text = text
        self._update_text()

    def _update_text(self):
        if isinstance(self.text, str) and "<" in self.text and ">" in self.text:
            self.formatted_text = HTML(self.text)
        else:
            self.formatted_text = self.text

    def __pt_container__(self):
        return Window(
            FormattedTextControl(self.formatted_text),
            dont_extend_height=True,
            style=self.style,
        )
