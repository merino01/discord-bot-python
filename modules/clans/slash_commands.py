from typing import Optional
from datetime import datetime
from discord import app_commands, Interaction, Member, Object, Embed, Color, ChannelType, Role, TextChannel, VoiceChannel
from discord.ext import commands
from discord.app_commands import Group
from settings import guild_id
from modules.core import send_paginated_embeds
from modules.clan_settings import ClanSettingsService
from .models import ClanMemberRole
from .service import ClanService
from .utils import create_clan_role, create_clan_channels, setup_clan_roles, logica_salir_del_clan, logica_expulsar_del_clan, crear_canal_adicional, remove_clan_roles_from_member
from .validators import ClanValidator
from .views import ClanSelectView
from .views.clan_invite_buttons import ClanInviteView
from .views.clan_leave_buttons import ClanLeaveView
from .views.clan_delete_buttons import ClanDeleteView
from modules.core import logger


class ClanCommands(commands.GroupCog, name="clan"):
    def __init__(self, bot):
        self.bot = bot
        self.service = ClanService()
        self.validator = ClanValidator()
        self.clan_settings_service = ClanSettingsService()
        super().__init__()

    lider = Group(name="lider", description="Comandos para líderes de clan")
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
            return await interaction.followup.send("Error al crear el rol.", ephemeral=True)

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
            await interaction.followup.send("Error al crear los canales.", ephemeral=True)
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
            f"Clan {nombre} creado con éxito en las categorías "
            f"Texto: <#{settings.text_category_id}> | Voz: <#{settings.voice_category_id}> "
            f"con {settings.max_members} miembros máximo.",
            ephemeral=True,
        )

    ### ? INFO ###
    @mod.command(name="info", description="Información de un clan")
    @app_commands.describe(id_clan="Id del clan")
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def clan_info(self, interaction: Interaction, id_clan: Optional[str] = None):
        clans = []
        if id_clan:
            clan, error = await self.service.get_clan_by_id(id_clan)
            if error or not clan:
                return await interaction.response.send_message(
                    error or "Clan no encontrado.", ephemeral=True
                )
            clans.append(clan)

        else:
            clans, error = await self.service.get_all_clans()
            if error or not clans or len(clans) == 0:
                return await interaction.response.send_message(
                    error or "No hay clanes.", ephemeral=True
                )

        embeds = []
        for clan in clans:
            embed = Embed(
                title=f"Información del clan **{clan.name}**",
                description=f"**Información del clan {clan.name}**.",
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
            embed.add_field(name="ID", value=clan.id, inline=True)
            embed.add_field(name="Nombre", value=clan.name, inline=True)
            leaders = [f"<@{member.user_id}>" for member in clan.members if member.role == "leader"]
            embed.add_field(name="Líderes", value=", ".join(leaders), inline=True)
            embed.add_field(name="Miembros", value=len(clan.members), inline=True)
            embed.add_field(name="Límite de miembros", value=clan.max_members, inline=True)
            embed.add_field(name="Rol", value=f"<@&{clan.role_id}>", inline=True)
            text_channels = [
                f"<#{channel.channel_id}>" for channel in clan.channels if channel.type == "text"
            ]
            voice_channels = [
                f"<#{channel.channel_id}>" for channel in clan.channels if channel.type == "voice"
            ]
            embed.add_field(name="Canales de texto", value=", ".join(text_channels), inline=True)
            embed.add_field(name="Canales de voz", value=", ".join(voice_channels), inline=True)
            embed.add_field(name="Fecha de creación", value=clan.created_at, inline=False)

            embeds.append(embed)
        await send_paginated_embeds(interaction=interaction, embeds=embeds, ephemeral=True)

    ### ? Eliminar clan ###
    @mod.command(name="eliminar", description="Eliminar un clan")
    @app_commands.describe(id_clan="Id del clan (opcional - sin especificar muestra lista para elegir)")
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def clan_delete(self, interaction: Interaction, id_clan: Optional[str] = None):
        await interaction.response.defer(ephemeral=True)
        
        if id_clan:
            # Si se proporciona ID, eliminar directamente
            clan, error = await self.service.get_clan_by_id(id_clan)
            if error or not clan:
                await interaction.followup.send(
                    error or "Clan no encontrado.", ephemeral=True
                )
                return

            # Eliminar clan de la base de datos PRIMERO
            error = await self.service.delete_clan(clan.id)
            if error:
                return await interaction.followup.send(
                    f"No se ha podido eliminar el clan: {error}", ephemeral=True
                )

            # Ahora quitar todos los roles de clan a todos los miembros
            for member in clan.members:
                await remove_clan_roles_from_member(
                    guild=interaction.guild,
                    member_id=member.user_id,
                    clan_role_id=clan.role_id,
                    should_check_other_clans=True
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

            await interaction.followup.send("Clan eliminado con éxito.", ephemeral=True)
        
        else:
            # Si no se proporciona ID, mostrar lista para elegir
            clans, error = await self.service.get_all_clans()
            if error or not clans or len(clans) == 0:
                return await interaction.followup.send(
                    error or "No hay clanes para eliminar.", ephemeral=True
                )
            
            # Crear embed con lista de clanes
            embed = Embed(
                title="🗑️ Seleccionar clan a eliminar",
                description="Selecciona el clan que deseas eliminar. **Esta acción no se puede deshacer.**",
                color=Color.red()
            )
            embed.add_field(
                name="📊 Total de clanes",
                value=f"{len(clans)} clanes disponibles",
                inline=False
            )
            
            view = ClanDeleteView(clans, self.service)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    ### ? Migrar clanes existentes ###
    @mod.command(name="migrar", description="Migrar un clan existente al sistema de base de datos")
    @app_commands.describe(
        rol="Rol del clan a migrar",
        canal_texto="Canal de texto del clan",
        canal_voz="Canal de voz del clan",
        lider="Líder del clan (si no se especifica se toma el primer miembro con el rol)"
    )
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def migrate_clans(
        self, 
        interaction: Interaction, 
        rol: Role,
        canal_texto: TextChannel,
        canal_voz: VoiceChannel,
        lider: Optional[Member] = None
    ):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Verificar si el clan ya existe en la BD
            existing_clans, _ = await self.service.get_all_clans()
            if existing_clans and any(clan.role_id == rol.id for clan in existing_clans):
                return await interaction.followup.send(
                    f"El rol {rol.name} ya está registrado como clan.", ephemeral=True
                )
            
            # Encontrar miembros con el rol
            members_with_role = [member for member in interaction.guild.members if rol in member.roles and not member.bot]
            
            if not members_with_role:
                return await interaction.followup.send(
                    f"No se encontraron miembros con el rol {rol.name}.", ephemeral=True
                )
            
            # Determinar el líder
            if lider:
                if rol not in lider.roles:
                    return await interaction.followup.send(
                        f"El miembro {lider.mention} no tiene el rol {rol.name}.", ephemeral=True
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
                    f"Error al crear clan {rol.name}: {error}", ephemeral=True
                )
            
            # Obtener el clan recién creado
            clan, _ = await self.service.get_clan_by_role_id(rol.id)
            if not clan:
                return await interaction.followup.send(
                    "Error: No se pudo obtener el clan después de crearlo.", ephemeral=True
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
                color=Color.green()
            )
            
            embed.add_field(name="👑 Líder", value=leader.mention, inline=True)
            embed.add_field(name="👥 Miembros totales", value=str(len(members_with_role)), inline=True)
            embed.add_field(name="🔧 Miembros añadidos", value=str(members_added + 1), inline=True)  # +1 por el líder
            embed.add_field(name="🎭 Rol", value=rol.mention, inline=True)
            embed.add_field(name="💬 Canal texto", value=canal_texto.mention, inline=True)
            embed.add_field(name="🔊 Canal voz", value=canal_voz.mention, inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error en migración de clan: {str(e)}")
            await interaction.followup.send(
                f"Error inesperado durante la migración: {str(e)}", ephemeral=True
            )
    @mod.command(name="estadisticas", description="Ver estadísticas generales de los clanes")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def clan_stats(self, interaction: Interaction):
        clans, error = await self.service.get_all_clans()
        if error or not clans:
            return await interaction.response.send_message(
                error or "No hay clanes creados.", ephemeral=True
            )

        # Calcular estadísticas
        total_clans = len(clans)
        total_members = sum(len(clan.members) for clan in clans)
        total_leaders = sum(len([m for m in clan.members if m.role == ClanMemberRole.LEADER.value]) for clan in clans)
        total_channels = sum(len(clan.channels) for clan in clans)
        
        # Clan con más miembros
        largest_clan = max(clans, key=lambda c: len(c.members))
        
        # Crear embed con estadísticas
        embed = Embed(
            title="📊 Estadísticas de Clanes",
            color=Color.blue(),
            description="Resumen general del sistema de clanes"
        )
        
        embed.add_field(
            name="📈 Números Generales",
            value=f"**Clanes totales:** {total_clans}\n"
                  f"**Miembros totales:** {total_members}\n"
                  f"**Líderes totales:** {total_leaders}\n"
                  f"**Canales totales:** {total_channels}",
            inline=True
        )
        
        embed.add_field(
            name="🏆 Clan más Grande",
            value=f"**{largest_clan.name}**\n"
                  f"{len(largest_clan.members)} miembros\n"
                  f"{len(largest_clan.channels)} canales",
            inline=True
        )
        
        embed.add_field(
            name="📊 Promedios",
            value=f"**Miembros por clan:** {total_members / total_clans:.1f}\n"
                  f"**Canales por clan:** {total_channels / total_clans:.1f}",
            inline=True
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


    #####################################
    ### Comandos para líderes de clan ###
    #####################################
    @lider.command(name="invitar")
    @app_commands.describe(miembro="Miembro a invitar al clan")
    async def invite_to_clan(self, interaction: Interaction, miembro: Member):
        clan, error = await self.service.get_clan_by_channel_id(interaction.channel.id)
        if error or not clan:
            return await interaction.response.send_message(
                "Este canal no pertenece a ningún clan.", ephemeral=True
            )
        
        is_leader, error = await self.service.is_clan_leader(interaction.user.id, clan.id)
        if error or not is_leader:
            return await interaction.response.send_message(
                "No tienes permisos para invitar miembros a este clan.", ephemeral=True
            )

        settings_service = ClanSettingsService()
        settings, _ = await settings_service.get_settings()
        user_clans, _ = await self.service.get_member_clans(miembro.id)
        if user_clans and len(user_clans) > 0 and not settings.allow_multiple_clans:
            return await interaction.response.send_message(
                "El usuario ya pertenece a un clan.", ephemeral=True
            )

        channel_message = await interaction.response.send_message(
            f"Invitación enviada a {miembro.mention}.", ephemeral=True
        )
        channel_message = await interaction.original_response()

        view = ClanInviteView(clan, interaction.guild, self.service, channel_message)
        invite_message = await miembro.send(
            f"Has sido invitado a unirte al clan **{clan.name}**.", view=view
        )
        view.message = invite_message

    @lider.command(name="expulsar")
    @app_commands.describe(miembro="Miembro a expulsar del clan")
    async def kick_from_clan(self, interaction: Interaction, miembro: Member):
        # Si el comando se ejecuta desde un canal de clan, usar ese clan
        clan, error = await self.service.get_clan_by_channel_id(interaction.channel.id)
        if clan:
            # Verificar que es líder del clan
            is_leader, error = await self.service.is_clan_leader(interaction.user.id, clan.id)
            if error or not is_leader:
                return await interaction.response.send_message(
                    "No tienes permisos para expulsar miembros de este clan.", ephemeral=True
                )
            
            # Verificar que el miembro está en el clan consultando la BD directamente
            member_clans, _ = await self.service.get_member_clans(miembro.id)
            is_member = member_clans and any(c.id == clan.id for c in member_clans)
            if not is_member:
                return await interaction.response.send_message(
                    f"{miembro.mention} no es miembro de este clan.", ephemeral=True
                )
            
            # No permitir auto-expulsión
            if miembro.id == interaction.user.id:
                return await interaction.response.send_message(
                    "No puedes expulsarte a ti mismo. Usa el comando `/clan salir` en su lugar.", ephemeral=True
                )
            
            # Expulsar directamente usando la lógica completa
            error = await logica_expulsar_del_clan(miembro.id, clan.id, interaction.guild)
            if error:
                return await interaction.response.send_message(
                    f"Error al expulsar al miembro: {error}", ephemeral=True
                )
            
            return await interaction.response.send_message(
                f"{miembro.mention} ha sido expulsado del clan **{clan.name}** exitosamente.", ephemeral=True
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
                    "No puedes expulsarte a ti mismo. Usa el comando `/clan salir` en su lugar.", ephemeral=True
                )
            
            # Expulsar directamente
            error = await logica_expulsar_del_clan(miembro.id, clan.id, interaction.guild)
            if error:
                return await interaction.response.send_message(
                    f"Error al expulsar al miembro: {error}", ephemeral=True
                )
            
            return await interaction.response.send_message(
                f"{miembro.mention} ha sido expulsado del clan **{clan.name}** exitosamente.", ephemeral=True
            )
        
        # Si es líder de múltiples clanes, mostrar selector (funcionalidad futura)
        return await interaction.response.send_message(
            "Ejecuta este comando desde el canal del clan específico del que quieres expulsar al miembro.", 
            ephemeral=True
        )

    @lider.command(name="miembros", description="Ver la lista de miembros del clan")
    async def list_members(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        
        clan, error = await self.service.get_clan_by_channel_id(interaction.channel.id)
        if error or not clan:
            return await interaction.followup.send(
                "Este canal no pertenece a ningún clan.", ephemeral=True
            )
        
        # Verificar que es líder del clan
        is_leader, error = await self.service.is_clan_leader(interaction.user.id, clan.id)
        if error or not is_leader:
            return await interaction.followup.send(
                "No tienes permisos para ver la lista de miembros.", ephemeral=True
            )

        if not clan.members:
            return await interaction.followup.send(
                "El clan no tiene miembros.", ephemeral=True
            )

        # Separar líderes y miembros
        leaders = [m for m in clan.members if m.role == ClanMemberRole.LEADER.value]
        members = [m for m in clan.members if m.role == ClanMemberRole.MEMBER.value]

        embed = Embed(
            title=f"👥 Miembros de {clan.name}",
            color=Color.green(),
            description=f"Total: {len(clan.members)} miembros"
        )

        if leaders:
            leaders_list = []
            for leader in leaders:
                try:
                    user = await interaction.client.fetch_user(leader.user_id)
                    leaders_list.append(f"👑 {user.mention} ({user.name})")
                except Exception:
                    leaders_list.append(f"👑 <@{leader.user_id}> (ID: {leader.user_id})")
            
            embed.add_field(
                name="🏆 Líderes",
                value="\n".join(leaders_list),
                inline=False
            )

        if members:
            members_list = []
            for member in members:
                try:
                    user = await interaction.client.fetch_user(member.user_id)
                    members_list.append(f"👤 {user.mention} ({user.name})")
                except Exception:
                    members_list.append(f"👤 <@{member.user_id}> (ID: {member.user_id})")
            
            embed.add_field(
                name="👥 Miembros",
                value="\n".join(members_list),
                inline=False
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @lider.command(name="info", description="Ver información del clan")
    async def clan_info(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            logger.info(f"Obteniendo clan para canal {interaction.channel.id}")
            clan, error = await self.service.get_clan_by_channel_id(interaction.channel.id)
            logger.info(f"Clan obtenido: {clan is not None}, error: {error}")
            
            if error or not clan:
                return await interaction.followup.send(
                    "Este canal no pertenece a ningún clan.", ephemeral=True
                )

            logger.info(f"Creando embed para clan {clan.name}")
            
            # Obtener líderes de forma segura
            leaders = []
            try:
                leaders = [f'<@{member.user_id}>' for member in clan.members if member.role == ClanMemberRole.LEADER.value]
            except Exception as e:
                logger.error(f"Error obteniendo líderes: {e}")
                leaders = ["Error obteniendo líderes"]
            
            # Obtener canales de forma segura
            text_channels = []
            voice_channels = []
            try:
                text_channels = [f'<#{channel.channel_id}>' for channel in clan.channels if channel.type == "text"]
                voice_channels = [f'<#{channel.channel_id}>' for channel in clan.channels if channel.type == "voice"]
            except Exception as e:
                logger.error(f"Error obteniendo canales: {e}")
                text_channels = ["Error obteniendo canales"]
                voice_channels = ["Error obteniendo canales"]
            
            embed = Embed(
                title=f"Información del clan: {clan.name}",
                color=Color.green(),
                description=f"ID: {clan.id}\n"
                            f"Líderes: {', '.join(leaders)}\n"
                            f"Miembros: {len(clan.members)}\n"
                            f"Límite de miembros: {clan.max_members}\n"
                            f"Rol del clan: <@&{clan.role_id}>\n"
                            f"Canales de texto: {', '.join(text_channels)}\n"
                            f"Canales de voz: {', '.join(voice_channels)}\n"
            )

            logger.info("Enviando respuesta...")
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info("Respuesta enviada correctamente")
            
        except Exception as e:
            logger.error(f"Error en clan_info: {str(e)}")
            await interaction.followup.send(f"Error inesperado: {str(e)}", ephemeral=True)

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
                    "No perteneces a ningún clan.", ephemeral=True
                )
            
            usuario_en_este_clan = any(c.id == clan_del_canal.id for c in clanes_usuario)
            if usuario_en_este_clan:
                # El usuario está en el clan de este canal, salir directamente
                error = await logica_salir_del_clan(interaction.user.id, clan_del_canal.id, interaction.guild)
                if error:
                    return await interaction.response.send_message(
                        f"Error al salir del clan: {error}", ephemeral=True
                    )
                return await interaction.response.send_message(
                    f"Has salido del clan **{clan_del_canal.name}** exitosamente.", ephemeral=True
                )
        
        # Si no se ejecuta desde un canal de clan o el usuario no está en ese clan,
        # obtener todos los clanes del usuario
        clans, error = await self.service.get_member_clans(interaction.user.id)
        if error or not clans or len(clans) == 0:
            return await interaction.response.send_message(
                "No perteneces a ningún clan.", ephemeral=True
            )
        
        # Si solo está en un clan, salir directamente
        if len(clans) == 1:
            clan = clans[0]
            error = await logica_salir_del_clan(interaction.user.id, clan.id, interaction.guild)
            if error:
                return await interaction.response.send_message(
                    f"Error al salir del clan: {error}", ephemeral=True
                )
            return await interaction.response.send_message(
                f"Has salido del clan **{clan.name}** exitosamente.", ephemeral=True
            )
        
        # Si está en múltiples clanes, mostrar botones para elegir
        view = ClanLeaveView(clans, interaction.user, self.service)
        await interaction.response.send_message(
            "Selecciona el clan del que quieres salir:", view=view, ephemeral=True
        )
        view.message = await interaction.original_response()



async def setup(bot):
    await bot.add_cog(ClanCommands(bot), guild=Object(id=guild_id))
