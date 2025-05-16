
from prompt_toolkit.layout import HSplit, ScrollablePane
from prompt_toolkit.filters import has_focus

from ..base import FocusableComponent
from .list_item import ListItem

class ListView(FocusableComponent):
    """List component with selectable items"""

    def __init__(self, items=None, style="class:list-view", multiselect=False):
        super().__init__()
        self.style = style
        self.multiselect = multiselect
        self.list_items = []
        self.selection_changed_handlers = []

        if items:
            for item in items:
                if isinstance(item, ListItem):
                    self.list_items.append(item)
                elif isinstance(item, tuple) and len(item) == 2:
                    text, data = item
                    self.list_items.append(ListItem(text, data))
                else:
                    self.list_items.append(ListItem(str(item), item))

        self._setup_key_bindings()

        for item in self.list_items:
            item.add_click_handler(lambda i=item: self._on_item_click(i))

    def _setup_key_bindings(self):
        @self.key_bindings.add("up", filter=has_focus(self))
        def _(event):
            self.select_previous()
            event.app.invalidate()

        @self.key_bindings.add("down", filter=has_focus(self))
        def _(event):
            self.select_next()
            event.app.invalidate()

        @self.key_bindings.add("home", filter=has_focus(self))
        def _(event):
            self.select_first()
            event.app.invalidate()

        @self.key_bindings.add("end", filter=has_focus(self))
        def _(event):
            self.select_last()
            event.app.invalidate()

        @self.key_bindings.add("pageup", filter=has_focus(self))
        def _(event):
            self.select_previous(10)
            event.app.invalidate()

        @self.key_bindings.add("pagedown", filter=has_focus(self))
        def _(event):
            self.select_next(10)
            event.app.invalidate()

    def add_selection_changed_handler(self, handler):
        self.selection_changed_handlers.append(handler)

    def _on_selection_changed(self):
        for handler in self.selection_changed_handlers:
            handler(self.get_selected_items())

    def _on_item_click(self, item):
        if self.multiselect:
            item.selected = not item.selected
        else:
            for other_item in self.list_items:
                if other_item is not item:
                    other_item.selected = False
            item.selected = True

        self._on_selection_changed()

    def add_item(self, text, data=None):
        item = ListItem(text, data)
        item.add_click_handler(lambda i=item: self._on_item_click(i))
        self.list_items.append(item)
        return item

    def remove_item(self, item):
        if item in self.list_items:
            self.list_items.remove(item)

    def clear(self):
        self.list_items = []

    def get_selected_items(self):
        return [item for item in self.list_items if item.selected]

    def get_selected_item(self):
        selected = self.get_selected_items()
        return selected[0] if selected else None

    def get_selected_data(self):
        return [item.data for item in self.get_selected_items()]

    def select_item(self, item):
        if item in self.list_items:
            if not self.multiselect:
                for other_item in self.list_items:
                    if other_item is not item:
                        other_item.selected = False

            item.selected = True
            self._on_selection_changed()

    def select_index(self, index):
        if 0 <= index < len(self.list_items):
            self.select_item(self.list_items[index])

    def deselect_all(self):
        for item in self.list_items:
            item.selected = False
        self._on_selection_changed()

    def select_all(self):
        if self.multiselect:
            for item in self.list_items:
                item.selected = True
            self._on_selection_changed()

    def select_next(self, count=1):
        if not self.list_items:
            return

        selected = self.get_selected_item()
        if selected:
            index = self.list_items.index(selected)
            new_index = min(len(self.list_items) - 1, index + count)
        else:
            new_index = 0

        self.select_index(new_index)

    def select_previous(self, count=1):
        if not self.list_items:
            return

        selected = self.get_selected_item()
        if selected:
            index = self.list_items.index(selected)
            new_index = max(0, index - count)
        else:
            new_index = 0

        self.select_index(new_index)

    def select_first(self):
        if self.list_items:
            self.select_index(0)

    def select_last(self):
        if self.list_items:
            self.select_index(len(self.list_items) - 1)

    def __pt_container__(self):
        container = HSplit(self.list_items)
        return ScrollablePane(container, style=self.style)
