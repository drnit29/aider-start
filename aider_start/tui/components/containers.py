"""
Container components for Aider-Start TUI.
Provides layout and container components.
"""

from prompt_toolkit.layout import (
    HSplit,
    VSplit,
    Window,
    FormattedTextControl,
    FloatContainer,
    Float,
)
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Box, Frame, Shadow
from prompt_toolkit.formatted_text import HTML

from .base import Component, FocusableComponent
from ..style import get_symbol


class BoxContainer(Component):
    """Box container component with padding and borders"""

    def __init__(self, child, padding=1, style="class:box", title=None, border=True):
        """
        Initialize box container component.

        Args:
            child: Child component
            padding (int): Padding inside the box
            style (str): Box style
            title (str, optional): Box title
            border (bool): Whether to show a border
        """
        super().__init__()
        self.child = child
        self.padding = padding
        self.style = style
        self.title = title
        self.border = border

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Container: The box container
        """
        content = self.child

        if self.padding > 0:
            content = Box(content, padding=self.padding)

        if self.border:
            content = Frame(content, title=self.title, style=self.style)

        return content


class RowContainer(Component):
    """Row container component for horizontal layout"""

    def __init__(
        self, children, spacing=1, equal_width=False, padding=0, style="class:row"
    ):
        """
        Initialize row container component.

        Args:
            children (list): Child components
            spacing (int): Spacing between children
            equal_width (bool): Whether children should have equal width
            padding (int): Padding inside the container
            style (str): Container style
        """
        super().__init__()
        self.children = children
        self.spacing = spacing
        self.equal_width = equal_width
        self.padding = padding
        self.style = style

    def add_child(self, child):
        """
        Add a child component.

        Args:
            child: Child component
        """
        self.children.append(child)

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Container: The row container
        """
        # Add spacing between children
        spaced_children = []

        if self.padding > 0:
            # Add left padding
            spaced_children.append(Window(width=D.exact(self.padding)))

        for i, child in enumerate(self.children):
            spaced_children.append(child)

            # Add spacing after each child except the last one
            if i < len(self.children) - 1 and self.spacing > 0:
                spaced_children.append(Window(width=D.exact(self.spacing)))

        if self.padding > 0:
            # Add right padding
            spaced_children.append(Window(width=D.exact(self.padding)))

        return VSplit(
            spaced_children,
            style=self.style,
            padding=0,
            padding_char=" ",
            padding_style=self.style,
            width_for_exact_window_indices=None if self.equal_width else [],
        )


class ColumnContainer(Component):
    """Column container component for vertical layout"""

    def __init__(
        self, children, spacing=1, equal_height=False, padding=0, style="class:column"
    ):
        """
        Initialize column container component.

        Args:
            children (list): Child components
            spacing (int): Spacing between children
            equal_height (bool): Whether children should have equal height
            padding (int): Padding inside the container
            style (str): Container style
        """
        super().__init__()
        self.children = children
        self.spacing = spacing
        self.equal_height = equal_height
        self.padding = padding
        self.style = style

    def add_child(self, child):
        """
        Add a child component.

        Args:
            child: Child component
        """
        self.children.append(child)

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Container: The column container
        """
        # Add spacing between children
        spaced_children = []

        if self.padding > 0:
            # Add top padding
            spaced_children.append(Window(height=D.exact(self.padding)))

        for i, child in enumerate(self.children):
            spaced_children.append(child)

            # Add spacing after each child except the last one
            if i < len(self.children) - 1 and self.spacing > 0:
                spaced_children.append(Window(height=D.exact(self.spacing)))

        if self.padding > 0:
            # Add bottom padding
            spaced_children.append(Window(height=D.exact(self.padding)))

        return HSplit(
            spaced_children,
            style=self.style,
            padding=0,
            padding_char=" ",
            padding_style=self.style,
            height_for_exact_window_indices=None if self.equal_height else [],
        )


class SplitContainer(Component):
    """Splitter container that can be adjusted dynamically"""

    def __init__(
        self,
        left_or_top,
        right_or_bottom,
        vertical=False,
        initial_split=0.5,
        min_split=0.1,
        max_split=0.9,
        style="class:split",
    ):
        """
        Initialize split container component.

        Args:
            left_or_top: Left or top component
            right_or_bottom: Right or bottom component
            vertical (bool): Whether the split is vertical
            initial_split (float): Initial split position (0.0 to 1.0)
            min_split (float): Minimum split position
            max_split (float): Maximum split position
            style (str): Container style
        """
        super().__init__()
        self.left_or_top = left_or_top
        self.right_or_bottom = right_or_bottom
        self.vertical = vertical
        self.split = min(max(initial_split, min_split), max_split)
        self.min_split = min_split
        self.max_split = max_split
        self.style = style

        self._setup_key_bindings()

    def _setup_key_bindings(self):
        """Set up key bindings for the split container"""

        @self.key_bindings.add("left", filter=has_focus(self) & ~self.vertical)
        def _(event):
            self.decrease_split(0.05)
            event.app.invalidate()

        @self.key_bindings.add("right", filter=has_focus(self) & ~self.vertical)
        def _(event):
            self.increase_split(0.05)
            event.app.invalidate()

        @self.key_bindings.add("up", filter=has_focus(self) & self.vertical)
        def _(event):
            self.decrease_split(0.05)
            event.app.invalidate()

        @self.key_bindings.add("down", filter=has_focus(self) & self.vertical)
        def _(event):
            self.increase_split(0.05)
            event.app.invalidate()

    def increase_split(self, amount=0.1):
        """
        Increase split position.

        Args:
            amount (float): Amount to increase by
        """
        self.split = min(self.split + amount, self.max_split)

    def decrease_split(self, amount=0.1):
        """
        Decrease split position.

        Args:
            amount (float): Amount to decrease by
        """
        self.split = max(self.split - amount, self.min_split)

    def set_split(self, position):
        """
        Set split position.

        Args:
            position (float): New split position (0.0 to 1.0)
        """
        self.split = min(max(position, self.min_split), self.max_split)

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Container: The split container
        """
        if self.vertical:
            return HSplit(
                [
                    self.left_or_top,
                    # Separator
                    Window(
                        height=D.exact(1), char="─", style=f"{self.style}.separator"
                    ),
                    self.right_or_bottom,
                ],
                style=self.style,
                heights=[D(weight=self.split), D.exact(1), D(weight=1.0 - self.split)],
            )
        else:
            return VSplit(
                [
                    self.left_or_top,
                    # Separator
                    Window(width=D.exact(1), char="│", style=f"{self.style}.separator"),
                    self.right_or_bottom,
                ],
                style=self.style,
                widths=[D(weight=self.split), D.exact(1), D(weight=1.0 - self.split)],
            )


class CardContainer(Component):
    """Card container with title, content, and footer"""

    def __init__(self, title, content, footer=None, style="class:card", padding=1):
        """
        Initialize card container component.

        Args:
            title (str): Card title
            content: Card content
            footer: Card footer (optional)
            style (str): Card style
            padding (int): Padding inside the card
        """
        super().__init__()
        self.title = title
        self.content = content
        self.footer = footer
        self.style = style
        self.padding = padding

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Container: The card container
        """
        # Create title bar
        title_bar = Window(
            FormattedTextControl(HTML(f"<b>{self.title}</b>")),
            height=D.exact(1),
            style=f"{self.style}.title",
        )

        # Create content area with padding
        content_area = Box(
            self.content, padding=self.padding, style=f"{self.style}.content"
        )

        if self.footer:
            # Create footer separator and area
            footer_separator = Window(
                height=D.exact(1), char="─", style=f"{self.style}.separator"
            )

            footer_area = self.footer

            # Combine all parts
            card_content = HSplit(
                [
                    title_bar,
                    Window(
                        height=D.exact(1), char="─", style=f"{self.style}.separator"
                    ),
                    content_area,
                    footer_separator,
                    footer_area,
                ]
            )
        else:
            # No footer, just title and content
            card_content = HSplit(
                [
                    title_bar,
                    Window(
                        height=D.exact(1), char="─", style=f"{self.style}.separator"
                    ),
                    content_area,
                ]
            )

        # Create frame around the card
        return Frame(card_content, style=self.style)


class TabContainer(FocusableComponent):
    """Tab container with switchable tabs"""

    def __init__(self, tabs, active_tab=0, style="class:tabs"):
        """
        Initialize tab container component.

        Args:
            tabs (list): List of (title, content) tuples
            active_tab (int): Initially active tab index
            style (str): Tab container style
        """
        super().__init__()
        self.tabs = tabs
        self.active_tab = active_tab
        self.style = style

        self._setup_key_bindings()

    def _setup_key_bindings(self):
        """Set up key bindings for the tab container"""

        @self.key_bindings.add("tab", filter=has_focus(self))
        def _(event):
            self.next_tab()
            event.app.invalidate()

        @self.key_bindings.add("s-tab", filter=has_focus(self))
        def _(event):
            self.previous_tab()
            event.app.invalidate()

    def next_tab(self):
        """Switch to the next tab"""
        self.active_tab = (self.active_tab + 1) % len(self.tabs)

    def previous_tab(self):
        """Switch to the previous tab"""
        self.active_tab = (self.active_tab - 1) % len(self.tabs)

    def switch_to_tab(self, index):
        """
        Switch to a specific tab.

        Args:
            index (int): Tab index
        """
        if 0 <= index < len(self.tabs):
            self.active_tab = index

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Container: The tab container
        """
        # Create tab headers
        tab_headers = []
        for i, (title, _) in enumerate(self.tabs):
            # Determine tab style
            if i == self.active_tab:
                tab_style = f"{self.style}.active"

                # Add left and right borders for active tab
                left_border = get_symbol("tl_corner")
                right_border = get_symbol("tr_corner")
                bottom_border = " "  # No bottom border for active tab
            else:
                tab_style = f"{self.style}.inactive"

                # Plain spaces for inactive tabs
                left_border = " "
                right_border = " "
                bottom_border = get_symbol("h_line")

            # Create tab header
            tab_header = Window(
                FormattedTextControl(f"{left_border}{title}{right_border}"),
                style=tab_style,
                width=len(title) + 2,
                height=D.exact(1),
                dont_extend_width=True,
            )

            tab_headers.append(tab_header)

        # Create tab header row
        header_row = VSplit(tab_headers)

        # Create tab content
        _, content = self.tabs[self.active_tab]

        # Create container with header and content
        return HSplit(
            [
                header_row,
                Window(
                    height=D.exact(1),
                    char=get_symbol("h_line"),
                    style=f"{self.style}.border",
                ),
                content,
            ]
        )


class DialogContainer(Component):
    """Modal dialog container"""

    def __init__(
        self, title, content, buttons, style="class:dialog", width=60, height=None
    ):
        """
        Initialize dialog container component.

        Args:
            title (str): Dialog title
            content: Dialog content
            buttons: Dialog buttons (list of Button components)
            style (str): Dialog style
            width (int): Dialog width
            height (int, optional): Dialog height
        """
        super().__init__()
        self.title = title
        self.content = content
        self.buttons = buttons
        self.style = style
        self.width = width
        self.height = height

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Container: The dialog container
        """
        # Create button row
        button_row = RowContainer(
            self.buttons, spacing=2, style=f"{self.style}.buttons"
        )

        # Create dialog content
        dialog_content = HSplit(
            [
                # Content area
                Box(self.content, padding=1, style=f"{self.style}.content"),
                # Button area
                Box(button_row, padding=1, style=f"{self.style}.footer"),
            ]
        )

        # Create dialog frame
        dialog_frame = Frame(
            dialog_content,
            title=self.title,
            style=self.style,
            width=self.width,
            height=self.height,
        )

        # Add shadow effect
        shadowed_dialog = Shadow(dialog_frame)

        return shadowed_dialog


class TooltipContainer(Component):
    """Tooltip container that shows on hover"""

    def __init__(self, child, tooltip_text, position="bottom", style="class:tooltip"):
        """
        Initialize tooltip container component.

        Args:
            child: Child component to attach tooltip to
            tooltip_text (str): Tooltip text
            position (str): Tooltip position ("top", "bottom", "left", "right")
            style (str): Tooltip style
        """
        super().__init__()
        self.child = child
        self.tooltip_text = tooltip_text
        self.position = position
        self.style = style
        self.show_tooltip = False

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Container: The tooltip container
        """
        # Create tooltip content
        tooltip = Window(
            FormattedTextControl(self.tooltip_text),
            style=self.style,
            dont_extend_width=True,
            dont_extend_height=True,
        )

        # Position the tooltip
        if self.position == "top":
            top = -1
            left = 0
        elif self.position == "bottom":
            top = 1
            left = 0
        elif self.position == "left":
            top = 0
            left = -len(self.tooltip_text) - 2
        else:  # right
            top = 0
            left = 5

        # Create float container
        if self.show_tooltip:
            return FloatContainer(
                content=self.child, floats=[Float(content=tooltip, top=top, left=left)]
            )
        else:
            return self.child

    def show(self):
        """Show the tooltip"""
        self.show_tooltip = True

    def hide(self):
        """Hide the tooltip"""
        self.show_tooltip = False

    def toggle(self):
        """Toggle tooltip visibility"""
        self.show_tooltip = not self.show_tooltip
