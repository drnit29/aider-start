
from prompt_toolkit.layout import HSplit, Window
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.formatted_text import FormattedTextControl
from prompt_toolkit.filters import has_focus
from prompt_toolkit.mouse_events import MouseEventType
from .labels import LabelComponent
from ..base import FocusableComponent
from ..style import get_symbol

class CheckBox(FocusableComponent):
    """Checkbox input component"""

    def __init__(self, name, label, value=False, style="class:checkbox"):
        super().__init__()
        self.name = name
        self.value = value
        self.label_text = label
        self.style = style
        self.change_handlers = []
        self._create_control()

    def _create_control(self):
        def get_text():
            checked = (
                get_symbol("checkbox_on") if self.value else get_symbol("checkbox_off")
            )
            return f" {checked} {self.label_text}"

        self.control = FormattedTextControl(
            get_text,
            focusable=True,
            key_bindings=self.key_bindings,
            show_cursor=False,
            mouse_handlers=self._get_mouse_handlers(),
        )

        @self.key_bindings.add("enter", filter=has_focus(self))
        @self.key_bindings.add("space", filter=has_focus(self))
        def _(event):
            self.toggle()
            event.app.invalidate()

    def _get_mouse_handlers(self):
        mouse_handlers = {}

        def mouse_handler(mouse_event):
            if mouse_event.event_type == MouseEventType.MOUSE_UP:
                self.toggle()
                return None
            return NotImplemented

        mouse_handlers[MouseEventType.MOUSE_UP] = mouse_handler
        return mouse_handlers

    def toggle(self):
        self.value = not self.value
        self.on_value_change()

    def set_value(self, value):
        self.value = bool(value)
        self.on_value_change()

    def on_value_change(self):
        for handler in self.change_handlers:
            handler(self.value)

    def add_change_handler(self, handler):
        self.change_handlers.append(handler)

    def __pt_container__(self):
        return Window(
            self.control,
            height=D.exact(1),
            dont_extend_height=True,
            style=self.style if not has_focus(self)() else f"{self.style}.focused",
        )

class RadioButton(CheckBox):
    """Radio button input component"""

    def __init__(self, name, label, group, value=False, style="class:radio"):
        self.group = group
        super().__init__(name, label, value, style)

    def _create_control(self):
        def get_text():
            selected = get_symbol("radio_on") if self.value else get_symbol("radio_off")
            return f" {selected} {self.label_text}"

        self.control = FormattedTextControl(
            get_text,
            focusable=True,
            key_bindings=self.key_bindings,
            show_cursor=False,
            mouse_handlers=self._get_mouse_handlers(),
        )

        @self.key_bindings.add("enter", filter=has_focus(self))
        @self.key_bindings.add("space", filter=has_focus(self))
        def _(event):
            self.select()
            event.app.invalidate()

    def select(self):
        if not self.value:
            self.value = True
            self.on_value_change()

class RadioGroup(FocusableComponent):
    """Group of radio buttons"""

    def __init__(
        self, name, options, label=None, selected_value=None, style="class:radio-group"
    ):
        super().__init__()
        self.name = name
        self.value = selected_value
        self.options = options
        self.style = style
        self.validation_error = None
        self.change_handlers = []

        if label:
            self.label = LabelComponent(label)
        else:
            self.label = None

        self.buttons = []
        for value, label in options:
            button = RadioButton(
                name=f"{name}_{value}",
                label=label,
                group=name,
                value=(value == selected_value),
                style=style,
            )
            button.option_value = value
            button.add_change_handler(lambda b=button: self._on_button_change(b))
            self.buttons.append(button)

    def _on_button_change(self, changed_button):
        if changed_button.value:
            self.value = changed_button.option_value
            for button in self.buttons:
                if button is not changed_button and button.value:
                    button.value = False
            self.on_value_change()

    def set_value(self, value):
        self.value = value
        for button in self.buttons:
            button.set_value(button.option_value == value)

    def on_value_change(self):
        for handler in self.change_handlers:
            handler(self.value)

    def add_change_handler(self, handler):
        self.change_handlers.append(handler)

    def __pt_container__(self):
        radio_buttons = HSplit(self.buttons)
        if self.label:
            if self.validation_error:
                error_label = LabelComponent(
                    f"  {get_symbol('error')} {self.validation_error}",
                    style="class:label.error",
                )
                return HSplit([self.label, radio_buttons, error_label])
            else:
                return HSplit([self.label, radio_buttons])
        else:
            if self.validation_error:
                error_label = LabelComponent(
                    f"  {get_symbol('error')} {self.validation_error}",
                    style="class:label.error",
                )
                return HSplit([radio_buttons, error_label])
            else:
                return radio_buttons
