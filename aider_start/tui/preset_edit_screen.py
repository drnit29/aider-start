import sqlite3
from typing import Optional, Dict
import shlex

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

try:
    from ..db import database
    from ..db.models import Preset
    from ..config.config_manager import FlagManager
except ImportError:
    database = None
    Preset = None
    FlagManager = None


def display_preset_edit_screen(
    conn: sqlite3.Connection, flag_manager: FlagManager, preset_id: Optional[int] = None
) -> bool:
    """
    TUI screen for creating or editing a preset.
    Returns True if saved, False if cancelled.
    """
    is_editing = preset_id is not None
    current_preset_data: Optional[Preset] = None
    original_flags: Dict[str, Optional[str]] = {}

    if is_editing and preset_id is not None:
        current_preset_data = database.get_preset_by_id(conn, preset_id)
        if not current_preset_data:
            message_dialog(
                title="Error",
                text=f"Preset with ID {preset_id} not found.",
                style=default_style,
            ).run()
            return False
        original_flags = dict(current_preset_data.flags)
    else:
        current_preset_data = Preset(name="", description="", flags={})

    name_text_area = TextArea(
        text=current_preset_data.name,
        height=1,
        multiline=False,
        style="class:text-area",
        width=70,
    )
    description_text_area = TextArea(
        text=current_preset_data.description,
        height=3,
        multiline=True,
        style="class:text-area",
        width=70,
    )

    flags_text_initial = ""
    if current_preset_data.flags:
        for name, val in current_preset_data.flags.items():
            if val is None or val == "":
                flags_text_initial += f"--{name}\n"
            else:
                flags_text_initial += f"--{name} {shlex.quote(str(val))}\n"

    flags_area = TextArea(
        text=flags_text_initial.strip(),
        scrollbar=True,
        line_numbers=False,
        height=10,
        style="class:text-area",
    )

    error_message_control = FormattedTextControl(text="")
    error_display_frame = Frame(
        Window(content=error_message_control, height=1, style="class:label.error"),
        title="Status",
        style="class:frame.label",
    )

    show_error_message = Condition(
        lambda: bool(str(error_message_control.text).strip())
    )

    error_container = ConditionalContainer(
        content=error_display_frame, filter=show_error_message
    )

    app_instance_holder = {}

    def do_save():
        error_message_control.text = ""
        new_name = name_text_area.text.strip()
        new_description = description_text_area.text.strip()

        if not new_name:
            error_message_control.text = "Preset name cannot be empty."
            if app_instance_holder.get("app"):
                app_instance_holder["app"].invalidate()
            return

        new_flags: Dict[str, Optional[str]] = {}
        try:
            lines = flags_area.text.strip().split("\n")
            for line_num, line_content in enumerate(lines):
                line_content = line_content.strip()
                if not line_content:
                    continue
                parts = shlex.split(line_content)
                if not parts:
                    continue
                flag_name_raw = parts[0]
                if not flag_name_raw.startswith("--"):
                    raise ValueError(
                        f"Line {line_num+1}: Flag '{flag_name_raw}' must start with '--'."
                    )
                flag_name = flag_name_raw[2:]
                flag_value: Optional[str] = None
                if len(parts) > 2:
                    raise ValueError(
                        f"Line {line_num+1}: Flag '{flag_name}' has too many parts. Value should be one argument (use quotes if it contains spaces)."
                    )
                elif len(parts) == 2:
                    flag_value = parts[1]

                is_valid, msg = flag_manager.validate_flag(flag_name, flag_value)
                if not is_valid:
                    raise ValueError(f"Line {line_num+1} ('{flag_name}'): {msg}")
                new_flags[flag_name] = flag_value
        except ValueError as e:
            error_message_control.text = f"Flag Parsing Error: {str(e)}"
            if app_instance_holder.get("app"):
                app_instance_holder["app"].invalidate()
            return

        saved_successfully = False
        try:
            if (
                is_editing
                and current_preset_data
                and current_preset_data.id is not None
            ):
                preset_db_id = current_preset_data.id
                database.update_preset_details(
                    conn, preset_db_id, new_name, new_description
                )
                flags_to_delete = set(original_flags.keys()) - set(new_flags.keys())
                for flag_to_delete in flags_to_delete:
                    database.delete_flag_from_preset(conn, preset_db_id, flag_to_delete)
                for name, value in new_flags.items():
                    database.add_flag_to_preset(conn, preset_db_id, name, value)
                saved_successfully = True
            else:
                new_preset_id = database.create_preset(conn, new_name, new_description)
                if new_preset_id:
                    for name, value in new_flags.items():
                        database.add_flag_to_preset(conn, new_preset_id, name, value)
                    saved_successfully = True
                else:
                    error_message_control.text = (
                        "Failed to create preset (name might exist or DB error)."
                    )
                    if app_instance_holder.get("app"):
                        app_instance_holder["app"].invalidate()
                    return
        except Exception as db_e:
            error_message_control.text = f"Database save error: {db_e}"
            if app_instance_holder.get("app"):
                app_instance_holder["app"].invalidate()
            return

        if saved_successfully and app_instance_holder.get("app"):
            app_instance_holder["app"].exit(result=True)

    def do_cancel():
        if app_instance_holder.get("app"):
            app_instance_holder["app"].exit(result=False)

    dialog_title_text = "Edit Preset" if is_editing else "Create New Preset"

    dialog_body_children = [
        error_container,
        Label(text="Preset Name:"),
        name_text_area,
        Window(height=1, char=" "),
        Label(text="Description:"),
        description_text_area,
        Window(height=1, char=" "),
        Label(text="Flags (one per line, e.g., --model 'gpt-4o' or --stream):"),
        flags_area,
    ]

    dialog = Dialog(
        title=dialog_title_text,
        body=HSplit(dialog_body_children, padding=1),
        buttons=[
            SelectableButton(text="Save", handler=do_save, group="preset_edit"),
            SelectableButton(text="Cancel", handler=do_cancel, group="preset_edit"),
        ],
        width=80,
        modal=True,
    )

    dialog_kb = KeyBindings()

    @dialog_kb.add("escape")
    def _(event):
        do_cancel()

    application = Application(
        layout=Layout(FloatContainer(content=Window(), floats=[Float(dialog)])),
        key_bindings=dialog_kb,
        full_screen=True,
        style=default_style,
        mouse_support=True,
    )
    app_instance_holder["app"] = application

    return application.run()
