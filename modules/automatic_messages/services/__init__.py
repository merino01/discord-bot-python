from .message_service import MessageService
from .query_service import QueryService
from .schedule_service import ScheduleService


class AutomaticMessagesService(QueryService, ScheduleService):
    pass


__all__ = ['MessageService', 'QueryService', 'ScheduleService', 'AutomaticMessagesService']
