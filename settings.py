"""
settings.py
Configuración del bot.
"""

from typing import Dict, Any
import json

CONFIG_FILE_PATH = "config.json"


def load_config(file_path: str = CONFIG_FILE_PATH) -> Dict[str, Any]:
    """
    Lee un archivo JSON y convierte sus valores a tipos de datos apropiados.
    Args:
        file_path (str): Ruta del archivo JSON a leer.
    Returns:
        dict: Un diccionario con los valores convertidos.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            config = json.load(file)
            print(f"Configuración cargada desde {file_path}")
            return config
    except FileNotFoundError:
        print(f"El archivo de configuración no se ha encontrado: {file_path}")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error al procesar el archivo JSON: {file_path}")
        exit(1)


_config = load_config(CONFIG_FILE_PATH)

app_name: str = _config.get("app_name", "")
bot_token: str = _config.get("bot_token", "")
prefix: str = _config.get("prefix", "!")
guild_id: int = _config.get("guild_id", 0)
admin_id: int = _config.get("admin_id", 0)
send_to_admin: bool = _config.get("send_to_admin", False)
language: str = _config.get("language", "es")
