"""
logger.py
Módulo para la configuración del logger.
"""

from sys import stdout
import logging
from pathlib import Path
from datetime import datetime
from typing import cast
from settings import app_name

APP_NAME = app_name.replace(" ", "-").lower()

root_dir = Path(__file__).resolve().parent.parent.parent


class CustomLogger(logging.Logger):
    """Logger personalizado con método de inicialización."""

    _file_handler = None
    _console_handler = None
    _initialized = False

    def __init__(self, name, level=logging.NOTSET):
        """
        Inicializa el logger con un nombre y nivel.
        """
        super().__init__(name, level)

    def start(self) -> None:
        """
        Inicializa el logger con los handlers y configuración.
        """
        if self._initialized:
            return

        self.setLevel(logging.INFO)

        # Crear carpeta de logs si no existe
        logs_dir = root_dir / "logs"
        logs_dir.mkdir(exist_ok=True)

        # Configurar el formato de fecha para el nombre del archivo
        date = datetime.now().strftime("%Y-%m-%d")
        filename = f"logs/{APP_NAME}__{date}.log"

        # Configurar handlers
        _file_handler = logging.FileHandler(
            filename=filename, encoding="utf-8", mode="a"
        )
        _console_handler = logging.StreamHandler(stdout)

        # Definir el formato de los logs
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<7}] {name}: {message}", dt_fmt, style="{"
        )

        # Aplicar el formato a ambos handlers
        _file_handler.setFormatter(formatter)
        _console_handler.setFormatter(formatter)

        # Añadir los handlers al logger
        self.addHandler(_file_handler)
        self.addHandler(_console_handler)

        self._initialized = True


# Registrar la clase personalizada
logging.setLoggerClass(CustomLogger)

# Crear la instancia del logger (solo se crea una vez)
logger = cast(CustomLogger, logging.getLogger(APP_NAME))
