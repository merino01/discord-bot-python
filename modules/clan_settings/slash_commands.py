from typing import Optional
from discord import app_commands, Interaction, Role, CategoryChannel, Embed, Color, Object
from discord.ext import commands
from settings import guild_id
from .service import ClanSettingsService
from modules.clans.service import ClanService


class ClanSettingsCommands(commands.GroupCog, name="clan_settings"):
    def __init__(self, bot):
        self.bot = bot
        self.service = ClanSettingsService()
        super().__init__()

    @app_commands.command(name="config")
    @app_commands.checks.has_permissions(administrator=True)
    async def clan_config(
        self,
        interaction: Interaction,
        categoria_testo: Optional[CategoryChannel] = None,
        categoria_voz: Optional[CategoryChannel] = None,
        max_miembros: Optional[int] = None,
        rol_lider: Optional[Role] = None,
        color_roles: Optional[str] = None,
        varios_clanes: Optional[bool] = None,
        varios_lideres: Optional[bool] = None,
        max_texto: Optional[int] = None,
        max_voz: Optional[int] = None,
    ):
        settings, error = await self.service.get_settings()
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        if not settings:
            return

        if categoria_testo:
            settings.text_category_id = categoria_testo.id
        if categoria_voz:
            settings.voice_category_id = categoria_voz.id
        if max_miembros:
            settings.max_members = max_miembros
        if rol_lider:
            settings.leader_role_id = rol_lider.id
        if color_roles:
            try:
                settings.default_role_color = int(color_roles, 16)
            except ValueError:
                await interaction.response.send_message(
                    "El color de roles debe ser un valor hexadecimal válido.", ephemeral=True
                )
                return
        if varios_clanes is not None:
            settings.allow_multiple_clans = varios_clanes
        if varios_lideres is not None:
            settings.allow_multiple_leaders = varios_lideres
        if max_texto:
            settings.max_text_channels = max_texto
        if max_voz:
            settings.max_voice_channels = max_voz

        # Guardar cambios
        error = await self.service.save_settings(settings)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        await interaction.response.send_message(
            "Configuración actualizada con éxito.", ephemeral=True
        )

    @app_commands.command(name="info")
    @app_commands.checks.has_permissions(administrator=True)
    async def ver_config(self, interaction: Interaction):
        settings, error = await self.service.get_settings()
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        if not settings:
            return

        embed = Embed(
            title="Configuración de Clanes",
            color=Color.blue(),
            description="Configuración actual de los clanes",
        )

        # Canales
        embed.add_field(
            name="Categorías",
            value=(
                f"Texto: <#{settings.text_category_id}>\nVoz: <#{settings.voice_category_id}>"
                if settings.text_category_id and settings.voice_category_id
                else "No configurado"
            ),
            inline=False,
        )
        embed.add_field(
            name="Máx. Canales",
            value=f"Texto: {settings.max_text_channels}\nVoz: {settings.max_voice_channels}",
            inline=True,
        )

        # Roles
        additional_roles_text = (
            ", ".join([f"<@&{role_id}>" for role_id in settings.additional_roles])
            if settings.additional_roles
            else "No configurados"
        )
        embed.add_field(
            name="Roles Adicionales",
            value=additional_roles_text,
            inline=False,
        )
        embed.add_field(
            name="Rol de Líder",
            value=f"<@&{settings.leader_role_id}>" if settings.leader_role_id else "No configurado",
            inline=True,
        )
        embed.add_field(name="Color de Roles", value=f"#{settings.default_role_color}", inline=True)

        # Límites
        embed.add_field(
            name="Límites",
            value=f"Máx. Miembros: {settings.max_members}\n"
            f"Múltiples Clanes: {'Sí' if settings.allow_multiple_clans else 'No'}\n"
            f"Múltiples Líderes: {'Sí' if settings.allow_multiple_leaders else 'No'}",
            inline=False,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="añadir_rol_adicional")
    @app_commands.describe(rol="Rol adicional a asignar a todos los miembros de clanes")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_additional_role(self, interaction: Interaction, rol: Role):
        settings, error = await self.service.get_settings()
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        if not settings:
            return

        if rol.id in settings.additional_roles:
            await interaction.response.send_message(
                f"El rol {rol.mention} ya está en la lista de roles adicionales.", 
                ephemeral=True
            )
            return

        settings.additional_roles.append(rol.id)
        error = await self.service.save_settings(settings)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        await interaction.response.send_message(
            f"Rol adicional {rol.mention} agregado con éxito. "
            f"Se asignará automáticamente a todos los nuevos miembros de clanes.",
            ephemeral=True
        )

    @app_commands.command(name="quitar_rol_adicional")
    @app_commands.describe(rol="Rol adicional a remover de la lista")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_additional_role(self, interaction: Interaction, rol: Role):
        settings, error = await self.service.get_settings()
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        if not settings:
            return

        if rol.id not in settings.additional_roles:
            await interaction.response.send_message(
                f"El rol {rol.mention} no está en la lista de roles adicionales.", 
                ephemeral=True
            )
            return

        settings.additional_roles.remove(rol.id)
        error = await self.service.save_settings(settings)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        await interaction.response.send_message(
            f"Rol adicional {rol.mention} removido con éxito. "
            f"Ya no se asignará a los nuevos miembros de clanes.",
            ephemeral=True
        )

    @app_commands.command(name="limpiar_roles_adicionales")
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_additional_roles(self, interaction: Interaction):
        settings, error = await self.service.get_settings()
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        if not settings:
            return

        if not settings.additional_roles:
            await interaction.response.send_message(
                "No hay roles adicionales configurados.", 
                ephemeral=True
            )
            return

        settings.additional_roles = []
        error = await self.service.save_settings(settings)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        await interaction.response.send_message(
            "Todos los roles adicionales han sido removidos.",
            ephemeral=True
        )

    @app_commands.command(name="aplicar_roles_adicionales")
    @app_commands.checks.has_permissions(administrator=True)
    async def apply_additional_roles_to_existing_members(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        
        settings, error = await self.service.get_settings()
        if error:
            await interaction.followup.send(error, ephemeral=True)
            return
        if not settings:
            return

        if not settings.additional_roles:
            await interaction.followup.send(
                "No hay roles adicionales configurados.", 
                ephemeral=True
            )
            return

        clan_service = ClanService()
        
        # Obtener todos los clanes
        clans, error = await clan_service.get_all_clans()
        if error or not clans:
            await interaction.followup.send(
                error or "No hay clanes para procesar.", 
                ephemeral=True
            )
            return

        guild = interaction.guild
        total_members = 0
        successful_assignments = 0
        
        # Obtener los roles adicionales
        additional_roles = []
        for role_id in settings.additional_roles:
            if role := guild.get_role(role_id):
                additional_roles.append(role)

        if not additional_roles:
            await interaction.followup.send(
                "No se encontraron roles adicionales válidos en el servidor.", 
                ephemeral=True
            )
            return

        # Aplicar roles a cada miembro de cada clan
        for clan in clans:
            for member_data in clan.members:
                total_members += 1
                try:
                    member = await guild.fetch_member(member_data.user_id)
                    if member and not member.bot:
                        roles_to_add = []
                        for additional_role in additional_roles:
                            if additional_role not in member.roles:
                                roles_to_add.append(additional_role)
                        
                        if roles_to_add:
                            await member.add_roles(*roles_to_add, reason="Aplicación de roles adicionales de clan")
                            successful_assignments += 1
                except Exception:
                    continue  # Continuar con el siguiente miembro si hay error

        await interaction.followup.send(
            f"Proceso completado. Se procesaron {total_members} miembros. "
            f"Se asignaron roles adicionales exitosamente a {successful_assignments} miembros.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(ClanSettingsCommands(bot), guild=Object(id=guild_id))
