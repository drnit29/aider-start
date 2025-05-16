"""
Components package for Aider-Start TUI.
Exports all UI components.
"""

# Base components
from .base import (
    Component,
    FocusableComponent,
    DisableableComponent,
    ClickableComponent,
    StatefulComponent,
    FormComponent,
    ContainerComponent,
    LabelComponent,
    SeparatorComponent,
    SpacerComponent,
    BorderComponent,
    ScrollableComponent,
    KeybindingComponent,
)

# Button components
from .buttons import (
    Button,
    IconButton,
    SelectableButton,
    ButtonGroup,
    RadioButtonGroup,
    DropdownButton,
)

# Form input components
from .inputs import InputField, CheckBox, RadioButton, RadioGroup, SelectField, Form

# List and table components
from .lists import ListItem, ListView, ListSeparator, Table, TreeItem, TreeView

# Container components
from .containers import (
    BoxContainer,
    RowContainer,
    ColumnContainer,
    SplitContainer,
    CardContainer,
    TabContainer,
    DialogContainer,
    TooltipContainer,
)

# For convenience, export all components in a flat namespace
__all__ = [
    # Base components
    "Component",
    "FocusableComponent",
    "DisableableComponent",
    "ClickableComponent",
    "StatefulComponent",
    "FormComponent",
    "ContainerComponent",
    "LabelComponent",
    "SeparatorComponent",
    "SpacerComponent",
    "BorderComponent",
    "ScrollableComponent",
    "KeybindingComponent",
    # Button components
    "Button",
    "IconButton",
    "SelectableButton",
    "ButtonGroup",
    "RadioButtonGroup",
    "DropdownButton",
    # Form input components
    "InputField",
    "CheckBox",
    "RadioButton",
    "RadioGroup",
    "SelectField",
    "Form",
    # List and table components
    "ListItem",
    "ListView",
    "ListSeparator",
    "Table",
    "TreeItem",
    "TreeView",
    # Container components
    "BoxContainer",
    "RowContainer",
    "ColumnContainer",
    "SplitContainer",
    "CardContainer",
    "TabContainer",
    "DialogContainer",
    "TooltipContainer",
]
