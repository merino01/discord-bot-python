from typing import Optional
from discord import app_commands, Interaction, Role, CategoryChannel, Embed, Color, Object
from discord.ext import commands
from settings import guild_id
from .service import ClanSettingsService
from modules.clans.service import ClanService
from i18n import __


class ClanSettingsCommands(commands.GroupCog, name="clan_settings"):
    def __init__(self, bot):
        self.bot = bot
        self.service = ClanSettingsService()
        super().__init__()

    @app_commands.command(name="config", description=__("clanSettings.commands.config"))
    @app_commands.describe(
        categoria_testo=__("clanSettings.params.textCategory"),
        categoria_voz=__("clanSettings.params.voiceCategory"),
        max_miembros=__("clanSettings.params.maxMembers"),
        rol_lider=__("clanSettings.params.leaderRole"),
        color_roles=__("clanSettings.params.roleColor"),
        varios_clanes=__("clanSettings.params.multipleClans"),
        varios_lideres=__("clanSettings.params.multipleLeaders"),
        max_texto=__("clanSettings.params.maxText"),
        max_voz=__("clanSettings.params.maxVoice")
    )
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
                    __("clanSettings.errors.invalidColor"), ephemeral=True
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
            __("clanSettings.success.configUpdated"), ephemeral=True
        )

    @app_commands.command(name="info", description=__("clanSettings.commands.info"))
    @app_commands.checks.has_permissions(administrator=True)
    async def ver_config(self, interaction: Interaction):
        settings, error = await self.service.get_settings()
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        if not settings:
            return

        embed = Embed(
            title=__("clanSettings.embeds.clanConfigTitle"),
            color=Color.blue(),
            description=__("clanSettings.embeds.description"),
        )

        # Canales
        embed.add_field(
            name=__("clanSettings.fields.categories"),
            value=(
                __("clanSettings.values.categoriesFormat", 
                    text_category=settings.text_category_id,
                    voice_category=settings.voice_category_id
                )
                if settings.text_category_id and settings.voice_category_id
                else __("clanSettings.values.notConfigured")
            ),
            inline=False,
        )
        embed.add_field(
            name=__("clanSettings.fields.maxChannels"),
            value=__("clanSettings.values.maxChannelsFormat", 
                max_text=settings.max_text_channels,
                max_voice=settings.max_voice_channels
            ),
            inline=True,
        )

        # Roles
        additional_roles_text = (
            ", ".join([f"<@&{role_id}>" for role_id in settings.additional_roles])
            if settings.additional_roles
            else __("clanSettings.values.noAdditionalRoles")
        )
        embed.add_field(
            name=__("clanSettings.fields.additionalRoles"),
            value=additional_roles_text,
            inline=False,
        )
        embed.add_field(
            name=__("clanSettings.fields.leaderRole"),
            value=f"<@&{settings.leader_role_id}>" if settings.leader_role_id else __("clanSettings.values.notConfigured"),
            inline=True,
        )
        embed.add_field(name=__("clanSettings.fields.roleColor"), value=f"#{settings.default_role_color}", inline=True)

        # Límites
        embed.add_field(
            name=__("clanSettings.fields.limits"),
            value=__("clanSettings.values.limitsFormat", 
                max_members=settings.max_members,
                multiple_clans=__("clanSettings.values.yes") if settings.allow_multiple_clans else __("clanSettings.values.no"),
                multiple_leaders=__("clanSettings.values.yes") if settings.allow_multiple_leaders else __("clanSettings.values.no")
            ),
            inline=False,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="añadir_rol_adicional", description=__("clanSettings.commands.addRole"))
    @app_commands.describe(rol=__("clanSettings.params.additionalRole"))
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
                __("clanSettings.errors.roleAlreadyExists", role=rol.mention), 
                ephemeral=True
            )
            return

        settings.additional_roles.append(rol.id)
        error = await self.service.save_settings(settings)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        await interaction.response.send_message(
            __("clanSettings.success.additionalRoleAdded", role=rol.mention),
            ephemeral=True
        )

    @app_commands.command(name="quitar_rol_adicional", description=__("clanSettings.commands.removeRole"))
    @app_commands.describe(rol=__("clanSettings.params.removeRole"))
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
                __("clanSettings.errors.roleNotInList", role=rol.mention), 
                ephemeral=True
            )
            return

        settings.additional_roles.remove(rol.id)
        error = await self.service.save_settings(settings)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        await interaction.response.send_message(
            __("clanSettings.success.additionalRoleRemoved", role=rol.mention),
            ephemeral=True
        )

    @app_commands.command(name="limpiar_roles_adicionales", description=__("clanSettings.commands.clearRoles"))
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
                __("clanSettings.messages.noAdditionalRolesConfigured"), 
                ephemeral=True
            )
            return

        settings.additional_roles = []
        error = await self.service.save_settings(settings)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        await interaction.response.send_message(
            __("clanSettings.success.allAdditionalRolesCleared"),
            ephemeral=True
        )

    @app_commands.command(name="aplicar_roles_adicionales", description=__("clanSettings.commands.applyRoles"))
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
                __("clanSettings.messages.noAdditionalRolesConfigured"), 
                ephemeral=True
            )
            return

        clan_service = ClanService()
        
        # Obtener todos los clanes
        clans, error = await clan_service.get_all_clans()
        if error or not clans:
            await interaction.followup.send(
                error or __("clanSettings.errors.noClansToProcess"), 
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
                __("clanSettings.errors.noValidAdditionalRoles"), 
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
            __("clanSettings.success.rolesApplied", 
                total_members=total_members,
                successful_members=successful_assignments
            ),
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(ClanSettingsCommands(bot), guild=Object(id=guild_id))
