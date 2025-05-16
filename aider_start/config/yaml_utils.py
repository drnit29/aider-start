import sys
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


def load_yaml_file(file_path: Path) -> Optional[Dict[Any, Any]]:
    """Loads data from a YAML file."""
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else None
    except FileNotFoundError:
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {file_path}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error loading YAML file {file_path}: {e}", file=sys.stderr)
        return None


def save_yaml_file(data: Dict[Any, Any], file_path: Path) -> bool:
    """Saves data to a YAML file."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as f:
            yaml.dump(
                data, f, default_flow_style=False, sort_keys=False, allow_unicode=True
            )
        return True
    except Exception as e:
        print(f"Error saving YAML file {file_path}: {e}", file=sys.stderr)
        return False
