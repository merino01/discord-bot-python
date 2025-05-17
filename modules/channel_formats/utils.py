"""util functions for channel formats"""

from re import compile as regex_compile, error as re_error
from discord import Message, TextChannel
from modules.core import logger
from .service import ChannelFormatsService


async def check_channel_format(message: Message):
    """
    Check if the message format is valid for the channel.
    If the format is invalid, delete the message.
    """
    channel_format, error = ChannelFormatsService.get_one_by_channel_id(
        message.channel.id
    )
    if error:
        logger.error(f"Error al obtener el formato de canal: {error}")
        return
    if channel_format is None:
        return

    try:
        regex = regex_compile(channel_format.regex)
        is_valid_format = regex.search(message.content)
        if is_valid_format:
            return
    except re_error as e:
        logger.error("Error en la expresión regular: %s", e)
        return

    if not isinstance(message.channel, TextChannel):
        logger.error("El canal no es de texto")
        return

    log_info = {
        "channel_id": message.channel.id,
        "channel_name": message.channel.name,
        "author_id": message.author.id,
        "author_name": message.author.name,
        "message_content": message.content,
    }
    logger.info("Formato de mensaje incorrecto")
    logger.info(log_info)
    await message.delete()
