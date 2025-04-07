"""
Message events for the bot.
"""

from re import compile as regex_compile, error as re_error
from discord.ext import commands
from utils.logger import logger
from utils.channels import get_chatlog_channel, send_message_to_channel
from utils.embeds import get_message_edit_embed, get_message_delete_embed
from utils.check_trigger import check_trigger
from services import ChannelFormatsService

class MessageEvents(commands.Cog):
    """
    Base events for the bot.
    """
    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Called when a message is sent.
        """
        if message.author.bot:
            return

        await self.check_channel_format(message)
        await check_trigger(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """
        Called when a message is edited.
        """
        if before.author.bot:
            return

        await self.check_channel_format(after)
        await check_trigger(message=after)

        channel_to_send = await get_chatlog_channel(self.bot)
        if channel_to_send is None:
            return
        if before.content == after.content:
            return
        if before.author.bot:
            return
        embed = get_message_edit_embed(before, after)
        if embed is None:
            return
        await send_message_to_channel(
            channel=channel_to_send,
            embed=embed
        )


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """
        Called when a message is deleted.
        """
        if message.author.bot:
            return

        channel_to_send = await get_chatlog_channel(self.bot)
        if channel_to_send is None:
            return
        if message.author.bot:
            return
        embed = get_message_delete_embed(message)
        if embed is None:
            return

        await send_message_to_channel(channel=channel_to_send, embed=embed)

    # Custom functions
    async def check_channel_format(self, message):
        """
        Check if the message format is valid for the channel.
        If the format is invalid, delete the message.
        """
        channel_format = ChannelFormatsService.get_one_by_channel_id(message.channel.id)
        if channel_format is None:
            return

        try:
            regex = regex_compile(channel_format.regex)
            is_valid_format = regex.search(message.content)
            if is_valid_format:
                return
        except re_error as e:
            logger.error(f"Error en la expresión regular: {e}")

        log_info = {
            "channel_id": message.channel.id,
            "channel_name": message.channel.name,
            "author_id": message.author.id,
            "author_name": message.author.name,
            "message_content": message.content
        }
        logger.info("Formato de mensaje incorrecto")
        logger.info(log_info)
        await message.delete()


async def setup(bot):
    """setup"""
    await bot.add_cog(MessageEvents(bot))
