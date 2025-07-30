"""
Script para aplicar migraciones pendientes de la base de datos
"""

import sqlite3
import os
from pathlib import Path


def apply_migration_if_needed():
    """Aplica las migraciones necesarias si no han sido aplicadas"""
    
    # Ruta a la base de datos
    db_path = Path(__file__).parent.parent / "database" / "database.db"
    
    if not db_path.exists():
        print("La base de datos no existe. Ejecuta el bot primero para crearla.")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Verificar si las columnas nuevas ya existen
        cursor.execute("PRAGMA table_info(automatic_messages)")
        columns = [row[1] for row in cursor.fetchall()]
        
        needs_migration = False
        missing_columns = []
        
        required_columns = ['schedule_type', 'weekdays', 'cron_expression']
        for col in required_columns:
            if col not in columns:
                needs_migration = True
                missing_columns.append(col)
        
        if needs_migration:
            print(f"Aplicando migración para columnas: {', '.join(missing_columns)}")
            
            # Aplicar las migraciones
            if 'schedule_type' not in columns:
                cursor.execute("ALTER TABLE automatic_messages ADD COLUMN schedule_type TEXT DEFAULT 'interval'")
                print("✅ Columna schedule_type añadida")
            
            if 'weekdays' not in columns:
                cursor.execute("ALTER TABLE automatic_messages ADD COLUMN weekdays TEXT")
                print("✅ Columna weekdays añadida")
            
            if 'cron_expression' not in columns:
                cursor.execute("ALTER TABLE automatic_messages ADD COLUMN cron_expression TEXT")
                print("✅ Columna cron_expression añadida")
            
            conn.commit()
            print("🎉 Migración completada exitosamente")
        else:
            print("✅ La base de datos ya está actualizada")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error aplicando migración: {e}")
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    apply_migration_if_needed()
