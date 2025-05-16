
if __name__ == "__main__" and __package__ is None:
    import sys
    import os
    # Add the parent directory of aider_start to sys.path for package imports to work
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aider_start.cli import AppContext, app, main_operations, launch_tui_command, hello, run_cli

__all__ = [
    "AppContext",
    "app",
    "main_operations",
    "launch_tui_command",
    "hello",
    "run_cli",
]

if __name__ == "__main__":
    run_cli()
