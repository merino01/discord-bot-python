"""Comandos de clanes"""

from typing import Mapping
from discord import app_commands, Interaction, Member, Role, Object, PermissionOverwrite
from discord.ext import commands
from discord.app_commands import Group
from settings import guild_id
from .service import ClanService

class ClanCommands(commands.GroupCog, name="clan"):
    """Comandos para gestionar clanes"""

    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    clan = Group(name="clan", description="Comandos básicos de clanes")
    lider = Group(name="lider", description="Comandos para líderes de clan")
    mod = Group(name="mod", description="Comandos de moderación de clanes")

    #######################################
    ### Comandos para miembros del clan ###
    #######################################
    @clan.command(name="unirse")
    async def clan_join(self, interaction: Interaction, nombre: str):
        """Unirse a un clan"""
        # ...código para unirse a un clan..

    #####################################
    ### Comandos para líderes de clan ###
    #####################################
    @lider.command(name="expulsar")
    @app_commands.checks.has_role("Líder de Clan")
    async def clan_kick(self, interaction: Interaction, miembro: Member):
        """Expulsar a alguien del clan"""
        # ...código para expulsar...


    ###########################################
    ### Comandos para el staff del servidor ###
    ###########################################

    ### ? Crear clan ###
    @mod.command(name="crear", description="Crear un nuevo clan")
    @app_commands.describe(
        nombre="Nombre del clan",
        lider="Líder del clan"
    )
    @app_commands.checks.has_permissions(
        manage_roles=True,
        manage_channels=True
    )
    async def clan_create(
        self,
        interaction: Interaction,
        nombre: str,
        lider: Member,
    ):
        """Crear un nuevo clan"""
        if interaction.guild is None:
            await interaction.response.send_message(
                "Este comando solo se puede usar en un servidor."
            )
            return
        role = await interaction.guild.create_role(name=nombre)
        text_channel_overwrites: Mapping[Role, PermissionOverwrite] = {
            interaction.guild.default_role: PermissionOverwrite(read_messages=False),
            role: PermissionOverwrite(read_messages=True)
        }
        voice_channel_overwrites: Mapping[Role, PermissionOverwrite] = {
            interaction.guild.default_role: PermissionOverwrite(connect=False),
            role: PermissionOverwrite(connect=True)
        }
        text_channel = await interaction.guild.create_text_channel(
            name=nombre,
            overwrites=text_channel_overwrites
        )
        voice_channel = await interaction.guild.create_voice_channel(
            name=nombre,
            overwrites=voice_channel_overwrites
        )

        await lider.add_roles(role)

        _, error = await ClanService.create_clan(
            name=nombre,
            leader_id=lider.id,
            role_id=role.id,
            text_channel=text_channel,
            voice_channel=voice_channel
        )
        if error:
            await interaction.response.send_message(error)
            return
        await interaction.response.send_message("Clan creado con éxito.")

    ### ? INFO ###
    @mod.command(name="info", description="Información de un clan")
    @app_commands.describe(
        id_clan="Id del clan"
    )
    async def clan_info(self, interaction: Interaction, id_clan: str):
        """Información de un clan"""
        clan, error = await ClanService.get_clan_by_id(id_clan)
        if error:
            await interaction.response.send_message(error)
            return
        await interaction.response.send_message(clan)


async def setup(bot):
    """setup"""
    await bot.add_cog(
        ClanCommands(bot),
        guild=Object(id=guild_id)
    )
