"""
Button components for Aider-Start TUI.
Provides various button types and styles.
"""

from prompt_toolkit.layout import Window, HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.mouse_events import MouseEventType
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding.key_processor import KeyPress
from prompt_toolkit.keys import Keys
from prompt_toolkit.filters import has_focus

from .base import ClickableComponent, DisableableComponent


class Button(ClickableComponent, DisableableComponent):
    """Standard button component"""

    def __init__(
        self, text, handler=None, style="class:button", width=None, key=None, icon=None
    ):
        """
        Initialize button component.

        Args:
            text (str): Button text
            handler (callable, optional): Click handler
            style (str): Button style
            width (int, optional): Fixed button width
            key (str, optional): Keyboard shortcut
            icon (str, optional): Button icon
        """
        ClickableComponent.__init__(self)
        DisableableComponent.__init__(self)

        self.text = text
        self.base_style = style
        self.width = width
        self.key = key
        self.icon = icon
        self.pressed = False

        if handler:
            self.add_click_handler(handler)

        self._create_control()
        self._setup_key_bindings()

    def _create_control(self):
        """Create the button control"""

        def get_formatted_text():
            result = []

            # Prepare the button text with optional icon
            button_text = self.text
            if self.icon:
                button_text = f"{self.icon} {button_text}"

            # Add key shortcut if defined
            if self.key:
                button_text = f"{button_text} ({self.key})"

            # Format the text based on state
            if self.disabled:
                style = f"{self.base_style}.disabled"
            elif self.pressed:
                style = f"{self.base_style}.active"
            elif self.has_focus():
                style = f"{self.base_style}.focused"
            else:
                style = self.base_style

            result.append((style, button_text))
            return result

        self.control = FormattedTextControl(
            get_formatted_text,
            key_bindings=self.key_bindings,
            focusable=True,
            show_cursor=False,
            mouse_handlers=self._get_mouse_handlers(),
        )

    def _get_mouse_handlers(self):
        """Get mouse event handlers"""
        mouse_handlers = {}

        def mouse_handler(mouse_event):
            if mouse_event.event_type == MouseEventType.MOUSE_UP and not self.disabled:
                self.on_click()
                return None
            return NotImplemented

        mouse_handlers[MouseEventType.MOUSE_UP] = mouse_handler

        def mouse_down_handler(mouse_event):
            if (
                mouse_event.event_type == MouseEventType.MOUSE_DOWN
                and not self.disabled
            ):
                self.pressed = True
                return None
            return NotImplemented

        mouse_handlers[MouseEventType.MOUSE_DOWN] = mouse_down_handler

        def mouse_move_handler(mouse_event):
            if mouse_event.event_type == MouseEventType.MOUSE_MOVE:
                self.pressed = False
                return None
            return NotImplemented

        mouse_handlers[MouseEventType.MOUSE_MOVE] = mouse_move_handler

        return mouse_handlers

    def _setup_key_bindings(self):
        """Set up key bindings"""

        @self.key_bindings.add("enter", filter=has_focus(self))
        def _(event):
            if not self.disabled:
                self.pressed = True
                self.on_click()
                event.app.invalidate()

        @self.key_bindings.add("space", filter=has_focus(self))
        def _(event):
            if not self.disabled:
                self.pressed = True
                self.on_click()
                event.app.invalidate()

        # If a shortcut key is defined, bind it
        if self.key:
            # Handle simple keys like "c", "x", etc.
            @self.key_bindings.add(self.key)
            def _(event):
                if not self.disabled:
                    self.pressed = True
                    self.on_click()
                    self.pressed = False
                    event.app.invalidate()

    def set_text(self, text):
        """
        Set button text.

        Args:
            text (str): New button text
        """
        self.text = text

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Window: The button window
        """
        return Window(
            self.control,
            width=D.exact(self.width) if self.width else None,
            height=D.exact(1),
            dont_extend_width=False if self.width else True,
            dont_extend_height=True,
            style=self.base_style,
        )


class IconButton(Button):
    """Button with only an icon"""

    def __init__(
        self, icon, handler=None, style="class:button", tooltip=None, key=None
    ):
        """
        Initialize icon button.

        Args:
            icon (str): Button icon
            handler (callable, optional): Click handler
            style (str): Button style
            tooltip (str, optional): Button tooltip
            key (str, optional): Keyboard shortcut
        """
        super().__init__(
            text="", handler=handler, style=style, width=3, key=key, icon=icon
        )
        self.tooltip = tooltip

    def _create_control(self):
        """Create the icon button control"""

        def get_formatted_text():
            if self.disabled:
                style = f"{self.base_style}.disabled"
            elif self.pressed:
                style = f"{self.base_style}.active"
            elif self.has_focus():
                style = f"{self.base_style}.focused"
            else:
                style = self.base_style

            return [(style, f" {self.icon} ")]

        self.control = FormattedTextControl(
            get_formatted_text,
            key_bindings=self.key_bindings,
            focusable=True,
            show_cursor=False,
            mouse_handlers=self._get_mouse_handlers(),
        )


class SelectableButton(Button):
    """Button that can be selected/toggled"""

    def __init__(
        self,
        text,
        handler=None,
        style="class:button",
        width=None,
        key=None,
        icon=None,
        selected=False,
    ):
        """
        Initialize selectable button.

        Args:
            text (str): Button text
            handler (callable, optional): Click handler
            style (str): Button style
            width (int, optional): Fixed button width
            key (str, optional): Keyboard shortcut
            icon (str, optional): Button icon
            selected (bool): Whether the button is initially selected
        """
        self.selected = selected
        super().__init__(
            text=text, handler=handler, style=style, width=width, key=key, icon=icon
        )

    def _create_control(self):
        """Create the selectable button control"""

        def get_formatted_text():
            result = []

            # Prepare the button text with optional icon
            button_text = self.text
            if self.icon:
                button_text = f"{self.icon} {button_text}"

            # Add key shortcut if defined
            if self.key:
                button_text = f"{button_text} ({self.key})"

            # Format the text based on state
            if self.disabled:
                style = f"{self.base_style}.disabled"
            elif self.selected:
                style = f"{self.base_style}.selected"
            elif self.pressed:
                style = f"{self.base_style}.active"
            elif self.has_focus():
                style = f"{self.base_style}.focused"
            else:
                style = self.base_style

            result.append((style, button_text))
            return result

        self.control = FormattedTextControl(
            get_formatted_text,
            key_bindings=self.key_bindings,
            focusable=True,
            show_cursor=False,
            mouse_handlers=self._get_mouse_handlers(),
        )

    def toggle(self):
        """Toggle the selected state"""
        self.selected = not self.selected

    def select(self):
        """Select the button"""
        self.selected = True

    def deselect(self):
        """Deselect the button"""
        self.selected = False


class ButtonGroup(Button):
    """Group of buttons with grouped behavior"""

    def __init__(self, buttons, direction="horizontal", style="class:button-group"):
        """
        Initialize button group.

        Args:
            buttons (list): List of Button objects
            direction (str): "horizontal" or "vertical"
            style (str): Button group style
        """
        super().__init__(text="", style=style)
        self.buttons = buttons
        self.direction = direction

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Union[HSplit, VSplit]: The button group container
        """
        if self.direction == "vertical":
            from prompt_toolkit.layout import HSplit

            return HSplit(self.buttons)
        else:
            from prompt_toolkit.layout import VSplit

            return VSplit(self.buttons)


class RadioButtonGroup(ButtonGroup):
    """Group of buttons where only one can be selected at a time"""

    def __init__(
        self,
        buttons,
        direction="horizontal",
        style="class:button-group",
        selected_index=0,
    ):
        """
        Initialize radio button group.

        Args:
            buttons (list): List of SelectableButton objects
            direction (str): "horizontal" or "vertical"
            style (str): Button group style
            selected_index (int): Index of initially selected button
        """
        super().__init__(buttons, direction, style)

        # Ensure all buttons are SelectableButton type
        for button in self.buttons:
            if not isinstance(button, SelectableButton):
                raise TypeError("All buttons must be SelectableButton instances")

        # Set up the radio behavior
        for i, button in enumerate(self.buttons):
            # Deselect all buttons initially
            button.deselect()

            # Store the original click handler if any
            original_handlers = button.click_handlers.copy()
            button.click_handlers.clear()

            # Add the radio selection behavior
            button.add_click_handler(lambda i=i: self.select_button(i))

            # Re-add the original handlers
            for handler in original_handlers:
                button.add_click_handler(handler)

        # Select the initial button
        if 0 <= selected_index < len(self.buttons):
            self.select_button(selected_index)

    def select_button(self, index):
        """
        Select a button by index and deselect others.

        Args:
            index (int): Button index to select
        """
        if 0 <= index < len(self.buttons):
            for i, button in enumerate(self.buttons):
                if i == index:
                    button.select()
                else:
                    button.deselect()

    def get_selected_index(self):
        """
        Get the index of the currently selected button.

        Returns:
            int: Selected button index
        """
        for i, button in enumerate(self.buttons):
            if button.selected:
                return i
        return -1

    def get_selected_button(self):
        """
        Get the currently selected button.

        Returns:
            SelectableButton: Selected button
        """
        index = self.get_selected_index()
        if index >= 0:
            return self.buttons[index]
        return None


class DropdownButton(Button):
    """Button that shows a dropdown menu when clicked"""

    def __init__(self, text, menu_items, style="class:button", width=None, key=None):
        """
        Initialize dropdown button.

        Args:
            text (str): Button text
            menu_items (list): List of (text, handler) tuples
            style (str): Button style
            width (int, optional): Fixed button width
            key (str, optional): Keyboard shortcut
        """
        super().__init__(text=text, style=style, width=width, key=key, icon="▼")
        self.menu_items = menu_items
        self.dropdown_visible = False

        # Override click handler to show/hide the dropdown
        self.click_handlers.clear()
        self.add_click_handler(self.toggle_dropdown)

    def toggle_dropdown(self):
        """Toggle dropdown visibility"""
        self.dropdown_visible = not self.dropdown_visible

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Container: The dropdown button container
        """
        button = super().__pt_container__()

        if not self.dropdown_visible:
            return button

        # Create dropdown menu
        menu_items = []
        for text, handler in self.menu_items:
            menu_button = Button(
                text=text,
                handler=lambda h=handler: (h(), self.toggle_dropdown()),
                style=f"{self.base_style}.item",
                width=self.width or max(len(item[0]) for item in self.menu_items) + 4,
            )
            menu_items.append(menu_button)

        from prompt_toolkit.layout import Float, FloatContainer
        from prompt_toolkit.widgets import Shadow

        menu = Shadow(HSplit(menu_items))
        float_container = FloatContainer(
            content=button, floats=[Float(content=menu, top=1, left=0)]
        )

        return float_container
