# TUI Screens for aider-start
import sys
import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple, Any, Dict
import shlex

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
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.shortcuts import (
    message_dialog,
    yes_no_dialog,
    input_dialog,
    button_dialog,
)
from prompt_toolkit.formatted_text import FormattedText, PygmentsTokens
from prompt_toolkit.styles import Style
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.widgets import (
    TextArea,
    Label,
    Button,
    Dialog,
    CheckboxList,
    RadioList,
    Frame,
)
from prompt_toolkit.filters import Condition  # Added Condition import

# Ensure db module can be imported
try:
    from ..db import database
    from ..db.models import Preset
    from ..config.config_manager import FlagManager
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    try:
        from aider_start.db import database
        from aider_start.db.models import Preset
        from aider_start.config.config_manager import FlagManager
    except ImportError:
        print(
            "Critical Error: Could not import database, models or FlagManager for TUI.",
            file=sys.stderr,
        )

        class Preset:
            pass

        database = None
        FlagManager = None

from .style.themes import default_style


# Corrected imports after refactoring of screen functions into separate files
from .preset_list_screen import display_preset_list_screen
from .preset_edit_screen import display_preset_edit_screen

# display_advanced_settings_manager_screen is also needed by main.py via this facade
from .advanced_settings_manager_screen import display_advanced_settings_manager_screen
from .config_wizard_screen import display_config_wizard
from .wizard_flag_config_screen import (
    display_wizard_flag_config_screen,
)  # Added new screen

# display_edit_model_config_dialog is called by advanced_settings_manager_screen,
# so it does not need to be exported here for main.py.


from .command_preview import display_command_preview_screen


if __name__ == "__main__":
    print("Testing TUI Screens...")

    if not database or not FlagManager:
        print("Database or FlagManager module not loaded correctly. Aborting tests.")
        sys.exit(1)

    test_db_path = database.get_default_db_path().parent / "test_aider_start_tui.db"
    if test_db_path.exists():
        test_db_path.unlink()

    conn_test = database.get_db_connection(test_db_path)
    database.setup_database(test_db_path)

    test_flag_meta = [
        {
            "name": "model",
            "description": "Model name",
            "category": "Model",
            "value_type": "string",
            "default_value": None,
            "requires_value": True,
            "is_deprecated": False,
        },
        {
            "name": "stream",
            "description": "Stream response",
            "category": "Behavior",
            "value_type": "boolean",
            "default_value": None,
            "requires_value": False,
            "is_deprecated": False,
        },
        {
            "name": "auto-commits",
            "description": "Auto commit changes",
            "category": "Git",
            "value_type": "boolean",
            "default_value": None,
            "requires_value": False,
            "is_deprecated": False,
        },
        {
            "name": "custom-param",
            "description": "A custom parameter",
            "category": "Custom",
            "value_type": "string",
            "default_value": "default_val",
            "requires_value": True,
            "is_deprecated": False,
        },
        {
            "name": "yes",
            "description": "Confirm all",
            "category": "Runtime",
            "value_type": "boolean",
            "default_value": None,
            "requires_value": False,
            "is_deprecated": False,
        },
    ]
    database.populate_flag_metadata(conn_test, test_flag_meta)

    try:
        flag_manager_test = FlagManager(conn_test)
    except Exception as e_fm:
        print(f"Failed to initialize FlagManager for testing: {e_fm}")
        if conn_test:
            conn_test.close()
        sys.exit(1)

    p1_id = database.create_preset(
        conn_test, "Preset To Edit", "Initial description for editing."
    )
    if p1_id:
        database.add_flag_to_preset(conn_test, p1_id, "model", "gpt-3.5-turbo")
        database.add_flag_to_preset(conn_test, p1_id, "stream", None)

    print("Test data created. Launching Preset List Screen...")

    while True:
        action, data = display_preset_list_screen(conn_test)

        if action == "select" and data is not None:
            selected_preset_id = data
            print(f"\nUser selected preset ID: {selected_preset_id}")
            preset_to_run = database.get_preset_by_id(conn_test, selected_preset_id)
            if preset_to_run:
                cmd_parts_preview = ["aider"]
                for f_name, f_val in preset_to_run.flags.items():
                    cmd_parts_preview.append(f"--{f_name}")
                    if f_val is not None and f_val != "":
                        cmd_parts_preview.append(shlex.quote(str(f_val)))
                dummy_command = " ".join(cmd_parts_preview)

                print(f"\nShowing command preview for: {dummy_command}")
                if display_command_preview_screen(dummy_command):
                    print("User chose to EXECUTE the command (simulation).")
                else:
                    print("User chose to CANCEL execution.")
            else:
                print(f"Could not find preset with ID {selected_preset_id}")

        elif action == "create":
            print("\nUser chose to CREATE new preset.")
            saved = display_preset_edit_screen(
                conn_test, flag_manager_test, preset_id=None
            )
            if saved:
                print("New preset creation process finished (saved).")
            else:
                print("New preset creation process cancelled.")

        elif action == "edit" and data is not None:
            edit_preset_id = data
            print(f"\nUser chose to EDIT preset ID: {edit_preset_id}.")
            saved = display_preset_edit_screen(
                conn_test, flag_manager_test, preset_id=edit_preset_id
            )
            if saved:
                print(f"Preset ID {edit_preset_id} edit process finished (saved).")
            else:
                print(f"Preset ID {edit_preset_id} edit process cancelled.")

        elif action is None:
            print("\nUser exited the preset list screen.")
            break

        print("\n" + "-" * 30 + " Back to Preset List " + "-" * 30 + "\n")

    if conn_test:
        conn_test.close()
    print(f"\nTest database was at: {test_db_path}")
