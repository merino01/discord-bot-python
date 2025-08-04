from typing import Optional
from discord import Embed, Color
import json
from translator import __
from ..models import AutomaticMessage
from .. import constants


def format_message_for_embed(message: AutomaticMessage, bot) -> Embed:
    """Formatea un mensaje automático para mostrarlo en un embed"""
    embed = Embed(
        title=__("automaticMessages.embed.titleMessageId", name=message.display_name),
        description=__("automaticMessages.embed.description"),
        color=Color.blue(),
    )

    # Canal o categoría
    if message.channel_id:
        channel = bot.get_channel(message.channel_id)
        channel_name = channel.name if channel else __("automaticMessages.embed.valueInvalid")
        embed.add_field(
            name=__("automaticMessages.embed.fieldChannel"),
            value=f"<#{message.channel_id}> ({channel_name})",
            inline=True,
        )
    elif message.category_id:
        category = bot.get_channel(message.category_id)
        category_name = category.name if category else __("automaticMessages.embed.valueInvalid")
        embed.add_field(
            name=__("automaticMessages.embed.fieldCategory"),
            value=f"{category_name} (ID: {message.category_id})",
            inline=True,
        )

    # Tipo de programación
    schedule_type_display = (
        __("automaticMessages.scheduleTypes." + message.schedule_type)
        if message.schedule_type
        else __("automaticMessages.embed.valueNone")
    )
    embed.add_field(
        name=__("automaticMessages.embed.fieldScheduleType"),
        value=schedule_type_display,
        inline=True,
    )

    # Detalles específicos según el tipo de programación
    if message.schedule_type == "interval":
        if message.interval and message.interval_unit:
            unit_display = __("intervalUnits." + message.interval_unit)
            interval_value = __(
                "automaticMessages.embed.valueEveryX", interval=message.interval, unit=unit_display
            )
            embed.add_field(
                name=__("automaticMessages.embed.fieldInterval"), value=interval_value, inline=True
            )

    elif message.schedule_type == "daily":
        if message.hour is not None and message.minute is not None:
            time_value = __(
                "automaticMessages.embed.valueDailyAt", hour=message.hour, minute=message.minute
            )
            embed.add_field(
                name=__("automaticMessages.embed.fieldTime"), value=time_value, inline=True
            )

    elif message.schedule_type == "weekly":
        if message.hour is not None and message.minute is not None:
            weekdays_str = format_weekdays(message.weekdays)
            time_value = __(
                "automaticMessages.embed.valueWeeklyAt",
                days=weekdays_str,
                hour=message.hour,
                minute=message.minute,
            )
            embed.add_field(
                name=__("automaticMessages.embed.fieldTime"), value=time_value, inline=True
            )

    elif message.schedule_type == "custom" and message.cron_expression:
        embed.add_field(
            name=__("automaticMessages.embed.fieldCron"),
            value=f"`{message.cron_expression}`",
            inline=True,
        )

    # Texto del mensaje (limitado para el embed)
    text_preview = message.text[:100] + "..." if len(message.text) > 100 else message.text
    embed.add_field(
        name=__("automaticMessages.embed.fieldText"), value=f"```{text_preview}```", inline=False
    )

    return embed


def format_weekdays(weekdays_json: Optional[str]) -> str:
    """Formatea los días de la semana desde JSON a texto legible"""
    if not weekdays_json:
        return __("automaticMessages.embed.valueNone")

    try:
        weekdays = json.loads(weekdays_json)
        if not isinstance(weekdays, list):
            return __("automaticMessages.embed.valueInvalid")

        day_names = []
        for day in sorted(weekdays):
            if isinstance(day, int) and 0 <= day <= 6:
                day_names.append(__("weekdays." + constants.WEEKDAYS_MAP[day]))

        if not day_names:
            return __("automaticMessages.embed.valueNone")

        return ", ".join(day_names)
    except (json.JSONDecodeError, KeyError, TypeError):
        return __("automaticMessages.embed.valueInvalid")


def create_message_summary(message: AutomaticMessage, bot) -> str:
    """Crea un resumen de una línea para el mensaje automático"""
    prefix = "📨"
    name = message.display_name

    if message.channel_id:
        channel = bot.get_channel(message.channel_id)
        target = f"#{channel.name}" if channel else __("automaticMessages.summary.unknownChannel")
    else:
        category = bot.get_channel(message.category_id)
        target = __("automaticMessages.summary.categoryPrefix") + (
            category.name if category else __("automaticMessages.summary.unknownCategory")
        )

    schedule_info = ""
    if message.schedule_type == "interval" and message.interval and message.interval_unit:
        unit = __("intervalUnits." + message.interval_unit)
        schedule_info = __(
            "automaticMessages.summary.everyXUnit", interval=message.interval, unit=unit
        )
    elif (
        message.schedule_type == "daily" and message.hour is not None and message.minute is not None
    ):
        schedule_info = __(
            "automaticMessages.summary.dailyAt", hour=message.hour, minute=message.minute
        )
    elif message.schedule_type == "weekly":
        schedule_info = __("automaticMessages.summary.weekly")
    elif message.schedule_type == "on_channel_create":
        schedule_info = __("automaticMessages.summary.onChannelCreate")

    return f"{prefix} **{name}** → {target} ({schedule_info})"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Trunca un texto a la longitud máxima especificada"""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
