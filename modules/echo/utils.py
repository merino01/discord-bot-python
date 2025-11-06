"""Utilidades para el módulo Echo"""

import re
from typing import Optional, Tuple


def parse_message_link(message_link: str) -> Optional[Tuple[int, int]]:
    """
    Parsea un enlace de mensaje de Discord y extrae el ID del canal y del mensaje

    Formatos soportados:
    - https://discord.com/channels/guild_id/channel_id/message_id
    - https://discordapp.com/channels/guild_id/channel_id/message_id

    Returns: (channel_id, message_id) o None si el enlace no es válido
    """
    # Patrón para enlaces de mensajes de Discord
    pattern = r'https://(?:discord|discordapp)\.com/channels/\d+/(\d+)/(\d+)'

    match = re.match(pattern, message_link.strip())
    if match:
        channel_id = int(match.group(1))
        message_id = int(match.group(2))
        return channel_id, message_id

    return None


def is_message_id(text: str) -> bool:
    """
    Verifica si el texto es un ID de mensaje (solo dígitos)
    """
    return (
        text.strip().isdigit() and len(text.strip()) >= 17
    )  # Los IDs de Discord tienen al menos 17 dígitos


def extract_message_info(text: str) -> Optional[Tuple[int, int]]:
    """
    Extrae información del mensaje desde un enlace o ID

    Returns: (channel_id, message_id) o None si no es válido
    """
    text = text.strip()

    # Primero intentar como enlace
    link_result = parse_message_link(text)
    if link_result:
        return link_result

    # Si no es enlace, verificar si es solo un ID de mensaje
    # En este caso, necesitaríamos el canal actual
    if is_message_id(text):
        # Retornamos None para channel_id para indicar que se debe usar el canal actual
        return None, int(text)

    return None
