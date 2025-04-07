"""db"""

from typing import TypeVar, Type, Optional
from pathlib import Path
import sqlite3
from utils.logger import logger

T = TypeVar("T")

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
        if not hasattr(self, '_initialized'):
            db_path = Path(__file__).parent / "database.db"
            self._conn = sqlite3.connect(str(db_path))
            logger.info("Conectado a la base de datos")
            self._conn.row_factory = sqlite3.Row
            self._create_tables()
            self._initialized = True

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

                logger.info("Verificando base de datos")
                self._conn.executescript(sql_script)
                self._conn.commit()
                logger.info("Tablas creadas correctamente")

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

    def query(
        self,
        model: Type[T],
        query: str,
        params: tuple = ()
    ) -> list:
        """
        Fetch all results from a SQL query.
        """
        try:
            cursor = self.execute(query, params)
            if not cursor:
                return []
            return [model(**dict(row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("Error en la consulta: %s", e)
            return []

    def fetch_one(
        self,
        model: Type[T],
        query: str,
        params: tuple = (),
    ) -> T | None:
        """
        Fetch a single result from a SQL query.
        """
        cursor = self.execute(query, params)
        if not cursor:
            return None
        row = cursor.fetchone()
        if not row:
            return None

        return model(**dict(row))

    def insert(self, table: str, data: dict) -> int | None:
        """
        Insert a new record into a table.
        """
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join('?' * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            logger.info(
                "Ejecutando consulta en base de datos: %s con los valores %s",
                query,
                ', '.join([str(v) for v in tuple(data.values())])
            )
            cursor = self.execute(query, tuple(data.values()))
            if not cursor:
                return None
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error("Error en insert para tabla %s: %s", table, e)
            return None
        except Exception as e:
            logger.error("Error inesperado en insert para tabla %s: %s", table, e)
            return None

    def upsert(self, table: str, data: dict, primary_key: str) -> bool:
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
            columns = ', '.join(data.keys())
            placeholders = ', '.join('?' * len(data))
            # Excluimos la PK del UPDATE
            update_cols = [k for k in data.keys() if k != primary_key]
            update_stmt = ', '.join(f"{k} = ?" for k in update_cols)

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
                return False

            return True

        except sqlite3.Error as e:
            logger.error("Error en upsert para tabla %s: %s", table, e)
            return False


    def delete(self, table: str, key: str, value: str) -> bool:
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
            self.execute(query, (value,))
            return True
        except sqlite3.Error as e:
            logger.error("Error en delete para tabla %s: %s", table, e)
            return False
