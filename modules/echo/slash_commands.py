"""Comandos slash para el módulo Echo"""

from discord import app_commands, Interaction, TextChannel
from discord.ext import commands
from modules.core import logger
from . import constants


class EchoCommands(commands.Cog):
    """Comandos para enviar mensajes (echo) a canales específicos"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="echo", description=constants.COMMAND_ECHO_DESC)
    @app_commands.describe(
        texto=constants.PARAM_TEXT_DESC,
        canal=constants.PARAM_CHANNEL_DESC
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def echo(
        self,
        interaction: Interaction,
        texto: str,
        canal: TextChannel
    ):
        """Envía un mensaje al canal especificado"""

        # Verificar permisos del usuario en el canal de destino
        member_permissions = canal.permissions_for(interaction.user)
        if not member_permissions.send_messages:
            return await interaction.response.send_message(
                constants.ERROR_NO_PERMISSIONS,
                ephemeral=True
            )

        # Verificar permisos del bot en el canal de destino
        bot_permissions = canal.permissions_for(interaction.guild.me)
        if not bot_permissions.send_messages:
            return await interaction.response.send_message(
                constants.ERROR_NO_PERMISSIONS,
                ephemeral=True
            )

        # Verificar longitud del mensaje
        if len(texto) > 2000:
            return await interaction.response.send_message(
                constants.ERROR_MESSAGE_TOO_LONG,
                ephemeral=True
            )

        try:
            # Enviar el mensaje al canal especificado
            await canal.send(texto)

            # Confirmar al usuario que el mensaje fue enviado
            await interaction.response.send_message(
                constants.SUCCESS_MESSAGE_SENT.format(channel=canal.mention),
                ephemeral=True
            )

            logger.info(f"Echo comando usado por {interaction.user} en #{canal.name}: {texto[:50]}...")

        except Exception as e:
            logger.error(f"Error en comando echo: {str(e)}")
            await interaction.response.send_message(
                constants.ERROR_SENDING_MESSAGE.format(error=str(e)),
                ephemeral=True
            )

    @echo.error
    async def echo_error(self, interaction: Interaction, error):
        """Maneja errores del comando echo"""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Necesitas el permiso 'Gestionar mensajes' para usar este comando.",
                ephemeral=True
            )
        else:
            logger.error(f"Error no manejado en comando echo: {str(error)}")
            await interaction.response.send_message(
                "❌ Ocurrió un error inesperado.",
                ephemeral=True
            )


async def setup(bot):
    """Función requerida para cargar el módulo"""
    await bot.add_cog(EchoCommands(bot))
    logger.info("Módulo Echo cargado correctamente")
