
import sys
from pathlib import Path
from typing import Optional
import sqlite3

from aider_start.db import database
from aider_start.config.config_manager import FlagManager

class AppContext:
    def __init__(
        self,
        db_path: Path,
        flag_manager: Optional[FlagManager] = None,
    ):
        self.db_path = db_path
        self.db_conn: Optional[sqlite3.Connection] = None
        self.flag_manager = flag_manager

    def get_db_conn(self) -> sqlite3.Connection:
        if self.db_conn is None:
            self.db_conn = database.get_db_connection(self.db_path)
        return self.db_conn

    def close_db_conn(self):
        if self.db_conn is not None:
            self.db_conn.close()
            self.db_conn = None

    def get_flag_manager(self) -> FlagManager:
        if self.flag_manager is None:
            conn = self.get_db_conn()
            if FlagManager:
                self.flag_manager = FlagManager(conn)
            else:
                raise RuntimeError("FlagManager class not available.")
        return self.flag_manager
