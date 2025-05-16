"""
Base component classes for Aider-Start TUI.
Provides foundational components that other components extend.
"""

from prompt_toolkit.layout import (
    Window,
    FormattedTextControl,
    HSplit,
    VSplit,
    ScrollablePane,
)
from prompt_toolkit.layout.dimension import Dimension, D
from prompt_toolkit.widgets import Box
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import has_focus, is_done
from prompt_toolkit.mouse_events import MouseEventType

from ..style import get_symbol


class Component:
    """Base class for all UI components"""

    def __init__(self):
        """Initialize component"""
        self.key_bindings = KeyBindings()

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.
        This is an abstract method that should be implemented by subclasses.

        Returns:
            prompt_toolkit container: The component's container
        """
        raise NotImplementedError("Subclasses must implement this method")


class FocusableComponent(Component):
    """Base class for focusable components"""

    def __init__(self):
        """Initialize focusable component"""
        super().__init__()
        self.has_focus = has_focus(self)
        self.focus_handlers = []
        self.blur_handlers = []

    def add_focus_handler(self, handler):
        """
        Add focus event handler.

        Args:
            handler (callable): Function to call when component receives focus
        """
        self.focus_handlers.append(handler)

    def add_blur_handler(self, handler):
        """
        Add blur event handler.

        Args:
            handler (callable): Function to call when component loses focus
        """
        self.blur_handlers.append(handler)

    def on_focus(self):
        """Called when component receives focus"""
        for handler in self.focus_handlers:
            handler()

    def on_blur(self):
        """Called when component loses focus"""
        for handler in self.blur_handlers:
            handler()


class DisableableComponent(Component):
    """Base class for components that can be disabled"""

    def __init__(self, disabled=False):
        """
        Initialize disableable component.

        Args:
            disabled (bool): Whether the component is initially disabled
        """
        super().__init__()
        self.disabled = disabled

    def enable(self):
        """Enable the component"""
        self.disabled = False

    def disable(self):
        """Disable the component"""
        self.disabled = True

    def toggle_enabled(self):
        """Toggle the component's enabled state"""
        self.disabled = not self.disabled


class ClickableComponent(FocusableComponent):
    """Base class for clickable components"""

    def __init__(self):
        """Initialize clickable component"""
        super().__init__()
        self.click_handlers = []

    def add_click_handler(self, handler):
        """
        Add click event handler.

        Args:
            handler (callable): Function to call when component is clicked
        """
        self.click_handlers.append(handler)

    def on_click(self):
        """Called when component is clicked"""
        for handler in self.click_handlers:
            handler()


class StatefulComponent(Component):
    """Base class for components with state"""

    def __init__(self):
        """Initialize stateful component"""
        super().__init__()
        self.state_handlers = []

    def add_state_handler(self, handler):
        """
        Add state change handler.

        Args:
            handler (callable): Function to call when component state changes
        """
        self.state_handlers.append(handler)

    def on_state_change(self):
        """Called when component state changes"""
        for handler in self.state_handlers:
            handler()


class FormComponent(FocusableComponent):
    """Base class for form components"""

    def __init__(self, name, value=None):
        """
        Initialize form component.

        Args:
            name (str): Form field name
            value: Initial value
        """
        super().__init__()
        self.name = name
        self.value = value
        self.validators = []
        self.change_handlers = []
        self.validation_error = None
        self.label = None  # Initialize label attribute

    def add_validator(self, validator, error_message=None):
        """
        Add value validator.

        Args:
            validator (callable): Function that validates the value and returns a boolean
            error_message (str): Message to display if validation fails
        """
        self.validators.append((validator, error_message))

    def add_change_handler(self, handler):
        """
        Add value change handler.

        Args:
            handler (callable): Function to call when value changes
        """
        self.change_handlers.append(handler)

    def on_value_change(self):
        """Called when value changes"""
        self.validate()

        for handler in self.change_handlers:
            handler(self.value)

    def validate(self):
        """
        Validate the current value.

        Returns:
            bool: Whether validation passed
        """
        for validator, error_message in self.validators:
            if not validator(self.value):
                self.validation_error = error_message or "Invalid value"
                return False

        self.validation_error = None
        return True

    def is_valid(self):
        """
        Check if the component has a valid value.

        Returns:
            bool: Whether the value is valid
        """
        return self.validate()


class ContainerComponent(Component):
    """Base class for container components"""

    def __init__(self, children=None):
        """
        Initialize container component.

        Args:
            children (list): Child components
        """
        super().__init__()
        self.children = children or []

    def add_child(self, child):
        """
        Add a child component.

        Args:
            child: Child component
        """
        self.children.append(child)

    def remove_child(self, child):
        """
        Remove a child component.

        Args:
            child: Child component to remove
        """
        if child in self.children:
            self.children.remove(child)


class LabelComponent(Component):
    """Text label component"""

    def __init__(self, text, style="class:label"):
        """
        Initialize label component.

        Args:
            text (str): Label text
            style (str): Label style
        """
        super().__init__()
        self.text = text
        self.style = style
        self.formatted_text = None
        self._update_text()

    def set_text(self, text):
        """
        Set label text.

        Args:
            text (str): New text
        """
        self.text = text
        self._update_text()

    def _update_text(self):
        """Update formatted text from current text"""
        if isinstance(self.text, str) and "<" in self.text and ">" in self.text:
            # Assume HTML formatting
            self.formatted_text = HTML(self.text)
        else:
            self.formatted_text = self.text

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Window: The label window
        """
        return Window(
            FormattedTextControl(self.formatted_text),
            dont_extend_height=True,
            style=self.style,
        )


class SeparatorComponent(Component):
    """Horizontal or vertical separator component"""

    def __init__(self, vertical=False, char=None, style="class:separator"):
        """
        Initialize separator component.

        Args:
            vertical (bool): Whether the separator is vertical
            char (str, optional): Custom separator character
            style (str): Separator style
        """
        super().__init__()
        self.vertical = vertical

        if char is None:
            self.char = get_symbol("v_line" if vertical else "h_line")
        else:
            self.char = char

        self.style = style

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Window: The separator window
        """
        if self.vertical:
            return Window(width=D.exact(1), char=self.char, style=self.style)
        else:
            return Window(height=D.exact(1), char=self.char, style=self.style)


class SpacerComponent(Component):
    """Flexible space component"""

    def __init__(self, width=None, height=None, char=" "):
        """
        Initialize spacer component.

        Args:
            width (Dimension, optional): Width dimension
            height (Dimension, optional): Height dimension
            char (str): Spacer fill character
        """
        super().__init__()

        if width is None and height is None:
            # Default to horizontal flexible space
            self.width = D(weight=1)
            self.height = D.exact(1)
        else:
            self.width = width
            self.height = height

        self.char = char

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Window: The spacer window
        """
        return Window(width=self.width, height=self.height, char=self.char)


class BorderComponent(ContainerComponent):
    """Container with a border"""

    def __init__(self, child, title=None, style="class:frame", padding=0):
        """
        Initialize border component.

        Args:
            child: Child component
            title (str, optional): Border title
            style (str): Border style
            padding (int): Padding inside the border
        """
        super().__init__([child])
        self.title = title
        self.style = style
        self.padding = padding

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Frame: The bordered container
        """
        from prompt_toolkit.widgets import Frame, Box

        content = self.children[0]

        if self.padding > 0:
            content = Box(content, padding=self.padding)

        return Frame(content, title=self.title, style=self.style)


class ScrollableComponent(ContainerComponent):
    """Container with scrollable content"""

    def __init__(self, child, scrollbar=True, style="class:scrollable"):
        """
        Initialize scrollable component.

        Args:
            child: Child component
            scrollbar (bool): Whether to show a scrollbar
            style (str): Scrollbar style
        """
        super().__init__([child])
        self.scrollbar = scrollbar
        self.style = style

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            ScrollablePane: The scrollable container
        """
        return ScrollablePane(
            self.children[0], scrollbar=self.scrollbar, style=self.style
        )


class KeybindingComponent(Component):
    """Component that adds custom keybindings"""

    def __init__(self, child):
        """
        Initialize keybinding component.

        Args:
            child: Child component
        """
        super().__init__()
        self.child = child

    def add_keybinding(self, key, handler, filter=None):
        """
        Add a keybinding.

        Args:
            key (str): Key combination (e.g., "c-a" for Ctrl+A)
            handler (callable): Function to call when key is pressed
            filter (Filter, optional): Condition when binding is active
        """

        @self.key_bindings.add(key, filter=filter)
        def _(event):
            return handler(event)

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Container: The child container with keybindings
        """
        return self.child
