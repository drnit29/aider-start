import sqlite3
from typing import List, Optional, Dict, Any, Tuple

from .flags.flags_api import API_FLAGS
from .flags.flags_model import MODEL_FLAGS
from .flags.flags_git import GIT_FLAGS
from .flags.flags_output import OUTPUT_FLAGS
from .flags.flags_cache import CACHE_FLAGS
from .flags.flags_repomap import REPOMAP_FLAGS
from .flags.flags_history import HISTORY_FLAGS
from .flags.flags_fixing import FIXING_FLAGS
from .flags.flags_analytics import ANALYTICS_FLAGS
from .flags.flags_upgrading import UPGRADING_FLAGS
from .flags.flags_modes import MODES_FLAGS
from .flags.flags_voice import VOICE_FLAGS
from .flags.flags_other import OTHER_FLAGS
from .flags.flags_custom import CUSTOM_FLAGS

DEFAULT_FLAG_METADATA = (
    API_FLAGS
    + MODEL_FLAGS
    + GIT_FLAGS
    + OUTPUT_FLAGS
    + CACHE_FLAGS
    + REPOMAP_FLAGS
    + HISTORY_FLAGS
    + FIXING_FLAGS
    + ANALYTICS_FLAGS
    + UPGRADING_FLAGS
    + MODES_FLAGS
    + VOICE_FLAGS
    + OTHER_FLAGS
    + CUSTOM_FLAGS
)

class FlagManager:
    def __init__(self, db_conn: sqlite3.Connection, database_module=None):
        if database_module is None:
            from ..db import database as database_module
        self.conn = db_conn
        self.database = database_module
        self.metadata_cache: Optional[List[Dict[str, Any]]] = None
        self.metadata_dict_cache: Optional[Dict[str, Dict[str, Any]]] = None
        self.load_metadata()

    def load_metadata(self, force_reload: bool = False):
        """Loads flag metadata from the database, populating initial data if empty."""
        if self.metadata_cache is None or force_reload:
            all_meta = self.database.get_all_flag_metadata(self.conn)
            if not all_meta:
                print("Flag metadata table is empty. Populating with default flags...")
                self.database.populate_flag_metadata(self.conn, DEFAULT_FLAG_METADATA)
                all_meta = self.database.get_all_flag_metadata(self.conn)

            self.metadata_cache = all_meta
            self.metadata_dict_cache = {item["name"]: item for item in all_meta}

    def set_flag_wizard_visibility(self, flag_name: str, is_visible: bool) -> bool:
        """Sets the wizard_visible status for a flag and reloads metadata."""
        # Ensure database_module is correctly referenced, it's self.database
        updated = self.database.update_flag_wizard_visibility(
            self.conn, flag_name, is_visible
        )
        if updated:
            self.load_metadata(force_reload=True)  # Reload cache
        return updated

    def get_flag_details(self, flag_name: str) -> Optional[Dict[str, Any]]:
        """Returns details for a specific flag from the cache."""
        if self.metadata_dict_cache is None:
            self.load_metadata()
        return (
            self.metadata_dict_cache.get(flag_name)
            if self.metadata_dict_cache
            else None
        )

    def get_all_flags(self) -> List[Dict[str, Any]]:
        """Returns all flag metadata from the cache."""
        if self.metadata_cache is None:
            self.load_metadata()
        return self.metadata_cache if self.metadata_cache else []

    def get_flags_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Filters flags by category from the cache."""
        if self.metadata_cache is None:
            self.load_metadata()
        if self.metadata_cache:
            return [
                flag for flag in self.metadata_cache if flag.get("category") == category
            ]
        return []

    def validate_flag(self, flag_name: str, value: Optional[str]) -> Tuple[bool, str]:
        """
        Validates a flag's value based on its metadata (type, requires_value).
        Returns (isValid, message).
        """
        details = self.get_flag_details(flag_name)
        if not details:
            return False, f"Flag '{flag_name}' not recognized."

        requires_value = details.get("requires_value", True)
        value_type = details.get("value_type", "string")

        if requires_value and (value is None or str(value).strip() == ""):
            return False, f"Flag '{flag_name}' requires a value."

        if not requires_value and value is not None and str(value).strip() != "":
            if value_type == "boolean":
                if str(value).lower() not in [
                    "true",
                    "false",
                    "yes",
                    "no",
                    "1",
                    "0",
                    "",
                ]:
                    return (
                        False,
                        f"Flag '{flag_name}' is boolean; value '{value}' is not a recognized boolean.",
                    )

        if value_type == "integer" and value is not None:
            try:
                int(value)
            except ValueError:
                return False, f"Flag '{flag_name}' expects an integer, got '{value}'."

        return True, "Valid"
