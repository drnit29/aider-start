import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json


def load_json_file(file_path: Path) -> Optional[Dict[Any, Any]]:
    """Loads data from a JSON file."""
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else None
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {file_path}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error loading JSON file {file_path}: {e}", file=sys.stderr)
        return None


def save_json_file(data: Dict[Any, Any], file_path: Path) -> bool:
    """Saves data to a JSON file."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {e}", file=sys.stderr)
        return False
