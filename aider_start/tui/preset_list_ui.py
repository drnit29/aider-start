from prompt_toolkit.layout.containers import (
    Window,
    HSplit,
    VSplit,
    ConditionalContainer,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.dimension import Dimension


def make_header(title_text: FormattedText):
    """Create a more elegant header with proper spacing."""
    return HSplit(
        [
            # Top margin
            Window(height=1, char=" "),
            # Header content with left padding
            VSplit(
                [
                    Window(width=2, char=" "),  # Left margin
                    Window(
                        FormattedTextControl(title_text, focusable=False),
                        height=1,
                        style="class:title",
                    ),
                ]
            ),
            # Bottom separator with subtle styling
            Window(height=1, char="━", style="class:separator"),
        ]
    )


def make_status_bar(status_formatted_text: FormattedText):
    """Create a more polished status bar with proper spacing."""
    return HSplit(
        [
            # Top separator
            Window(height=1, char="━", style="class:separator"),
            # Status bar content
            Window(
                FormattedTextControl(status_formatted_text, focusable=False),
                height=1,
                style="class:status",
            ),
        ]
    )


def make_filter_bar_section(filter_text_area: TextArea):
    """Create a more visually distinct filter bar section."""
    return HSplit(
        [
            # Filter text area with improved styling
            filter_text_area,
            # Bottom separator
            Window(height=1, char="╌", style="class:frame.label"),
        ]
    )


def make_conditional_filter_bar(filter_bar_section, show_filter_bar_condition):
    """Create a conditional container for the filter bar with smooth transitions."""
    return ConditionalContainer(
        content=filter_bar_section, filter=show_filter_bar_condition
    )


def make_main_layout(header, conditional_filter_bar, body, status_bar):
    """Create a more structured and visually balanced main layout."""
    return HSplit(
        [
            # Header section
            header,
            # Filter bar (conditional)
            conditional_filter_bar,
            # Main content area with margins
            HSplit(
                [
                    # Top margin for content
                    Window(height=1, char=" "),
                    # Main body with side margins
                    VSplit(
                        [
                            # Left margin
                            Window(width=1, char=" "),
                            # Main content
                            body,
                            # Right margin
                            Window(width=1, char=" "),
                        ]
                    ),
                    # Bottom margin for content
                    Window(height=1, char=" "),
                ]
            ),
            # Status bar
            status_bar,
        ]
    )


def create_bordered_container(content, title=None):
    """
    Create a bordered container for content with an optional title.
    Useful for creating card-like UI elements.
    """
    # Top border with optional title
    if title:
        title_text = FormattedText([("class:frame.label", f" {title} ")])
        top_border = VSplit(
            [
                Window(width=1, char="┌"),
                Window(FormattedTextControl(title_text)),
                Window(char="┐", width=Dimension(weight=1)),
            ]
        )
    else:
        top_border = Window(char="┌┐", width=Dimension(weight=1))

    # Side borders with content
    middle = VSplit(
        [
            Window(width=1, char="│"),
            content,
            Window(width=1, char="│"),
        ]
    )

    # Bottom border
    bottom_border = Window(char="└┘", width=Dimension(weight=1))

    return HSplit([top_border, middle, bottom_border])
