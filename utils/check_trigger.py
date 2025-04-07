"""
This module contains functions to check if a message matches a trigger and to handle the response.
"""

import re
from asyncio import sleep
from enum import Enum
from typing import Optional
from discord import Forbidden
from utils.logger import logger
from database.models import Trigger
from services import TriggersService

class TriggerPosition(Enum):
    """
    Trigger position enum.
    """
    CONTAINS = 'contains'
    STARTS_WITH = 'starts_with'
    ENDS_WITH = 'ends_with'
    EXACT_MATCH = 'equal'
    TEXT_BETWEEN = 'text_between'
    REGEX = 'regex'


def find_trigger(channel_id: int, text: str) -> Optional[Trigger]:
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

    triggers = TriggersService.get_all_by_channel_id(channel_id)
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
    matched_trigger = find_trigger(message.channel.id, message.content)
    if not matched_trigger:
        return

    log_info = {
		"user_id": message.author.id,
		"user_name": message.author.name,
		"content": message.content,
		"channel_id": message.channel.id,
		"channel_name": message.channel.name
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
            logger.warning(
                "Error al eliminar el mensaje. No tengo permisos. ID del mensaje: %s",
                message.id
            )

    if not _reply and _delete_message:
        await delete_message(message)
        return
    if not _reply:
        return

    if _reply_timeout and isinstance(_reply_timeout, int):
        _reply_timeout = max(_reply_timeout, 1)
        _reply_timeout = min(_reply_timeout, 60)
        await sleep(_reply_timeout)

    await message.reply(content=_reply)
    if _delete_message:
        await delete_message(message)
