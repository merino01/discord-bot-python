from re import compile as compile_regex, error as re_error
from typing import Optional
from uuid import uuid4
from discord import app_commands, Interaction, TextChannel, Object, Embed, Color
from discord.ext import commands
from settings import guild_id
from modules.core import send_paginated_embeds
from .service import ChannelFormatsService
from .models import ChannelFormat
from .utils import (
    show_channel_format_selection_for_delete,
    show_channel_format_selection_for_edit,
    edit_channel_format_by_id,
)
from . import constants


class ChannelFormatsCommands(commands.GroupCog, name="formato_canales"):
    def __init__(self, bot):
        self.bot = bot
        self.service = ChannelFormatsService()

    #####################################################
    ### Comando para añadir un nuevo formato de canal ###
    #####################################################
    @app_commands.command(name="crear", description=constants.COMMAND_CREATE_DESC)
    @app_commands.describe(
        canal=constants.PARAM_CHANNEL_DESC,
        formato=constants.PARAM_FORMAT_DESC,
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def create_channel_format(
        self, interaction: Interaction, canal: TextChannel, formato: str
    ):
        try:
            compile_regex(formato)
        except re_error:
            await interaction.response.send_message(
                constants.ERROR_INVALID_REGEX,
                ephemeral=True,
            )
            return

        new_channel_format = ChannelFormat(id=str(uuid4()), channel_id=canal.id, regex=formato)
        _, error = self.service.add(new_channel_format)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return

        await interaction.response.send_message(
            constants.SUCCESS_FORMAT_ADDED.format(channel=canal.mention, format=formato),
            ephemeral=True,
        )

    #########################################################
    ### Comando para listar todos los formatos de canal #####
    #########################################################
    @app_commands.command(name="listar", description=constants.COMMAND_LIST_DESC)
    @app_commands.describe(
        id_formato=constants.PARAM_FORMAT_ID_DESC,
        canal=constants.PARAM_LIST_CHANNEL_DESC,
        persistente=constants.PARAM_PERSISTENT_DESC,
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def list_channel_formats(
        self,
        interaction: Interaction,
        id_formato: Optional[str],
        canal: Optional[TextChannel],
        persistente: Optional[bool] = False,
    ):
        channel_formats = []
        if id_formato:
            channel_format, error = self.service.get_by_id(id_formato)
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return
            if not channel_format:
                await interaction.response.send_message(
                    constants.ERROR_FORMAT_NOT_FOUND.format(id=id_formato),
                    ephemeral=True,
                )
                return
            channel_formats.append(channel_format)
        elif canal:
            channel_formats, error = self.service.get_all_by_channel_id(canal.id)
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return
        else:
            channel_formats, error = self.service.get_all()
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return

        if not channel_formats or len(channel_formats) == 0:
            await interaction.response.send_message(constants.NO_FORMATS_FOUND, ephemeral=True)
            return

        embeds = []
        for channel_format in channel_formats:
            embed = Embed(
                title=constants.TITLE_FORMAT_ID.format(id=channel_format.id), color=Color.blue()
            )
            embed.add_field(
                name=constants.FIELD_CHANNEL, value=f"<#{channel_format.channel_id}>", inline=True
            )
            embed.add_field(name=constants.FIELD_FORMAT, value=channel_format.regex, inline=True)
            embeds.append(embed)
        await send_paginated_embeds(
            interaction=interaction,
            embeds=embeds,
            ephemeral=not persistente,
            message=constants.SHOWING_FORMATS.format(count=len(channel_formats)),
        )

    ###################################################
    ### Comando para eliminar un formato de canal #####
    ###################################################
    @app_commands.command(name="eliminar", description=constants.COMMAND_DELETE_DESC)
    @app_commands.describe(id_formato=constants.PARAM_FORMAT_ID_DESC)
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def delete_channel_format(
        self, interaction: Interaction, id_formato: Optional[str] = None
    ):
        # Si no se proporciona ID, mostrar vista de selección
        if id_formato is None:
            await show_channel_format_selection_for_delete(interaction)
            return

        # Lógica original para cuando se proporciona ID
        channel_format, error = self.service.get_by_id(id_formato)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return

        if not channel_format:
            await interaction.response.send_message(
                constants.ERROR_FORMAT_NOT_FOUND.format(id=id_formato),
                ephemeral=True,
            )
            return

        _, error = self.service.delete(channel_format)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return
        await interaction.response.send_message(
            constants.SUCCESS_FORMAT_DELETED.format(id=channel_format.id), ephemeral=True
        )

    ###############################################
    ### Comando para editar un formato de canal ###
    ###############################################
    @app_commands.command(name="editar", description=constants.COMMAND_EDIT_DESC)
    @app_commands.describe(
        id_formato=constants.PARAM_FORMAT_ID_DESC,
        canal=constants.PARAM_CHANNEL_DESC,
        formato=constants.PARAM_FORMAT_DESC,
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def edit_channel_format(
        self,
        interaction: Interaction,
        id_formato: Optional[str] = None,
        canal: Optional[TextChannel] = None,
        formato: Optional[str] = None,
    ):
        # Si no se proporciona ID, mostrar vista de selección
        if id_formato is None:
            await show_channel_format_selection_for_edit(interaction, canal, formato)
            return

        # Lógica original para cuando se proporciona ID
        result = edit_channel_format_by_id(id_formato, canal, formato)

        if result['success']:
            await interaction.response.send_message(constants.SUCCESS_FORMAT_EDITED, ephemeral=True)
        else:
            await interaction.response.send_message(content=result['error'], ephemeral=True)


async def setup(bot):
    await bot.add_cog(ChannelFormatsCommands(bot), guild=Object(id=guild_id))
