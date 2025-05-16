import sys
import sqlite3
from typing import List, Optional, Dict, Any


def populate_flag_metadata(
    conn: sqlite3.Connection, flag_data_list: List[Dict[str, Any]]
):
    """Populates the flag_metadata table with initial data. Uses INSERT OR IGNORE."""
    sql = """
    INSERT OR IGNORE INTO flag_metadata
    (name, description, category, value_type, default_value, is_deprecated, requires_value, wizard_visible)
    VALUES (:name, :description, :category, :value_type, :default_value, :is_deprecated, :requires_value, :wizard_visible)
    """
    cursor = conn.cursor()
    try:
        # Convert boolean values to integers for SQLite
        processed_flag_data = []
        for item in flag_data_list:
            item_copy = item.copy()
            item_copy["is_deprecated"] = 1 if item_copy.get("is_deprecated") else 0
            item_copy["requires_value"] = (
                1 if item_copy.get("requires_value", True) else 0
            )
            item_copy["wizard_visible"] = (
                1 if item_copy.get("wizard_visible", True) else 0
            )
            processed_flag_data.append(item_copy)
        cursor.executemany(sql, processed_flag_data)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error populating flag_metadata: {e}", file=sys.stderr)
        conn.rollback()


def get_flag_metadata(
    conn: sqlite3.Connection, flag_name: str
) -> Optional[Dict[str, Any]]:
    """Retrieves metadata for a specific flag."""
    sql = "SELECT name, description, category, value_type, default_value, is_deprecated, requires_value, wizard_visible FROM flag_metadata WHERE name = ?"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (flag_name,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            data["is_deprecated"] = bool(data["is_deprecated"])
            data["requires_value"] = bool(data["requires_value"])
            data["wizard_visible"] = bool(
                data.get("wizard_visible", 1)
            )  # Default to True if somehow missing
            return data
        return None
    except sqlite3.Error as e:
        print(
            f"Database error getting flag metadata for '{flag_name}': {e}",
            file=sys.stderr,
        )
        return None


def get_all_flag_metadata(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Retrieves all flag metadata, ordered by category then name."""
    sql = "SELECT name, description, category, value_type, default_value, is_deprecated, requires_value, wizard_visible FROM flag_metadata ORDER BY category, name"
    cursor = conn.cursor()
    metadata_list = []
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            data = dict(row)
            data["is_deprecated"] = bool(data["is_deprecated"])
            data["requires_value"] = bool(data["requires_value"])
            data["wizard_visible"] = bool(
                data.get("wizard_visible", 1)
            )  # Default to True if somehow missing
            metadata_list.append(data)
        return metadata_list
    except sqlite3.Error as e:
        print(f"Database error listing all flag metadata: {e}", file=sys.stderr)
        return []


def update_flag_wizard_visibility(
    conn: sqlite3.Connection, flag_name: str, is_visible: bool
) -> bool:
    """Updates the wizard_visible status for a specific flag."""
    sql = "UPDATE flag_metadata SET wizard_visible = ? WHERE name = ?"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (1 if is_visible else 0, flag_name))
        conn.commit()
        return cursor.rowcount > 0  # True if a row was updated
    except sqlite3.Error as e:
        print(
            f"Database error updating wizard_visible for flag '{flag_name}': {e}",
            file=sys.stderr,
        )
        conn.rollback()
        return False


# Removed duplicate/misplaced except block:
#    except sqlite3.Error as e:
#        print(f"Database error listing all flag metadata: {e}", file=sys.stderr)
#        return []
