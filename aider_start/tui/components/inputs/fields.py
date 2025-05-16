
from prompt_toolkit.layout import HSplit, Window
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import TextArea, Label
from prompt_toolkit.filters import has_focus
from prompt_toolkit.formatted_text import HTML
from .labels import LabelComponent
from ..base import FocusableComponent
from ..style import get_symbol

class InputField(FocusableComponent):
    """Text input field component"""

    def __init__(
        self,
        name,
        label=None,
        value="",
        placeholder="",
        multiline=False,
        password=False,
        style="class:input",
        width=None,
        height=None,
        validators=None,
    ):
        super().__init__()
        self.name = name
        self.value = value
        self.placeholder = placeholder
        self.multiline = multiline
        self.password = password
        self.style = style
        self.width = width
        self.height = height
        self.validators = []
        self.change_handlers = []
        self.validation_error = None

        if label:
            self.label = LabelComponent(label)
        else:
            self.label = None

        if validators:
            for validator in validators:
                if isinstance(validator, tuple):
                    self.add_validator(*validator)
                else:
                    self.add_validator(validator)

        self._create_control()

    def _create_control(self):
        self.control = TextArea(
            text=self.value or "",
            multiline=self.multiline,
            password=self.password,
            focusable=True,
            focus_on_click=True,
            style=self.style,
            height=self.height or (D(min=3) if self.multiline else D.exact(1)),
            width=self.width,
            placeholder=self.placeholder,
        )

        def on_text_changed(text):
            self.value = text
            self.on_value_change()

        self.control.buffer.on_text_changed += on_text_changed

        @self.key_bindings.add("tab", filter=has_focus(self.control))
        def _(event):
            event.app.layout.focus_next()

        @self.key_bindings.add("s-tab", filter=has_focus(self.control))
        def _(event):
            event.app.layout.focus_previous()

    def add_validator(self, validator, error_message=None):
        self.validators.append((validator, error_message))

    def add_change_handler(self, handler):
        self.change_handlers.append(handler)

    def on_value_change(self):
        self.validate()
        for handler in self.change_handlers:
            handler(self.value)

    def validate(self):
        for validator, error_message in self.validators:
            if not validator(self.value):
                self.validation_error = error_message or "Invalid value"
                return False
        self.validation_error = None
        return True

    def is_valid(self):
        return self.validate()

    def set_value(self, value):
        self.value = value
        self.control.text = value
        self.on_value_change()

    def __pt_container__(self):
        if self.label:
            if self.validation_error:
                error_label = LabelComponent(
                    f"  {get_symbol('error')} {self.validation_error}",
                    style="class:label.error",
                )
                return HSplit([self.label, self.control, error_label])
            else:
                return HSplit([self.label, self.control])
        else:
            if self.validation_error:
                error_label = LabelComponent(
                    f"  {get_symbol('error')} {self.validation_error}",
                    style="class:label.error",
                )
                return HSplit([self.control, error_label])
            else:
                return self.control

class SelectField(FocusableComponent):
    """Dropdown select field component"""

    def __init__(
        self, name, options, label=None, value=None, style="class:select", width=None
    ):
        super().__init__()
        self.name = name
        self.value = value
        self.options = options
        self.style = style
        self.width = width
        self.dropdown_visible = False
        self.validation_error = None
        self.change_handlers = []

        if label:
            self.label = LabelComponent(label)
        else:
            self.label = None

        self.selected_label = ""
        for option_value, option_label in options:
            if option_value == value:
                self.selected_label = option_label
                break

        self._create_control()

    def _create_control(self):
        from prompt_toolkit.formatted_text import FormattedTextControl
        from prompt_toolkit.mouse_events import MouseEventType

        def get_text():
            return f" {self.selected_label} {get_symbol('down' if not self.dropdown_visible else 'up')} "

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
            self.toggle_dropdown()
            event.app.invalidate()

        @self.key_bindings.add("down", filter=has_focus(self))
        def _(event):
            self.show_dropdown()
            event.app.invalidate()

    def _get_mouse_handlers(self):
        from prompt_toolkit.mouse_events import MouseEventType
        mouse_handlers = {}

        def mouse_handler(mouse_event):
            if mouse_event.event_type == MouseEventType.MOUSE_UP:
                self.toggle_dropdown()
                return None
            return NotImplemented

        mouse_handlers[MouseEventType.MOUSE_UP] = mouse_handler
        return mouse_handlers

    def toggle_dropdown(self):
        self.dropdown_visible = not self.dropdown_visible

    def show_dropdown(self):
        self.dropdown_visible = True

    def hide_dropdown(self):
        self.dropdown_visible = False

    def select_option(self, value):
        self.value = value
        for option_value, option_label in self.options:
            if option_value == value:
                self.selected_label = option_label
                break
        self.hide_dropdown()
        self.on_value_change()

    def on_value_change(self):
        for handler in self.change_handlers:
            handler(self.value)

    def add_change_handler(self, handler):
        self.change_handlers.append(handler)

    def _create_dropdown(self):
        from prompt_toolkit.layout import HSplit, Window
        from prompt_toolkit.layout.dimension import D
        from prompt_toolkit.formatted_text import FormattedTextControl
        from prompt_toolkit.mouse_events import MouseEventType

        options = []
        for option_value, option_label in self.options:
            def get_option_text(v=option_value, l=option_label):
                selected = "● " if v == self.value else "  "
                return f"{selected}{l}"

            option_control = FormattedTextControl(
                get_option_text, focusable=True, key_bindings=self.key_bindings
            )

            def create_mouse_handler(v=option_value):
                def mouse_handler(mouse_event):
                    if mouse_event.event_type == MouseEventType.MOUSE_UP:
                        self.select_option(v)
                        return None
                    return NotImplemented
                return mouse_handler

            option_control.mouse_handlers = {
                MouseEventType.MOUSE_UP: create_mouse_handler()
            }

            option_window = Window(
                option_control, height=D.exact(1), style=f"{self.style}.item"
            )
            options.append(option_window)

        return HSplit(options)

    def __pt_container__(self):
        from prompt_toolkit.layout import Float, FloatContainer
        from prompt_toolkit.widgets import Shadow, Frame
        from prompt_toolkit.layout import HSplit, Window
        from prompt_toolkit.layout.dimension import D

        select_window = Window(
            self.control,
            height=D.exact(1),
            width=self.width,
            style=self.style if not has_focus(self)() else f"{self.style}.focused",
        )

        main_container = select_window

        if self.dropdown_visible:
            dropdown = Shadow(
                Frame(self._create_dropdown(), style=f"{self.style}.dropdown")
            )
            float_container = FloatContainer(
                content=select_window, floats=[Float(content=dropdown, top=1, left=0)]
            )
            main_container = float_container

        if self.label:
            if self.validation_error:
                error_label = LabelComponent(
                    f"  {get_symbol('error')} {self.validation_error}",
                    style="class:label.error",
                )
                return HSplit([self.label, main_container, error_label])
            else:
                return HSplit([self.label, main_container])
        else:
            if self.validation_error:
                error_label = LabelComponent(
                    f"  {get_symbol('error')} {self.validation_error}",
                    style="class:label.error",
                )
                return HSplit([main_container, error_label])
            else:
                return main_container
