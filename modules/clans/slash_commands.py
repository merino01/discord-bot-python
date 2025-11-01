from typing import Optional, Union
from datetime import datetime
from discord import (
    app_commands,
    Interaction,
    Member,
    Object,
    Embed,
    Color,
    ChannelType,
    Role,
    TextChannel,
    VoiceChannel,
    PermissionOverwrite,
)
from discord.ext import commands
from discord.app_commands import Group
from settings import guild_id
from modules.core import send_paginated_embeds
from modules.clan_settings import ClanSettingsService
from .models import ClanMemberRole, ClanChannel, ChannelType as ClanChannelType
from .service import ClanService
from .utils import (
    create_clan_role,
    create_clan_channels,
    setup_clan_roles,
    logica_salir_del_clan,
    logica_expulsar_del_clan,
    crear_canal_adicional,
    remove_clan_roles_from_member,
    assign_clan_roles_to_leader,
    generate_channel_name,
    demote_leader_to_member,
    remove_clan_channel,
)
from .validators import ClanValidator
from .views.clan_invite_buttons import ClanInviteView
from .views.clan_leave_buttons import ClanLeaveView
from .views.clan_mod_selection import ClanModSelectionView
from .views.clan_config_selection import ClanConfigSelectionView
from .views.clan_delete_buttons import ClanDeleteView
from .views.clan_selector import ClanSelectorView
from modules.core import logger
from . import constants


class ClanCommands(commands.GroupCog, name="clan"):
    def __init__(self, bot):
        self.bot = bot
        self.service = ClanService()
        self.validator = ClanValidator()
        self.clan_settings_service = ClanSettingsService()
        super().__init__()

    mod = Group(name="mod", description="Comandos de moderación de clanes")

    #################################
    ### Comandos para moderadores ###
    #################################
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
        await interaction.response.defer(ephemeral=True)

        can_create, error = await self.validator.can_create_clan(nombre, lider)
        if not can_create or error:
            return await interaction.followup.send(error, ephemeral=True)

        # Obtener la configuración
        settings, error = await self.clan_settings_service.get_settings()
        if error:
            return await interaction.followup.send(error, ephemeral=True)

        # Crear rol con la configuración
        role, error = await create_clan_role(interaction.guild, nombre)
        if error or not role:
            return await interaction.followup.send(constants.ERROR_CREATING_ROLE, ephemeral=True)

        # Crear canales en la categoría configurada
        text_channel, voice_channel, error = await create_clan_channels(
            interaction.guild, nombre, role
        )
        if error or not text_channel or not voice_channel:
            # Limpiar si hay error
            await role.delete()
            if text_channel:
                await text_channel.delete()
            if voice_channel:
                await voice_channel.delete()
            await interaction.followup.send(constants.ERROR_CREATING_CHANNELS, ephemeral=True)
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
            await interaction.followup.send(error, ephemeral=True)
            return

        # Crear clan en BD con límites configurados
        _, error = await self.service.create_clan(
            name=nombre,
            leader_id=lider.id,
            role_id=role.id,
            text_channel=text_channel,
            voice_channel=voice_channel,
            max_members=settings.max_members,
        )

        if error:
            # Limpiar todo si hay error
            await role.delete()
            await text_channel.delete()
            await voice_channel.delete()
            await interaction.followup.send(error, ephemeral=True)
            return

        await interaction.followup.send(
            constants.SUCCESS_CLAN_CREATED.format(
                nombre=nombre,
                text_category=settings.text_category_id,
                voice_category=settings.voice_category_id,
                max_members=settings.max_members,
            ),
            ephemeral=True,
        )

    ### ? INFO ###
    @mod.command(name="info", description="Información de un clan")
    @app_commands.describe(
        id_clan="Id del clan",
        persistente="Si la respuesta debe ser visible para todos (opcional, por defecto falso)",
    )
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def clan_info(
        self,
        interaction: Interaction,
        id_clan: Optional[str] = None,
        persistente: Optional[bool] = False,
    ):
        ephemeral = not persistente  # Si persistente=True, ephemeral=False
        if id_clan:
            clan, error = await self.service.get_clan_by_id(id_clan)
            if error or not clan:
                return await interaction.response.send_message(
                    error or constants.ERROR_CLAN_NOT_FOUND, ephemeral=ephemeral
                )
            # Mostrar info del clan directamente
            embed = Embed(
                title=constants.EMBED_CLAN_INFO_TITLE.format(clan_name=clan.name),
                description=constants.EMBED_CLAN_INFO_DESCRIPTION.format(clan_name=clan.name),
                color=Color.blue(),
                timestamp=datetime.now(),
            )
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_author(
                name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url
            )
            embed.set_footer(
                text=f"{interaction.guild.name}",
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None,
            )
            embed.add_field(name=constants.FIELD_ID, value=clan.id, inline=True)
            embed.add_field(name=constants.FIELD_NAME, value=clan.name, inline=True)
            leaders = [f"<@{member.user_id}>" for member in clan.members if member.role == "leader"]
            embed.add_field(name=constants.FIELD_LEADERS, value=", ".join(leaders), inline=True)
            embed.add_field(name=constants.FIELD_MEMBERS, value=len(clan.members), inline=True)
            embed.add_field(name=constants.FIELD_MEMBER_LIMIT, value=clan.max_members, inline=True)
            embed.add_field(name=constants.FIELD_ROLE, value=f"<@&{clan.role_id}>", inline=True)
            text_channels = [
                f"<#{channel.channel_id}>" for channel in clan.channels if channel.type == "text"
            ]
            voice_channels = [
                f"<#{channel.channel_id}>" for channel in clan.channels if channel.type == "voice"
            ]
            embed.add_field(
                name=constants.FIELD_TEXT_CHANNELS,
                value=f"{', '.join(text_channels) if text_channels else constants.VALUE_NONE} ({len(text_channels)}/{clan.max_text_channels})",
                inline=True,
            )
            embed.add_field(
                name=constants.FIELD_VOICE_CHANNELS,
                value=f"{', '.join(voice_channels) if voice_channels else constants.VALUE_NONE} ({len(voice_channels)}/{clan.max_voice_channels})",
                inline=True,
            )
            embed.add_field(name=constants.FIELD_CREATION_DATE, value=clan.created_at, inline=False)
            return await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        else:
            clans, error = await self.service.get_all_clans()
            if error or not clans or len(clans) == 0:
                return await interaction.response.send_message(
                    error or constants.ERROR_NO_CLANS, ephemeral=ephemeral
                )
            # Mostrar selector de clanes
            view = ClanSelectorView(clans, "info", ephemeral=ephemeral)
            embed = Embed(
                title="Selecciona un clan para ver su información",
                description="Usa el menú desplegable para elegir un clan.",
                color=Color.blue(),
            )
            await interaction.response.send_message(embed=embed, view=view, ephemeral=ephemeral)

    ### ? Eliminar clan ###
    @mod.command(name="eliminar", description="Eliminar un clan")
    @app_commands.describe(
        id_clan="Id del clan (opcional - sin especificar muestra lista para elegir)"
    )
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def clan_delete(self, interaction: Interaction, id_clan: Optional[str] = None):
        await interaction.response.defer(ephemeral=True)

        if id_clan:
            # Si se proporciona ID, eliminar directamente
            clan, error = await self.service.get_clan_by_id(id_clan)
            if error or not clan:
                await interaction.followup.send(
                    error or constants.ERROR_CLAN_NOT_FOUND, ephemeral=True
                )
                return

            # Eliminar clan de la base de datos PRIMERO
            error = await self.service.delete_clan(clan.id)
            if error:
                return await interaction.followup.send(
                    constants.ERROR_DELETING_CLAN.format(error=error), ephemeral=True
                )

            # Ahora quitar todos los roles de clan a todos los miembros
            for member in clan.members:
                await remove_clan_roles_from_member(
                    guild=interaction.guild,
                    member_id=member.user_id,
                    clan_role_id=clan.role_id,
                    should_check_other_clans=True,
                )

            # Eliminar el rol del clan
            role = interaction.guild.get_role(clan.role_id)
            if role:
                await role.delete()

            # Eliminar canales
            for channel in clan.channels:
                channel_obj = interaction.guild.get_channel(channel.channel_id)
                if channel_obj:
                    await channel_obj.delete()

            await interaction.followup.send(constants.SUCCESS_CLAN_DELETED, ephemeral=True)

        else:
            # Si no se proporciona ID, mostrar lista para elegir
            clans, error = await self.service.get_all_clans()
            if error or not clans or len(clans) == 0:
                return await interaction.followup.send(
                    error or constants.ERROR_NO_CLANS_TO_DELETE, ephemeral=True
                )

            # Crear embed con lista de clanes
            embed = Embed(
                title=constants.EMBED_SELECT_CLAN_DELETE_TITLE,
                description=constants.EMBED_SELECT_CLAN_DELETE_DESCRIPTION,
                color=Color.red(),
            )
            embed.add_field(
                name=constants.FIELD_TOTAL_CLANS,
                value=constants.VALUE_TOTAL_CLANS_AVAILABLE.format(count=len(clans)),
                inline=False,
            )

            view = ClanDeleteView(clans, self.service)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    ### ? Migrar clanes existentes ###
    @mod.command(name="migrar", description="Migrar un clan existente al sistema de base de datos")
    @app_commands.describe(
        rol="Rol del clan a migrar",
        canal_texto="Canal de texto del clan",
        canal_voz="Canal de voz del clan",
        lider="Líder del clan (si no se especifica se toma el primer miembro con el rol)",
    )
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def migrate_clans(
        self,
        interaction: Interaction,
        rol: Role,
        canal_texto: TextChannel,
        canal_voz: VoiceChannel,
        lider: Optional[Member] = None,
    ):
        await interaction.response.defer(ephemeral=True)

        try:
            # Verificar si el clan ya existe en la BD
            existing_clans, _ = await self.service.get_all_clans()
            if existing_clans and any(clan.role_id == rol.id for clan in existing_clans):
                return await interaction.followup.send(
                    constants.ERROR_ROLE_ALREADY_REGISTERED.format(role_name=rol.name),
                    ephemeral=True,
                )

            # Encontrar miembros con el rol
            members_with_role = [
                member
                for member in interaction.guild.members
                if rol in member.roles and not member.bot
            ]

            if not members_with_role:
                return await interaction.followup.send(
                    constants.ERROR_NO_MEMBERS_WITH_ROLE.format(role_name=rol.name), ephemeral=True
                )

            # Determinar el líder
            if lider:
                if rol not in lider.roles:
                    return await interaction.followup.send(
                        constants.ERROR_MEMBER_NO_ROLE.format(
                            member=lider.mention, role_name=rol.name
                        ),
                        ephemeral=True,
                    )
                leader = lider
            else:
                leader = members_with_role[0]  # Tomar el primer miembro como líder

            # Obtener configuración
            settings, _ = await self.clan_settings_service.get_settings()

            # Crear clan en la base de datos
            _, error = await self.service.create_clan(
                name=rol.name,  # Usar el nombre del rol como nombre del clan
                leader_id=leader.id,
                role_id=rol.id,
                text_channel=canal_texto,
                voice_channel=canal_voz,
                max_members=settings.max_members if settings else 50,
            )

            if error:
                return await interaction.followup.send(
                    constants.ERROR_CREATING_MIGRATED_CLAN.format(clan_name=rol.name, error=error),
                    ephemeral=True,
                )

            # Obtener el clan recién creado
            clan, _ = await self.service.get_clan_by_role_id(rol.id)
            if not clan:
                return await interaction.followup.send(
                    constants.ERROR_GETTING_CLAN_AFTER_CREATE, ephemeral=True
                )

            # Añadir todos los demás miembros al clan (el líder ya se añadió automáticamente)
            members_added = 0
            for member in members_with_role:
                if member != leader:  # El líder ya está añadido
                    error = await self.service.add_member_to_clan(member.id, clan.id)
                    if not error:
                        members_added += 1

            # Crear embed con resultado
            embed = Embed(
                title="✅ Clan migrado exitosamente",
                description=f"El clan **{rol.name}** ha sido migrado al sistema de base de datos.",
                color=Color.green(),
            )

            embed.add_field(name="👑 Líder", value=leader.mention, inline=True)
            embed.add_field(
                name="👥 Miembros totales", value=str(len(members_with_role)), inline=True
            )
            embed.add_field(
                name="🔧 Miembros añadidos", value=str(members_added + 1), inline=True
            )  # +1 por el líder
            embed.add_field(name="🎭 Rol", value=rol.mention, inline=True)
            embed.add_field(name="💬 Canal texto", value=canal_texto.mention, inline=True)
            embed.add_field(name="🔊 Canal voz", value=canal_voz.mention, inline=True)

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error en migración de clan: {str(e)}")
            await interaction.followup.send(
                constants.ERROR_UNEXPECTED_MIGRATION.format(error=str(e)), ephemeral=True
            )

    @mod.command(
        name="usuario", description="Ver los clanes a los que pertenece un usuario y si es líder"
    )
    @app_commands.describe(
        usuario="Usuario a consultar",
        persistente="Si la respuesta debe ser visible para todos (opcional, por defecto falso)",
    )
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def mod_user_clans(
        self, interaction: Interaction, usuario: Member, persistente: Optional[bool] = False
    ):
        ephemeral = not persistente
        await interaction.response.defer(ephemeral=ephemeral)
        clans, error = await self.service.get_member_clans(usuario.id)
        if error or not clans:
            return await interaction.followup.send(
                f"{usuario.mention} no pertenece a ningún clan.", ephemeral=ephemeral
            )

        # Buscar si es líder en cada clan y desde cuándo
        embed = Embed(
            title=f"Clanes de {usuario.display_name}",
            color=Color.purple(),
            timestamp=datetime.now(),
        )
        embed.set_author(
            name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)
        for clan in clans:
            # Buscar info de miembro en el clan
            sql = "SELECT * FROM clan_members WHERE user_id = ? AND clan_id = ?"
            member_row = self.service.db.single(sql, (usuario.id, clan.id))
            if not member_row:
                continue
            rol = member_row["role"]
            joined = member_row["joined_at"]
            try:
                fecha = datetime.fromisoformat(joined) if isinstance(joined, str) else joined
                fecha_str = fecha.strftime('%d/%m/%Y')
            except Exception:
                fecha_str = str(joined)
            es_lider = rol == ClanMemberRole.LEADER.value
            nombre_rol = "👑 Líder" if es_lider else "👤 Miembro"
            embed.add_field(
                name=f"{clan.name}", value=f"{nombre_rol}\nDesde: {fecha_str}", inline=False
            )
        await interaction.followup.send(embed=embed, ephemeral=ephemeral)

    @mod.command(name="estadisticas", description="Ver estadísticas generales de los clanes")
    @app_commands.describe(
        persistente="Si la respuesta debe ser visible para todos (opcional, por defecto falso)"
    )
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def clan_stats(self, interaction: Interaction, persistente: Optional[bool] = False):
        ephemeral = not persistente  # Si persistente=True, ephemeral=False
        clans, error = await self.service.get_all_clans()
        if error or not clans:
            return await interaction.response.send_message(
                error or constants.ERROR_NO_CLANS_STATS, ephemeral=ephemeral
            )

        # Calcular estadísticas
        total_clans = len(clans)
        total_members = sum(len(clan.members) for clan in clans)
        total_leaders = sum(
            len([m for m in clan.members if m.role == ClanMemberRole.LEADER.value])
            for clan in clans
        )
        total_channels = sum(len(clan.channels) for clan in clans)

        # Clan con más miembros
        largest_clan = max(clans, key=lambda c: len(c.members))

        # Crear embed con estadísticas
        embed = Embed(
            title=constants.EMBED_CLAN_STATS_TITLE,
            color=Color.blue(),
            description=constants.EMBED_CLAN_STATS_DESCRIPTION,
        )

        embed.add_field(
            name=constants.FIELD_GENERAL_NUMBERS,
            value=constants.STATS_GENERAL_FORMAT.format(
                total_clans=total_clans,
                total_members=total_members,
                total_leaders=total_leaders,
                total_channels=total_channels,
            ),
            inline=True,
        )

        embed.add_field(
            name=constants.FIELD_LARGEST_CLAN,
            value=constants.STATS_LARGEST_CLAN_FORMAT.format(
                clan_name=largest_clan.name,
                member_count=len(largest_clan.members),
                channel_count=len(largest_clan.channels),
            ),
            inline=True,
        )

        embed.add_field(
            name=constants.FIELD_AVERAGES,
            value=constants.STATS_AVERAGES_FORMAT.format(
                avg_members=total_members / total_clans, avg_channels=total_channels / total_clans
            ),
            inline=True,
        )

        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    ### ? Ver miembros de cualquier clan (para moderadores) ###
    @mod.command(name="miembros", description="Ver la lista de miembros de cualquier clan")
    @app_commands.describe(
        id_clan="ID del clan (opcional - si no se pone se muestra una lista para elegir)",
        persistente="Si la respuesta debe ser visible para todos (opcional, por defecto falso)",
    )
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def mod_list_members(
        self,
        interaction: Interaction,
        id_clan: Optional[str] = None,
        persistente: Optional[bool] = False,
    ):
        ephemeral = not persistente  # Si persistente=True, ephemeral=False
        await interaction.response.defer(ephemeral=True)  # Siempre defer ephemeral para el selector

        clan = None

        # Si se especifica ID de clan, usar ese directamente
        if id_clan:
            clan, error = await self.service.get_clan_by_id(id_clan)
            if error or not clan:
                return await interaction.followup.send(
                    error or constants.ERROR_CLAN_NOT_FOUND, ephemeral=True
                )
        else:
            # Si no se especifica ID, mostrar lista para elegir
            clans, error = await self.service.get_all_clans()
            if error or not clans or len(clans) == 0:
                return await interaction.followup.send(
                    error or constants.ERROR_NO_CLANS_AVAILABLE, ephemeral=True
                )

            if len(clans) == 1:
                clan = clans[0]
            else:
                # Mostrar selector de clanes
                view = ClanSelectorView(clans, "view_members", ephemeral=ephemeral)
                embed = Embed(
                    title=constants.TITLE_SELECT_CLAN_VIEW_MEMBERS,
                    description=constants.DESCRIPTION_SELECT_CLAN_VIEW_MEMBERS,
                    color=Color.blue(),
                )
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                view.message = await interaction.original_response()
                return

        # Si llegamos aquí, tenemos un clan específico
        if not clan.members:
            return await interaction.followup.send(
                constants.ERROR_CLAN_NO_MEMBERS, ephemeral=ephemeral
            )

        # Separar líderes y miembros (reutilizar la misma lógica)
        leaders = [m for m in clan.members if m.role == ClanMemberRole.LEADER.value]
        members = [m for m in clan.members if m.role == ClanMemberRole.MEMBER.value]

        # Preparar listas con un máximo de elementos por embed
        MAX_MEMBERS_PER_PAGE = 15  # Límite conservador para evitar problemas

        async def create_member_pages(member_list, role_type):
            pages = []
            for i in range(0, len(member_list), MAX_MEMBERS_PER_PAGE):
                chunk = member_list[i : i + MAX_MEMBERS_PER_PAGE]
                member_strings = []

                for member in chunk:
                    try:
                        user = await interaction.client.fetch_user(member.user_id)
                        if user:
                            if role_type == "leader":
                                member_strings.append(f"👑 {user.mention}")
                            else:
                                member_strings.append(f"👤 {user.mention}")
                        else:
                            # Si no podemos obtener el usuario, usar solo la mención
                            if role_type == "leader":
                                member_strings.append(f"👑 <@{member.user_id}>")
                            else:
                                member_strings.append(f"👤 <@{member.user_id}>")
                    except Exception:
                        # En caso de error, usar solo la mención
                        if role_type == "leader":
                            member_strings.append(f"👑 <@{member.user_id}>")
                        else:
                            member_strings.append(f"👤 <@{member.user_id}>")

                pages.append(member_strings)
            return pages

        # Crear páginas
        leader_pages = await create_member_pages(leaders, "leader") if leaders else []
        member_pages = await create_member_pages(members, "member") if members else []

        # Si todo cabe en una página, usar un solo embed
        if len(leaders) <= MAX_MEMBERS_PER_PAGE and len(members) <= MAX_MEMBERS_PER_PAGE:
            embed = Embed(
                title=constants.EMBED_CLAN_MEMBERS_TITLE.format(clan_name=clan.name),
                color=Color.green(),
                description=constants.EMBED_CLAN_MEMBERS_DESCRIPTION.format(
                    member_count=len(clan.members)
                ),
            )

            if leader_pages:
                embed.add_field(
                    name=constants.FIELD_LEADERS,
                    value="\n".join(leader_pages[0]) if leader_pages[0] else "Ninguno",
                    inline=False,
                )

            if member_pages:
                embed.add_field(
                    name=constants.FIELD_MEMBERS,
                    value="\n".join(member_pages[0]) if member_pages[0] else "Ninguno",
                    inline=False,
                )

            return await interaction.followup.send(embed=embed, ephemeral=ephemeral)

        # Si necesitamos múltiples páginas
        embeds = []
        max_pages = max(len(leader_pages), len(member_pages))

        for page_num in range(max_pages):
            embed = Embed(
                title=constants.EMBED_CLAN_MEMBERS_TITLE.format(clan_name=clan.name),
                color=Color.green(),
                description=constants.EMBED_CLAN_MEMBERS_DESCRIPTION.format(
                    member_count=len(clan.members)
                ),
            )

            # Añadir información de página
            embed.set_footer(text=f"Página {page_num + 1} de {max_pages}")

            # Añadir líderes si hay en esta página
            if page_num < len(leader_pages):
                field_name = constants.FIELD_LEADERS
                if len(leader_pages) > 1:
                    field_name += f" (Página {page_num + 1})"

                embed.add_field(
                    name=field_name, value="\n".join(leader_pages[page_num]), inline=False
                )

            # Añadir miembros si hay en esta página
            if page_num < len(member_pages):
                field_name = constants.FIELD_MEMBERS
                if len(member_pages) > 1:
                    field_name += f" (Página {page_num + 1})"

                embed.add_field(
                    name=field_name, value="\n".join(member_pages[page_num]), inline=False
                )

            embeds.append(embed)

        # Enviar con paginación
        await send_paginated_embeds(interaction=interaction, embeds=embeds, ephemeral=ephemeral)

    #####################################
    ### Comandos para líderes de clan ###
    #####################################
    @app_commands.command(name="invitar")
    @app_commands.describe(miembro="Miembro a invitar al clan")
    async def invite_to_clan(self, interaction: Interaction, miembro: Member):
        clan, error = await self.service.get_clan_by_channel_id(interaction.channel.id)
        if error or not clan:
            return await interaction.response.send_message(
                constants.ERROR_CHANNEL_NOT_CLAN, ephemeral=True
            )

        is_leader, error = await self.service.is_clan_leader(interaction.user.id, clan.id)
        if error or not is_leader:
            return await interaction.response.send_message(
                constants.ERROR_NO_INVITE_PERMISSIONS, ephemeral=True
            )

        settings_service = ClanSettingsService()
        settings, _ = await settings_service.get_settings()
        user_clans, _ = await self.service.get_member_clans(miembro.id)
        if user_clans and len(user_clans) > 0 and not settings.allow_multiple_clans:
            return await interaction.response.send_message(
                constants.ERROR_USER_ALREADY_IN_CLAN, ephemeral=True
            )

        channel_message = await interaction.response.send_message(
            constants.SUCCESS_INVITATION_SENT.format(member=miembro.mention), ephemeral=True
        )
        channel_message = await interaction.original_response()

        view = ClanInviteView(clan, interaction.guild, self.service, channel_message)
        invite_message = await miembro.send(
            constants.MESSAGE_CLAN_INVITATION.format(clan_name=clan.name), view=view
        )
        view.message = invite_message

    @app_commands.command(name="expulsar")
    @app_commands.describe(miembro="Miembro a expulsar del clan")
    async def kick_from_clan(self, interaction: Interaction, miembro: Member):
        # Si el comando se ejecuta desde un canal de clan, usar ese clan
        clan, error = await self.service.get_clan_by_channel_id(interaction.channel.id)
        if clan:
            # Verificar que es líder del clan
            is_leader, error = await self.service.is_clan_leader(interaction.user.id, clan.id)
            if error or not is_leader:
                return await interaction.response.send_message(
                    constants.ERROR_NO_KICK_PERMISSIONS, ephemeral=True
                )

            # Verificar que el miembro está en el clan consultando la BD directamente
            member_clans, _ = await self.service.get_member_clans(miembro.id)
            is_member = member_clans and any(c.id == clan.id for c in member_clans)
            if not is_member:
                return await interaction.response.send_message(
                    constants.ERROR_USER_NOT_CLAN_MEMBER.format(member=miembro.mention),
                    ephemeral=True,
                )

            # No permitir auto-expulsión
            if miembro.id == interaction.user.id:
                return await interaction.response.send_message(
                    constants.MESSAGE_USE_CLAN_LEAVE, ephemeral=True
                )

            # Expulsar directamente usando la lógica completa
            error = await logica_expulsar_del_clan(miembro.id, clan.id, interaction.guild)
            if error:
                return await interaction.response.send_message(
                    constants.ERROR_KICKING_MEMBER.format(error=error), ephemeral=True
                )

            return await interaction.response.send_message(
                constants.SUCCESS_MEMBER_KICKED.format(member=miembro.mention, clan_name=clan.name),
                ephemeral=True,
            )

        # Si no se ejecuta desde un canal de clan, mostrar selector (solo si es líder de múltiples clanes)
        clans, error = await self.service.get_member_clans(interaction.user.id)
        if error or not clans:
            return await interaction.response.send_message(
                "No tienes permisos para gestionar ningún clan.", ephemeral=True
            )

        # Filtrar solo los clanes donde es líder
        leader_clans = []
        for clan in clans:
            is_leader, _ = await self.service.is_clan_leader(interaction.user.id, clan.id)
            if is_leader:
                leader_clans.append(clan)

        if not leader_clans:
            return await interaction.response.send_message(
                "No eres líder de ningún clan.", ephemeral=True
            )

        if len(leader_clans) == 1:
            # Si solo es líder de un clan, expulsar directamente
            clan = leader_clans[0]

            # Verificar que el miembro está en el clan consultando la BD directamente
            member_clans, _ = await self.service.get_member_clans(miembro.id)
            is_member = member_clans and any(c.id == clan.id for c in member_clans)
            if not is_member:
                return await interaction.response.send_message(
                    f"{miembro.mention} no es miembro del clan **{clan.name}**.", ephemeral=True
                )

            # No permitir auto-expulsión
            if miembro.id == interaction.user.id:
                return await interaction.response.send_message(
                    "No puedes expulsarte a ti mismo. Usa el comando `/clan salir` en su lugar.",
                    ephemeral=True,
                )

            # Expulsar directamente
            error = await logica_expulsar_del_clan(miembro.id, clan.id, interaction.guild)
            if error:
                return await interaction.response.send_message(
                    f"Error al expulsar al miembro: {error}", ephemeral=True
                )

            return await interaction.response.send_message(
                f"{miembro.mention} ha sido expulsado del clan **{clan.name}** exitosamente.",
                ephemeral=True,
            )

        # Si es líder de múltiples clanes, mostrar selector (funcionalidad futura)
        return await interaction.response.send_message(
            "Ejecuta este comando desde el canal del clan específico del que quieres expulsar al miembro.",
            ephemeral=True,
        )

    @app_commands.command(name="miembros", description="Ver la lista de miembros del clan")
    @app_commands.describe(
        persistente="Si la respuesta debe ser visible para todos (opcional, por defecto falso)"
    )
    async def list_members(self, interaction: Interaction, persistente: Optional[bool] = False):
        ephemeral = not persistente  # Si persistente=True, ephemeral=False
        await interaction.response.defer(ephemeral=ephemeral)

        clan, error = await self.service.get_clan_by_channel_id(interaction.channel.id)
        if error or not clan:
            return await interaction.followup.send(
                constants.ERROR_CHANNEL_NOT_CLAN, ephemeral=ephemeral
            )

        # Verificar que es líder del clan
        is_leader, error = await self.service.is_clan_leader(interaction.user.id, clan.id)
        if error or not is_leader:
            return await interaction.followup.send(
                constants.ERROR_NO_VIEW_MEMBERS_PERMISSIONS, ephemeral=ephemeral
            )

        if not clan.members:
            return await interaction.followup.send(
                constants.ERROR_CLAN_NO_MEMBERS, ephemeral=ephemeral
            )

        # Separar líderes y miembros
        leaders = [m for m in clan.members if m.role == ClanMemberRole.LEADER.value]
        members = [m for m in clan.members if m.role == ClanMemberRole.MEMBER.value]

        # Preparar listas con un máximo de elementos por embed
        MAX_MEMBERS_PER_PAGE = 15  # Límite conservador para evitar problemas

        def create_member_pages(member_list, role_type):
            pages = []
            for i in range(0, len(member_list), MAX_MEMBERS_PER_PAGE):
                chunk = member_list[i : i + MAX_MEMBERS_PER_PAGE]
                member_strings = []

                for member in chunk:
                    try:
                        user = interaction.client.get_user(member.user_id)
                        if user:
                            if role_type == "leader":
                                member_strings.append(f"👑 {user.mention}")
                            else:
                                member_strings.append(f"👤 {user.mention}")
                        else:
                            # Si no podemos obtener el usuario, usar solo la mención
                            if role_type == "leader":
                                member_strings.append(f"👑 <@{member.user_id}>")
                            else:
                                member_strings.append(f"� <@{member.user_id}>")
                    except Exception:
                        # En caso de error, usar solo la mención
                        if role_type == "leader":
                            member_strings.append(f"👑 <@{member.user_id}>")
                        else:
                            member_strings.append(f"👤 <@{member.user_id}>")

                pages.append(member_strings)
            return pages

        # Crear páginas
        leader_pages = create_member_pages(leaders, "leader") if leaders else []
        member_pages = create_member_pages(members, "member") if members else []

        # Si todo cabe en una página, usar un solo embed
        if len(leaders) <= MAX_MEMBERS_PER_PAGE and len(members) <= MAX_MEMBERS_PER_PAGE:
            embed = Embed(
                title=constants.EMBED_CLAN_MEMBERS_TITLE.format(clan_name=clan.name),
                color=Color.green(),
                description=constants.EMBED_CLAN_MEMBERS_DESCRIPTION.format(
                    member_count=len(clan.members)
                ),
            )

            if leader_pages:
                embed.add_field(
                    name=constants.FIELD_LEADERS,
                    value="\n".join(leader_pages[0]) if leader_pages[0] else "Ninguno",
                    inline=False,
                )

            if member_pages:
                embed.add_field(
                    name=constants.FIELD_MEMBERS,
                    value="\n".join(member_pages[0]) if member_pages[0] else "Ninguno",
                    inline=False,
                )

            return await interaction.followup.send(embed=embed, ephemeral=ephemeral)

        # Si necesitamos múltiples páginas
        embeds = []
        max_pages = max(len(leader_pages), len(member_pages))

        for page_num in range(max_pages):
            embed = Embed(
                title=constants.EMBED_CLAN_MEMBERS_TITLE.format(clan_name=clan.name),
                color=Color.green(),
                description=constants.EMBED_CLAN_MEMBERS_DESCRIPTION.format(
                    member_count=len(clan.members)
                ),
            )

            # Añadir información de página
            embed.set_footer(text=f"Página {page_num + 1} de {max_pages}")

            # Añadir líderes si hay en esta página
            if page_num < len(leader_pages):
                field_name = constants.FIELD_LEADERS
                if len(leader_pages) > 1:
                    field_name += f" (Página {page_num + 1})"

                embed.add_field(
                    name=field_name, value="\n".join(leader_pages[page_num]), inline=False
                )

            # Añadir miembros si hay en esta página
            if page_num < len(member_pages):
                field_name = constants.FIELD_MEMBERS
                if len(member_pages) > 1:
                    field_name += f" (Página {page_num + 1})"

                embed.add_field(
                    name=field_name, value="\n".join(member_pages[page_num]), inline=False
                )

            embeds.append(embed)

        # Enviar con paginación
        await send_paginated_embeds(interaction=interaction, embeds=embeds, ephemeral=ephemeral)

    @app_commands.command(name="info", description="Ver información del clan")
    @app_commands.describe(
        persistente="Si la respuesta debe ser visible para todos (opcional, por defecto falso)"
    )
    async def clan_info(self, interaction: Interaction, persistente: Optional[bool] = False):
        ephemeral = not persistente  # Si persistente=True, ephemeral=False
        await interaction.response.defer(ephemeral=ephemeral)

        try:
            clan, error = await self.service.get_clan_by_channel_id(interaction.channel.id)
            if error or not clan:
                return await interaction.followup.send(
                    constants.ERROR_CHANNEL_NOT_CLAN, ephemeral=ephemeral
                )

            # Obtener líderes de forma segura
            leaders = []
            try:
                leaders = [
                    f'<@{member.user_id}>'
                    for member in clan.members
                    if member.role == ClanMemberRole.LEADER.value
                ]
            except Exception as e:
                logger.error(f"Error obteniendo líderes: {e}")
                leaders = ["Error obteniendo líderes"]

            # Obtener canales de forma segura
            text_channels = []
            voice_channels = []
            try:
                text_channels = [
                    f'<#{channel.channel_id}>'
                    for channel in clan.channels
                    if channel.type == "text"
                ]
                voice_channels = [
                    f'<#{channel.channel_id}>'
                    for channel in clan.channels
                    if channel.type == "voice"
                ]
            except Exception as e:
                logger.error(f"Error obteniendo canales: {e}")
                text_channels = ["Error obteniendo canales"]
                voice_channels = ["Error obteniendo canales"]

            embed = Embed(
                title=constants.EMBED_CLAN_INFO_TITLE.format(clan_name=clan.name),
                color=Color.green(),
                description=f"ID: {clan.id}\n"
                f"Líderes: {', '.join(leaders)}\n"
                f"Miembros: {len(clan.members)}\n"
                f"Límite de miembros: {clan.max_members}\n"
                f"Rol del clan: <@&{clan.role_id}>\n"
                f"Canales de texto: {', '.join(text_channels)} ({len(text_channels)}/{clan.max_text_channels})\n"
                f"Canales de voz: {', '.join(voice_channels)} ({len(voice_channels)}/{clan.max_voice_channels})\n"
                f"Límite de canales de texto: {clan.max_text_channels}\n"
                f"Límite de canales de voz: {clan.max_voice_channels}\n",
            )

            await interaction.followup.send(embed=embed, ephemeral=ephemeral)

        except Exception as e:
            logger.error(f"Error en clan_info: {str(e)}")
            await interaction.followup.send(
                constants.ERROR_UNEXPECTED.format(error=str(e)), ephemeral=ephemeral
            )

    @mod.command(name="añadir_canal", description="Añadir un canal adicional a un clan existente")
    @app_commands.describe(
        tipo="Tipo de canal (texto o voz)",
        id_clan="ID del clan (opcional - si no se pone y el comando se usa en un canal de clan, se usa ese clan)",
    )
    @app_commands.choices(
        tipo=[
            app_commands.Choice(name="Texto", value="text"),
            app_commands.Choice(name="Voz", value="voice"),
        ]
    )
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def add_channel_to_clan(
        self, interaction: Interaction, tipo: str, id_clan: Optional[str] = None
    ):
        await interaction.response.defer(ephemeral=True)

        clan = None

        # Si se especifica ID de clan, usar ese
        if id_clan:
            clan, error = await self.service.get_clan_by_id(id_clan)
            if error or not clan:
                return await interaction.followup.send(
                    error or constants.ERROR_CLAN_NOT_FOUND, ephemeral=True
                )
        else:
            # Si no se especifica ID, intentar detectar el clan del canal actual
            clan_del_canal, _ = await self.service.get_clan_by_channel_id(interaction.channel.id)
            if clan_del_canal:
                clan = clan_del_canal
            else:
                # Si no es un canal de clan, mostrar lista básica
                clans, error = await self.service.get_all_clans()
                if error or not clans or len(clans) == 0:
                    return await interaction.followup.send(
                        error or constants.ERROR_NO_CLANS_AVAILABLE, ephemeral=True
                    )

                if len(clans) == 1:
                    clan = clans[0]
                else:
                    # Usar la nueva view con botones para seleccionar clan
                    view = ClanModSelectionView(clans, "add_channel", tipo=tipo)
                    embed = Embed(
                        title=constants.TITLE_SELECT_CLAN_ADD_CHANNEL,
                        description=constants.DESCRIPTION_SELECT_CLAN_ADD_CHANNEL,
                        color=Color.blue(),
                    )
                    return await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        # Obtener configuración para verificar límites
        settings, error = await self.clan_settings_service.get_settings()
        if error:
            return await interaction.followup.send(
                constants.ERROR_GETTING_SETTINGS.format(error=error), ephemeral=True
            )

        # Verificar límites de canales
        canales_existentes = [c for c in clan.channels if c.type == tipo]
        max_canales = settings.max_text_channels if tipo == "text" else settings.max_voice_channels

        if len(canales_existentes) >= max_canales:
            return await interaction.followup.send(
                constants.ERROR_MAX_CHANNELS_REACHED.format(
                    clan_name=clan.name, type=tipo, max_channels=max_canales
                ),
                ephemeral=True,
            )

        # Obtener el rol del clan para los permisos
        rol_clan = interaction.guild.get_role(clan.role_id)
        if not rol_clan:
            return await interaction.followup.send(
                constants.ERROR_CLAN_ROLE_NOT_FOUND, ephemeral=True
            )

        try:
            # Generar nombre automático para el canal
            nombre = generate_channel_name(clan.name, clan.channels, tipo)

            # Obtener categorías configuradas
            if tipo == "text":
                id_categoria = settings.text_category_id
            else:
                id_categoria = settings.voice_category_id

            categoria = interaction.guild.get_channel(id_categoria) if id_categoria else None

            # Configurar permisos
            permisos = {
                interaction.guild.default_role: PermissionOverwrite(
                    view_channel=False,
                    read_messages=False if tipo == "text" else None,
                    connect=False if tipo == "voice" else None,
                ),
                rol_clan: PermissionOverwrite(
                    view_channel=True,
                    read_messages=True if tipo == "text" else None,
                    send_messages=True if tipo == "text" else None,
                    connect=True if tipo == "voice" else None,
                    speak=True if tipo == "voice" else None,
                ),
            }

            # Crear el canal
            if tipo == "text":
                if categoria:
                    nuevo_canal = await categoria.create_text_channel(
                        name=nombre, overwrites=permisos
                    )
                else:
                    nuevo_canal = await interaction.guild.create_text_channel(
                        name=nombre, overwrites=permisos
                    )
            else:  # voice
                if categoria:
                    nuevo_canal = await categoria.create_voice_channel(
                        name=nombre, overwrites=permisos
                    )
                else:
                    nuevo_canal = await interaction.guild.create_voice_channel(
                        name=nombre, overwrites=permisos
                    )

            # Guardar en la base de datos
            canal_obj = ClanChannel(
                channel_id=nuevo_canal.id,
                name=nuevo_canal.name,
                type=ClanChannelType.TEXT.value if tipo == "text" else ClanChannelType.VOICE.value,
                clan_id=clan.id,
                created_at=datetime.now(),
            )

            error = self.service.save_clan_channel(canal_obj)
            if error:
                # Si hay error al guardar, eliminar el canal creado
                await nuevo_canal.delete()
                return await interaction.followup.send(
                    constants.ERROR_SAVING_CHANNEL.format(error=error), ephemeral=True
                )

            await interaction.followup.send(
                constants.SUCCESS_CHANNEL_ADDED.format(
                    channel_name=nombre,
                    type=tipo,
                    clan_name=clan.name,
                    channel_mention=nuevo_canal.mention,
                ),
                ephemeral=True,
            )

        except Exception as e:
            logger.error(f"Error al crear canal adicional: {str(e)}")
            await interaction.followup.send(
                constants.ERROR_CREATING_ADDITIONAL_CHANNEL.format(error=str(e)), ephemeral=True
            )

    @mod.command(name="añadir_lider", description="Añadir un líder adicional a un clan existente")
    @app_commands.describe(
        miembro="Miembro del clan a promover a líder",
        id_clan="ID del clan (opcional - si no se pone y el comando se usa en un canal de clan, se usa ese clan)",
    )
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def add_leader_to_clan(
        self, interaction: Interaction, miembro: Member, id_clan: Optional[str] = None
    ):
        await interaction.response.defer(ephemeral=True)

        clan = None

        # Si se especifica ID de clan, usar ese
        if id_clan:
            clan, error = await self.service.get_clan_by_id(id_clan)
            if error or not clan:
                return await interaction.followup.send(
                    error or constants.ERROR_CLAN_NOT_FOUND, ephemeral=True
                )
        else:
            # Si no se especifica ID, intentar detectar el clan del canal actual
            clan_del_canal, _ = await self.service.get_clan_by_channel_id(interaction.channel.id)
            if clan_del_canal:
                clan = clan_del_canal
            else:
                # Si no es un canal de clan, mostrar lista básica
                clans, error = await self.service.get_all_clans()
                if error or not clans or len(clans) == 0:
                    return await interaction.followup.send(
                        error or constants.ERROR_NO_CLANS_AVAILABLE, ephemeral=True
                    )

                if len(clans) == 1:
                    clan = clans[0]
                else:
                    # Usar la nueva view con botones para seleccionar clan
                    view = ClanModSelectionView(clans, "add_leader", miembro=miembro)
                    embed = Embed(
                        title=constants.TITLE_SELECT_CLAN_ADD_LEADER,
                        description=constants.DESCRIPTION_SELECT_CLAN_ADD_LEADER.format(
                            member=miembro.mention
                        ),
                        color=Color.gold(),
                    )
                    return await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        # Verificar que el miembro está en el clan
        miembro_en_clan = any(m.user_id == miembro.id for m in clan.members)
        if not miembro_en_clan:
            return await interaction.followup.send(
                constants.ERROR_MEMBER_NOT_IN_CLAN.format(
                    member=miembro.mention, clan_name=clan.name
                ),
                ephemeral=True,
            )

        # Verificar que el miembro no es ya líder
        es_lider = any(
            m.user_id == miembro.id and m.role == ClanMemberRole.LEADER.value for m in clan.members
        )
        if es_lider:
            return await interaction.followup.send(
                constants.ERROR_MEMBER_ALREADY_LEADER.format(
                    member=miembro.mention, clan_name=clan.name
                ),
                ephemeral=True,
            )

        try:
            # Promover a líder en la base de datos
            error = self.service.promote_member_to_leader(miembro.id, clan.id)
            if error:
                return await interaction.followup.send(
                    constants.ERROR_PROMOTING_MEMBER.format(error=error), ephemeral=True
                )

            # Asignar roles de clan al nuevo líder
            success, role_error = await assign_clan_roles_to_leader(
                interaction.guild, miembro, clan.id, self.service
            )

            if success:
                await interaction.followup.send(
                    constants.SUCCESS_MEMBER_PROMOTED.format(
                        member=miembro.mention, clan_name=clan.name
                    ),
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    constants.SUCCESS_MEMBER_PROMOTED_WITH_ROLE_WARNING.format(
                        member=miembro.mention, clan_name=clan.name, role_error=role_error
                    ),
                    ephemeral=True,
                )

        except Exception as e:
            logger.error(f"Error al promover a líder: {str(e)}")
            await interaction.followup.send(
                constants.ERROR_PROMOTING_MEMBER.format(error=str(e)), ephemeral=True
            )

    @mod.command(name="quitar_lider", description="Quitar el liderazgo a un líder del clan")
    @app_commands.describe(
        miembro="Líder del clan a degradar a miembro regular",
        id_clan="ID del clan (opcional - si no se pone y el comando se usa en un canal de clan, se usa ese clan)",
    )
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def remove_leader_from_clan(
        self, interaction: Interaction, miembro: Member, id_clan: Optional[str] = None
    ):
        await interaction.response.defer(ephemeral=True)

        clan = None

        # Si se especifica ID de clan, usar ese
        if id_clan:
            clan, error = await self.service.get_clan_by_id(id_clan)
            if error or not clan:
                return await interaction.followup.send(
                    error or constants.ERROR_CLAN_NOT_FOUND, ephemeral=True
                )
        else:
            # Si no se especifica ID, intentar detectar el clan del canal actual
            clan_del_canal, _ = await self.service.get_clan_by_channel_id(interaction.channel.id)
            if clan_del_canal:
                clan = clan_del_canal
            else:
                # Si no es un canal de clan, mostrar lista básica
                clans, error = await self.service.get_all_clans()
                if error or not clans or len(clans) == 0:
                    return await interaction.followup.send(
                        error or constants.ERROR_NO_CLANS_AVAILABLE, ephemeral=True
                    )

                if len(clans) == 1:
                    clan = clans[0]
                else:
                    # Usar la nueva view con botones para seleccionar clan
                    view = ClanModSelectionView(clans, "remove_leader", miembro=miembro)
                    embed = Embed(
                        title=constants.TITLE_SELECT_CLAN_REMOVE_LEADER,
                        description=constants.DESCRIPTION_SELECT_CLAN_REMOVE_LEADER.format(
                            member=miembro.mention
                        ),
                        color=Color.orange(),
                    )
                    return await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        try:
            # Quitar liderazgo
            success, error_msg = await demote_leader_to_member(
                interaction.guild, miembro, clan.id, self.service
            )

            if success:
                await interaction.followup.send(
                    constants.SUCCESS_LEADER_DEMOTED.format(
                        member=miembro.mention, clan_name=clan.name
                    ),
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    constants.ERROR_DEMOTING_LEADER.format(error=error_msg), ephemeral=True
                )

        except Exception as e:
            logger.error(f"Error al quitar liderazgo: {str(e)}")
            await interaction.followup.send(
                constants.ERROR_DEMOTING_LEADER.format(error=str(e)), ephemeral=True
            )

    @mod.command(name="quitar_canal", description="Eliminar un canal de un clan")
    @app_commands.describe(
        canal="Canal a eliminar (debe ser un canal del clan)",
        id_clan="ID del clan (opcional - si no se pone y el comando se usa en un canal de clan, se usa ese clan)",
    )
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def remove_channel_from_clan(
        self,
        interaction: Interaction,
        canal: Union[TextChannel, VoiceChannel],
        id_clan: Optional[str] = None,
    ):
        await interaction.response.defer(ephemeral=True)

        clan = None

        # Si se especifica ID de clan, usar ese
        if id_clan:
            clan, error = await self.service.get_clan_by_id(id_clan)
            if error or not clan:
                return await interaction.followup.send(
                    error or constants.ERROR_CLAN_NOT_FOUND, ephemeral=True
                )
        else:
            # Si no se especifica ID, intentar detectar el clan del canal actual
            clan_del_canal, _ = await self.service.get_clan_by_channel_id(interaction.channel.id)
            if clan_del_canal:
                clan = clan_del_canal
            else:
                # Si no es un canal de clan, mostrar lista básica
                clans, error = await self.service.get_all_clans()
                if error or not clans or len(clans) == 0:
                    return await interaction.followup.send(
                        error or constants.ERROR_NO_CLANS_AVAILABLE, ephemeral=True
                    )

                if len(clans) == 1:
                    clan = clans[0]
                else:
                    # Usar la nueva view con botones para seleccionar clan
                    view = ClanModSelectionView(clans, "remove_channel", canal=canal)
                    embed = Embed(
                        title=constants.TITLE_SELECT_CLAN_REMOVE_CHANNEL,
                        description=constants.DESCRIPTION_SELECT_CLAN_REMOVE_CHANNEL.format(
                            channel=canal.mention
                        ),
                        color=Color.red(),
                    )
                    return await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        try:
            # Verificar que el canal pertenece al clan
            canal_existe = any(ch.channel_id == canal.id for ch in clan.channels)
            if not canal_existe:
                return await interaction.followup.send(
                    constants.ERROR_CHANNEL_NOT_IN_CLAN.format(
                        channel=canal.mention, clan_name=clan.name
                    ),
                    ephemeral=True,
                )

            # Eliminar canal
            success, error_msg = await remove_clan_channel(interaction.guild, canal.id, clan.id)

            if success:
                await interaction.followup.send(
                    constants.SUCCESS_CHANNEL_DELETED.format(
                        channel_name=canal.name, clan_name=clan.name
                    ),
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    constants.ERROR_DELETING_CHANNEL.format(error=error_msg), ephemeral=True
                )

        except Exception as e:
            logger.error(f"Error al eliminar canal: {str(e)}")
            await interaction.followup.send(
                constants.ERROR_DELETING_CHANNEL.format(error=str(e)), ephemeral=True
            )

    @mod.command(name="añadir", description="Añadir un usuario directamente a un clan")
    @app_commands.describe(usuario="Usuario a añadir al clan")
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def add_member_to_clan(self, interaction: Interaction, usuario: Member):
        await interaction.response.defer(ephemeral=True)

        # Obtener todos los clanes
        clans, error = await self.service.get_all_clans()
        if error or not clans or len(clans) == 0:
            return await interaction.followup.send(
                error or constants.ERROR_NO_CLANS_AVAILABLE, ephemeral=True
            )

        # Verificar si el usuario ya está en algún clan
        settings_service = ClanSettingsService()
        settings, _ = await settings_service.get_settings()
        user_clans, _ = await self.service.get_member_clans(usuario.id)

        if user_clans and not settings.allow_multiple_clans:
            return await interaction.followup.send(
                constants.ERROR_USER_ALREADY_IN_CLAN, ephemeral=True
            )

        # Mostrar selector de clanes
        view = ClanModSelectionView(clans, "add_member", miembro=usuario)
        embed = Embed(
            title=constants.TITLE_SELECT_CLAN_ADD_MEMBER,
            description=constants.DESCRIPTION_SELECT_CLAN_ADD_MEMBER.format(member=usuario.mention),
            color=Color.green(),
        )
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    #######################################
    ### Comandos para miembros del clan ###
    #######################################
    @app_commands.command(name="salir", description="Salir del clan al que perteneces")
    async def leave_clan(self, interaction: Interaction):
        # Primero intentar detectar el clan del canal actual
        clan_del_canal, _ = await self.service.get_clan_by_channel_id(interaction.channel.id)

        if clan_del_canal:
            # Verificar que el usuario está en este clan
            clanes_usuario, error = await self.service.get_member_clans(interaction.user.id)
            if error or not clanes_usuario:
                return await interaction.response.send_message(
                    constants.ERROR_USER_NOT_IN_ANY_CLAN, ephemeral=True
                )

            usuario_en_este_clan = any(c.id == clan_del_canal.id for c in clanes_usuario)
            if usuario_en_este_clan:
                # El usuario está en el clan de este canal, salir directamente
                error = await logica_salir_del_clan(
                    interaction.user.id, clan_del_canal.id, interaction.guild
                )
                if error:
                    return await interaction.response.send_message(
                        constants.ERROR_LEAVING_CLAN.format(error=error), ephemeral=True
                    )
                return await interaction.response.send_message(
                    constants.SUCCESS_LEFT_CLAN_MESSAGE.format(clan_name=clan_del_canal.name),
                    ephemeral=True,
                )

        # Si no se ejecuta desde un canal de clan o el usuario no está en ese clan,
        # obtener todos los clanes del usuario
        clans, error = await self.service.get_member_clans(interaction.user.id)
        if error or not clans or len(clans) == 0:
            return await interaction.response.send_message(
                constants.ERROR_USER_NOT_IN_ANY_CLAN, ephemeral=True
            )

        # Si solo está en un clan, salir directamente
        if len(clans) == 1:
            clan = clans[0]
            error = await logica_salir_del_clan(interaction.user.id, clan.id, interaction.guild)
            if error:
                return await interaction.response.send_message(
                    constants.ERROR_LEAVING_CLAN.format(error=error), ephemeral=True
                )
            return await interaction.response.send_message(
                constants.SUCCESS_LEFT_CLAN_MESSAGE.format(clan_name=clan.name), ephemeral=True
            )

        # Si está en múltiples clanes, mostrar botones para elegir
        view = ClanLeaveView(clans, interaction.user, self.service)
        await interaction.response.send_message(
            constants.MESSAGE_SELECT_CLAN_TO_LEAVE, view=view, ephemeral=True
        )
        view.message = await interaction.original_response()

    @mod.command(name="configurar", description="[MOD] Configurar límites específicos de un clan")
    @app_commands.describe(
        max_miembros="Máximo número de miembros (opcional)",
        max_canales_texto="Máximo número de canales de texto (opcional)",
        max_canales_voz="Máximo número de canales de voz (opcional)",
    )
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def configurar_clan(
        self,
        interaction: Interaction,
        max_miembros: Optional[int] = None,
        max_canales_texto: Optional[int] = None,
        max_canales_voz: Optional[int] = None,
    ):
        """Configurar límites específicos de un clan"""
        # Verificar permisos de moderador
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                constants.ERROR_NO_PERMISSIONS_CONFIG, ephemeral=True
            )

        # Validar que se proporcione al menos un parámetro
        if all(param is None for param in [max_miembros, max_canales_texto, max_canales_voz]):
            return await interaction.response.send_message(
                constants.ERROR_NO_PARAMS_PROVIDED, ephemeral=True
            )

        # Validar valores positivos
        for param_name, param_value in [
            ("max_miembros", max_miembros),
            ("max_canales_texto", max_canales_texto),
            ("max_canales_voz", max_canales_voz),
        ]:
            if param_value is not None and param_value < 1:
                return await interaction.response.send_message(
                    constants.ERROR_PARAM_MUST_BE_POSITIVE.format(param_name=param_name),
                    ephemeral=True,
                )

        await interaction.response.defer(ephemeral=True)

        # Obtener todos los clanes
        clans, error = await self.service.get_all_clans()
        if error:
            return await interaction.followup.send(
                constants.ERROR_GETTING_CLANS_CONFIG.format(error=error), ephemeral=True
            )

        if not clans:
            return await interaction.followup.send(
                constants.ERROR_NO_CLANS_TO_CONFIGURE, ephemeral=True
            )

        # Mostrar vista de selección de clan
        view = ClanConfigSelectionView(
            clans,
            self.service,
            max_miembros=max_miembros,
            max_canales_texto=max_canales_texto,
            max_canales_voz=max_canales_voz,
        )
        await interaction.followup.send(
            constants.MESSAGE_CONFIGURE_CLAN_TITLE, view=view, ephemeral=True
        )
        view.message = await interaction.original_response()


async def setup(bot):
    await bot.add_cog(ClanCommands(bot), guild=Object(id=guild_id))
