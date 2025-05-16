import sys
import sqlite3
from typing import List, Optional
from datetime import datetime

try:
    from .models import Preset
except ImportError:
    from dataclasses import dataclass, field

    @dataclass
    class Preset:
        id: Optional[int] = None
        name: str = ""
        description: str = ""
        flags: dict = field(default_factory=dict)
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None


def create_preset(
    conn: sqlite3.Connection, name: str, description: str = ""
) -> Optional[int]:
    """Creates a new preset and returns its ID, or None on error."""
    sql = "INSERT INTO presets (name, description, created_at, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (name, description))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"Error: Preset name '{name}' already exists.", file=sys.stderr)
        conn.rollback()
        return None
    except sqlite3.Error as e:
        print(f"Database error creating preset '{name}': {e}", file=sys.stderr)
        conn.rollback()
        return None


def get_preset_by_id(conn: sqlite3.Connection, preset_id: int) -> Optional[Preset]:
    """Retrieves a preset by its ID, including its flags, advanced settings, and metadata."""
    from .advanced import get_all_advanced_settings_for_preset
    import json

    preset_sql = (
        "SELECT id, name, description, created_at, updated_at FROM presets WHERE id = ?"
    )
    flags_sql = "SELECT flag_name, flag_value FROM preset_flags WHERE preset_id = ?"
    cursor = conn.cursor()

    try:
        cursor.execute(preset_sql, (preset_id,))
        preset_row = cursor.fetchone()

        if preset_row:
            created_at_dt = None
            if preset_row["created_at"]:
                try:
                    created_at_dt = datetime.fromisoformat(
                        str(preset_row["created_at"])
                    )
                except (ValueError, TypeError):
                    pass

            updated_at_dt = None
            if preset_row["updated_at"]:
                try:
                    updated_at_dt = datetime.fromisoformat(
                        str(preset_row["updated_at"])
                    )
                except (ValueError, TypeError):
                    pass

            adv_settings, adv_metadata = get_all_advanced_settings_for_preset(
                conn, preset_id
            )

            preset_adv_settings_content = {}
            preset_adv_settings_paths = {}
            for model_name, (json_str, path_str) in adv_settings.items():
                try:
                    preset_adv_settings_content[model_name] = (
                        json.loads(json_str) if json_str else {}
                    )
                except json.JSONDecodeError:
                    preset_adv_settings_content[model_name] = {
                        "error": "Failed to parse settings_json"
                    }
                if path_str:
                    preset_adv_settings_paths[model_name] = path_str

            preset_adv_metadata_content = {}
            preset_adv_metadata_paths = {}
            for model_name, (json_str, path_str) in adv_metadata.items():
                try:
                    preset_adv_metadata_content[model_name] = (
                        json.loads(json_str) if json_str else {}
                    )
                except json.JSONDecodeError:
                    preset_adv_metadata_content[model_name] = {
                        "error": "Failed to parse metadata_json"
                    }
                if path_str:
                    preset_adv_metadata_paths[model_name] = path_str

            preset = Preset(
                id=preset_row["id"],
                name=preset_row["name"],
                description=preset_row["description"],
                created_at=created_at_dt,
                updated_at=updated_at_dt,
                flags={},
                advanced_model_settings=preset_adv_settings_content,
                advanced_model_settings_paths=preset_adv_settings_paths,
                advanced_model_metadata=preset_adv_metadata_content,
                advanced_model_metadata_paths=preset_adv_metadata_paths,
            )

            cursor.execute(flags_sql, (preset_id,))
            flags_rows = cursor.fetchall()
            preset.flags = {row["flag_name"]: row["flag_value"] for row in flags_rows}

            return preset
        else:
            return None
    except sqlite3.Error as e:
        print(f"Database error getting preset ID {preset_id}: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as je:
        print(
            f"JSON decode error processing advanced settings for preset ID {preset_id}: {je}",
            file=sys.stderr,
        )
        return None


def list_presets(conn: sqlite3.Connection) -> List[Preset]:
    """Lists all presets (id, name, description, updated_at for sorting)."""
    sql = "SELECT id, name, description, updated_at FROM presets ORDER BY name ASC"
    cursor = conn.cursor()
    presets_list = []
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            updated_at_dt = None
            if row["updated_at"]:
                try:
                    updated_at_dt = datetime.fromisoformat(str(row["updated_at"]))
                except (ValueError, TypeError):
                    pass
            presets_list.append(
                Preset(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    updated_at=updated_at_dt,
                )
            )
        return presets_list
    except sqlite3.Error as e:
        print(f"Database error listing presets: {e}", file=sys.stderr)
        return []


def update_preset_details(
    conn: sqlite3.Connection, preset_id: int, name: str, description: str
):
    """Updates a preset's name and description. updated_at is handled by trigger."""
    sql = "UPDATE presets SET name = ?, description = ? WHERE id = ?"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (name, description, preset_id))
        conn.commit()
        return cursor.rowcount # Adicionado retorno
    except sqlite3.IntegrityError:
        print(
            f"Error: Cannot update preset ID {preset_id}, name '{name}' might already exist.",
            file=sys.stderr,
        )
        conn.rollback()
        return 0 # Retornar 0 em caso de erro
        return 0 # Retornar 0 em caso de erro
    except sqlite3.Error as e:
        print(
            f"Database error updating preset details for ID {preset_id}: {e}",
            file=sys.stderr,
        )
        conn.rollback()


def delete_preset(conn: sqlite3.Connection, preset_id: int) -> bool:
    """Deletes a preset by its ID. Flags are deleted via CASCADE."""
    sql = "DELETE FROM presets WHERE id = ?"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (preset_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error deleting preset ID {preset_id}: {e}", file=sys.stderr)
        conn.rollback()
        return False
