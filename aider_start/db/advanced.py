import sys
import sqlite3
from typing import Dict, Tuple, Optional


def get_all_advanced_settings_for_preset(
    conn: sqlite3.Connection, preset_id: int
) -> Tuple[Dict[str, Tuple[str, Optional[str]]], Dict[str, Tuple[str, Optional[str]]]]:
    """
    Retrieves all advanced model settings and metadata for a given preset.
    Returns a tuple of two dictionaries:
    ( {model_name: (settings_json, file_path)}, {model_name: (metadata_json, file_path)} )
    """
    all_settings: Dict[str, Tuple[str, Optional[str]]] = {}
    all_metadata: Dict[str, Tuple[str, Optional[str]]] = {}

    settings_sql = "SELECT model_name, settings_json, file_path FROM model_settings WHERE preset_id = ?"
    metadata_sql = "SELECT model_name, metadata_json, file_path FROM model_metadata WHERE preset_id = ?"

    cursor = conn.cursor()
    try:
        cursor.execute(settings_sql, (preset_id,))
        for row in cursor.fetchall():
            all_settings[row["model_name"]] = (row["settings_json"], row["file_path"])

        cursor.execute(metadata_sql, (preset_id,))
        for row in cursor.fetchall():
            all_metadata[row["model_name"]] = (row["metadata_json"], row["file_path"])

    except sqlite3.Error as e:
        print(
            f"Database error getting all advanced settings for preset ID {preset_id}: {e}",
            file=sys.stderr,
        )

    print(
        f"DEBUG: get_all_advanced_settings_for_preset for preset_id {preset_id} - returning settings: {all_settings}, metadata: {all_metadata}"
    )  # DEBUG
    return all_settings, all_metadata
