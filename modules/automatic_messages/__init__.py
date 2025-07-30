"""
Módulo de mensajes automáticos para el bot de Discord

Este módulo permite configurar mensajes que se envían automáticamente
en canales específicos o cuando se crean canales en categorías.

Tipos de programación soportados:
- Por intervalo: cada X segundos/minutos/horas
- Diario: todos los días a una hora específica  
- Semanal: ciertos días de la semana a una hora específica
- Personalizado: usando expresiones cron
- Al crear canal: cuando se crea un canal en una categoría
"""

from .service import AutomaticMessagesService
from .models import AutomaticMessage, ScheduleTypeEnum, IntervalUnitEnum
from .slash_commands import AutomaticMessagesCommands

__all__ = [
    'AutomaticMessagesService',
    'AutomaticMessage', 
    'ScheduleTypeEnum',
    'IntervalUnitEnum',
    'AutomaticMessagesCommands'
]
