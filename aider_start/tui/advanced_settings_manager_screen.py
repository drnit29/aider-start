import sqlite3
from typing import Any
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.shortcuts import message_dialog, yes_no_dialog

from .style.themes import default_style
from .preset_list_screen import display_preset_list_screen
from .preset_edit_screen import display_preset_edit_screen
from .edit_model_config_dialog import display_edit_model_config_dialog

from .advanced_settings_manager_helpers import (
    reload_data_for_list_view,
    get_display_items_for_list_view,
    get_formatted_text_for_list_view,
)


def display_advanced_settings_manager_screen(
    conn: sqlite3.Connection,
    config_mngr: Any,
    preset_id: int,
) -> None:
    """
    TUI screen to manage advanced model settings (YAML) and metadata (JSON) for a given preset.
    This screen now loops, allowing Add/Edit operations to call another dialog and then refresh this list.
    """
    try:
        from ..db import database
        from ..db.models import Preset
        from ..config.config_manager import FlagManager
    except ImportError:
        message_dialog(
            title="Error",
            text="Core modules not loaded. Cannot display advanced settings.",
            style=default_style,
        ).run()
        return

    try:
        from ..config import config_manager as cm_file_handlers
    except ImportError:
        from aider_start.config import config_manager as cm_file_handlers

    while True:
        app_ref_list = {"app": None}
        selected_model_index_list = 0
        ADD_NEW_MODEL_MARKER = "[+] Add New Model Settings/Metadata"

        preset_details_list, managed_models_info_list, selected_model_index_list = (
            reload_data_for_list_view(
                database, conn, preset_id, app_ref_list, selected_model_index_list
            )
        )

        if not preset_details_list:
            message_dialog(
                title="Error",
                text=f"Preset ID {preset_id} not found or inaccessible.",
                style=default_style,
            ).run()
            return

        def get_formatted_text():
            return get_formatted_text_for_list_view(
                preset_details_list,
                managed_models_info_list,
                selected_model_index_list,
                ADD_NEW_MODEL_MARKER,
                FormattedText,
            )

        list_manager_kb = KeyBindings()

        @list_manager_kb.add("up")
        def _(event):
            nonlocal selected_model_index_list
            selected_model_index_list = max(0, selected_model_index_list - 1)
            event.app.invalidate()

        @list_manager_kb.add("down")
        def _(event):
            nonlocal selected_model_index_list
            display_items = get_display_items_for_list_view(
                managed_models_info_list, ADD_NEW_MODEL_MARKER
            )
            selected_model_index_list = min(
                len(display_items) - 1, selected_model_index_list + 1
            )
            event.app.invalidate()

        @list_manager_kb.add("n")
        def _(event):
            event.app.exit(result=("trigger_add_dialog", None))

        @list_manager_kb.add("enter")
        @list_manager_kb.add("e")
        def _(event):
            display_items = get_display_items_for_list_view(
                managed_models_info_list, ADD_NEW_MODEL_MARKER
            )
            if selected_model_index_list < len(managed_models_info_list):
                model_name_to_edit = managed_models_info_list[
                    selected_model_index_list
                ]["name"]
                event.app.exit(result=("trigger_edit_dialog", model_name_to_edit))
            elif display_items[selected_model_index_list] == ADD_NEW_MODEL_MARKER:
                event.app.exit(result=("trigger_add_dialog", None))

        @list_manager_kb.add("d")
        def _(event):
            display_items = get_display_items_for_list_view(
                managed_models_info_list, ADD_NEW_MODEL_MARKER
            )
            if selected_model_index_list < len(managed_models_info_list):
                model_name_to_delete = managed_models_info_list[
                    selected_model_index_list
                ]["name"]
                event.app.exit(result=("trigger_delete_dialog", model_name_to_delete))
            else:
                message_dialog(
                    title="Info",
                    text="Select a model configuration to delete.",
                    style=default_style,
                ).run()
                event.app.invalidate()

        @list_manager_kb.add("q")
        @list_manager_kb.add("escape")
        def _(event):
            event.app.exit(result=("quit_manager_entirely", None))

        title_text_val = FormattedText(
            [
                (
                    "class:title",
                    f" Advanced Settings for Preset: {preset_details_list.name} ",
                )
            ]
        )
        status_text_val = FormattedText(
            [
                ("class:status", " "),
                ("class:key", "↑/↓"),
                ("class:status", " Nav "),
                ("class:key", "Enter/E"),
                ("class:status", " Edit/Add "),
                ("class:key", "N"),
                ("class:status", " Add New "),
                ("class:key", "D"),
                ("class:status", " Delete "),
                ("class:key", "Q/Esc"),
                ("class:status", " Back to Main Menu "),
                ("class:status", " "),
            ]
        )
        header = Window(
            FormattedTextControl(title_text_val, focusable=False),
            height=1,
            style="class:title",
        )
        body = Window(
            FormattedTextControl(
                get_formatted_text,
                focusable=True,
                key_bindings=list_manager_kb,
            )
        )
        status_bar = Window(
            FormattedTextControl(status_text_val, focusable=False),
            height=1,
            style="class:status",
        )
        layout = Layout(
            HSplit(
                [
                    header,
                    Window(height=1, char="─", style="class:frame.label"),
                    body,
                    Window(height=1, char="─", style="class:frame.label"),
                    status_bar,
                ]
            )
        )

        list_application = Application(
            layout=layout,
            key_bindings=list_manager_kb,
            full_screen=True,
            style=default_style,
            mouse_support=True,
        )
        app_ref_list["app"] = list_application

        action_result = list_application.run()

        action_type = None
        action_data = None

        if isinstance(action_result, tuple) and len(action_result) == 2:
            action_type, action_data = action_result

        if action_type == "exit_manager_due_to_error":
            return

        elif action_type == "quit_manager_entirely":
            break

        elif action_type == "trigger_add_dialog":
            display_edit_model_config_dialog(
                conn, config_mngr, preset_id, existing_model_name=None
            )

        elif action_type == "trigger_edit_dialog":
            model_name_to_edit = action_data
            display_edit_model_config_dialog(
                conn, config_mngr, preset_id, existing_model_name=model_name_to_edit
            )

        elif action_type == "trigger_delete_dialog":
            model_name_to_delete = action_data
            model_info_to_delete = next(
                (
                    m
                    for m in managed_models_info_list
                    if m["name"] == model_name_to_delete
                ),
                None,
            )

            confirm_text = f"Delete all advanced settings and metadata for model '{model_name_to_delete}'?"
            if model_info_to_delete:
                if model_info_to_delete.get("settings_path"):
                    confirm_text += f"\nAssociated settings file: {model_info_to_delete['settings_path']}"
                if model_info_to_delete.get("metadata_path"):
                    confirm_text += f"\nAssociated metadata file: {model_info_to_delete['metadata_path']}"
            confirm_text += "\n\n(Files themselves will NOT be deleted from disk by this action, only database records)."

            if yes_no_dialog(
                "Confirm Deletion", confirm_text, style=default_style
            ).run():
                database.delete_model_settings(conn, preset_id, model_name_to_delete)
                database.delete_model_metadata(conn, preset_id, model_name_to_delete)
                message_dialog(
                    title="Success",
                    text=f"Advanced config for '{model_name_to_delete}' deleted from database.",
                    style=default_style,
                ).run()
