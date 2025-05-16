
from prompt_toolkit.layout import HSplit, Window, FormattedTextControl
from prompt_toolkit.layout.dimension import D

from ..base import Component
from .list_view import ListView

class Table(Component):
    """Table component with columns and rows"""

    def __init__(
        self,
        columns,
        rows=None,
        style="class:table",
        selectable=False,
        multiselect=False,
    ):
        super().__init__()
        self.columns = columns
        self.rows = rows or []
        self.style = style
        self.selectable = selectable
        self.multiselect = multiselect
        self.selection_changed_handlers = []

        self.processed_columns = []
        for column in columns:
            if isinstance(column, dict):
                self.processed_columns.append(column)
            elif isinstance(column, tuple):
                if len(column) == 3:
                    name, width, align = column
                    self.processed_columns.append(
                        {"name": name, "width": width, "align": align}
                    )
                elif len(column) == 2:
                    name, width = column
                    self.processed_columns.append(
                        {"name": name, "width": width, "align": "left"}
                    )
                else:
                    self.processed_columns.append(
                        {"name": column[0], "width": None, "align": "left"}
                    )
            else:
                self.processed_columns.append(
                    {"name": str(column), "width": None, "align": "left"}
                )

        if selectable:
            self.list_view = ListView(multiselect=multiselect)
            self.list_view.add_selection_changed_handler(self._on_selection_changed)
        else:
            self.list_view = None

    def add_selection_changed_handler(self, handler):
        self.selection_changed_handlers.append(handler)

    def _on_selection_changed(self, selected_items):
        for handler in self.selection_changed_handlers:
            handler(self.get_selected_rows())

    def add_row(self, row_data):
        self.rows.append(row_data)

        if self.selectable and self.list_view is not None:
            row_text = self._format_row(row_data)
            self.list_view.add_item(row_text, row_data)

    def clear(self):
        self.rows = []

        if self.selectable and self.list_view is not None:
            self.list_view.clear()

    def _format_header(self):
        header_parts = []

        for column in self.processed_columns:
            header = column["name"]
            width = column["width"] or len(header) + 2
            align = column["align"]

            if align == "center":
                formatted = header.center(width)
            elif align == "right":
                formatted = header.rjust(width)
            else:
                formatted = header.ljust(width)

            header_parts.append(formatted)

        return " | ".join(header_parts)

    def _format_row(self, row_data):
        row_parts = []

        for i, column in enumerate(self.processed_columns):
            if i < len(row_data):
                cell = str(row_data[i])
            else:
                cell = ""

            width = column["width"] or len(column["name"]) + 2
            align = column["align"]

            if align == "center":
                formatted = cell.center(width)
            elif align == "right":
                formatted = cell.rjust(width)
            else:
                formatted = cell.ljust(width)

            row_parts.append(formatted)

        return " | ".join(row_parts)

    def get_selected_rows(self):
        if self.selectable and self.list_view is not None:
            return self.list_view.get_selected_data()
        return []

    def __pt_container__(self):
        if self.selectable and self.list_view is not None:
            self.list_view.clear()
            for row in self.rows:
                row_text = self._format_row(row)
                self.list_view.add_item(row_text, row)

            header = Window(
                FormattedTextControl(self._format_header()),
                height=D.exact(1),
                style=f"{self.style}.header",
            )

            separator = Window(
                height=D.exact(1), char="─", style=f"{self.style}.separator"
            )

            return HSplit([header, separator, self.list_view])
        else:
            header = Window(
                FormattedTextControl(self._format_header()),
                height=D.exact(1),
                style=f"{self.style}.header",
            )

            separator = Window(
                height=D.exact(1), char="─", style=f"{self.style}.separator"
            )

            rows = []
            for row in self.rows:
                row_text = self._format_row(row)
                row_window = Window(
                    FormattedTextControl(row_text), height=D.exact(1), style=self.style
                )
                rows.append(row_window)

            return HSplit([header, separator, *rows])
