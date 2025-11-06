from re import compile as compile_regex, error as re_error
from typing import Optional
from uuid import uuid4
from discord import app_commands, Interaction, TextChannel, Object, Embed, Color
from discord.ext import commands
from settings import guild_id
from modules.core import send_paginated_embeds
from .service import ChannelFormatsService
from .models import ChannelFormat
from .utils import show_channel_format_selection_for_delete, show_channel_format_selection_for_edit, edit_channel_format_by_id
from i18n import __


class ChannelFormatsCommands(commands.GroupCog, name="formato_canales"):
    def __init__(self, bot):
        self.bot = bot
        self.service = ChannelFormatsService()

    #####################################################
    ### Comando para añadir un nuevo formato de canal ###
    #####################################################
    @app_commands.command(name="crear", description=__("triggers.commands.create"))
    @app_commands.describe(
        canal=__("triggers.params.channel"),
        formato=__("channelFormats.params.format"),
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def create_channel_format(
        self, interaction: Interaction, canal: TextChannel, formato: str
    ):
        try:
            compile_regex(formato)
        except re_error:
            await interaction.response.send_message(
                __("channelFormats.errors.invalidRegex"),
                ephemeral=True,
            )
            return

        new_channel_format = ChannelFormat(id=str(uuid4()), channel_id=canal.id, regex=formato)
        _, error = self.service.add(new_channel_format)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return

        await interaction.response.send_message(
            __("channelFormats.success.formatAdded", channel=canal.mention, format=formato), ephemeral=True
        )

    #########################################################
    ### Comando para listar todos los formatos de canal #####
    #########################################################
    @app_commands.command(name="listar", description=__("triggers.commands.list"))
    @app_commands.describe(
        id_formato=__("channelFormats.params.formatId"),
        canal=__("triggers.params.listChannel"),
        persistente=__("triggers.params.persistent"),
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
                    __("channelFormats.errors.formatNotFound", id=id_formato),
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
            await interaction.response.send_message(
                __("channelFormats.messages.noFormatsFound"), ephemeral=True
            )
            return

        embeds = []
        for channel_format in channel_formats:
            embed = Embed(title=__("channelFormats.embeds.formatIdTitle", id=channel_format.id), color=Color.blue())
            embed.add_field(name=__("triggers.fields.channel"), value=f"<#{channel_format.channel_id}>", inline=True)
            embed.add_field(name=__("channelFormats.fields.format"), value=channel_format.regex, inline=True)
            embeds.append(embed)
        await send_paginated_embeds(
            interaction=interaction,
            embeds=embeds,
            ephemeral=not persistente,
            message=__("channelFormats.messages.showingFormats", count=len(channel_formats)),
        )

    ###################################################
    ### Comando para eliminar un formato de canal #####
    ###################################################
    @app_commands.command(name="eliminar", description=__("triggers.commands.delete"))
    @app_commands.describe(id_formato=__("channelFormats.params.formatId"))
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def delete_channel_format(self, interaction: Interaction, id_formato: Optional[str] = None):
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
                __("channelFormats.errors.formatNotFound", id=id_formato),
                ephemeral=True,
            )
            return

        _, error = self.service.delete(channel_format)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return
        await interaction.response.send_message(
            __("channelFormats.success.formatDeleted", id=channel_format.id), ephemeral=True
        )

    ###############################################
    ### Comando para editar un formato de canal ###
    ###############################################
    @app_commands.command(name="editar", description=__("triggers.commands.edit"))
    @app_commands.describe(
        id_formato=__("channelFormats.params.formatId"),
        canal=__("triggers.params.channel"),
        formato=__("channelFormats.params.format"),
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
            await interaction.response.send_message(__("channelFormats.success.formatEdited"), ephemeral=True)
        else:
            await interaction.response.send_message(content=result['error'], ephemeral=True)


async def setup(bot):
    await bot.add_cog(ChannelFormatsCommands(bot), guild=Object(id=guild_id))
