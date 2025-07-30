from discord.ext import commands
from modules.logs_config import LogHandler
from modules.automatic_messages.tasks import get_scheduler
from modules.core import logger


class GuildEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_handler = LogHandler(bot)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.log_handler.log_member_join(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.log_handler.log_member_remove(member)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Maneja la creación de canales para mensajes automáticos"""
        if not hasattr(channel, 'category') or not channel.category:
            return
            
        try:
            scheduler = get_scheduler()
            if scheduler:
                await scheduler.send_category_message(channel.category.id, channel)
        except Exception as e:
            logger.error(f"Error enviando mensajes automáticos de categoría en {channel.name}: {e}")


async def setup(bot):
    await bot.add_cog(GuildEvents(bot))
