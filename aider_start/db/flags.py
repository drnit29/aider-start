import sys
import sqlite3
from typing import Optional # Adicionado Optional


def add_flag_to_preset(
    conn: sqlite3.Connection, preset_id: int, flag_name: str, flag_value: str
) -> Optional[int]: # Adicionado tipo de retorno
    """Adds or updates a flag for a given preset. Updates preset's updated_at. Returns lastrowid or None."""
    sql_upsert_flag = "INSERT OR REPLACE INTO preset_flags (preset_id, flag_name, flag_value) VALUES (?, ?, ?)"
    sql_update_preset_ts = (
        "UPDATE presets SET updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    )
    cursor = conn.cursor()
    try:
        cursor.execute(sql_upsert_flag, (preset_id, flag_name, flag_value))
        cursor.execute(sql_update_preset_ts, (preset_id,))
        conn.commit()
        return cursor.lastrowid # Adicionado retorno
    except sqlite3.Error as e:
        print(
            f"Database error adding/updating flag '{flag_name}' for preset ID {preset_id}: {e}",
            file=sys.stderr,
        )
        conn.rollback()
        return False # Adicionado retorno
        return None # Adicionado retorno


def delete_flag_from_preset(conn: sqlite3.Connection, preset_id: int, flag_name: str) -> bool: # Adicionado tipo de retorno
    """Deletes a specific flag from a preset. Updates preset's updated_at. Returns True if a row was deleted."""
    sql_delete_flag = "DELETE FROM preset_flags WHERE preset_id = ? AND flag_name = ?"
    sql_update_preset_ts = (
        "UPDATE presets SET updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    )
    cursor = conn.cursor()
    try:
        cursor.execute(sql_delete_flag, (preset_id, flag_name))
        if cursor.rowcount > 0:
            cursor.execute(sql_update_preset_ts, (preset_id,))
        conn.commit()
        return cursor.rowcount > 0 # Adicionado retorno
    except sqlite3.Error as e:
        print(
            f"Database error deleting flag '{flag_name}' from preset ID {preset_id}: {e}",
            file=sys.stderr,
        )
        conn.rollback()
