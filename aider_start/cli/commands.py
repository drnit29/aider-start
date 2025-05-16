
import typer
import sys
from typing import Optional

from aider_start.db import database
from aider_start.tui.preset_list_screen import display_preset_list_screen
from aider_start.tui.config_wizard_screen import display_config_wizard
from aider_start.tui.preset_edit_screen import display_preset_edit_screen
from aider_start.tui.advanced_settings_manager_screen import display_advanced_settings_manager_screen
from aider_start.tui.command_preview import display_command_preview_screen
from aider_start.commands import executor
from aider_start.config.config_manager import FlagManager
from aider_start.tui.style.themes import default_style as tui_default_style

from .app import AppContext

app = typer.Typer(
    help="aider-start: Manage configuration presets for the aider tool.",
    no_args_is_help=False,
    add_completion=False,
)

@app.callback(invoke_without_command=True)
def main_operations(ctx: typer.Context):
    """
    Initializes database, FlagManager, and creates an AppContext.
    """
    db_path = database.get_default_db_path()
    database.setup_database(db_path)

    temp_conn_for_fm = database.get_db_connection(db_path)
    flag_manager_instance = None
    if FlagManager:
        flag_manager_instance = FlagManager(temp_conn_for_fm)

    app_context = AppContext(
        db_path=db_path
    )
    ctx.obj = app_context

    if temp_conn_for_fm:
        temp_conn_for_fm.close()

    if ctx.invoked_subcommand is None:
        if "tui" in ctx.command.commands:
            ctx.invoke(launch_tui_command, ctx=ctx)
        else:
            typer.echo(
                "Error: TUI command not found. Cannot launch by default.", err=True
            )

    ctx.call_on_close(app_context.close_db_conn)

@app.command(name="tui", help="Launch the Text User Interface to manage presets.")
def launch_tui_command(ctx: typer.Context):
    """
    Launch the main Text User Interface for managing presets.
    """
    app_context: AppContext = ctx.obj
    conn = None

    while True:
        try:
            conn = app_context.get_db_conn()
            flag_manager_instance = app_context.get_flag_manager()

            action, item_id = display_preset_list_screen(conn)

            if action == "select" and item_id is not None:
                typer.echo(f"TUI: User selected preset ID: {item_id}")
                preset_details = database.get_preset_by_id(conn, item_id)
                if preset_details:
                    command_str = executor.build_aider_command(
                        preset_details, conn
                    )
                    if command_str:
                        if display_command_preview_screen(command_str):
                            executor.execute_aider_command(command_str)
                        else:
                            typer.echo("Execution cancelled by user.")
                    else:
                        typer.echo("Error: Could not build command string.", err=True)
                else:
                    typer.echo(
                        f"Error: Could not retrieve details for preset ID {item_id}.",
                        err=True,
                    )
                break

            elif action == "create":
                typer.echo("TUI: User chose to CREATE new preset via Wizard.")
                saved = display_config_wizard(
                    conn, flag_manager_instance
                )
                if saved:
                    typer.echo("New preset creation process finished (saved).")
                else:
                    typer.echo("New preset creation process cancelled.")

            elif action == "edit" and item_id is not None:
                typer.echo(f"TUI: User chose to EDIT preset ID: {item_id}.")
                saved = display_preset_edit_screen(
                    conn, flag_manager_instance, preset_id=item_id
                )
                if saved:
                    typer.echo(f"Preset ID {item_id} edit process finished (saved).")
                else:
                    typer.echo(f"Preset ID {item_id} edit process cancelled.")

            elif action == "wizard_flag_config":
                typer.echo("TUI: User chose to configure Wizard Flags.")
                from aider_start.tui.wizard_flag_config_screen import display_wizard_flag_config_screen
                display_wizard_flag_config_screen(flag_manager_instance, app_context)

            elif action == "confirm_delete" and item_id is not None:
                preset_to_delete_id = item_id
                preset_to_delete_details = database.get_preset_by_id(
                    conn, preset_to_delete_id
                )
                preset_name = (
                    preset_to_delete_details.name
                    if preset_to_delete_details
                    else f"ID {preset_to_delete_id}"
                )

                from prompt_toolkit.shortcuts import yes_no_dialog as pt_yes_no_dialog
                from prompt_toolkit.shortcuts import message_dialog as pt_message_dialog

                confirm_delete = pt_yes_no_dialog(
                    title="Confirm Deletion",
                    text=f"Are you sure you want to delete preset '{preset_name}'?",
                    style=tui_default_style,
                ).run()

                if confirm_delete:
                    deleted = database.delete_preset(conn, preset_to_delete_id)
                    if deleted:
                        pt_message_dialog(
                            title="Success",
                            text=f"Preset '{preset_name}' deleted.",
                            style=tui_default_style,
                        ).run()
                    else:
                        pt_message_dialog(
                            title="Error",
                            text=f"Failed to delete preset '{preset_name}'.",
                            style=tui_default_style,
                        ).run()
                else:
                    typer.echo("Deletion cancelled by user.")

            elif action == "advanced_settings" and item_id is not None:
                preset_id_for_adv_settings = item_id
                typer.echo(
                    f"TUI: User chose to manage ADVANCED settings for preset ID: "
                    f"{preset_id_for_adv_settings}."
                )
                config_manager_instance = (
                    app_context.get_flag_manager()
                )

                display_advanced_settings_manager_screen(
                    conn,
                    config_manager_instance,
                    preset_id_for_adv_settings,
                )

            elif action is None:
                typer.echo("TUI: User exited.")
                break

        except Exception as e:
            typer.echo(
                f"Error during TUI loop or command processing: {e}",
                err=True,
            )
            break

@app.command()
def hello(name: str = typer.Argument("World", help="The name to say hello to.")):
    """
    A simple command that says hello. Useful for testing the CLI setup.
    """
    typer.echo(f"Hello {name} from aider-start!")
