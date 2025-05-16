import sqlite3
import json
import yaml
from pathlib import Path
from typing import Optional, Any, Dict

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    Window,
    HSplit,
    ConditionalContainer,
    FloatContainer,
    Float,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.widgets import TextArea, Label, Dialog, Frame
from .selectable_button import SelectableButton
from prompt_toolkit.filters import Condition

from .style.themes import default_style
from .edit_model_config_helpers import (
    get_user_data_dir_for_preset_configs,
    process_settings_yaml,
    process_metadata_json,
)

try:
    from ..db import database
except ImportError:
    database = None


def display_edit_model_config_dialog(
    conn: sqlite3.Connection,
    config_mngr: Any,
    preset_id: int,
    existing_model_name: Optional[str] = None,
) -> bool:
    """
    A dialog to add or edit advanced settings (YAML) and metadata (JSON) for a specific model within a preset.
    Returns True if saved, False otherwise.
    """
    is_editing_existing_model = existing_model_name is not None

    current_settings_dict: Dict[Any, Any] = {}
    current_settings_path: Optional[str] = None
    current_metadata_dict: Dict[Any, Any] = {}
    current_metadata_path: Optional[str] = None

    if is_editing_existing_model and existing_model_name:
        settings_data = database.get_model_settings(
            conn, preset_id, existing_model_name
        )
        if settings_data:
            try:
                current_settings_dict = (
                    json.loads(settings_data[0]) if settings_data[0] else {}
                )
            except json.JSONDecodeError:
                current_settings_dict = {
                    "error": "Failed to parse existing settings JSON"
                }
            current_settings_path = settings_data[1]

        metadata_data = database.get_model_metadata(
            conn, preset_id, existing_model_name
        )
        if metadata_data:
            try:
                current_metadata_dict = (
                    json.loads(metadata_data[0]) if metadata_data[0] else {}
                )
            except json.JSONDecodeError:
                current_metadata_dict = {
                    "error": "Failed to parse existing metadata JSON"
                }
            current_metadata_path = metadata_data[1]

    settings_text_initial = (
        yaml.dump(
            current_settings_dict,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
        if current_settings_dict
        else ""
    )
    metadata_text_initial = (
        json.dumps(current_metadata_dict, indent=2, ensure_ascii=False)
        if current_metadata_dict
        else ""
    )

    model_name_area = TextArea(
        text=existing_model_name or "",
        height=1,
        multiline=False,
        read_only=is_editing_existing_model,
        style="class:text-area",
    )
    settings_text_area = TextArea(
        text=settings_text_initial,
        height=8,
        multiline=True,
        scrollbar=True,
        line_numbers=True,
        style="class:text-area",
    )
    settings_path_area = TextArea(
        text=current_settings_path or "",
        height=1,
        multiline=False,
        style="class:text-area",
    )

    metadata_text_area = TextArea(
        text=metadata_text_initial,
        height=8,
        multiline=True,
        scrollbar=True,
        line_numbers=True,
        style="class:text-area",
    )
    metadata_path_area = TextArea(
        text=current_metadata_path or "",
        height=1,
        multiline=False,
        style="class:text-area",
    )

    error_message_control = FormattedTextControl(text="")
    error_display_frame = Frame(
        Window(content=error_message_control, height=1, style="class:label.error"),
        title="Status",
        style="class:frame.label",
    )
    show_error_filter = Condition(lambda: bool(str(error_message_control.text).strip()))
    error_container = ConditionalContainer(
        content=error_display_frame, filter=show_error_filter
    )

    app_instance_holder = {}

    _file_handlers_module = (
        config_mngr if hasattr(config_mngr, "save_yaml_file") else None
    )
    if not _file_handlers_module:
        try:
            from ..config import config_manager as _fh_module_direct

            _file_handlers_module = _fh_module_direct
        except ImportError:
            from aider_start.config import config_manager as _fh_module_direct_fallback

            _file_handlers_module = _fh_module_direct_fallback

    def do_save_config():
        error_message_control.text = ""
        model_name = model_name_area.text.strip()
        if not model_name:
            error_message_control.text = "Model name cannot be empty."
            if app_instance_holder.get("app"):
                app_instance_holder["app"].invalidate()
            return

        settings_str = settings_text_area.text
        metadata_str = metadata_text_area.text

        try:
            final_settings_json_str, final_settings_path = process_settings_yaml(
                settings_str,
                model_name,
                preset_id,
                _file_handlers_module,
                settings_path_area,
            )
            final_metadata_json_str, final_metadata_path = process_metadata_json(
                metadata_str,
                model_name,
                preset_id,
                _file_handlers_module,
                metadata_path_area,
            )

            if final_settings_json_str or final_settings_path:
                database.add_or_update_model_settings(
                    conn,
                    preset_id,
                    model_name,
                    final_settings_json_str or "{}",
                    final_settings_path,
                )

            if final_metadata_json_str or final_metadata_path:
                database.add_or_update_model_metadata(
                    conn,
                    preset_id,
                    model_name,
                    final_metadata_json_str or "{}",
                    final_metadata_path,
                )

            if app_instance_holder.get("app"):
                app_instance_holder["app"].exit(result=True)

        except yaml.YAMLError as ye:
            error_message_control.text = f"YAML Parsing Error: {ye}"
        except json.JSONDecodeError as je:
            error_message_control.text = f"JSON Parsing Error: {je}"
        except ValueError as ve:
            error_message_control.text = f"Validation Error: {ve}"
        except IOError as ioe:
            error_message_control.text = f"File Error: {ioe}"
        except Exception as e:
            error_message_control.text = f"Unexpected Error: {e}"

        if app_instance_holder.get("app"):
            app_instance_holder["app"].invalidate()

    def do_cancel_config():
        if app_instance_holder.get("app"):
            app_instance_holder["app"].exit(result=False)

    dialog_title = (
        f"Edit Config for '{existing_model_name}'"
        if is_editing_existing_model
        else "Add New Model Config"
    )

    dialog_content = HSplit(
        [
            error_container,
            Label(text="Model Name:"),
            model_name_area,
            Window(height=1, char=" "),
            Label(text="Model Settings (YAML):"),
            settings_text_area,
            Label(
                text="Settings File Path (optional, will auto-generate if empty & content exists):"
            ),
            settings_path_area,
            Window(height=1, char=" "),
            Label(text="Model Metadata (JSON):"),
            metadata_text_area,
            Label(
                text="Metadata File Path (optional, will auto-generate if empty & content exists):"
            ),
            metadata_path_area,
        ],
        padding=1,
    )

    dialog = Dialog(
        title=dialog_title,
        body=dialog_content,
        buttons=[
            SelectableButton(text="Save", handler=do_save_config, group="model_config"),
            SelectableButton(
                text="Cancel", handler=do_cancel_config, group="model_config"
            ),
        ],
        width=100,
        modal=True,
    )

    dialog_kb = KeyBindings()

    @dialog_kb.add("escape")
    def _(event):
        do_cancel_config()

    application = Application(
        layout=Layout(FloatContainer(content=Window(), floats=[Float(dialog)])),
        key_bindings=dialog_kb,
        full_screen=True,
        style=default_style,
        mouse_support=True,
    )
    app_instance_holder["app"] = application
    return application.run()
