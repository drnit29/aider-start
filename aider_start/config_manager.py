import json
import os
from pathlib import Path

def get_config_path():
    home = Path.home()
    config_dir = home / ".aider-start"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "presets.json"

def load_presets():
    config_file = get_config_path()
    if not config_file.exists():
        return {}
    try:
        return json.loads(config_file.read_text())
    except json.JSONDecodeError:
        return {}

def save_presets(presets):
    config_file = get_config_path()
    config_file.write_text(json.dumps(presets, indent=2))
