# aider_start/tui/config_wizard_screen.py
import sqlite3
from typing import Optional, List, Tuple, Any

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    Window,
    HSplit,
    VSplit,
    ConditionalContainer,
    FloatContainer,
    Float,
)
from prompt_toolkit.layout.dimension import Dimension  # Added Dimension
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.shortcuts import message_dialog, input_dialog, button_dialog
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.widgets import (
    TextArea,
    Label,
    Dialog,
    CheckboxList,
    RadioList,
    Frame,
)
from .selectable_button import SelectableButton
from prompt_toolkit.filters import Condition

from .style.themes import default_style

try:
    from ..db import database
    from ..presets.wizard import ConfigWizard
    from ..config.config_manager import FlagManager
except ImportError:
    database = None
    ConfigWizard = None
    FlagManager = None


def display_config_wizard(
    conn: sqlite3.Connection, flag_manager_instance: FlagManager
) -> bool:
    """
    Displays a multi-step wizard to create a new configuration preset.
    Returns True if the preset was saved, False otherwise.
    """
    if not database or not ConfigWizard or not flag_manager_instance:
        message_dialog(
            title="Error",
            text="Core modules for wizard not loaded.",
            style=default_style,
        ).run()
        return False

    wizard = ConfigWizard(conn, flag_manager_instance)

    # Step 1: Get Name and Description
    name_text = input_dialog(
        title="Preset Wizard - Step 1: Name",
        text="Enter a name for your new preset:",
        style=default_style,
    ).run()

    if name_text is None:  # User cancelled
        return False
    wizard.wizard_data["name"] = name_text.strip()
    if not wizard.wizard_data["name"]:
        message_dialog(
            title="Error", text="Preset name cannot be empty.", style=default_style
        ).run()
        return False  # Or loop back to name input

    description_text = input_dialog(
        title="Preset Wizard - Step 1: Description",
        text="Enter a description for your preset (optional):",
        style=default_style,
    ).run()

    if description_text is None:  # User cancelled
        # If name was entered, maybe ask to save with empty desc or discard
        return False
    wizard.wizard_data["description"] = description_text.strip()

    # Step 2: Select Flag Categories
    all_categories = wizard.get_categories()
    if not all_categories:
        message_dialog(
            title="Wizard Info",
            text="No flag categories found. Proceeding to save basic preset.",
            style=default_style,
        ).run()
        # Fall through to save with just name/desc if no categories
    else:
        category_checkbox_list = CheckboxList(
            values=[(cat, cat) for cat in all_categories]
        )

        def category_dialog_ok_handler():
            wizard.wizard_data["selected_categories"] = (
                category_checkbox_list.current_values
            )
            return True  # Proceed

        def get_checkbox_list_frame_style():
            # Assuming `app` is the Application instance for this dialog
            try:
                if app.layout.has_focus(category_checkbox_list):
                    return "class:frame.focused"
            except (
                Exception
            ):  # App may not be fully initialized when style is first accessed
                pass
            return "class:frame"  # Default frame style

        checkbox_list_frame = Frame(
            body=category_checkbox_list,
            # title="Categorias", # Optional title for the frame
            style="class:frame",  # Temporarily use a fixed string style for debugging
        )

        category_dialog = Dialog(
            title="Preset Wizard - Step 2: Select Flag Categories",
            body=HSplit(
                [
                    Label("Select categories to configure:"),
                    checkbox_list_frame,
                ],  # Use the frame here
                padding=1,
            ),
            buttons=[
                SelectableButton(
                    text="Next",
                    handler=lambda: category_dialog_ok_handler()
                    and app.exit(result=True),
                    group="category_dialog",
                ),
                SelectableButton(
                    text="Cancel",
                    handler=lambda: app.exit(result=False),
                    group="category_dialog",
                ),
            ],
            width=80,
            modal=True,
        )

        # Give the base Window of FloatContainer some dimension hints
        base_window_for_cat_dialog_float = Window(width=Dimension(), height=Dimension())
        app = Application(
            layout=Layout(
                FloatContainer(
                    base_window_for_cat_dialog_float, floats=[Float(category_dialog)]
                )
            ),
            full_screen=True,
            style=default_style,
        )
        categories_selected_proceed = app.run()

        if (
            not categories_selected_proceed
            or not wizard.wizard_data["selected_categories"]
        ):
            # User cancelled or selected no categories, proceed to save basic preset or ask
            message_dialog(
                title="Wizard Info",
                text="No categories selected. Proceeding to save basic preset.",
                style=default_style,
            ).run()
            # Fall through to save with just name/desc

    # Step 3+: Configure flags for selected categories
    if wizard.wizard_data.get("selected_categories"):
        for category_name in wizard.wizard_data["selected_categories"]:
            flags_in_category = wizard.get_flags_for_category(category_name)
            if not flags_in_category:
                continue

            # For each category, create a dialog to configure its flags
            category_flags_data: Dict[str, Optional[str]] = {}

            form_items = []
            flag_text_areas: Dict[str, TextArea] = (
                {}
            )  # To store text areas for string flags
            flag_checkboxes: Dict[str, CheckboxList] = (
                {}
            )  # To store checkboxes for boolean flags

            for flag_meta in flags_in_category:
                flag_name = flag_meta["name"]
                flag_desc = flag_meta.get("description", "")
                flag_type = flag_meta.get("value_type", "string")
                requires_value = flag_meta.get(
                    "requires_value", True
                )  # Default based on typical CLI flags

                form_items.append(Label(text=f"\n--{flag_name}:"))
                if flag_desc:
                    form_items.append(Label(text=f"  ({flag_desc})"))

                if flag_type == "boolean":
                    # For boolean flags, we'll use a checkbox: checked means include the flag (value None if no explicit value needed)
                    # Aider typically treats presence of flag as true. If it needs --flag true/false, that's different.
                    # Assuming presence means true, or user can clear if they don't want it.
                    # If requires_value is True for a boolean, it's an odd case, treat as string for now.
                    # For now, simple checkbox: "Include this flag?"
                    cb = CheckboxList(values=[(flag_name, f"Include --{flag_name}")])
                    flag_checkboxes[flag_name] = cb
                    form_items.append(cb)
                else:  # string, path, integer etc. - use TextArea for now
                    ta = TextArea(
                        text="", multiline=False, height=1, style="class:text-area"
                    )
                    flag_text_areas[flag_name] = ta
                    form_items.append(ta)

            if (
                not form_items
            ):  # No configurable flags in this category (e.g. all are just info)
                continue

            def on_category_flags_save():
                for name, ta_widget in flag_text_areas.items():
                    value = ta_widget.text.strip()
                    flag_meta_details = wizard.flag_manager.get_flag_details(
                        name
                    )  # Get details again for requires_value
                    requires_val = (
                        flag_meta_details.get("requires_value", True)
                        if flag_meta_details
                        else True
                    )

                    if value:
                        category_flags_data[name] = value
                    elif (
                        not requires_val
                    ):  # Flag doesn't require a value, and user left it blank
                        # This case is tricky. If it's a boolean handled by checkbox, it's different.
                        # For non-booleans that don't require value but are empty, we might not add them,
                        # or add them with a special marker if needed. For now, skip if empty and not boolean.
                        pass

                for name, cb_widget in flag_checkboxes.items():
                    if (
                        cb_widget.current_values and name in cb_widget.current_values
                    ):  # Checkbox is ticked
                        # For boolean flags, if ticked, add it. Aider usually takes --flag as true.
                        # If it needed --flag true, the type would be string.
                        category_flags_data[name] = (
                            None  # Indicates presence of the flag
                        )

                wizard.wizard_data["flags"].update(category_flags_data)
                return True  # Signal to proceed

            category_flags_dialog = Dialog(
                title=f"Preset Wizard - Configure: {category_name}",
                body=HSplit(form_items, padding=0),
                buttons=[
                    SelectableButton(
                        text="Save & Next Category",
                        handler=lambda: on_category_flags_save()
                        and cat_app.exit(result=True),
                        group="category_flags",
                    ),
                    SelectableButton(
                        text="Skip Category",
                        handler=lambda: cat_app.exit(result=True),
                        group="category_flags",
                    ),  # Skip but still proceed
                    SelectableButton(
                        text="Cancel Wizard",
                        handler=lambda: cat_app.exit(result=False),
                        group="category_flags",
                    ),
                ],
                width=100,
                modal=True,
            )
            # Give the base Window of FloatContainer some dimension hints
            base_window_for_cat_flags_float = Window(
                width=Dimension(), height=Dimension()
            )
            cat_app = Application(
                layout=Layout(
                    FloatContainer(
                        base_window_for_cat_flags_float,
                        floats=[Float(category_flags_dialog)],
                    )
                ),
                full_screen=True,
                style=default_style,
            )

            if not cat_app.run():  # User chose Cancel Wizard
                return False  # Exit the whole wizard

    # Final Step: Save Preset
    saved_preset_id = wizard.save_preset()
    if saved_preset_id:
        message_dialog(
            title="Success",
            text=f"Preset '{wizard.wizard_data['name']}' saved with ID {saved_preset_id}.",
            style=default_style,
        ).run()
        return True
    else:
        message_dialog(
            title="Error", text="Failed to save the preset.", style=default_style
        ).run()
        return False


if __name__ == "__main__":
    # Basic test for this screen (requires a DB and FlagManager)
    # This is a simplified test, more comprehensive testing needed
    print("This screen is best tested via main.py's TUI flow.")
    # Example:
    # from aider_start.db.database_connection import get_default_db_path, get_db_connection, setup_database
    # from aider_start.config.config_manager import FlagManager, DEFAULT_FLAG_METADATA
    # from aider_start.db.database_flag_metadata import populate_flag_metadata
    #
    # test_db = get_default_db_path().parent / "wizard_test.db"
    # if test_db.exists(): test_db.unlink()
    # setup_database(test_db)
    # test_conn = get_db_connection(test_db)
    # populate_flag_metadata(test_conn, DEFAULT_FLAG_METADATA)
    # test_fm = FlagManager(test_conn)
    # display_config_wizard(test_conn, test_fm)
    # if test_conn: test_conn.close()
