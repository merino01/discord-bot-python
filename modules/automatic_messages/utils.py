from typing import List, Optional, Dict, Any
from discord import Embed, Color, TextChannel, CategoryChannel, Interaction
from datetime import datetime, time as dt_time
import json
import re
from .models import AutomaticMessage, WeekDay
from . import constants


def format_message_for_embed(message: AutomaticMessage, bot) -> Embed:
    """Formatea un mensaje automático para mostrarlo en un embed"""
    embed = Embed(
        title=constants.TITLE_MESSAGE_ID.format(name=message.display_name),
        description=constants.EMBED_DESCRIPTION,
        color=Color.blue()
    )
    
    # Canal o categoría
    if message.channel_id:
        channel = bot.get_channel(message.channel_id)
        channel_name = channel.name if channel else constants.VALUE_INVALID
        embed.add_field(
            name=constants.FIELD_CHANNEL,
            value=f"<#{message.channel_id}> ({channel_name})",
            inline=True
        )
    elif message.category_id:
        category = bot.get_channel(message.category_id)
        category_name = category.name if category else constants.VALUE_INVALID
        embed.add_field(
            name=constants.FIELD_CATEGORY,
            value=f"{category_name} (ID: {message.category_id})",
            inline=True
        )
    
    # Tipo de programación
    schedule_type_display = constants.SCHEDULE_TYPE_TRANSLATIONS.get(
        message.schedule_type, message.schedule_type or constants.VALUE_NONE
    )
    embed.add_field(
        name=constants.FIELD_SCHEDULE_TYPE,
        value=schedule_type_display,
        inline=True
    )
    
    # Detalles específicos según el tipo de programación
    if message.schedule_type == "interval":
        if message.interval and message.interval_unit:
            unit_display = constants.INTERVAL_UNIT_TRANSLATIONS.get(
                message.interval_unit, message.interval_unit
            )
            interval_value = constants.VALUE_EVERY_X.format(
                interval=message.interval,
                unit=unit_display
            )
            embed.add_field(
                name=constants.FIELD_INTERVAL,
                value=interval_value,
                inline=True
            )
    
    elif message.schedule_type == "daily":
        if message.hour is not None and message.minute is not None:
            time_value = constants.VALUE_DAILY_AT.format(
                hour=message.hour,
                minute=message.minute
            )
            embed.add_field(
                name=constants.FIELD_TIME,
                value=time_value,
                inline=True
            )
    
    elif message.schedule_type == "weekly":
        if message.hour is not None and message.minute is not None:
            weekdays_str = format_weekdays(message.weekdays)
            time_value = constants.VALUE_WEEKLY_AT.format(
                days=weekdays_str,
                hour=message.hour,
                minute=message.minute
            )
            embed.add_field(
                name=constants.FIELD_TIME,
                value=time_value,
                inline=True
            )
    
    elif message.schedule_type == "custom" and message.cron_expression:
        embed.add_field(
            name=constants.FIELD_CRON,
            value=f"`{message.cron_expression}`",
            inline=True
        )
    
    # Texto del mensaje (limitado para el embed)
    text_preview = message.text[:100] + "..." if len(message.text) > 100 else message.text
    embed.add_field(
        name=constants.FIELD_TEXT,
        value=f"```{text_preview}```",
        inline=False
    )
    
    return embed


def format_weekdays(weekdays_json: Optional[str]) -> str:
    """Formatea los días de la semana desde JSON a texto legible"""
    if not weekdays_json:
        return constants.VALUE_NONE
    
    try:
        weekdays = json.loads(weekdays_json)
        if not isinstance(weekdays, list):
            return constants.VALUE_INVALID
        
        day_names = []
        for day in sorted(weekdays):
            if isinstance(day, int) and 0 <= day <= 6:
                day_names.append(constants.WEEKDAY_TRANSLATIONS[day])
        
        if not day_names:
            return constants.VALUE_NONE
        
        return ", ".join(day_names)
    except (json.JSONDecodeError, KeyError, TypeError):
        return constants.VALUE_INVALID


def validate_cron_expression(cron_expr: str) -> bool:
    """Valida una expresión cron básica (formato: min hour day month weekday)"""
    if not cron_expr or not isinstance(cron_expr, str):
        return False
    
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        return False
    
    # Patrones básicos para validación
    patterns = [
        r'^(\*|([0-5]?[0-9])(,([0-5]?[0-9]))*|\*/([0-5]?[0-9])|([0-5]?[0-9])-([0-5]?[0-9]))$',  # minutos
        r'^(\*|([01]?[0-9]|2[0-3])(,([01]?[0-9]|2[0-3]))*|\*/([01]?[0-9]|2[0-3])|([01]?[0-9]|2[0-3])-([01]?[0-9]|2[0-3]))$',  # horas
        r'^(\*|([1-9]|[12][0-9]|3[01])(,([1-9]|[12][0-9]|3[01]))*|\*/([1-9]|[12][0-9]|3[01])|([1-9]|[12][0-9]|3[01])-([1-9]|[12][0-9]|3[01]))$',  # día del mes
        r'^(\*|([1-9]|1[0-2])(,([1-9]|1[0-2]))*|\*/([1-9]|1[0-2])|([1-9]|1[0-2])-([1-9]|1[0-2]))$',  # mes
        r'^(\*|[0-6](,[0-6])*|\*/[0-6]|[0-6]-[0-6])$'  # día de la semana
    ]
    
    for i, part in enumerate(parts):
        if not re.match(patterns[i], part):
            return False
    
    return True


def validate_weekdays_json(weekdays_str: str) -> bool:
    """Valida que el JSON de días de la semana sea correcto"""
    if not weekdays_str:
        return True  # Opcional
    
    try:
        weekdays = json.loads(weekdays_str)
        if not isinstance(weekdays, list):
            return False
        
        for day in weekdays:
            if not isinstance(day, int) or day < 0 or day > 6:
                return False
        
        return True
    except json.JSONDecodeError:
        return False


def validate_time(hour: int, minute: int) -> bool:
    """Valida que la hora y minuto sean válidos"""
    return (
        isinstance(hour, int) and 0 <= hour <= 23 and
        isinstance(minute, int) and 0 <= minute <= 59
    )


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


def create_message_summary(message: AutomaticMessage, bot) -> str:
    """Crea un resumen de una línea para el mensaje automático"""
    prefix = "📨"
    name = message.display_name
    
    if message.channel_id:
        channel = bot.get_channel(message.channel_id)
        target = f"#{channel.name}" if channel else f"Canal desconocido"
    else:
        category = bot.get_channel(message.category_id)
        target = f"Categoría: {category.name}" if category else "Categoría desconocida"
    
    schedule_info = ""
    if message.schedule_type == "interval" and message.interval and message.interval_unit:
        unit = constants.INTERVAL_UNIT_TRANSLATIONS.get(message.interval_unit, message.interval_unit)
        schedule_info = f"cada {message.interval} {unit}"
    elif message.schedule_type == "daily" and message.hour is not None and message.minute is not None:
        schedule_info = f"diario a las {message.hour:02d}:{message.minute:02d}"
    elif message.schedule_type == "weekly":
        schedule_info = "semanal"
    elif message.schedule_type == "on_channel_create":
        schedule_info = "al crear canal"
    
    return f"{prefix} **{name}** → {target} ({schedule_info})"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Trunca un texto a la longitud máxima especificada"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


async def send_error_message(interaction: Interaction, error_message: str):
    """Envía un mensaje de error de forma consistente"""
    if interaction.response.is_done():
        await interaction.followup.send(error_message, ephemeral=True)
    else:
        await interaction.response.send_message(error_message, ephemeral=True)


async def send_success_message(interaction: Interaction, success_message: str):
    """Envía un mensaje de éxito de forma consistente"""
    if interaction.response.is_done():
        await interaction.followup.send(success_message, ephemeral=True)
    else:
        await interaction.response.send_message(success_message, ephemeral=True)
