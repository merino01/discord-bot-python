"""Automatic message model for the database."""

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class AutomaticMessage:
    """Dataclass representing an automatic message."""

    id: str
    text: str
    name: Optional[str] = None
    channel_id: Optional[int] = None
    category_id: Optional[int] = None
    interval: Optional[int] = None
    interval_unit: Optional[Literal["seconds", "minutes", "hours"]] = None
    hour: Optional[int] = None
    minute: Optional[int] = None

    def __post_init__(self):
        """Post-initialization to validate the automatic message."""
        self._validate_channel_and_category()
        
        # Si es un mensaje por categoría, no necesita configuración de tiempo
        if self.category_id:
            self._clear_time_settings()
            return
        
        # Para mensajes de canal, aplicar las validaciones de tiempo
        self._setup_time_settings()
        self._validate_time_ranges()

    def _validate_channel_and_category(self):
        """Validar que se especifique canal o categoría, pero no ambos."""
        if not self.channel_id and not self.category_id:
            raise ValueError("Debe especificar un canal o una categoría")
        if self.channel_id and self.category_id:
            raise ValueError("No se puede especificar tanto canal como categoría")

    def _clear_time_settings(self):
        """Limpiar configuraciones de tiempo para mensajes basados en categoría."""
        self.interval = None
        self.interval_unit = None
        self.hour = None
        self.minute = None

    def _setup_time_settings(self):
        """Configurar valores por defecto para mensajes de canal."""
        if not self.hour and not self.minute and not self.interval:
            self.interval = 10
        if self.interval and not self.interval_unit:
            self.interval_unit = "seconds"
        if self.hour and self.minute:
            self.interval = None

    def _validate_time_ranges(self):
        """Validar que los rangos de tiempo estén dentro de los límites."""
        if self.hour and self.hour < 0:
            self.hour = 0
        if self.hour and self.hour > 23:
            self.hour = 23
        if self.minute and self.minute < 0:
            self.minute = 0
        if self.minute and self.minute > 59:
            self.minute = 59
        if self.interval and self.interval < 1:
            self.interval = 1

    @property
    def is_category_based(self) -> bool:
        """Verifica si este mensaje automático está basado en categoría."""
        return self.category_id is not None
