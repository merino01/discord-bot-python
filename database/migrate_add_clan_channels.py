"""
Script de migración para añadir columnas max_text_channels y max_voice_channels
a la tabla clans en bases de datos existentes.

Ejecutar este script si ya tienes una base de datos creada y quieres actualizar el esquema.
"""

import sqlite3
from pathlib import Path


def migrate_database():
    """Añadir columnas de límites de canales a la tabla clans"""
    db_path = Path(__file__).parent.parent / "database" / "database.db"

    if not db_path.exists():
        print(f"Base de datos no encontrada en {db_path}")
        print("No es necesaria la migración para una instalación nueva.")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(clans)")
        columns = [column[1] for column in cursor.fetchall()]

        # Añadir max_text_channels si no existe
        if 'max_text_channels' not in columns:
            print("Añadiendo columna max_text_channels...")
            cursor.execute("ALTER TABLE clans ADD COLUMN max_text_channels INTEGER DEFAULT 1")
            print("✓ Columna max_text_channels añadida")
        else:
            print("✓ Columna max_text_channels ya existe")

        # Añadir max_voice_channels si no existe
        if 'max_voice_channels' not in columns:
            print("Añadiendo columna max_voice_channels...")
            cursor.execute("ALTER TABLE clans ADD COLUMN max_voice_channels INTEGER DEFAULT 1")
            print("✓ Columna max_voice_channels añadida")
        else:
            print("✓ Columna max_voice_channels ya existe")

        conn.commit()
        print("\n✅ Migración completada exitosamente")

    except sqlite3.Error as e:
        print(f"\n❌ Error durante la migración: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("=== Migración de Base de Datos ===\n")
    migrate_database()
