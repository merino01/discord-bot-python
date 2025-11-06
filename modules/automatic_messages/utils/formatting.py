from typing import Optional
from discord import Embed, Color
import json
from ..models import AutomaticMessage
from i18n import __


def format_message_for_embed(message: AutomaticMessage, bot) -> Embed:
    """Formatea un mensaje automático para mostrarlo en un embed"""
    embed = Embed(
        title=constants.TITLE_MESSAGE_ID.format(name=message.display_name),
        description=__("clanSettings.embeds.description"),
        color=Color.blue()
    )
    
    # Canal o categoría
    if message.channel_id:
        channel = bot.get_channel(message.channel_id)
        channel_name = channel.name if channel else __("triggers.values.invalid")
        embed.add_field(
            name=__("triggers.fields.channel"),
            value=f"<#{message.channel_id}> ({channel_name})",
            inline=True
        )
    elif message.category_id:
        category = bot.get_channel(message.category_id)
        category_name = category.name if category else __("triggers.values.invalid")
        embed.add_field(
            name=constants.FIELD_CATEGORY,
            value=f"{category_name} (ID: {message.category_id})",
            inline=True
        )
    
    # Tipo de programación
    schedule_type_display = constants.SCHEDULE_TYPE_TRANSLATIONS.get(
        message.schedule_type, message.schedule_type or __("triggers.values.none")
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
        return __("triggers.values.none")
    
    try:
        weekdays = json.loads(weekdays_json)
        if not isinstance(weekdays, list):
            return __("triggers.values.invalid")
        
        day_names = []
        for day in sorted(weekdays):
            if isinstance(day, int) and 0 <= day <= 6:
                day_names.append(constants.WEEKDAY_TRANSLATIONS[day])
        
        if not day_names:
            return __("triggers.values.none")
        
        return ", ".join(day_names)
    except (json.JSONDecodeError, KeyError, TypeError):
        return __("triggers.values.invalid")


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
