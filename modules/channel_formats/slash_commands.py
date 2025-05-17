"""
channel formats commands
"""

from re import compile as compile_regex, error as re_error
from typing import Optional
from uuid import uuid4
from discord import app_commands, Interaction, TextChannel, Object, Embed, Color
from discord.ext import commands
from settings import guild_id
from modules.core import send_paginated_embeds
from .service import ChannelFormatsService
from .models import ChannelFormat


class ChannelFormatsCommands(commands.GroupCog, name="formato_canales"):
    """
    Commands for configuring the channel formats
    """

    def __init__(self, bot):
        self.bot = bot

    #####################################################
    ### Comando para añadir un nuevo formato de canal ###
    #####################################################
    @app_commands.command(name="crear", description="Añade un nuevo formato de canal")
    @app_commands.describe(
        canal="Canal donde se aplicará el formato",
        formato="Formato que se aplicará al canal",
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def create_channel_format(
        self, interaction: Interaction, canal: TextChannel, formato: str
    ):
        """Add channel format command"""
        try:
            compile_regex(formato)
        except re_error:
            await interaction.response.send_message(
                "Formato inválido. Asegúrate de que sea una expresión regular válida",
                ephemeral=True,
            )
            return

        new_channel_format = ChannelFormat(
            id=str(uuid4()), channel_id=canal.id, regex=formato
        )
        _, error = ChannelFormatsService.add(new_channel_format)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return

        await interaction.response.send_message(
            f"Formato de canal añadido: {canal.mention} - {formato}", ephemeral=True
        )

    #########################################################
    ### Comando para listar todos los formatos de canal #####
    #########################################################
    @app_commands.command(
        name="listar", description="Lista todos los formatos de canal"
    )
    @app_commands.describe(
        id_formato="ID del formato de canal",
        canal="Listar formatos por canal",
        persistente="Hacer persistente",
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def list_channel_formats(
        self,
        interaction: Interaction,
        id_formato: Optional[str],
        canal: Optional[TextChannel],
        persistente: Optional[bool] = False,
    ):
        """List channel formats command"""
        channel_formats = []
        if id_formato:
            channel_format, error = ChannelFormatsService.get_by_id(id_formato)
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return
            if not channel_format:
                await interaction.response.send_message(
                    f"No se ha encontrado el formato de canal con ID {id_formato}",
                    ephemeral=True,
                )
                return
            channel_formats.append(channel_format)
        elif canal:
            channel_formats, error = ChannelFormatsService.get_all_by_channel_id(
                canal.id
            )
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return
        else:
            channel_formats, error = ChannelFormatsService.get_all()
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return

        if not channel_formats or len(channel_formats) == 0:
            await interaction.response.send_message(
                "No hay formatos de canal configurados", ephemeral=True
            )
            return

        embeds = []
        for channel_format in channel_formats:
            embed = Embed(
                title=f"Formato de canal {channel_format.id}", color=Color.blue()
            )
            embed.add_field(
                name="Canal", value=f"<#{channel_format.channel_id}>", inline=True
            )
            embed.add_field(name="Formato", value=channel_format.regex, inline=True)
            embeds.append(embed)
        await send_paginated_embeds(
            interaction=interaction,
            embeds=embeds,
            ephemeral=not persistente,
            message=f"Mostrando {len(channel_formats)} formatos de canal",
        )

    ###################################################
    ### Comando para eliminar un formato de canal #####
    ###################################################
    @app_commands.command(name="eliminar", description="Elimina un formato de canal")
    @app_commands.describe(id_formato="ID del formato de canal")
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def delete_channel_format(self, interaction: Interaction, id_formato: str):
        """Delete channel format command"""
        channel_format, error = ChannelFormatsService.get_by_id(id_formato)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return

        if not channel_format:
            await interaction.response.send_message(
                f"No se ha encontrado el formato de canal con ID {id_formato}.",
                ephemeral=True,
            )
            return

        _, error = ChannelFormatsService.delete(channel_format)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return
        await interaction.response.send_message(
            f"Formato de canal eliminado: {channel_format.id}", ephemeral=True
        )

    ###############################################
    ### Comando para editar un formato de canal ###
    ###############################################
    @app_commands.command(name="editar", description="Edita un formato de canal")
    @app_commands.describe(
        id_formato="ID del formato de canal",
        canal="Canal donde se aplicará el formato",
        formato="Formato que se aplicará al canal",
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def edit_channel_format(
        self,
        interaction: Interaction,
        id_formato: str,
        canal: Optional[TextChannel],
        formato: Optional[str],
    ):
        """Edit channel format command"""
        try:
            compile_regex(formato)
        except re_error:
            await interaction.response.send_message(
                "Formato inválido. Asegúrate de que sea una expresión regular válida",
                ephemeral=True,
            )
            return

        channel_format, error = ChannelFormatsService.get_by_id(id_formato)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return
        if not channel_format:
            await interaction.response.send_message(
                f"No se ha encontrado el formato de canal con ID {id_formato}.",
                ephemeral=True,
            )
            return
        if canal:
            channel_format.channel_id = canal.id
        if formato:
            channel_format.regex = formato
        error = ChannelFormatsService.update(channel_format)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return
        await interaction.response.send_message(
            "Formato de canal editado", ephemeral=True
        )


async def setup(bot):
    """setup"""
    await bot.add_cog(ChannelFormatsCommands(bot), guild=Object(id=guild_id))
