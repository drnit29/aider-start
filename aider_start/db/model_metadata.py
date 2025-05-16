
import sys
import sqlite3
from typing import Optional, Tuple, Dict, Any  # Adicionado Dict, Any

def add_or_update_model_metadata(
    conn: sqlite3.Connection,
    preset_id: int,
    model_name: str,
    metadata_json: str,
    file_path: Optional[str] = None,
):
    """Adds or updates model-specific metadata for a preset."""
    cursor = conn.cursor()
    try:
        # Garantir que o preset existe
        cursor.execute(
            "INSERT OR IGNORE INTO presets (id, name, description) VALUES (?, ?, ?)",
            (preset_id, f"Preset {preset_id}", ""),
        )

        sql = """
        INSERT OR REPLACE INTO model_metadata (preset_id, model_name, metadata_json, file_path)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(sql, (preset_id, model_name, metadata_json, file_path))
        cursor.execute(
            "UPDATE presets SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (preset_id,),
        )
        conn.commit()
    except sqlite3.Error as e:
        print(
            f"Database error adding/updating model metadata for preset ID {preset_id}, model '{model_name}': {e}",
            file=sys.stderr,
        )
        conn.rollback()

def get_model_metadata(
    conn: sqlite3.Connection, preset_id: int, model_name: str
) -> Optional[Dict[str, Any]]:  # Alterado tipo de retorno para Dict
    """Retrieves model-specific metadata as a dictionary for a preset and model name."""
    sql = "SELECT preset_id, model_name, metadata_json, file_path FROM model_metadata WHERE preset_id = ? AND model_name = ?"  # Adicionado preset_id, model_name para o dict
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (preset_id, model_name))
        row = cursor.fetchone()
        # return (row["metadata_json"], row["file_path"]) if row else None
        return dict(row) if row else None  # Retorna um dicionário
    except sqlite3.Error as e:
        print(
            f"Database error getting model metadata for preset ID {preset_id}, model '{model_name}': {e}",
            file=sys.stderr,
        )
        return None

def delete_model_metadata(
    conn: sqlite3.Connection, preset_id: int, model_name: str
) -> bool:
    """Deletes model-specific metadata for a preset and model name."""
    sql = "DELETE FROM model_metadata WHERE preset_id = ? AND model_name = ?"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (preset_id, model_name))
        if (
            cursor.rowcount > 0
        ):  # Only update timestamp if something was actually deleted
            cursor.execute(
                "UPDATE presets SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (preset_id,),
            )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(
            f"Database error deleting model metadata for preset ID {preset_id}, model '{model_name}': {e}",
            file=sys.stderr,
        )
        conn.rollback()
        return False
