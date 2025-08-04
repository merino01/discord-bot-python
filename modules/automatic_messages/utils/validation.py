import json
import re
from translator import __


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
        r'^(\*|[0-6](,[0-6])*|\*/[0-6]|[0-6]-[0-6])$',  # día de la semana
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
        isinstance(hour, int) and 0 <= hour <= 23 and isinstance(minute, int) and 0 <= minute <= 59
    )


def validate_message_content(message_data: dict):
    """
    Valida que el mensaje tenga contenido útil (texto, embed o imagen)

    Args:
        message_data: Diccionario con los datos del mensaje

    Returns:
        Tupla (es_valido, mensaje_error)
    """
    text = message_data.get('text', '').strip()
    has_embed = bool(message_data.get('embed_config'))
    has_attachment_image = bool(message_data.get('attachment_image_url'))

    # Si no hay texto, debe haber al menos embed o imagen
    if not text and not has_embed and not has_attachment_image:
        return False, __("automaticMessages.errorMessages.messageNoContent")

    # Si solo hay embed, debe tener título o descripción
    if not text and has_embed and not has_attachment_image:
        embed_config = message_data['embed_config']
        if not embed_config.get('title') and not embed_config.get('description'):
            return False, __("automaticMessages.errorMessages.embedNoContent")

    return True, ""
