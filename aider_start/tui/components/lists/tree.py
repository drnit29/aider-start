
from prompt_toolkit.layout import HSplit, Window, FormattedTextControl, ScrollablePane
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.filters import has_focus
from prompt_toolkit.mouse_events import MouseEventType

from ..base import FocusableComponent
from .list_item import ListItem
from ..style import get_symbol

class TreeItem(ListItem):
    """Tree view item component"""

    def __init__(
        self,
        text,
        data=None,
        style="class:tree-item",
        selected=False,
        expanded=False,
        parent=None,
        children=None,
    ):
        super().__init__(text, data, style, selected)
        self.expanded = expanded
        self.parent = parent
        self.children = children or []

    def _create_control(self):
        def get_formatted_text():
            indent = 0
            parent = self.parent
            while parent:
                indent += 2
                parent = parent.parent

            if self.children:
                icon = get_symbol("down" if self.expanded else "forward")
            else:
                icon = " "

            indented_text = " " * indent + f"{icon} {self.text}"

            if self.selected and self.has_focus():
                style = f"{self.base_style}.selected.focused"
            elif self.selected:
                style = f"{self.base_style}.selected"
            elif self.has_focus():
                style = f"{self.base_style}.focused"
            else:
                style = self.base_style

            return [(style, indented_text)]

        self.control = FormattedTextControl(
            get_formatted_text,
            focusable=True,
            key_bindings=self.key_bindings,
            show_cursor=False,
            mouse_handlers=self._get_mouse_handlers(),
        )

        @self.key_bindings.add("enter", filter=has_focus(self))
        def _(event):
            self.on_click()
            event.app.invalidate()

        @self.key_bindings.add("space", filter=has_focus(self))
        def _(event):
            self.toggle_expanded()
            event.app.invalidate()

        @self.key_bindings.add("right", filter=has_focus(self))
        def _(event):
            if self.children and not self.expanded:
                self.expanded = True
                event.app.invalidate()

        @self.key_bindings.add("left", filter=has_focus(self))
        def _(event):
            if self.expanded:
                self.expanded = False
                event.app.invalidate()

    def _get_mouse_handlers(self):
        mouse_handlers = {}

        def mouse_handler(mouse_event):
            if mouse_event.event_type == MouseEventType.MOUSE_UP:
                text_position = mouse_event.position.x
                indent = 0
                parent = self.parent
                while parent:
                    indent += 2
                    parent = parent.parent

                if self.children and text_position == indent:
                    self.toggle_expanded()
                else:
                    self.on_click()

                return None
            return NotImplemented

        mouse_handlers[MouseEventType.MOUSE_UP] = mouse_handler
        return mouse_handlers

    def toggle_expanded(self):
        if self.children:
            self.expanded = not self.expanded

    def add_child(self, text, data=None):
        child = TreeItem(text, data, self.base_style, False, False, self)
        self.children.append(child)
        return child

class TreeView(FocusableComponent):
    """Tree view component with hierarchical items"""

    def __init__(self, style="class:tree-view"):
        super().__init__()
        self.style = style
        self.root_items = []
        self.flat_items = []
        self.selection_changed_handlers = []

        self._setup_key_bindings()

    def _setup_key_bindings(self):
        @self.key_bindings.add("up", filter=has_focus(self))
        def _(event):
            self.select_previous()
            event.app.invalidate()

        @self.key_bindings.add("down", filter=has_focus(self))
        def _(event):
            self.select_next()
            event.app.invalidate()

    def add_selection_changed_handler(self, handler):
        self.selection_changed_handlers.append(handler)

    def _on_selection_changed(self):
        for handler in self.selection_changed_handlers:
            handler(self.get_selected_item())

    def _on_item_click(self, item):
        for other_item in self.flat_items:
            if other_item is not item:
                other_item.selected = False
        item.selected = True

        self._on_selection_changed()

    def add_item(self, text, data=None):
        item = TreeItem(text, data, f"{self.style}.item")
        item.add_click_handler(lambda i=item: self._on_item_click(i))
        self.root_items.append(item)
        self._update_flat_items()
        return item

    def _update_flat_items(self):
        self.flat_items = []

        def add_item_and_children(item):
            self.flat_items.append(item)
            if item.expanded:
                for child in item.children:
                    add_item_and_children(child)

        for item in self.root_items:
            add_item_and_children(item)

    def get_selected_item(self):
        for item in self.flat_items:
            if item.selected:
                return item
        return None

    def select_item(self, item):
        if item in self.flat_items:
            for other_item in self.flat_items:
                if other_item is not item:
                    other_item.selected = False

            item.selected = True
            self._on_selection_changed()

    def select_next(self):
        if not self.flat_items:
            return

        selected = self.get_selected_item()
        if selected:
            index = self.flat_items.index(selected)
            new_index = min(len(self.flat_items) - 1, index + 1)
        else:
            new_index = 0

        self.select_item(self.flat_items[new_index])

    def select_previous(self):
        if not self.flat_items:
            return

        selected = self.get_selected_item()
        if selected:
            index = self.flat_items.index(selected)
            new_index = max(0, index - 1)
        else:
            new_index = 0

        self.select_item(self.flat_items[new_index])

    def __pt_container__(self):
        self._update_flat_items()

        if not self.flat_items:
            return Window(FormattedTextControl("(empty)"), style=f"{self.style}.empty")

        container = HSplit(self.flat_items)
        return ScrollablePane(container, style=self.style)
