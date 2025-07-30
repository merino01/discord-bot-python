from typing import Optional, Literal
from dataclasses import dataclass
from enum import Enum

ScheduleType = Literal["interval", "daily", "weekly", "custom", "on_channel_create"]
IntervalUnit = Literal["seconds", "minutes", "hours"]


@dataclass
class AutomaticMessage:
    id: str
    channel_id: Optional[int]
    category_id: Optional[int]
    text: str
    name: Optional[str]
    interval: Optional[int]
    interval_unit: Optional[IntervalUnit]
    hour: Optional[int]
    minute: Optional[int]
    schedule_type: Optional[ScheduleType] = "interval"
    weekdays: Optional[str] = None  # JSON array de días de la semana
    cron_expression: Optional[str] = None

    def __post_init__(self):
        # Validaciones post-inicialización más permisivas para datos existentes
        if self.channel_id is None and self.category_id is None:
            raise ValueError("Se debe especificar channel_id o category_id")
        
        if self.channel_id is not None and self.category_id is not None:
            raise ValueError("No se puede especificar tanto channel_id como category_id")
        
        # Configurar valores por defecto para datos antiguos
        if self.schedule_type is None:
            self.schedule_type = "interval"
        
        # Para datos antiguos sin schedule_type específico, inferir el tipo
        if self.schedule_type == "interval":
            # Si no tiene interval/interval_unit, configurar valores por defecto
            if self.interval is None:
                self.interval = 60  # 60 minutos por defecto
            if self.interval_unit is None:
                self.interval_unit = "minutes"

    @property
    def is_category_based(self) -> bool:
        """Retorna True si el mensaje está asociado a una categoría"""
        return self.category_id is not None

    @property
    def is_channel_based(self) -> bool:
        """Retorna True si el mensaje está asociado a un canal específico"""
        return self.channel_id is not None

    @property
    def display_name(self) -> str:
        """Retorna el nombre para mostrar del mensaje automático"""
        return self.name if self.name else f"Mensaje {self.id[:8]}"


class ScheduleTypeEnum(Enum):
    INTERVAL = "interval"
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"
    ON_CHANNEL_CREATE = "on_channel_create"


class IntervalUnitEnum(Enum):
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"


class WeekDay(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
