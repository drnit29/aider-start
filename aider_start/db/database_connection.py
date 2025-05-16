import sys
import sqlite3
from pathlib import Path
from typing import Optional


def get_default_db_path() -> Path:
    """Gets the default platform-specific path for the database file."""
    home = Path.home()
    if sys.platform == "win32":
        path = home / "AppData" / "Local" / "aider-start"
    elif sys.platform == "darwin":
        path = home / "Library" / "Application Support" / "aider-start"
    else:
        path = home / ".config" / "aider-start"
    path.mkdir(parents=True, exist_ok=True)
    return path / "aider_start.db"


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Gets a database connection with row_factory and foreign keys enabled."""
    if db_path is None:
        db_path = get_default_db_path()
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error to {db_path}: {e}", file=sys.stderr)
        raise


def setup_database(
    db_path: Optional[Path] = None, conn: Optional[sqlite3.Connection] = None
):
    """
    Sets up the database schema if it doesn't already exist.
    Uses the provided connection if given, otherwise creates one based on db_path.
    """
    close_conn_after = False
    if conn is None:
        if db_path is None:
            db_path = get_default_db_path()
        conn = get_db_connection(db_path)
        close_conn_after = True  # Only close if we opened it here

    # conn must be non-None at this point
    if conn is None:  # Should not happen if get_db_connection raises on failure
        print("Failed to establish database connection for setup.", file=sys.stderr)
        return

    try:
        cursor = conn.cursor()

        # Create presets table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )
        # Add trigger to update updated_at on preset update
        cursor.execute(
            """
        CREATE TRIGGER IF NOT EXISTS update_preset_updated_at
        AFTER UPDATE ON presets
        FOR EACH ROW
        BEGIN
            UPDATE presets SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
        END;
        """
        )

        # Create preset_flags table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS preset_flags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preset_id INTEGER NOT NULL,
            flag_name TEXT NOT NULL,
            flag_value TEXT,
            FOREIGN KEY (preset_id) REFERENCES presets (id) ON DELETE CASCADE,
            UNIQUE (preset_id, flag_name)
        )
        """
        )

        # Create model_settings table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS model_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preset_id INTEGER, -- Made nullable for global/model-specific settings
            model_name TEXT,   -- Made nullable for global/preset-specific settings
            settings_json TEXT NOT NULL,
            file_path TEXT,
            FOREIGN KEY (preset_id) REFERENCES presets (id) ON DELETE CASCADE,
            UNIQUE (preset_id, model_name) -- Handles NULLs correctly for uniqueness
        )
        """
        )

        # Create model_metadata table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS model_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preset_id INTEGER NOT NULL,
            model_name TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            file_path TEXT,
            FOREIGN KEY (preset_id) REFERENCES presets (id) ON DELETE CASCADE,
            UNIQUE (preset_id, model_name)
        )
        """
        )

        # Create flag_metadata table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS flag_metadata (
            name TEXT PRIMARY KEY,
            description TEXT,
            category TEXT,
            value_type TEXT,
            default_value TEXT,
            is_deprecated BOOLEAN DEFAULT 0,
            requires_value BOOLEAN DEFAULT 0,
            wizard_visible BOOLEAN DEFAULT 1
        )
        """
        )

        # Create settings_templates table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS settings_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            settings_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )
        # Add trigger to update updated_at on settings_template update
        cursor.execute(
            """
        CREATE TRIGGER IF NOT EXISTS update_settings_template_updated_at
        AFTER UPDATE ON settings_templates
        FOR EACH ROW
        BEGIN
            UPDATE settings_templates SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
        END;
        """
        )

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error during setup: {e}", file=sys.stderr)
        # Rollback might be good here if conn was passed in and an error occurs
        if (
            conn and close_conn_after
        ):  # Or if conn was passed, caller handles rollback/commit
            try:
                conn.rollback()
            except sqlite3.Error as rb_err:
                print(f"Error during rollback: {rb_err}", file=sys.stderr)

    finally:
        if conn and close_conn_after:  # Only close if this function opened it
            conn.close()
