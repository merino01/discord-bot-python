from typing import Optional
from datetime import datetime
import json
from ..models import AutomaticMessage


def get_next_execution_time(message: AutomaticMessage) -> Optional[datetime]:
    """Calcula el próximo tiempo de ejecución para un mensaje programado"""
    if message.schedule_type == "interval":
        # Para intervalos, no podemos calcular un "próximo" tiempo sin saber cuándo fue el último
        return None
    
    now = datetime.now()
    
    if message.schedule_type == "daily":
        if message.hour is not None and message.minute is not None:
            next_time = now.replace(hour=message.hour, minute=message.minute, second=0, microsecond=0)
            if next_time <= now:
                next_time = next_time.replace(day=next_time.day + 1)
            return next_time
    
    elif message.schedule_type == "weekly":
        if message.hour is not None and message.minute is not None and message.weekdays:
            try:
                weekdays = json.loads(message.weekdays)
                # Encontrar el próximo día de la semana válido
                # Implementación simplificada - retorna None por ahora
                return None
            except json.JSONDecodeError:
                return None
    
    return None
