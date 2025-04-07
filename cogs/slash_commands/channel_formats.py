"""
channel formats commands
"""
from re import compile as compile_regex, error as re_error
from typing import Optional
from uuid import uuid4
from discord import app_commands, Interaction, TextChannel, Object, Embed, Color
from discord.ext import commands
from settings import guild_id
from services import ChannelFormatsService
from database.models import ChannelFormat

class ChannelFormatsCommands(commands.GroupCog, name="formato_canales"):
    """
    Commands for configuring the channel formats
    """
    def __init__(self, bot):
        self.bot = bot

    #####################################################
    ### Comando para añadir un nuevo formato de canal ###
    #####################################################
    @app_commands.command(
        name="crear",
        description="Añade un nuevo formato de canal"
    )
    @app_commands.describe(
        canal="Canal donde se aplicará el formato",
        formato="Formato que se aplicará al canal"
    )
    @app_commands.checks.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    async def add_channel_format(
        self,
        interaction: Interaction,
        canal: TextChannel,
        formato: str
    ):
        """Add channel format command"""
        try:
            compile_regex(formato)
        except re_error:
            await interaction.response.send_message(
                "Formato inválido. Asegúrate de que sea una expresión regular válida.",
                ephemeral=True
            )
            return

        new_channel_format = ChannelFormat(
            id=uuid4(),
            channel_id=canal.id,
            regex=formato
        )
        ChannelFormatsService.add(new_channel_format)
        await interaction.response.send_message(
            f"Formato de canal añadido: {canal.mention} - {formato}",
            ephemeral=True
        )

    #########################################################
    ### Comando para listar todos los formatos de canal #####
    #########################################################
    @app_commands.command(
        name="listar",
        description="Lista todos los formatos de canal"
    )
    @app_commands.describe(
        id_formato="ID del formato de canal",
        canal="Listar formatos por canal",
        persistente="Hacer persistente"
    )
    @app_commands.checks.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    async def list_channel_formats(
        self,
        interaction: Interaction,
        id_formato: Optional[str],
        canal: Optional[TextChannel],
        persistente: Optional[bool] = False
    ):
        """List channel formats command"""
        channel_formats = []
        if id_formato:
            channel_format = ChannelFormatsService.get_by_id(id_formato)
            if not channel_format:
                await interaction.response.send_message(
                    f"No se encontró el formato de canal con ID {id_formato}.",
                    ephemeral=True
                )
                return
            channel_formats.append(channel_format)
        elif canal:
            channel_formats = ChannelFormatsService.get_all_by_channel_id(canal.id)
            if not channel_formats:
                await interaction.response.send_message(
                    f"No hay formatos de canal configurados para el canal {canal.mention}.",
                    ephemeral=True
                )
                return
        else:
            channel_formats = ChannelFormatsService.get_all()
            if not channel_formats:
                await interaction.response.send_message(
                    "No hay formatos de canal configurados.",
                    ephemeral=True
                )
                return

        # Enviamos el primer mensaje para confirmar que recibimos el comando
        await interaction.response.send_message(
            f"Mostrando {len(channel_formats)} formatos de canal:",
            ephemeral=not persistente
        )

        for channel_format in channel_formats:
            embed = Embed(
                title=f"Formato de canal {channel_format.id}",
                color=Color.blue()
            )
            embed.add_field(
                name="Canal",
                value=f"<#{channel_format.channel_id}>",
                inline=True
            )
            embed.add_field(
                name="Formato",
                value=channel_format.regex,
                inline=True
            )
            await interaction.followup.send(embed=embed, ephemeral=not persistente)


    ###################################################
    ### Comando para eliminar un formato de canal #####
    ###################################################
    @app_commands.command(
        name="eliminar",
        description="Elimina un formato de canal"
    )
    @app_commands.describe(
        id_formato="ID del formato de canal"
    )
    @app_commands.checks.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    async def delete_channel_format(
        self,
        interaction: Interaction,
        id_formato: str
    ):
        """Delete channel format command"""
        channel_format = ChannelFormatsService.get_by_id(id_formato)
        if not channel_format:
            await interaction.response.send_message(
                f"No se encontró el formato de canal con ID {id_formato}.",
                ephemeral=True
            )
            return

        is_ok = ChannelFormatsService.delete(channel_format)
        if is_ok:
            await interaction.response.send_message(
                f"Formato de canal eliminado: {channel_format.regex}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"No se pudo eliminar el formato de canal con ID {id_formato}.",
                ephemeral=True
            )


async def setup(bot):
    """setup"""
    await bot.add_cog(
        ChannelFormatsCommands(bot),
        guild=Object(id=guild_id)
    )
