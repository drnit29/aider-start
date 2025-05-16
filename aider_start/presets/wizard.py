# aider_start/presets/wizard.py
from typing import List, Dict, Any, Optional, Tuple
import sqlite3

try:
    from ..config.config_manager import FlagManager
    from ..db import database
    from ..db.models import Preset
except ImportError:
    # Fallback for standalone testing or path issues
    # This is a simplified fallback, real imports should work in package context
    FlagManager = None
    database = None
    Preset = None


class ConfigWizard:
    def __init__(self, conn: sqlite3.Connection, flag_manager: FlagManager):
        self.conn = conn
        self.flag_manager = flag_manager
        self.current_step = 0
        self.wizard_data: Dict[str, Any] = {
            "name": "",
            "description": "",
            "selected_categories": [],
            "flags": {},  # To store {flag_name: flag_value}
        }

    def get_categories(self) -> List[str]:
        """Returns a unique, sorted list of all flag categories."""
        if not self.flag_manager:
            return []
        all_flags = self.flag_manager.get_all_flags()
        # Filter flags that are wizard_visible before extracting categories
        visible_flags = [flag for flag in all_flags if flag.get("wizard_visible", True)]
        categories = sorted(
            list(
                set(
                    flag.get("category", "Other")
                    for flag in visible_flags  # Use filtered list
                    if flag.get("category")
                )
            )
        )
        return categories

    def get_flags_for_category(self, category: str) -> List[Dict[str, Any]]:
        """Returns wizard_visible flags belonging to a specific category."""
        if not self.flag_manager:
            return []
        category_flags = self.flag_manager.get_flags_by_category(category)
        # Further filter by wizard_visible
        return [flag for flag in category_flags if flag.get("wizard_visible", True)]

    def save_preset(self) -> Optional[int]:
        """Saves the configured preset to the database."""
        if not database or not self.wizard_data["name"]:
            return None

        preset_id = database.create_preset(
            self.conn, self.wizard_data["name"], self.wizard_data["description"]
        )
        if preset_id:
            for flag_name, flag_value in self.wizard_data["flags"].items():
                database.add_flag_to_preset(self.conn, preset_id, flag_name, flag_value)
        return preset_id


# Example usage or more methods to be added here for TUI interaction.
