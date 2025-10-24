from typing import Optional
from discord import app_commands, Interaction, Role, CategoryChannel, Embed, Color, Object
from discord.ext import commands
from settings import guild_id
from .service import ClanSettingsService
from modules.clans.service import ClanService
from translator import __


class ClanSettingsCommands(commands.GroupCog, name="clan_settings"):
    def __init__(self, bot):
        self.bot = bot
        self.service = ClanSettingsService()
        super().__init__()

    @app_commands.command(name="config", description=constants.COMMAND_CONFIG_DESC)
    @app_commands.describe(
        categoria_testo=constants.PARAM_TEXT_CATEGORY_DESC,
        categoria_voz=constants.PARAM_VOICE_CATEGORY_DESC,
        max_miembros=constants.PARAM_MAX_MEMBERS_DESC,
        rol_lider=constants.PARAM_LEADER_ROLE_DESC,
        color_roles=constants.PARAM_ROLE_COLOR_DESC,
        varios_clanes=constants.PARAM_MULTIPLE_CLANS_DESC,
        varios_lideres=constants.PARAM_MULTIPLE_LEADERS_DESC,
        max_texto=constants.PARAM_MAX_TEXT_DESC,
        max_voz=constants.PARAM_MAX_VOICE_DESC
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
                    __("clanSettings.errorMessages.invalidColor"), ephemeral=True
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
            __("clanSettings.successMessages.configUpdated"), ephemeral=True
        )

    @app_commands.command(name="info", description=constants.COMMAND_INFO_DESC)
    @app_commands.checks.has_permissions(administrator=True)
    async def ver_config(self, interaction: Interaction):
        settings, error = await self.service.get_settings()
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        if not settings:
            return

        embed = Embed(
            title=constants.TITLE_CLAN_CONFIG,
            color=Color.blue(),
            description=constants.EMBED_DESCRIPTION,
        )

        # Canales
        embed.add_field(
            name=constants.FIELD_CATEGORIES,
            value=(
                constants.VALUE_CATEGORIES_FORMAT.format(
                    text_category=settings.text_category_id,
                    voice_category=settings.voice_category_id
                )
                if settings.text_category_id and settings.voice_category_id
                else constants.VALUE_NOT_CONFIGURED
            ),
            inline=False,
        )
        embed.add_field(
            name=constants.FIELD_MAX_CHANNELS,
            value=constants.VALUE_MAX_CHANNELS_FORMAT.format(
                max_text=settings.max_text_channels,
                max_voice=settings.max_voice_channels
            ),
            inline=True,
        )

        # Roles
        additional_roles_text = (
            ", ".join([f"<@&{role_id}>" for role_id in settings.additional_roles])
            if settings.additional_roles
            else constants.VALUE_NO_ADDITIONAL_ROLES
        )
        embed.add_field(
            name=constants.FIELD_ADDITIONAL_ROLES,
            value=additional_roles_text,
            inline=False,
        )
        embed.add_field(
            name=constants.FIELD_LEADER_ROLE,
            value=f"<@&{settings.leader_role_id}>" if settings.leader_role_id else constants.VALUE_NOT_CONFIGURED,
            inline=True,
        )
        embed.add_field(name=constants.FIELD_ROLE_COLOR, value=f"#{settings.default_role_color}", inline=True)

        # Límites
        embed.add_field(
            name=constants.FIELD_LIMITS,
            value=constants.VALUE_LIMITS_FORMAT.format(
                max_members=settings.max_members,
                multiple_clans=constants.VALUE_YES if settings.allow_multiple_clans else constants.VALUE_NO,
                multiple_leaders=constants.VALUE_YES if settings.allow_multiple_leaders else constants.VALUE_NO
            ),
            inline=False,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="añadir_rol_adicional", description=constants.COMMAND_ADD_ROLE_DESC)
    @app_commands.describe(rol=constants.PARAM_ADDITIONAL_ROLE_DESC)
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
                __("clanSettings.errorMessages.roleAlreadyExists", role=rol.mention), 
                ephemeral=True
            )
            return

        settings.additional_roles.append(rol.id)
        error = await self.service.save_settings(settings)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        await interaction.response.send_message(
            __("clanSettings.successMessages.additionalRoleAdded", role=rol.mention),
            ephemeral=True
        )

    @app_commands.command(name="quitar_rol_adicional", description=constants.COMMAND_REMOVE_ROLE_DESC)
    @app_commands.describe(rol=constants.PARAM_REMOVE_ROLE_DESC)
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
                __("clanSettings.errorMessages.roleNotInList", role=rol.mention), 
                ephemeral=True
            )
            return

        settings.additional_roles.remove(rol.id)
        error = await self.service.save_settings(settings)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return

        await interaction.response.send_message(
            __("clanSettings.successMessages.additionalRoleRemoved", role=rol.mention),
            ephemeral=True
        )

    @app_commands.command(name="limpiar_roles_adicionales", description=constants.COMMAND_CLEAR_ROLES_DESC)
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
            __("clanSettings.successMessages.allAdditionalRolesCleared"),
            ephemeral=True
        )

    @app_commands.command(name="aplicar_roles_adicionales", description=constants.COMMAND_APPLY_ROLES_DESC)
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
                error or __("clanSettings.errorMessages.noClansToProcess"), 
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
                __("clanSettings.errorMessages.noValidAdditionalRoles"), 
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
            __("clanSettings.successMessages.rolesApplied", 
                total_members=total_members,
                successful_members=successful_assignments
            ),
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(ClanSettingsCommands(bot), guild=Object(id=guild_id))
