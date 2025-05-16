
import sys
import sqlite3
from typing import Optional, Tuple, Dict, Any  # Adicionado Dict, Any

def add_or_update_model_settings(
    conn: sqlite3.Connection,
    preset_id: Optional[int] = None,
    model_name: Optional[str] = None,
    settings_json: str = "",
    file_path: Optional[str] = None,
):
    """Adds or updates model settings.

    Args:
        conn: sqlite3.Connection
        preset_id: int or None (Preset ID to associate, or None for global/model-specific)
        model_name: str or None (Model name to associate, or None for preset-specific/global)
        settings_json: str (JSON string of settings)
        file_path: str or None (optional file path for settings)

    Usage patterns:
        - Global default: preset_id=None, model_name=None
        - Model-specific: preset_id=None, model_name=str
        - Preset-specific: preset_id=int, model_name=None
        - Preset-model: preset_id=int, model_name=str

    NOTE: The argument order matches usage throughout the codebase and tests!
    """
    cursor = conn.cursor()
    try:
        # Garantir que o preset existe se preset_id não é None
        if preset_id is not None:
            cursor.execute(
                "INSERT OR IGNORE INTO presets (id, name, description) VALUES (?, ?, ?)",
                (preset_id, f"Preset {preset_id}", ""),
            )

        sql = """
        INSERT OR REPLACE INTO model_settings (preset_id, model_name, settings_json, file_path)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(sql, (preset_id, model_name, settings_json, file_path))
        if preset_id is not None:
            cursor.execute(
                "UPDATE presets SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (preset_id,),
            )
        conn.commit()
    except sqlite3.Error as e:
        err_context = f"preset ID {preset_id}" if preset_id else "global settings"
        if model_name:
            err_context += f", model '{model_name}'"
        print(
            f"Database error adding/updating model settings for {err_context}: {e}",
            file=sys.stderr,
        )
        conn.rollback()


def get_model_settings(
    conn: sqlite3.Connection,
    preset_id: Optional[int] = None,
    model_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieves specific model settings as a dictionary.
    Uses IS NULL for None values of preset_id or model_name.
    """
    conditions = []
    params = []

    if preset_id is None:
        conditions.append("preset_id IS NULL")
    else:
        conditions.append("preset_id = ?")
        params.append(preset_id)

    if model_name is None:
        conditions.append("model_name IS NULL")
    else:
        conditions.append("model_name = ?")
        params.append(model_name)

    sql = f"SELECT preset_id, model_name, settings_json, file_path FROM model_settings WHERE {' AND '.join(conditions)}"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, tuple(params))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        err_context = f"preset ID {preset_id}" if preset_id else "global settings"
        if model_name:
            err_context += f", model '{model_name}'"
        print(
            f"Database error getting model settings for {err_context}: {e}",
            file=sys.stderr,
        )
        return None


def delete_model_settings(
    conn: sqlite3.Connection,
    preset_id: Optional[int] = None,
    model_name: Optional[str] = None,
) -> bool:
    """Deletes specific model settings.
    Uses IS NULL for None values of preset_id or model_name.
    """
    conditions = []
    params = []

    if preset_id is None:
        conditions.append("preset_id IS NULL")
    else:
        conditions.append("preset_id = ?")
        params.append(preset_id)

    if model_name is None:
        conditions.append("model_name IS NULL")
    else:
        conditions.append("model_name = ?")
        params.append(model_name)
    
    # Ensure at least one identifier is not None to prevent deleting all settings
    if preset_id is None and model_name is None:
        # This case could be for deleting global default settings.
        # If this is not desired, add a check here. For now, we allow it.
        pass  # Allow deleting global default if both are None

    sql = f"DELETE FROM model_settings WHERE {' AND '.join(conditions)}"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, tuple(params))
        if cursor.rowcount > 0 and preset_id is not None:
            cursor.execute(
                "UPDATE presets SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (preset_id,),
            )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        err_context = f"preset ID {preset_id}" if preset_id else "global settings"
        if model_name:
            err_context += f", model '{model_name}'"
        print(
            f"Database error deleting model settings for {err_context}: {e}",
            file=sys.stderr,
        )
        conn.rollback()
        return False
