
import sys
from pathlib import Path

from .commands import app

def run_cli():
    is_run_as_module = (
        Path(sys.argv[0]).name == "main.py"
        and Path(sys.argv[0]).parent.name == "aider_start"
    )
    is_run_as_script = Path(sys.argv[0]).name == "main.py"

    if (is_run_as_module and len(sys.argv) == 1) or (
        is_run_as_script
        and len(sys.argv) == 1
        and not (len(sys.argv) > 1 and sys.argv[1].startswith("-"))
    ):
        sys.argv.insert(1, "tui")

    app()
