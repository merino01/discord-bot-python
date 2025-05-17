"""db"""

from typing import TypeVar, Type, Optional, Any
from pathlib import Path
import sqlite3
from modules.core import logger

T = TypeVar("T")
NO_RESULTS = "No se han encontrado resultados"
NO_CURSOR = "No se ha podido ejecutar la consulta a la base de datos"
QUERY_ERROR = "Error en la consulta a la base de datos"


class Database:
    """
    A class to manage a simple SQLite database.
    """

    _instance = None
    _conn = None

    def __new__(cls):
        """
        Ensure that only one instance of the database exists.
        """
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
        """
        Create the necessary tables in the database.
        """
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
        """
        Close the database connection.
        """
        if self._conn:
            self._conn.close()
            self._conn = None

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a SQL query with optional parameters.
        """
        if self._conn is None:
            raise sqlite3.Error("Database connection is not established.")
        cursor = self._conn.cursor()
        cursor.execute(query, params)
        self._conn.commit()
        return cursor

    def select_one(
        self, model: Type[T], table: str, columns: list[str], conditions: dict[str, Any]
    ) -> tuple[Optional[T], Optional[str]]:
        """
        Fetch a single result from a SQL query.
        """
        try:
            columns_str = ", ".join(columns)
            conditions_str = " AND ".join([f"{k} = ?" for k in conditions.keys()])
            query = f"SELECT {columns_str} FROM {table} WHERE {conditions_str}"
            cursor = self.execute(query, tuple(conditions.values()))
            if not cursor:
                return None, NO_CURSOR
            row = cursor.fetchone()
            if not row:
                return None, None

            return model(**dict(row)), None
        except sqlite3.Error as e:
            logger.error("Error en la consulta: %s", e)
            return None, QUERY_ERROR

    def select(
        self,
        model: Type[T],
        table: str,
        columns: list[str],
        conditions: Optional[dict[str, Any]] = None,
    ) -> tuple[Optional[list[T]], Optional[str]]:
        """
        Fetch all results from a SQL query.
        """
        try:
            columns_str = ", ".join(columns)
            query = f"SELECT {columns_str} FROM {table}"
            params = ()
            if conditions:
                conditions_str = " AND ".join([f"{k} = ?" for k in conditions.keys()])
                query += f" WHERE {conditions_str}"
                params = tuple(conditions.values())
            cursor = self.execute(query, params)
            if not cursor:
                return None, NO_CURSOR
            rows = cursor.fetchall()
            if not rows:
                return [], None

            return [model(**dict(row)) for row in rows], None
        except sqlite3.Error as e:
            logger.error("Error en la consulta: %s", e)
            return None, QUERY_ERROR

    def insert(self, table: str, data: dict) -> tuple[Optional[int], Optional[str]]:
        """
        Insert a new record into a table.
        """
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join("?" * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            cursor = self.execute(query, tuple(data.values()))
            if not cursor:
                return None, NO_CURSOR
            return cursor.lastrowid, None
        except sqlite3.Error as e:
            logger.error("Error en insert para tabla %s: %s", table, e)
            return None, QUERY_ERROR

    def upsert(
        self, table: str, data: dict, primary_key: str
    ) -> tuple[Optional[int], Optional[str]]:
        """
        Inserta o actualiza un registro en la tabla.

        Args:
            table: Nombre de la tabla
            data: Diccionario con los datos a insertar/actualizar
            primary_key: Nombre de la columna que es clave primaria

        Returns:
            int | None: ID del registro insertado/actualizado o None si hay error
        """
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join("?" * len(data))
            # Excluimos la PK del UPDATE
            update_cols = [k for k in data.keys() if k != primary_key]
            update_stmt = ", ".join(f"{k} = ?" for k in update_cols)

            query = f"""
                INSERT INTO {table} ({columns})
                VALUES ({placeholders})
                ON CONFLICT({primary_key}) DO UPDATE SET
                {update_stmt}
            """

            # Para el UPDATE solo necesitamos los valores que no son PK
            values = tuple(data.values()) + tuple(data[k] for k in update_cols)

            cursor = self.execute(query, values)
            if not cursor:
                return None, NO_CURSOR

            return cursor.lastrowid, None

        except sqlite3.Error as e:
            logger.error("Error en upsert para tabla %s: %s", table, e)
            return None, QUERY_ERROR

    def delete(
        self, table: str, key: str, value: str
    ) -> tuple[Optional[int], Optional[str]]:
        """
        Delete a record from a table based on the key.

        Args:
            table: Nombre de la tabla
            key: Nombre de la columna que es clave primaria
            value: Valor de la clave primaria del registro a eliminar

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            query = f"DELETE FROM {table} WHERE {key} = ?"
            cursor = self.execute(query, (value,))
            return cursor.rowcount, None
        except sqlite3.Error as e:
            logger.error("Error en delete para tabla %s: %s", table, e)
            return None, QUERY_ERROR
