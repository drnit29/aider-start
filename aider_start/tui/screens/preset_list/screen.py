
from prompt_toolkit.layout import (
    HSplit,
    VSplit,
    Window,
    FormattedTextControl,
    ScrollablePane,
)
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import has_focus
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.widgets import TextArea, Button, Frame, Box, Shadow

# Style symbol
def get_search_symbol():
    return "🔍"  # Simple search icon

class PresetListScreen:
    """Modernized preset list screen"""

    def __init__(
        self, presets, on_select=None, on_edit=None, on_delete=None, on_create=None
    ):
        """
        Initialize preset list screen.

        Args:
            presets (list): List of presets
            on_select (callable, optional): Function to call when a preset is selected
            on_edit (callable, optional): Function to call when a preset is edited
            on_delete (callable, optional): Function to call when a preset is deleted
            on_create (callable, optional): Function to call when a new preset is created
        """
        self.presets = presets
        self.on_select = on_select
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_create = on_create

        self.filter_text = ""
        self.selected_preset = None
        self.selected_index = -1

        self.key_bindings = KeyBindings()
        self._setup_key_bindings()
        self._create_components()

    def _setup_key_bindings(self):
        """Set up key bindings for the screen"""

        @self.key_bindings.add("c")
        def _(event):
            if self.on_create:
                self.on_create()

        @self.key_bindings.add("e")
        def _(event):
            if self.selected_preset and self.on_edit:
                self.on_edit(self.selected_preset)

        @self.key_bindings.add("d")
        def _(event):
            if self.selected_preset and self.on_delete:
                self.on_delete(self.selected_preset)

        @self.key_bindings.add("/")
        def _(event):
            # Focus on filter field
            event.app.layout.focus(self.filter_field)

        @self.key_bindings.add("up")
        def _(event):
            self._select_previous()
            event.app.invalidate()

        @self.key_bindings.add("down")
        def _(event):
            self._select_next()
            event.app.invalidate()

    def _create_components(self):
        """Create UI components"""
        # Create filter field
        self.filter_field = TextArea(
            text="",
            multiline=False,
            focusable=True,
            focus_on_click=True,
            style="class:filter-bar",
            height=D.exact(1),
        )

        # Update component value when text changes
        def on_text_changed(buffer):
            self.filter_text = buffer.text
            self._refresh_list()

        self.filter_field.buffer.on_text_changed += on_text_changed

        # Create list view with simplified approach
        self.filtered_presets = []
        self.list_items = []
        self.list_view = HSplit(self.list_items)

        # Create action buttons
        self.create_button = Button(text="Create", handler=self._on_create_click)

        self.edit_button = Button(text="Edit", handler=self._on_edit_click)

        self.delete_button = Button(text="Delete", handler=self._on_delete_click)

        # Create right side detail panel
        self.detail_panel = self._create_detail_panel()

        # Refresh list
        self._refresh_list()

    def _create_detail_panel(self):
        """Create the right side detail panel"""
        # Create placeholder content
        detail_content = Window(
            FormattedTextControl("Select a preset to view details"),
            style="class:detail-panel",
            dont_extend_height=True,
        )

        return Frame(detail_content, title="Preset Details", style="class:detail-panel")

    def _update_detail_panel(self):
        """Update the detail panel with selected preset info"""
        if self.selected_preset:
            # Extract preset details for display
            name = self.selected_preset.get("name", "Unnamed Preset")
            description = self.selected_preset.get("description", "No description")
            command = self.selected_preset.get("command", "")
            model = self.selected_preset.get("model", "")
            tags = self.selected_preset.get("tags", [])

            # Format tags
            tags_text = ""
            if tags:
                tags_text = "Tags: " + ", ".join(tags)

            # Create detailed info display
            details_text = f"""
{name}

{description}

Model: {model}
Command: {command}
{tags_text}
"""

            # Create details content
            details_content = Window(
                FormattedTextControl(details_text),
                style="class:detail-panel",
                dont_extend_height=True,
            )

            # Create button for running the preset
            run_button = Button(
                text="Run Preset", handler=lambda: self._on_select_click()
            )

            # Add run button at the bottom
            details_layout = HSplit(
                [details_content, Window(height=D.exact(1)), run_button]  # Spacer
            )

            # Update detail panel
            self.detail_panel.body = Box(details_layout, padding=1)
        else:
            # No selection, show placeholder
            self.detail_panel.body = Box(
                Window(
                    FormattedTextControl("Select a preset to view details"),
                    style="class:detail-panel",
                ),
                padding=1,
            )

    def _refresh_list(self):
        """Refresh the preset list based on current filter"""
        # Filter presets
        self.filtered_presets = []
        self.list_items = []

        filter_text = self.filter_text.lower()

        for preset in self.presets:
            name = preset.get("name", "Unnamed Preset")
            description = preset.get("description", "")
            model = preset.get("model", "")

            # Apply filtering
            if (
                filter_text in name.lower()
                or filter_text in description.lower()
                or filter_text in model.lower()
            ):

                self.filtered_presets.append(preset)

        # Create list items
        for i, preset in enumerate(self.filtered_presets):
            name = preset.get("name", "Unnamed Preset")
            model = preset.get("model", "")

            # Format text
            item_text = f"{name} · {model}"

            # Style based on selection
            style = (
                "class:list-item.selected"
                if i == self.selected_index
                else "class:list-item"
            )

            # Create window for item
            item = Window(
                FormattedTextControl(item_text),
                height=D.exact(1),
                style=style,
                dont_extend_height=True,
            )

            self.list_items.append(item)

        # If no items, show empty message
        if not self.list_items:
            self.list_items.append(
                Window(
                    FormattedTextControl("No presets match your filter"),
                    height=D.exact(1),
                    style="class:list-item.empty",
                )
            )

        # Reset selection if needed
        if self.selected_index >= len(self.filtered_presets):
            self.selected_index = -1
            self.selected_preset = None
            self._update_buttons()
            self._update_detail_panel()

        # Update the list view container
        self.list_view.children = self.list_items

    def _select_previous(self):
        """Select the previous item in the list"""
        if self.filtered_presets:
            if self.selected_index > 0:
                self.selected_index -= 1
            elif self.selected_index == -1:
                self.selected_index = len(self.filtered_presets) - 1

            self.selected_preset = self.filtered_presets[self.selected_index]
            self._update_buttons()
            self._update_detail_panel()
            self._refresh_list()

    def _select_next(self):
        """Select the next item in the list"""
        if self.filtered_presets:
            if self.selected_index < len(self.filtered_presets) - 1:
                self.selected_index += 1
            else:
                self.selected_index = 0

            self.selected_preset = self.filtered_presets[self.selected_index]
            self._update_buttons()
            self._update_detail_panel()
            self._refresh_list()

    def _update_buttons(self):
        """Update button states based on selection"""
        if self.selected_preset:
            self.edit_button.text = "Edit"
            self.delete_button.text = "Delete"
        else:
            self.edit_button.text = "Edit (disabled)"
            self.delete_button.text = "Delete (disabled)"

    def _on_create_click(self):
        """Handle create button click"""
        if self.on_create:
            self.on_create()

    def _on_edit_click(self):
        """Handle edit button click"""
        if self.selected_preset and self.on_edit:
            self.on_edit(self.selected_preset)

    def _on_delete_click(self):
        """Handle delete button click"""
        if self.selected_preset and self.on_delete:
            self.on_delete(self.selected_preset)

    def _on_select_click(self):
        """Handle select/run button click"""
        if self.selected_preset and self.on_select:
            self.on_select(self.selected_preset)

    def __pt_container__(self):
        """
        Return the prompt_toolkit container.

        Returns:
            Container: The screen container
        """
        # Create filter bar
        filter_bar = HSplit(
            [
                VSplit(
                    [
                        Window(
                            FormattedTextControl(get_search_symbol()),
                            width=D.exact(2),
                            dont_extend_width=True,
                        ),
                        self.filter_field,
                    ]
                )
            ]
        )

        # Create list container with filter
        list_container = HSplit(
            [
                filter_bar,
                Window(height=D.exact(1)),  # Spacer
                ScrollablePane(self.list_view),
            ]
        )

        # Create action buttons container
        action_buttons = HSplit(
            [
                VSplit(
                    [
                        self.create_button,
                        Window(width=D.exact(2)),  # Spacer
                        self.edit_button,
                        Window(width=D.exact(2)),  # Spacer
                        self.delete_button,
                    ]
                )
            ]
        )

        # Check terminal width for layout
        small_terminal = False  # Simplified check

        # Create main container with list and detail panel
        if small_terminal:
            # On small terminals, only show the list
            main_container = list_container
        else:
            # On larger terminals, show list and detail panel side by side
            main_container = VSplit(
                [
                    list_container,
                    Window(width=D.exact(1), char="│"),  # Separator
                    self.detail_panel,
                ]
            )

        # Create the complete layout
        screen = HSplit(
            [
                # Title
                Window(
                    FormattedTextControl("Presets"),
                    height=D.exact(1),
                    style="class:title",
                ),
                Window(height=D.exact(1)),  # Spacer
                # Main content
                main_container,
                # Bottom bar
                Window(height=D.exact(1)),  # Spacer
                action_buttons,
                # Status bar
                Window(
                    FormattedTextControl(
                        "Press (?) for help | (c) Create | (e) Edit | (d) Delete"
                    ),
                    height=D.exact(1),
                    style="class:status",
                ),
            ]
        )

        return screen
