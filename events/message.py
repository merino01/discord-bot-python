from discord.ext import commands
from modules.triggers.utils import check_trigger
from modules.channel_formats.utils import check_channel_format
from modules.logs_config import LogHandler


class MessageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_handler = LogHandler(bot)

    # Events
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        await check_channel_format(message)
        await check_trigger(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return

        await check_channel_format(after)
        await check_trigger(message=after)
        await self.log_handler.log_message_edit(before, after)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        await self.log_handler.log_message_delete(message)


async def setup(bot):
    await bot.add_cog(MessageEvents(bot))
