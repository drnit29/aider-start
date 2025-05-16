# aider_start/tui/wizard_flag_config_screen.py
import sqlite3
from typing import Dict, List, Any, Optional

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    HSplit,
    VSplit,
    Window,
    FloatContainer,
    Float,
)  # ScrollablePane removido
from prompt_toolkit.layout.scrollable_pane import (
    ScrollablePane,
)  # Importação correta adicionada
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Label, CheckboxList, Button, Dialog, Frame
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.application.current import (
    get_app,
)  # For focus checks if needed later

from .style.themes import default_style

try:
    from ..config.config_manager import FlagManager
    from ..db import database  # For type hinting if needed, FlagManager handles DB ops
except ImportError:
    FlagManager = None
    database = None


class WizardFlagConfigScreen:
    def __init__(self, flag_manager: FlagManager, app_context=None):
        self.flag_manager = flag_manager
        self.app_context = app_context
        self.categories: List[str] = []
        self.flags_by_category: Dict[str, List[Dict[str, Any]]] = {}
        self.checkbox_lists: Dict[str, CheckboxList] = {}  # Stores all checkbox lists
        self.current_category_index: int = 0

        self._load_flags_and_init_checkboxes()

    def _load_flags_and_init_checkboxes(self):
        all_flags = self.flag_manager.get_all_flags()
        temp_categories: Dict[str, List[Dict[str, Any]]] = {}
        for flag in all_flags:
            category = flag.get("category", "Other")
            if category not in temp_categories:
                temp_categories[category] = []
            temp_categories[category].append(flag)

        self.categories = sorted(temp_categories.keys())
        self.flags_by_category = {
            cat: sorted(temp_categories[cat], key=lambda x: x["name"])
            for cat in self.categories
        }

        # Initialize all checkbox lists once and store them
        for category_name in self.categories:
            flags_in_cat = self.flags_by_category.get(category_name, [])

            checkbox_values = []
            current_wizard_visible_flags = []
            if flags_in_cat:
                for flag in flags_in_cat:
                    desc_snippet = flag.get("description", "")
                    if len(desc_snippet) > 40:
                        desc_snippet = desc_snippet[:37] + "..."
                    checkbox_values.append(
                        (flag["name"], f"{flag['name']} ({desc_snippet})")
                    )

                    if flag.get("wizard_visible", True):
                        current_wizard_visible_flags.append(flag["name"])

            cl = CheckboxList(values=checkbox_values)
            cl.current_values = current_wizard_visible_flags
            self.checkbox_lists[category_name] = cl

    def build_body_for_current_category(self) -> Any:
        """Builds the UI content for the current category."""
        if not self.categories:  # Handle case with no categories/flags
            return HSplit([Label("No flag categories found to configure.")])

        if not (0 <= self.current_category_index < len(self.categories)):
            # This case should ideally not be reached if navigation is handled correctly
            self.current_category_index = 0  # Reset to first category
            if not self.categories:  # Still no categories after reset (empty list)
                return HSplit([Label("No categories available.")])

        category_name = self.categories[self.current_category_index]
        checkbox_list_for_category = self.checkbox_lists.get(category_name)

        if checkbox_list_for_category is None:
            return HSplit(
                [Label(f"Error: CheckboxList for {category_name} not found.")]
            )

        content_body: Any
        if not checkbox_list_for_category.values:  # Check if the list itself is empty
            content_body = HSplit(
                [Label("(No flags in this category to configure for wizard)")]
            )
        else:
            content_body = (
                checkbox_list_for_category  # This is the CheckboxList or HSplit
            )

        # The Frame should wrap the ScrollablePane which contains the content_body
        # For now, build_body_for_current_category will return the content_body directly
        # and the Dialog will wrap it in ScrollablePane and Frame.
        # Let's simplify: build_body_for_current_category returns the HSplit/CheckboxList
        # The Dialog's body will handle the Frame and ScrollablePane.

        # For now, let's return the content that needs to be scrollable
        return content_body

    def _get_selected_visibility(self) -> Dict[str, bool]:
        """Returns a dict of {flag_name: is_visible} based on checkbox states."""
        visibility_map = {}
        for category_name, cl in self.checkbox_lists.items():
            flags_in_cat = self.flags_by_category.get(category_name, [])
            visible_in_category = cl.current_values
            for flag_dict in flags_in_cat:
                flag_name = flag_dict["name"]
                visibility_map[flag_name] = flag_name in visible_in_category
        return visibility_map

    # __pt_container__ is not needed if the Dialog directly uses the body built by build_body_for_current_category


def display_wizard_flag_config_screen(flag_manager: FlagManager, app_context=None):
    screen_instance = WizardFlagConfigScreen(flag_manager, app_context)

    # This variable will hold the Application instance for the current dialog
    # It needs to be accessible by the button handlers to call app.exit()
    # We can use a list or dict to pass it by reference if handlers are defined outside the loop
    app_holder = {"app": None}

    while True:  # Loop to display categories one by one
        current_body_container = screen_instance.build_body_for_current_category()

        def go_next_category_handler():
            if (
                screen_instance.current_category_index
                < len(screen_instance.categories) - 1
            ):
                screen_instance.current_category_index += 1
                if app_holder["app"]:
                    app_holder["app"].exit(result="next_category")
            # else: stay on current if it's the last one

        def go_prev_category_handler():
            if screen_instance.current_category_index > 0:
                screen_instance.current_category_index -= 1
                if app_holder["app"]:
                    app_holder["app"].exit(result="prev_category")
            # else: stay on current if it's the first one

        def save_changes_handler():
            visibility_map = screen_instance._get_selected_visibility()
            try:
                for flag_name, is_visible in visibility_map.items():
                    flag_manager.set_flag_wizard_visibility(flag_name, is_visible)
                flag_manager.load_metadata(force_reload=True)
                if app_holder["app"]:
                    app_holder["app"].exit(result="saved")
            except Exception as e:
                if app_holder["app"]:
                    app_holder["app"].exit(result=f"error_saving: {str(e)}")

        dialog_buttons = []
        if (
            len(screen_instance.categories) > 1
        ):  # Only show nav buttons if multiple categories
            dialog_buttons.extend(
                [
                    Button(text="< Prev", handler=go_prev_category_handler),
                    Button(text="Next >", handler=go_next_category_handler),
                    Window(width=5, char=" "),  # Spacer
                ]
            )

        dialog_buttons.extend(
            [
                Button(text="Save All", handler=save_changes_handler),
                Button(
                    text="Cancel",
                    handler=lambda: app_holder["app"].exit(result="cancel"),
                ),
            ]
        )

        # Disable Prev/Next if at boundaries
        if (
            screen_instance.current_category_index == 0
            and len(screen_instance.categories) > 1
        ):
            dialog_buttons[0] = Button(
                text="< Prev", handler=lambda: None
            )  # "Disabled"
        if (
            screen_instance.current_category_index
            == len(screen_instance.categories) - 1
            and len(screen_instance.categories) > 1
        ):
            # The index for "Next >" button depends on whether Prev was added
            next_button_index = 1 if len(screen_instance.categories) > 1 else 0
            dialog_buttons[next_button_index] = Button(
                text="Next >", handler=lambda: None
            )  # "Disabled"

        dialog = Dialog(
            title="Configure Wizard Flag Visibility (Space to toggle)",
            body=Frame(
                body=HSplit(
                    [
                        Window(height=1, char="─"),
                        current_body_container,  # Removed ScrollablePane, current_body_container is CheckboxList or HSplit
                        Window(height=1, char="─"),
                    ]
                ),
                title=(
                    f"{screen_instance.categories[screen_instance.current_category_index]} ({screen_instance.current_category_index + 1}/{len(screen_instance.categories)})"
                    if screen_instance.categories
                    else "Configure Flags"
                ),
                style="class:frame",
            ),
            buttons=dialog_buttons,
            width=100,
            modal=True,
        )

        root_container = FloatContainer(content=Window(), floats=[Float(dialog)])
        layout = Layout(container=root_container)

        kb_dialog = KeyBindings()

        @kb_dialog.add("escape")
        def _(event):
            event.app.exit(result="cancel")

        current_app = Application(
            layout=layout,
            key_bindings=kb_dialog,
            full_screen=True,
            style=default_style,
            mouse_support=True,
        )
        app_holder["app"] = current_app  # Store current app instance

        result = current_app.run()

        if result == "saved":
            message_dialog(
                title="Success",
                text="Wizard flag visibility settings saved.",
                style=default_style,
            ).run()
            break
        elif result == "cancel":
            break
        elif result is not None and str(result).startswith("error_saving:"):
            error_message = str(result).replace("error_saving: ", "")
            message_dialog(
                title="Error",
                text=f"Failed to save settings: {error_message}",
                style=default_style,
            ).run()
            break  # Exit on error or let user try again? For now, exit.
        elif result == "next_category" or result == "prev_category":
            continue  # Loop to display the new category
        else:  # Includes "stay" or unexpected exit
            if (
                len(screen_instance.categories) <= 1
            ):  # If only one category, or user didn't navigate
                break
            # If user exits via other means (e.g. Ctrl-C if not caught by dialog's kb)
            # or if next/prev was "disabled" and returned "stay"
            # We might need a more robust way to handle this if "stay" is a common exit path from app.run()
            # For now, assume if not save/cancel/error, and not explicit nav, it's a break.
            # This might need refinement if next/prev on boundaries return None/stay and cause premature exit.
            # If next/prev are disabled, their handlers are None, so they won't exit the app.
            # The app would be exited by Esc or Save/Cancel in that case.
            pass  # Stay in loop if next/prev was clicked but no change in index (e.g. at boundary)


if __name__ == "__main__":
    print(
        "To test this screen, integrate it into the main TUI flow and call display_wizard_flag_config_screen."
    )
