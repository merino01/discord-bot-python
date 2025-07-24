from typing import Optional
from datetime import datetime
from discord import app_commands, Interaction, Member, Object, Embed, Color
from discord.ext import commands
from discord.app_commands import Group
from settings import guild_id
from modules.core import send_paginated_embeds
from modules.clan_settings import ClanSettingsService
from .models import Clan, ClanMemberRole
from .service import ClanService
from .utils import create_clan_role, create_clan_channels, setup_clan_roles, logica_salir_del_clan, crear_canal_adicional
from .validators import ClanValidator
from .views import ClanSelectView
from .views.clan_invite_buttons import ClanInviteView
from .views.clan_leave_buttons import ClanLeaveView
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

    #######################################
    ### Comandos para miembros del clan ###
    #######################################

    @app_commands.command(name="salir", description="Salir del clan al que perteneces")
    async def leave_clan(self, interaction: Interaction):
        clans, error = await self.service.get_clans_by_user_id(interaction.user.id)
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
        user_clans, _ = await self.service.get_clans_by_user_id(miembro.id)
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
        clans, error = await self.service.get_member_clans(interaction.user.id)
        if error or clans is None:
            return await interaction.response.send_message(
                "No tienes permisos para gestionar ningún clan.", ephemeral=True
            )
        view = ClanSelectView(clans, miembro, self.service, interaction)
        await interaction.response.send_message(
            "Selecciona el clan del que quieres expulsar al miembro.", view=view, ephemeral=True
        )
        view.message = await interaction.original_response()

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
        can_create, error = await self.validator.can_create_clan(nombre, lider)
        if not can_create or error:
            return await interaction.response.send_message(error, ephemeral=True)

        # Obtener la configuración
        settings, error = await self.clan_settings_service.get_settings()
        if error:
            return await interaction.response.send_message(error, ephemeral=True)

        # Crear rol con la configuración
        role, error = await create_clan_role(interaction.guild, nombre)
        if error or not role:
            return await interaction.response.send_message("Error al crear el rol.", ephemeral=True)

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
            await interaction.response.send_message(error, ephemeral=True)
            return

        await interaction.response.send_message(
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
    @app_commands.describe(id_clan="Id del clan")
    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    async def clan_delete(self, interaction: Interaction, id_clan: str):
        clan, error = await self.service.get_clan_by_id(id_clan)
        if error or not clan:
            await interaction.response.send_message(
                error or "Clan no encontrado.", ephemeral=True
            )
            return

        # Quitar el rol de líder solo a los líderes de este clan
        settings, _ = await self.clan_settings_service.get_settings()
        leader_role = None
        if settings and settings.leader_role_id:
            leader_role = interaction.guild.get_role(settings.leader_role_id)
        if leader_role:
            for member in clan.members:
                discord_member = interaction.guild.get_member(member.user_id)
                if discord_member and member.role == ClanMemberRole.LEADER.value and leader_role in discord_member.roles:
                    try:
                        await discord_member.remove_roles(leader_role, reason="Eliminación del clan")
                    except Exception:
                        pass

        # Eliminar el rol del clan
        role = interaction.guild.get_role(clan.role_id)
        if role:
            await role.delete()

        # Eliminar canales
        for channel in clan.channels:
            channel_obj = interaction.guild.get_channel(channel.channel_id)
            if channel_obj:
                await channel_obj.delete()

        # Eliminar clan de la base de datos
        error = await self.service.delete_clan(clan.id)
        if error:
            return await interaction.response.send_message(
                f"No se ha podido eliminar el clan: {error}", ephemeral=True
            )

        await interaction.response.send_message("Clan eliminado con éxito.", ephemeral=True)

    @lider.command(name="crear_canal_texto", description="Crear un canal de texto adicional para el clan")
    @app_commands.describe(nombre="Nombre del canal de texto")
    async def create_text_channel(self, interaction: Interaction, nombre: str):
        _, mensaje = await crear_canal_adicional(interaction, nombre, "text")
        await interaction.response.send_message(mensaje, ephemeral=True)

    @lider.command(name="crear_canal_voz", description="Crear un canal de voz adicional para el clan")
    @app_commands.describe(nombre="Nombre del canal de voz")
    async def create_voice_channel(self, interaction: Interaction, nombre: str):
        _, mensaje = await crear_canal_adicional(interaction, nombre, "voice")
        await interaction.response.send_message(mensaje, ephemeral=True)

    @lider.command(name="transferir_liderazgo", description="Transferir el liderazgo del clan a otro miembro")
    @app_commands.describe(miembro="Miembro al que transferir el liderazgo")
    async def transfer_leadership(self, interaction: Interaction, miembro: Member):
        # Verificar que es un canal de clan
        clan, error = await self.service.get_clan_by_channel_id(interaction.channel.id)
        if error or not clan:
            return await interaction.response.send_message(
                "Este canal no pertenece a ningún clan.", ephemeral=True
            )
        
        # Verificar que es líder del clan
        is_leader, error = await self.service.is_clan_leader(interaction.user.id, clan.id)
        if error or not is_leader:
            return await interaction.response.send_message(
                "No tienes permisos para transferir el liderazgo.", ephemeral=True
            )

        # Verificar que el miembro objetivo está en el clan
        target_member = next((m for m in clan.members if m.user_id == miembro.id), None)
        if not target_member:
            return await interaction.response.send_message(
                "El usuario no pertenece a este clan.", ephemeral=True
            )

        # Verificar que no se está transfiriendo a sí mismo
        if miembro.id == interaction.user.id:
            return await interaction.response.send_message(
                "No puedes transferir el liderazgo a ti mismo.", ephemeral=True
            )

        try:
            # Cambiar roles en la base de datos
            # El miembro objetivo se convierte en líder
            update_leader_sql = "UPDATE clan_members SET role = ? WHERE user_id = ? AND clan_id = ?"
            self.service.db.execute(update_leader_sql, (ClanMemberRole.LEADER.value, miembro.id, clan.id))
            
            # El líder actual se convierte en miembro normal
            update_member_sql = "UPDATE clan_members SET role = ? WHERE user_id = ? AND clan_id = ?"
            self.service.db.execute(update_member_sql, (ClanMemberRole.MEMBER.value, interaction.user.id, clan.id))

            # Actualizar roles de Discord si está configurado
            settings, _ = await self.clan_settings_service.get_settings()
            if settings and settings.leader_role_id:
                leader_role = interaction.guild.get_role(settings.leader_role_id)
                if leader_role:
                    # Quitar rol de líder al usuario actual
                    current_leader = await interaction.guild.fetch_member(interaction.user.id)
                    if current_leader and leader_role in current_leader.roles:
                        await current_leader.remove_roles(leader_role)
                    
                    # Dar rol de líder al nuevo líder
                    new_leader = await interaction.guild.fetch_member(miembro.id)
                    if new_leader:
                        await new_leader.add_roles(leader_role)

            await interaction.response.send_message(
                f"Liderazgo transferido exitosamente a {miembro.mention}.", ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"Error al transferir el liderazgo: {str(e)}", ephemeral=True
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

    @lider.command(name="miembros", description="Ver la lista de miembros del clan")
    async def list_members(self, interaction: Interaction):
        clan, error = await self.service.get_clan_by_channel_id(interaction.channel.id)
        if error or not clan:
            return await interaction.response.send_message(
                "Este canal no pertenece a ningún clan.", ephemeral=True
            )
        
        # Verificar que es líder del clan
        is_leader, error = await self.service.is_clan_leader(interaction.user.id, clan.id)
        if error or not is_leader:
            return await interaction.response.send_message(
                "No tienes permisos para ver la lista de miembros.", ephemeral=True
            )

        if not clan.members:
            return await interaction.response.send_message(
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
                except:
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
                except:
                    members_list.append(f"👤 <@{member.user_id}> (ID: {member.user_id})")
            
            embed.add_field(
                name="👥 Miembros",
                value="\n".join(members_list),
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def on_app_command_error(self, interaction: Interaction, error: Exception):
        import traceback

        traceback.print_exc()
        await interaction.response.send_message(
            "Ha ocurrido un error inesperado al ejecutar el comando. Por favor, contacta con el staff si el problema persiste.",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(ClanCommands(bot), guild=Object(id=guild_id))
