from typing import Optional
from pathlib import Path
import sqlite3
from modules.core import logger
import json

NO_RESULTS = "No se han encontrado resultados"
NO_CURSOR = "No se ha podido ejecutar la consulta a la base de datos"
QUERY_ERROR = "Error en la consulta a la base de datos"


class Database:
    _instance = None
    _conn = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._conn = None
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            db_path = Path(__file__).parent / "database.db"
            self._conn = sqlite3.connect(str(db_path))
            self._conn.row_factory = sqlite3.Row
            self._create_tables()
            self._initialized = True
            self._conn.execute("PRAGMA foreign_keys = ON")

    def _create_tables(self):
        if self._conn is None:
            logger.error("No hay conexión a la base de datos")
            return

        try:
            sql_path = Path(__file__).parent / "schema.sql"
            if not sql_path.exists():
                logger.error("No se encuentra el archivo %s", str(sql_path))
                return

            with open(sql_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
                if not sql_script:
                    logger.error("El archivo schema.sql está vacío")
                    return

                self._conn.executescript(sql_script)
                self._conn.commit()

        except sqlite3.Error as e:
            logger.error("Error de SQLite al crear las tablas: %s", e)

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        logger.info("Ejecutando consulta: %s", query)

        if self._conn is None:
            raise sqlite3.Error("Database connection is not established.")
        cursor = self._conn.cursor()
        cursor.execute(query, params)
        self._conn.commit()
        return cursor

    def select(self, sql: str, bindings: tuple = ()) -> list[dict]:
        try:
            cursor = self.execute(sql, bindings)
            if not cursor:
                return []
            rows = cursor.fetchall()

            response = [dict(row) for row in rows] if rows else []
            logger.debug(json.dumps(response, ensure_ascii=False, indent=2))
            return response
        except sqlite3.Error as e:
            logger.error("Error en la consulta: %s", e)
            return []

    def single(self, sql: str, bindings: tuple = ()) -> Optional[dict]:
        try:
            cursor = self.execute(sql, bindings)
            if not cursor:
                return None
            row = cursor.fetchone()

            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error("Error en la consulta: %s", e)
            return None

