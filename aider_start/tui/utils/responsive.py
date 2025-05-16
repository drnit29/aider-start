"""
Responsive layout utilities for Aider-Start TUI.
"""

from prompt_toolkit.layout.dimension import D, Dimension
from prompt_toolkit.layout import HSplit, VSplit, Window

from .terminal import get_terminal_size


class ResponsiveSize:
    """Helper class for responsive dimensions"""

    def __init__(self, terminal_width=None, terminal_height=None):
        """
        Initialize responsive size helper.

        Args:
            terminal_width (int, optional): Terminal width
            terminal_height (int, optional): Terminal height
        """
        if terminal_width is None or terminal_height is None:
            width, height = get_terminal_size()
            self.terminal_width = terminal_width or width
            self.terminal_height = terminal_height or height
        else:
            self.terminal_width = terminal_width
            self.terminal_height = terminal_height

    def percent_width(self, percentage):
        """
        Calculate width based on percentage of terminal width.

        Args:
            percentage (float): Percentage (0.0 to 1.0)

        Returns:
            int: Width in characters
        """
        return int(self.terminal_width * percentage)

    def percent_height(self, percentage):
        """
        Calculate height based on percentage of terminal height.

        Args:
            percentage (float): Percentage (0.0 to 1.0)

        Returns:
            int: Height in characters
        """
        return int(self.terminal_height * percentage)

    def width_dimension(self, percentage=None, min_width=None, max_width=None):
        """
        Create a width dimension.

        Args:
            percentage (float, optional): Percentage of terminal width
            min_width (int, optional): Minimum width
            max_width (int, optional): Maximum width

        Returns:
            Dimension: Prompt toolkit dimension
        """
        if percentage is not None:
            width = self.percent_width(percentage)

            if min_width is not None:
                width = max(width, min_width)
            if max_width is not None:
                width = min(width, max_width)

            return D.exact(width)
        else:
            return D()

    def height_dimension(self, percentage=None, min_height=None, max_height=None):
        """
        Create a height dimension.

        Args:
            percentage (float, optional): Percentage of terminal height
            min_height (int, optional): Minimum height
            max_height (int, optional): Maximum height

        Returns:
            Dimension: Prompt toolkit dimension
        """
        if percentage is not None:
            height = self.percent_height(percentage)

            if min_height is not None:
                height = max(height, min_height)
            if max_height is not None:
                height = min(height, max_height)

            return D.exact(height)
        else:
            return D()

    def is_small_terminal(self):
        """
        Check if the terminal is small.

        Returns:
            bool: Whether the terminal is small
        """
        return self.terminal_width < 80 or self.terminal_height < 24

    def is_medium_terminal(self):
        """
        Check if the terminal is medium-sized.

        Returns:
            bool: Whether the terminal is medium-sized
        """
        return (80 <= self.terminal_width < 120) or (24 <= self.terminal_height < 30)

    def is_large_terminal(self):
        """
        Check if the terminal is large.

        Returns:
            bool: Whether the terminal is large
        """
        return self.terminal_width >= 120 and self.terminal_height >= 30


def create_responsive_split(left_or_top, right_or_bottom, min_width_for_horizontal=100):
    """
    Create a split that switches between horizontal and vertical based on terminal width.

    Args:
        left_or_top: Left or top component
        right_or_bottom: Right or bottom component
        min_width_for_horizontal (int): Minimum width to use horizontal split

    Returns:
        Union[HSplit, VSplit]: Split container
    """
    width, _ = get_terminal_size()

    if width >= min_width_for_horizontal:
        # Terminal is wide enough for horizontal layout
        return VSplit(
            [
                left_or_top,
                Window(width=D.exact(1), char="│"),  # Separator
                right_or_bottom,
            ]
        )
    else:
        # Terminal is narrow, use vertical layout
        return HSplit(
            [
                left_or_top,
                Window(height=D.exact(1), char="─"),  # Separator
                right_or_bottom,
            ]
        )


def create_responsive_container(components, min_width_for_grid=100, columns=2):
    """
    Create a container that switches between grid and list based on terminal width.

    Args:
        components (list): List of components
        min_width_for_grid (int): Minimum width to use grid layout
        columns (int): Number of columns in the grid

    Returns:
        Union[HSplit, Float]: Container
    """
    width, _ = get_terminal_size()

    if width >= min_width_for_grid:
        # Terminal is wide enough for grid layout
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
    else:
        # Terminal is narrow, use list layout
        return HSplit(components)


def get_responsive_dimensions(terminal_width=None, terminal_height=None):
    """
    Get responsive dimensions based on terminal size.

    Args:
        terminal_width (int, optional): Terminal width override
        terminal_height (int, optional): Terminal height override

    Returns:
        dict: Dictionary of responsive dimensions
    """
    responsive = ResponsiveSize(terminal_width, terminal_height)

    # Determine appropriate dimensions based on terminal size
    if responsive.is_small_terminal():
        return {
            "sidebar_width": responsive.width_dimension(
                0.3, min_width=15, max_width=25
            ),
            "detail_width": responsive.width_dimension(0.7),
            "list_height": responsive.height_dimension(0.6, min_height=10),
            "form_width": responsive.width_dimension(0.9, max_width=60),
            "dialog_width": responsive.width_dimension(0.9, max_width=50),
            "dialog_height": responsive.height_dimension(0.8, max_height=20),
            "toolbar_height": D.exact(1),
            "status_height": D.exact(1),
            "padding": 0,
            "use_grid": False,
            "columns": 1,
        }
    elif responsive.is_medium_terminal():
        return {
            "sidebar_width": responsive.width_dimension(
                0.25, min_width=20, max_width=30
            ),
            "detail_width": responsive.width_dimension(0.75),
            "list_height": responsive.height_dimension(0.7, min_height=15),
            "form_width": responsive.width_dimension(0.8, max_width=80),
            "dialog_width": responsive.width_dimension(0.7, max_width=70),
            "dialog_height": responsive.height_dimension(0.7, max_height=25),
            "toolbar_height": D.exact(1),
            "status_height": D.exact(1),
            "padding": 1,
            "use_grid": True,
            "columns": 2,
        }
    else:  # Large terminal
        return {
            "sidebar_width": responsive.width_dimension(
                0.2, min_width=25, max_width=40
            ),
            "detail_width": responsive.width_dimension(0.8),
            "list_height": responsive.height_dimension(0.8, min_height=20),
            "form_width": responsive.width_dimension(0.6, max_width=100),
            "dialog_width": responsive.width_dimension(0.5, max_width=80),
            "dialog_height": responsive.height_dimension(0.6, max_height=30),
            "toolbar_height": D.exact(1),
            "status_height": D.exact(2),
            "padding": 2,
            "use_grid": True,
            "columns": 3,
        }


def adapt_layout_to_terminal(layout, update_handler=None):
    """
    Set up a terminal size change handler for responsive layouts.

    Args:
        layout: Application layout
        update_handler (callable, optional): Function to call when terminal size changes

    Returns:
        callable: Function that updates layout based on terminal size
    """
    prev_width, prev_height = get_terminal_size()

    def on_terminal_size_change(width, height):
        """Handle terminal size change"""
        nonlocal prev_width, prev_height

        # Only update if size actually changed
        if width != prev_width or height != prev_height:
            prev_width, prev_height = width, height

            # Call custom update handler if provided
            if update_handler:
                update_handler(width, height)

            # Return True to indicate layout should be redrawn
            return True

        return False

    return on_terminal_size_change
