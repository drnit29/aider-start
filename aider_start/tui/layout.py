"""
Layout utilities and helpers for Aider-Start TUI.
Provides a responsive grid system and layout containers.
"""

from prompt_toolkit.layout import HSplit, VSplit, Window, FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension, D
from prompt_toolkit.formatted_text import HTML


class ResponsiveLayout:
    """
    Responsive layout system that adapts to different terminal sizes.
    """

    def __init__(self, min_width=80, min_height=24):
        """
        Initialize responsive layout.

        Args:
            min_width (int): Minimum terminal width to enable responsive features
            min_height (int): Minimum terminal height to enable responsive features
        """
        self.min_width = min_width
        self.min_height = min_height
        self.terminal_width = min_width
        self.terminal_height = min_height

    def update_dimensions(self, width, height):
        """
        Update terminal dimensions.

        Args:
            width (int): Current terminal width
            height (int): Current terminal height
        """
        self.terminal_width = max(width, self.min_width)
        self.terminal_height = max(height, self.min_height)

    def get_column_width(self, columns=1, weight=1, min_width=None, max_width=None):
        """
        Calculate column width based on total columns and current terminal width.

        Args:
            columns (int): Total number of columns in the grid
            weight (float): Weight of this column relative to others (1.0 is standard)
            min_width (int): Minimum width of the column
            max_width (int): Maximum width of the column

        Returns:
            Dimension: Prompt toolkit dimension object
        """
        # Calculate proportional width
        base_width = int(self.terminal_width / columns * weight)

        # Apply min/max constraints
        if min_width is not None:
            base_width = max(min_width, base_width)
        if max_width is not None:
            base_width = min(max_width, base_width)

        return D(preferred=base_width)

    def get_row_height(self, rows=1, weight=1, min_height=None, max_height=None):
        """
        Calculate row height based on total rows and current terminal height.

        Args:
            rows (int): Total number of rows in the grid
            weight (float): Weight of this row relative to others (1.0 is standard)
            min_height (int): Minimum height of the row
            max_height (int): Maximum height of the row

        Returns:
            Dimension: Prompt toolkit dimension object
        """
        # Calculate proportional height
        base_height = int(self.terminal_height / rows * weight)

        # Apply min/max constraints
        if min_height is not None:
            base_height = max(min_height, base_height)
        if max_height is not None:
            base_height = min(max_height, base_height)

        return D(preferred=base_height)

    def create_grid(self, components, columns=1):
        """
        Create a grid layout with the given components.

        Args:
            components (list): List of component objects to arrange in the grid
            columns (int): Number of columns in the grid

        Returns:
            HSplit: Container with components arranged in a grid
        """
        rows = []
        current_row = []

        for i, component in enumerate(components):
            current_row.append(component)

            # When we reach the column count or the last component, add the row
            if len(current_row) == columns or i == len(components) - 1:
                # If the row is not full, pad with empty cells
                while len(current_row) < columns:
                    current_row.append(Window())

                rows.append(VSplit(current_row))
                current_row = []

        return HSplit(rows)

    def create_responsive_split(
        self, left_component, right_component, threshold_width=100
    ):
        """
        Create a split that's horizontal if terminal is wide enough, vertical otherwise.

        Args:
            left_component: Left/top component
            right_component: Right/bottom component
            threshold_width (int): Width threshold to switch between VSplit and HSplit

        Returns:
            Union[VSplit, HSplit]: Split container based on terminal width
        """
        if self.terminal_width >= threshold_width:
            # Wide terminal - show components side by side
            return VSplit(
                [
                    left_component,
                    Window(width=D.exact(1), char="│"),  # Separator
                    right_component,
                ]
            )
        else:
            # Narrow terminal - show components stacked
            return HSplit(
                [
                    left_component,
                    Window(height=D.exact(1), char="─"),  # Separator
                    right_component,
                ]
            )


# Layout Containers


class BorderedContainer:
    """Container with a border around content"""

    def __init__(self, body, title=None, style="class:frame"):
        """
        Create a bordered container.

        Args:
            body: The container body
            title (str, optional): Title to display in border
            style (str): Style string for the border
        """
        self.body = body
        self.title = title
        self.style = style

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            prompt_toolkit container: The container with a border
        """
        from prompt_toolkit.widgets import Frame

        return Frame(self.body, title=self.title, style=self.style)


class CardContainer:
    """Card container with title and content sections"""

    def __init__(self, title, content, style="class:card", padding=1):
        """
        Create a card container.

        Args:
            title (str): Card title
            content: Card content
            style (str): Style string for the card
            padding (int): Padding inside the card
        """
        self.title = title
        self.content = content
        self.style = style
        self.padding = padding

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            prompt_toolkit container: The card container
        """
        from prompt_toolkit.widgets import Box, Frame

        title_window = Window(
            FormattedTextControl(HTML(f"<b>{self.title}</b>")),
            height=D.exact(1),
            style=f"{self.style}.title",
        )

        content_box = Box(
            self.content, padding=self.padding, style=f"{self.style}.content"
        )

        return Frame(HSplit([title_window, content_box]), style=self.style)


class TabContainer:
    """Container with tabs for switching between content"""

    def __init__(self, tabs, active_tab=0, style="class:tabs"):
        """
        Create a tab container.

        Args:
            tabs (list): List of (title, content) tuples
            active_tab (int): Index of initially active tab
            style (str): Style string for the tabs
        """
        self.tabs = tabs
        self.active_tab = active_tab
        self.style = style

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            prompt_toolkit container: The tab container
        """
        from prompt_toolkit.widgets import Frame

        # Create tab headers
        tab_headers = []
        for i, (title, _) in enumerate(self.tabs):
            tab_style = (
                f"{self.style}.tab.active"
                if i == self.active_tab
                else f"{self.style}.tab"
            )
            tab_window = Window(
                FormattedTextControl(HTML(f" {title} ")),
                style=tab_style,
                width=D.exact(len(title) + 4),
            )
            tab_headers.append(tab_window)

        headers = VSplit(tab_headers)

        # Get active content
        _, content = self.tabs[self.active_tab]

        # Create container
        return Frame(
            HSplit(
                [
                    headers,
                    Window(
                        height=D.exact(1), char="─", style=f"{self.style}.separator"
                    ),
                    content,
                ]
            ),
            style=self.style,
        )

    def show_tab(self, index):
        """Change the active tab"""
        if 0 <= index < len(self.tabs):
            self.active_tab = index


class ScrollContainer:
    """Container with scrollable content"""

    def __init__(self, content, scrollbar=True, style="class:scroll"):
        """
        Create a scrollable container.

        Args:
            content: The container content
            scrollbar (bool): Whether to show a scrollbar
            style (str): Style string for the scrollbar
        """
        self.content = content
        self.scrollbar = scrollbar
        self.style = style

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            prompt_toolkit container: The scrollable container
        """
        from prompt_toolkit.widgets import Frame

        return HSplit(
            [Window(self.content, scrollbar=self.scrollbar, style=self.style)]
        )


# Screen templates


def create_list_view_template(
    title, list_content, status_bar=None, actions=None, detail_panel=None
):
    """
    Create a list view screen template.

    Args:
        title (str): Screen title
        list_content: The main list container
        status_bar: Status bar content
        actions: Action buttons/controls
        detail_panel: Optional detail panel for selected item

    Returns:
        HSplit: Container with list view layout
    """
    layout = ResponsiveLayout()

    header = Window(
        FormattedTextControl(HTML(f"<b>{title}</b>")),
        height=D.exact(1),
        style="class:title",
    )

    main_container = list_content

    if detail_panel:
        main_container = layout.create_responsive_split(list_content, detail_panel)

    if actions:
        action_bar = HSplit([Window(height=D.exact(1), char="─"), actions])
    else:
        action_bar = Window()

    if status_bar:
        status_container = BorderedContainer(status_bar, style="class:status")
    else:
        status_container = Window(height=D.exact(1))

    return HSplit(
        [
            header,
            Window(height=D.exact(1)),
            main_container,
            action_bar,
            status_container,
        ]
    )


def create_form_template(title, form_content, buttons=None):
    """
    Create a form screen template.

    Args:
        title (str): Form title
        form_content: The form fields container
        buttons: Action buttons

    Returns:
        HSplit: Container with form layout
    """
    header = Window(
        FormattedTextControl(HTML(f"<b>{title}</b>")),
        height=D.exact(1),
        style="class:title",
    )

    form_container = BorderedContainer(form_content, style="class:form")

    if buttons:
        button_container = VSplit(
            [Window(width=D(weight=1)), buttons]  # Fill space to right-align buttons
        )
    else:
        button_container = Window(height=D.exact(1))

    return HSplit(
        [
            header,
            Window(height=D.exact(1)),
            form_container,
            Window(height=D.exact(1)),
            button_container,
        ]
    )


def create_dialog_template(title, content, buttons):
    """
    Create a dialog template.

    Args:
        title (str): Dialog title
        content: Dialog content
        buttons: Dialog buttons

    Returns:
        Frame: Dialog container
    """
    from prompt_toolkit.widgets import Frame, Box, Shadow

    dialog_content = HSplit(
        [
            Window(
                FormattedTextControl(HTML(f"<b>{title}</b>")),
                height=D.exact(1),
                style="class:dialog.title",
            ),
            Window(height=D.exact(1), char="─"),
            Box(content, padding=1),
            Window(height=D.exact(1)),
            VSplit(
                [
                    Window(width=D(weight=1)),  # Fill space to right-align buttons
                    buttons,
                ]
            ),
        ]
    )

    dialog = Frame(dialog_content, style="class:dialog")

    # Add shadow effect
    return Shadow(dialog)


# Utility functions


def create_spacer(height=1):
    """Create a vertical spacer with specified height"""
    return Window(height=D.exact(height))


def create_horizontal_separator(char="─", style="class:separator"):
    """Create a horizontal separator line"""
    return Window(height=D.exact(1), char=char, style=style)


def create_vertical_separator(char="│", style="class:separator"):
    """Create a vertical separator line"""
    return Window(width=D.exact(1), char=char, style=style)
