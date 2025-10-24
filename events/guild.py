from discord.ext import commands
from modules.logs_config import LogHandler
from modules.automatic_messages.tasks import get_scheduler
from modules.core import logger
from modules.clans.service import ClanService


class GuildEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_handler = LogHandler(bot)
        self.clan_service = ClanService()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.log_handler.log_member_join(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.log_handler.log_member_remove(member)

        # Remover al usuario de los clanes si pertenece a alguno
        try:
            clans, error = await self.clan_service.get_member_clans(member.id)
            if error and error != self.clan_service.CLAN_NOT_FOUND_MSG:
                # Log error if it's not just "member not found in any clan"
                logger.error(f"Error al verificar clanes del usuario {member.id}: {error}")
            elif clans:
                for clan in clans:
                    removal_error = await self.clan_service.kick_member_from_clan(
                        member.id, clan.id
                    )
                    if removal_error:
                        logger.error(
                            f"Error al remover usuario {member.id} del clan {clan.id}: {removal_error}"
                        )
                    else:
                        logger.info(
                            f"Usuario {member.id} removido del clan {clan.id} al salir del servidor"
                        )
        except Exception as e:
            logger.error(f"Error al procesar remoción de clanes para usuario {member.id}: {str(e)}")

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
