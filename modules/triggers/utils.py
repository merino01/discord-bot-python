"""triggers util functions."""

import re
from asyncio import sleep
from typing import Optional
from discord import Forbidden
from modules.core import logger
from .service import TriggersService
from .models import TriggerPosition, Trigger


def _find_trigger(channel_id: int, text: str) -> Optional[Trigger]:
    """
    Searches for a trigger in the message.
    The function iterates through the triggers and checks if any of them match the message.
    If a trigger is found, it returns the trigger.
    If no trigger is found, it returns None.

    Args:
        channel_id (int): The ID of the channel where the message was sent.
        text (str): The message content to check.
    Returns:
        Optional[dict]: The trigger that was found, or None if no trigger was found.
    """

    def activates_trigger(trigger: Trigger) -> bool:
        position = trigger.position
        key = trigger.key

        if position == TriggerPosition.CONTAINS.value:
            return key in text
        if position == TriggerPosition.STARTS_WITH.value:
            return text.startswith(key)
        if position == TriggerPosition.ENDS_WITH.value:
            return text.endswith(key)
        if position == TriggerPosition.EXACT_MATCH.value:
            return text == key
        if position == TriggerPosition.TEXT_BETWEEN.value:
            words = [word for word in key.split() if word.strip()]
            pattern = ".*".join(words)
            return bool(re.search(pattern, text, re.IGNORECASE))
        if position == TriggerPosition.REGEX.value:
            return bool(re.search(key, text, re.IGNORECASE))

        return False

    service = TriggersService()
    triggers, error = service.get_all_by_channel_id(channel_id)
    if error:
        logger.error("Error al obtener los triggers: %s", error)
        return None

    if not triggers:
        return None

    for trigger in triggers:
        if activates_trigger(trigger):
            return trigger

    return None


async def check_trigger(message) -> None:
    """
    Comprueba si el mensaje es un trigger.

    Args:
        message (str): The message to check.

    Returns:
        None
    """
    matched_trigger = _find_trigger(message.channel.id, message.content)
    if not matched_trigger:
        return

    log_info = {
        "user_id": message.author.id,
        "user_name": message.author.name,
        "content": message.content,
        "channel_id": message.channel.id,
        "channel_name": message.channel.name,
    }
    logger.info("Trigger activado")
    logger.info(log_info)

    _delete_message = matched_trigger.delete_message
    _reply = matched_trigger.response
    _reply_timeout = matched_trigger.response_timeout

    async def delete_message(message):
        try:
            await message.delete()
        except Forbidden:
            logger.warning("No tengo permisos para eliminar el mensaje")

    if not _reply and _delete_message:
        if _reply_timeout:
            await sleep(_reply_timeout)
            await delete_message(message)
        return
    if not _reply:
        return

    if _reply_timeout:
        await sleep(_reply_timeout)

    await message.reply(content=_reply)
    if _delete_message:
        await delete_message(message)
