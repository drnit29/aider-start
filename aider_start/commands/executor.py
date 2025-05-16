# Command execution module for aider-start
import sys
import shlex  # For proper argument splitting/quoting
import subprocess  # For executing commands
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Dict
import sqlite3  # Added for db_conn type hint

# Import database module for DB calls
try:
    from ..db import database as db_module
except ImportError:
    # Fallback for standalone execution or if path issues occur during testing
    # This is a common pattern in the project, but ensure it's robust.
    # For executor, direct relative import should be preferred if structure is stable.
    project_root_db_import = Path(__file__).resolve().parent.parent.parent
    if str(project_root_db_import) not in sys.path:
        sys.path.insert(0, str(project_root_db_import))
    try:
        from aider_start.db import database as db_module
    except ImportError:
        print(
            "Critical Error: Could not import database module for executor.",
            file=sys.stderr,
        )
        db_module = None


if TYPE_CHECKING:
    from ..db.models import Preset
else:
    try:
        from ..db.models import Preset
    except ImportError:
        project_root_model_import = Path(__file__).resolve().parent.parent.parent
        if str(project_root_model_import) not in sys.path:
            sys.path.insert(0, str(project_root_model_import))
        try:
            from aider_start.db.models import Preset
        except ImportError:
            print(
                "Critical Error: Could not import Preset model for executor.",
                file=sys.stderr,
            )

            class Preset:  # type: ignore
                id: Optional[int] = None  # Add id for db calls
                flags: Dict[str, Optional[str]]  # Ensure flags is typed
                name: str

                def __init__(
                    self,
                flags: Optional[Dict[str, Optional[str]]] = None,
                name: str = "dummy",
                id: Optional[int] = None,
            ):
                    self.flags = flags if flags is not None else {}
                    self.name = name
                    self.id = id


def build_aider_command(preset: Preset, db_conn: sqlite3.Connection) -> str:
    """
    Constructs the aider command-line string from a preset object.
    It now fetches advanced model settings/metadata paths from the DB.
    """
    command_parts = ["aider"]

    if preset.flags:
        for flag_name, flag_value in preset.flags.items():
            clean_flag_name = str(flag_name).lstrip("-")

            # Não pular mais aqui, deixar que sejam adicionadas se estiverem em preset.flags
            # if clean_flag_name in ["model-settings-file", "model-metadata-file"]:
            #     continue

            if flag_value is None or str(flag_value).strip() == "":
                command_parts.append(f"--{clean_flag_name}")
            else:
                command_parts.append(f"--{clean_flag_name}")
                command_parts.append(shlex.quote(str(flag_value)))

    # Fetch and append advanced model settings/metadata file paths
    # Ensure preset.id is not None before using it in DB calls.
    # The Preset model in models.py defines id as Optional[int]=.
    if preset.id is not None and db_module:
        primary_model_name = preset.flags.get("model")
        if primary_model_name:
            # Get settings file path only if not already specified in preset.flags
            if "model-settings-file" not in preset.flags:
                settings_data = db_module.get_model_settings(
                    db_conn, preset.id, primary_model_name
                )
                if settings_data and settings_data.get("file_path"):
                    command_parts.append("--model-settings-file")
                    command_parts.append(
                        shlex.quote(str(settings_data["file_path"]))
                    )

            # Get metadata file path only if not already specified in preset.flags
            if "model-metadata-file" not in preset.flags:
                metadata_data = db_module.get_model_metadata(
                    db_conn, preset.id, primary_model_name
                )
                if metadata_data and metadata_data.get("file_path"):
                    command_parts.append("--model-metadata-file")
                    command_parts.append(
                        shlex.quote(str(metadata_data["file_path"]))
                    )

    return " ".join(command_parts)


def execute_aider_command(command_string: str):
    """
    Executes the given command string.
    For now, it prints the command and uses subprocess.run.
    This might be changed to Popen for more interactive scenarios later.
    """
    print(f"\nExecuting: {command_string}")
    try:
        # Using shell=False is safer if command_string is already a single string.
        # If command_string needs shell interpretation (like pipes, wildcards not handled by shlex),
        # then shell=True would be needed, but it's less safe.
        # For `aider` commands built with shlex.quote, shell=False with shlex.split is best.
        # However, the current build_aider_command returns a single string.
        # If `aider` itself is a simple executable name without path issues,
        # `shlex.split(command_string)` would be the argument to `subprocess.run`.

        # For simplicity and direct execution as if typed in a shell:
        # (Assumes 'aider' is in PATH)
        # Note: On Windows, subprocess.run with a string command often requires shell=True
        # or the full path to the executable.
        # If 'aider' is a script (e.g., aider.cmd, aider.sh), shell=True might be more reliable
        # cross-platform without knowing exact aider installation.

        # Let's try to make it more robust by splitting if not on Windows,
        # as shell=True can be risky.
        if sys.platform == "win32":
            process = subprocess.run(
                command_string, shell=True, check=False
            )  # check=False to inspect returncode
        else:
            process = subprocess.run(shlex.split(command_string), check=False)

        if process.returncode != 0:
            print(
                f"Command exited with error code: {process.returncode}",
                file=sys.stderr,
            )
        # No output is captured here, command runs in the same terminal context.
        # For TUI integration, we might want to use Popen to handle I/O differently or run in a new terminal.
    except FileNotFoundError:
        print(
            f"Error: The 'aider' command was not found. Is it installed and in your PATH?",
            file=sys.stderr,
        )
    except subprocess.CalledProcessError as e:
        # This won't be hit if check=False
        print(f"Error executing aider: {e}", file=sys.stderr)
    except Exception as e:
        print(
            f"An unexpected error occurred during command execution: {e}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    print("Testing command executor functions...")
    print("\n--- Testing build_aider_command ---")

    ActualPreset = None
    try:
        from aider_start.db.models import Preset as ImportedPreset

        ActualPreset = ImportedPreset
    except ImportError:
        print(
            "Warning: aider_start.db.models.Preset not found, using dummy for testing build_aider_command."
        )

        class DummyPresetForBuild:  # type: ignore
            def __init__(
                self,
                name,
                flags=None,
                description=None,
                id=None,
                created_at=None,
                updated_at=None,
                model_settings_file=None,
                model_metadata_file=None,
            ):
                self.id = id
                self.name = name
                self.description = description
                self.created_at = created_at
                self.updated_at = updated_at
                self.flags = flags if flags is not None else {}
                self.model_settings_file = model_settings_file
                self.model_metadata_file = model_metadata_file

        ActualPreset = DummyPresetForBuild

    # Test cases for build_aider_command (copied from previous step, assumed to pass)
    preset1_flags = {"model": "gpt-4o", "stream": None}
    test_preset1 = ActualPreset(name="Test1", flags=preset1_flags)
    cmd1 = build_aider_command(test_preset1)
    expected_cmd1 = "aider --model gpt-4o --stream"
    assert cmd1 == expected_cmd1, "Test Case 1 Failed"
    print("Build Test Case 1 Passed.")

    preset2_flags = {
        "model": "ollama/deepseek-coder:33b-instruct-q8_0",
        "custom-prompt": "Act as a helpful assistant.",
    }
    test_preset2 = ActualPreset(name="Test2", flags=preset2_flags)
    cmd2 = build_aider_command(test_preset2)
    expected_cmd2 = (
        "aider --model ollama/deepseek-coder:33b-instruct-q8_0 --custom-prompt 'Act as a helpful assistant.'"
    )
    assert cmd2 == expected_cmd2, "Test Case 2 Failed"
    print("Build Test Case 2 Passed.")

    # ... (other build test cases can be added back if desired for completeness) ...

    print("\n--- Testing execute_aider_command ---")
    print("Note: This test will attempt to run 'aider --version'.")
    print(
        "Ensure 'aider' is installed and accessible in your PATH "
        "for this test to pass meaningfully."
    )

    # Test with a simple, non-interactive aider command like --version
    # This assumes 'aider' is installed and in the PATH.
    version_command = "aider --version"
    execute_aider_command(version_command)

    print("\nExecutor tests finished.")
    print(
        "If 'aider --version' ran and showed output, "
        "execute_aider_command is likely working."
    )
    print(
        "If 'aider' command not found error, check your aider installation and PATH."
    )
