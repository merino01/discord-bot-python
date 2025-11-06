# Importaciones de servicios
from .message_service import MessageService
from .query_service import QueryService
from .schedule_service import ScheduleService


# Clase principal que mantiene compatibilidad con el código existente
class AutomaticMessagesService(QueryService, ScheduleService):
    """
    Servicio principal que combina todas las funcionalidades.
    Mantiene compatibilidad con el código existente.
    """

    pass


# Lista de todas las clases exportadas
__all__ = ['MessageService', 'QueryService', 'ScheduleService', 'AutomaticMessagesService']
