"""Comandos de configuración de clanes"""

from typing import Optional, List
from discord import (
    app_commands,
    Interaction,
    Role,
    CategoryChannel,
    Embed,
    Color,
    Object
)
from discord.ext import commands
from settings import guild_id
from .service import ClanSettingsService

class ClanSettingsCommands(commands.GroupCog, name="clan_settings"):
    """Comandos para gestionar la configuración de clanes"""

    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="config")
    @app_commands.checks.has_permissions(administrator=True)
    async def clan_config(
        self,
        interaction: Interaction,
        categoria: Optional[CategoryChannel] = None,
        max_miembros: Optional[int] = None,
        rol_lider: Optional[Role] = None,
        color_roles: Optional[str] = None,
        varios_clanes: Optional[bool] = None,
        varios_lideres: Optional[bool] = None,
        max_texto: Optional[int] = None,
        max_voz: Optional[int] = None
    ):
        """Configurar sistema de clanes"""
        settings, error = await ClanSettingsService.get_settings()
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        if not settings:
            return

        # Actualizar valores proporcionados
        if categoria:
            settings.category_id = categoria.id
        if max_miembros:
            settings.max_members = max_miembros
        if rol_lider:
            settings.leader_role_id = rol_lider.id
        if color_roles:
            settings.default_role_color = color_roles
        if varios_clanes is not None:
            settings.allow_multiple_clans = varios_clanes
        if varios_lideres is not None:
            settings.allow_multiple_leaders = varios_lideres
        if max_texto:
            settings.max_text_channels = max_texto
        if max_voz:
            settings.max_voice_channels = max_voz

        # Guardar cambios
        error = await ClanSettingsService.save_settings(settings)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        await interaction.response.send_message(
            "Configuración actualizada con éxito.",
            ephemeral=True
        )

    @app_commands.command(name="info")
    @app_commands.checks.has_permissions(administrator=True)
    async def ver_config(self, interaction: Interaction):
        """Ver la configuración actual de clanes"""
        settings, error = await ClanSettingsService.get_settings()
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        if not settings:
            return

        embed = Embed(
            title="Configuración de Clanes",
            color=Color.blue(),
            description="Configuración actual de los clanes"
        )

        # Canales
        embed.add_field(
            name="Categoría",
            value=f"<#{settings.category_id}>" if settings.category_id else "No configurada",
            inline=True
        )
        embed.add_field(
            name="Máx. Canales",
            value=f"Texto: {settings.max_text_channels}\nVoz: {settings.max_voice_channels}",
            inline=True
        )

        # Roles
        embed.add_field(
            name="Rol de Líder",
            value=f"<@&{settings.leader_role_id}>" if settings.leader_role_id else "No configurado",
            inline=True
        )
        embed.add_field(
            name="Color de Roles",
            value=f"#{settings.default_role_color}",
            inline=True
        )

        # Límites
        embed.add_field(
            name="Límites",
            value=f"Máx. Miembros: {settings.max_members}\n" \
                  f"Múltiples Clanes: {'Sí' if settings.allow_multiple_clans else 'No'}\n" \
                  f"Múltiples Líderes: {'Sí' if settings.allow_multiple_leaders else 'No'}",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    """Configuración del módulo"""
    await bot.add_cog(
        ClanSettingsCommands(bot),
        guild=Object(id=guild_id)
    )
