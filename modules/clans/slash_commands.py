"""Comandos de clanes"""

from typing import Optional
from datetime import datetime
from discord import (
    app_commands,
    Interaction,
    Member,
    Object,
    Embed, Color
)
from discord.ext import commands
from discord.app_commands import Group
from settings import guild_id
from modules.core import send_paginated_embeds
from modules.clan_settings import ClanSettingsService
from .service import ClanService
from .utils import create_clan_role, create_clan_channels, setup_clan_roles
from .validators import ClanValidator
from .views import ClanSelectView

class ClanCommands(commands.GroupCog, name="clan"):
    """Comandos para gestionar clanes"""

    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    lider = Group(name="lider", description="Comandos para líderes de clan")
    mod = Group(name="mod", description="Comandos de moderación de clanes")

    #######################################
    ### Comandos para miembros del clan ###
    #######################################
    @app_commands.command(name="unirse")
    async def clan_join(self, interaction: Interaction, nombre: str):
        """Unirse a un clan"""
        # ...código para unirse a un clan..

    #####################################
    ### Comandos para líderes de clan ###
    #####################################
    @lider.command(name="invitar")
    @app_commands.describe(
        miembro="Miembro a invitar al clan"
    )
    async def invite_to_clan(self, interaction: Interaction, miembro: Member):
        """Invitar a alguien del clan"""
        clans, error = await ClanService.get_member_clans(interaction.user.id)
        if error or clans is None:
            await interaction.response.send_message(
                "No tienes permisos para gestionar ningún clan.",
                ephemeral=True
            )
            return
        view = ClanSelectView(clans, miembro)
        await interaction.response.send_message(
            "Selecciona el clan al que quieres invitar al usuario.",
            view=view,
            ephemeral=True
        )
        view.message = await interaction.original_response()
        return



    ###########################################
    ### Comandos para el staff del servidor ###
    ###########################################

    ### ? Crear clan ###
    @mod.command(name="crear", description="Crear un nuevo clan")
    @app_commands.describe(nombre="Nombre del clan", lider="Líder del clan")
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def clan_create(
        self,
        interaction: Interaction,
        nombre: str,
        lider: Member,
    ):
        """Crear un nuevo clan"""
        if not interaction.guild:
            await interaction.response.send_message(
                "Este comando solo se puede usar en un servidor.",
                ephemeral=True
            )
            return

        can_create, error = await ClanValidator.can_create_clan(
            name=nombre,
            leader=lider
        )
        if not can_create or error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        # Obtener la configuración
        settings, error = await ClanSettingsService.get_settings()
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        # Crear rol con la configuración
        role, error = await create_clan_role(interaction.guild, nombre)
        if error or not role:
            await interaction.response.send_message("Error al crear el rol.", ephemeral=True)
            return

        # Crear canales en la categoría configurada
        text_channel, voice_channel, error = await create_clan_channels(
            interaction.guild,
            nombre,
            role
        )
        if error or not text_channel or not voice_channel:
            # Limpiar si hay error
            await role.delete()
            if text_channel:
                await text_channel.delete()
            if voice_channel:
                await voice_channel.delete()
            await interaction.response.send_message("Error al crear los canales.", ephemeral=True)
            return

        # Configurar roles del líder
        error = await setup_clan_roles(interaction.guild, lider, role)
        if error:
            # Limpiar si hay error
            await role.delete()
            if text_channel:
                await text_channel.delete()
            if voice_channel:
                await voice_channel.delete()
            await interaction.response.send_message(error, ephemeral=True)
            return

        # Crear clan en BD con límites configurados
        _, error = await ClanService.create_clan(
            name=nombre,
            leader_id=lider.id,
            role_id=role.id,
            text_channel=text_channel,
            voice_channel=voice_channel,
            max_members=settings.max_members
        )

        if error:
            # Limpiar todo si hay error
            await role.delete()
            await text_channel.delete()
            await voice_channel.delete()
            await interaction.response.send_message(error, ephemeral=True)
            return

        await interaction.response.send_message(
            f"Clan {nombre} creado con éxito en la categoría " \
            f"<#{settings.category_id}> con {settings.max_members} miembros máximo.",
            ephemeral=True
        )


    ### ? INFO ###
    @mod.command(name="info", description="Información de un clan")
    @app_commands.describe(
        id_clan="Id del clan"
    )
    @app_commands.checks.has_permissions(
        manage_roles=True,
        manage_channels=True
    )
    async def clan_info(self, interaction: Interaction, id_clan: Optional[str] = None):
        """Información de un clan"""
        if not interaction.guild:
            await interaction.response.send_message(
                "Este comando solo se puede usar en un servidor.",
                ephemeral=True
            )
            return

        clans = []

        if id_clan:
            clan, error = await ClanService.get_clan_by_id(id_clan)
            if error:
                await interaction.response.send_message(error, ephemeral=True)
                return
            if not clan:
                await interaction.response.send_message("Clan no encontrado.", ephemeral=True)
                return
            clans.append(clan)

        else:
            clans, error = await ClanService.get_all()
            if error:
                await interaction.response.send_message(
                    content=error,
                    ephemeral=True
                )
                return
            if not clans:
                await interaction.response.send_message("No hay clanes.", ephemeral=True)
                return

        embeds = []
        for clan in clans:
            embed = Embed(
                title=f"Información del clan **{clan.clan.name}**",
                description=f"**Información del clan {clan.clan.name}**.",
                color=Color.blue(),
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url
            )
            embed.set_footer(
                text=f"{interaction.guild.name}",
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None
            )
            embed.add_field(name="ID", value=clan.clan.id, inline=True)
            embed.add_field(name="Nombre", value=clan.clan.name, inline=True)
            leaders = [f"<@{member.user_id}>" for member in clan.members if member.role == "leader"]
            embed.add_field(name="Líderes", value=", ".join(leaders), inline=True)
            embed.add_field(name="Miembros", value=len(clan.members), inline=True)
            embed.add_field(name="Límite de miembros", value=clan.clan.max_members, inline=True)
            embed.add_field(name="Rol", value=f"<@&{clan.clan.role_id}>", inline=True)
            text_channels = [
                f"<#{channel.channel_id}>" for channel in clan.channels if channel.type == "text"
            ]
            voice_channels = [
                f"<#{channel.channel_id}>" for channel in clan.channels if channel.type == "voice"
            ]
            embed.add_field(name="Canales de texto", value=", ".join(text_channels), inline=True)
            embed.add_field(name="Canales de voz", value=", ".join(voice_channels), inline=True)
            embed.add_field(name="Fecha de creación", value=clan.clan.created_at, inline=False)

            embeds.append(embed)
        await send_paginated_embeds(
            interaction=interaction,
            embeds=embeds,
            ephemeral=True
        )

    ### ? Eliminar clan ###
    @mod.command(name="eliminar", description="Eliminar un clan")
    @app_commands.describe(
        id_clan="Id del clan"
    )
    @app_commands.checks.has_permissions(
        manage_roles=True,
        manage_channels=True
    )
    async def clan_delete(self, interaction: Interaction, id_clan: str):
        """Eliminar un clan"""
        if not interaction.guild:
            await interaction.response.send_message(
                "Este comando solo se puede usar en un servidor.",
                ephemeral=True
            )
            return

        clan, error = await ClanService.get_clan_by_id(id_clan)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        if not clan:
            await interaction.response.send_message("Clan no encontrado.", ephemeral=True)
            return

        # Eliminar rol
        role = interaction.guild.get_role(clan.clan.role_id)
        if role:
            await role.delete()

        # Eliminar canales
        for channel in clan.channels:
            channel_obj = interaction.guild.get_channel(channel.channel_id)
            if channel_obj:
                await channel_obj.delete()

        # Eliminar clan de la base de datos
        _, error = await ClanService.delete(clan.clan.id)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        await interaction.response.send_message(
            "Clan eliminado con éxito.",
            ephemeral=True
        )


async def setup(bot):
    """setup"""
    await bot.add_cog(ClanCommands(bot), guild=Object(id=guild_id))
