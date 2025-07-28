from discord.ext import commands
from modules.logs_config import LogHandler
from modules.automatic_messages import AutomaticMessagesService
from modules.automatic_messages.utils import process_message_text
from modules.core import logger


class GuildEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_handler = LogHandler(bot)
        self.automatic_messages_service = AutomaticMessagesService()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.log_handler.log_member_join(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.log_handler.log_member_remove(member)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if not hasattr(channel, 'category'): return            
        if not channel.category: return

        messages, error = self.automatic_messages_service.get_by_category_id(channel.category.id)
        if error:
            logger.error(f"Error fetching automatic messages for category {channel.category.name}: {error}")
            return
            
        if not messages: return

        for message in messages:
            try:
                # Procesar el texto para interpretar \n como saltos de línea
                processed_text = process_message_text(message.text)
                await channel.send(processed_text)
            except Exception as e:
                logger.error(f"Error sending automatic message in channel {channel.name}: {e}")


async def setup(bot):
    await bot.add_cog(GuildEvents(bot))
