"""
Programador adicional para funcionalidades específicas de mensajes automáticos
"""

from typing import Optional, List
from datetime import datetime, timedelta
import asyncio
from .models import AutomaticMessage
from .services import AutomaticMessagesService
from modules.core import logger
import json


class AdvancedScheduler:
    """Programador avanzado para casos especiales"""

    def __init__(self, bot):
        self.bot = bot
        self.service = AutomaticMessagesService()

    async def calculate_next_runs(self, message_id: str) -> Optional[datetime]:
        """Calcula la próxima ejecución de un mensaje automático"""
        message, error = self.service.get_by_id(message_id)

        if error or not message:
            return None

        now = datetime.now()

        if message.schedule_type == "interval":
            # Para intervalos no podemos calcular sin saber la última ejecución
            return None

        elif message.schedule_type == "daily":
            if message.hour is not None and message.minute is not None:
                next_run = now.replace(
                    hour=message.hour, minute=message.minute, second=0, microsecond=0
                )

                if next_run <= now:
                    next_run += timedelta(days=1)

                return next_run

        elif message.schedule_type == "weekly":
            # Implementación simplificada para programación semanal
            if message.hour is not None and message.minute is not None and message.weekdays:

                try:
                    weekdays = json.loads(message.weekdays)

                    # Encontrar el próximo día válido
                    current_weekday = now.weekday()
                    target_time = now.replace(
                        hour=message.hour, minute=message.minute, second=0, microsecond=0
                    )

                    for days_ahead in range(7):
                        check_date = now + timedelta(days=days_ahead)
                        check_weekday = check_date.weekday()

                        if check_weekday in weekdays:
                            next_run = check_date.replace(
                                hour=message.hour, minute=message.minute, second=0, microsecond=0
                            )

                            if next_run > now:
                                return next_run

                except (json.JSONDecodeError, ValueError):
                    logger.error("Error procesando días de la semana para mensaje %s", message_id)
                    return None

        return None

    async def get_upcoming_messages(self, hours_ahead: int = 24) -> List[tuple]:
        """
        Obtiene una lista de mensajes que se ejecutarán en las próximas X horas
        Retorna lista de tuplas (AutomaticMessage, datetime_next_run)
        """
        messages, error = self.service.get_all()

        if error or not messages:
            return []

        upcoming = []
        cutoff_time = datetime.now() + timedelta(hours=hours_ahead)

        for message in messages:
            if message.schedule_type == "interval":
                continue  # No podemos predecir intervalos

            next_run = await self.calculate_next_runs(message.id)
            if next_run and next_run <= cutoff_time:
                upcoming.append((message, next_run))

        # Ordenar por tiempo de ejecución
        upcoming.sort(key=lambda x: x[1])
        return upcoming

    async def validate_message_config(self, message: AutomaticMessage) -> List[str]:
        """
        Valida la configuración de un mensaje automático
        Retorna lista de errores encontrados
        """
        errors = []

        # Validar que existe el canal o categoría
        if message.channel_id:
            channel = self.bot.get_channel(message.channel_id)
            if not channel:
                errors.append(f"El canal con ID {message.channel_id} no existe")

        elif message.category_id:
            category = self.bot.get_channel(message.category_id)
            if not category:
                errors.append(f"La categoría con ID {message.category_id} no existe")

        # Validar configuración según el tipo
        if message.schedule_type == "interval":
            if not message.interval or message.interval <= 0:
                errors.append("El intervalo debe ser un número positivo")

            if message.interval_unit not in ["seconds", "minutes", "hours"]:
                errors.append("La unidad de intervalo debe ser seconds, minutes o hours")

        elif message.schedule_type in ["daily", "weekly"]:
            if message.hour is None or not (0 <= message.hour <= 23):
                errors.append("La hora debe estar entre 0 y 23")

            if message.minute is None or not (0 <= message.minute <= 59):
                errors.append("Los minutos deben estar entre 0 y 59")

            if message.schedule_type == "weekly":
                if not message.weekdays:
                    errors.append(
                        "Los días de la semana son obligatorios para programación semanal"
                    )
                else:
                    try:
                        import json

                        weekdays = json.loads(message.weekdays)
                        if not isinstance(weekdays, list):
                            errors.append("Los días de la semana deben ser una lista")
                        elif not all(isinstance(d, int) and 0 <= d <= 6 for d in weekdays):
                            errors.append("Los días de la semana deben ser números entre 0 y 6")
                    except json.JSONDecodeError:
                        errors.append("Formato inválido de días de la semana")

        elif message.schedule_type == "custom":
            if not message.cron_expression:
                errors.append("La expresión cron es obligatoria para programación personalizada")
            # TODO: Validar expresión cron

        return errors

    async def get_message_statistics(self) -> dict:
        """Obtiene estadísticas de los mensajes automáticos"""
        messages, error = self.service.get_all()

        if error or not messages:
            return {
                "total": 0,
                "by_type": {},
                "by_channel": 0,
                "by_category": 0,
                "active": 0,
                "errors": 1 if error else 0,
            }

        stats = {
            "total": len(messages),
            "by_type": {},
            "by_channel": 0,
            "by_category": 0,
            "active": 0,
            "errors": 0,
        }

        for message in messages:
            # Contar por tipo
            schedule_type = message.schedule_type or "unknown"
            stats["by_type"][schedule_type] = stats["by_type"].get(schedule_type, 0) + 1

            # Contar por destino
            if message.channel_id:
                stats["by_channel"] += 1
            elif message.category_id:
                stats["by_category"] += 1

            # Verificar si está activo (canal/categoría existe)
            if message.channel_id:
                if self.bot.get_channel(message.channel_id):
                    stats["active"] += 1
            elif message.category_id:
                if self.bot.get_channel(message.category_id):
                    stats["active"] += 1

        return stats

    async def cleanup_invalid_messages(self) -> int:
        """
        Elimina mensajes automáticos que apuntan a canales/categorías inexistentes
        Retorna el número de mensajes eliminados
        """
        messages, error = self.service.get_all()

        if error or not messages:
            return 0

        deleted_count = 0

        for message in messages:
            should_delete = False

            if message.channel_id:
                channel = self.bot.get_channel(message.channel_id)
                if not channel:
                    should_delete = True
                    logger.info(
                        "Eliminando mensaje automático %s - canal %s no existe",
                        message.display_name,
                        message.channel_id,
                    )

            elif message.category_id:
                category = self.bot.get_channel(message.category_id)
                if not category:
                    should_delete = True
                    logger.info(
                        "Eliminando mensaje automático %s - categoría %s no existe",
                        message.display_name,
                        message.category_id,
                    )

            if should_delete:
                success, error = self.service.delete(message.id)
                if success:
                    deleted_count += 1
                else:
                    logger.error("Error eliminando mensaje automático %s: %s", message.id, error)

        if deleted_count > 0:
            logger.info("Limpieza completada: %d mensajes automáticos eliminados", deleted_count)

        return deleted_count
