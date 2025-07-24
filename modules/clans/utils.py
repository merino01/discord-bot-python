from typing import Optional, Tuple, Mapping, Union
from discord import (
    Guild,
    Role,
    Member,
    Object,
    TextChannel,
    VoiceChannel,
    CategoryChannel,
    Color,
    PermissionOverwrite,
    Forbidden,
    HTTPException,
    Interaction,
)
from modules.clan_settings.service import ClanSettingsService
from modules.core import logger
from .service import ClanService
from .models import Clan


async def create_clan_role(guild: Guild, name: str) -> Tuple[Optional[Role], Optional[str]]:
    try:
        settings_service = ClanSettingsService()
        settings, error = await settings_service.get_settings()
        if error:
            return None, error

        role = await guild.create_role(
            name=name, color=Color.from_str(f"#{settings.default_role_color}")
        )
        return role, None
    except Forbidden as forbidden:
        logger.error(f"Error al crear rol del clan: {forbidden.text}")
        return None, "No tengo permisos para crear el rol del clan"
    except HTTPException as http_exception:
        logger.error("Error al crear rol del clan: %s", http_exception.text)
        return None, "Ha habido un error al crear el rol del clan"
    except TypeError as type_error:
        logger.error("Error al crear rol del clan: %s", type_error)
        return None, "Ha habido un error al crear el rol del clan"


async def create_clan_channels(
    guild: Guild, name: str, role: Role
) -> Tuple[Optional[TextChannel], Optional[VoiceChannel], Optional[str]]:
    try:
        settings_service = ClanSettingsService()
        settings, error = await settings_service.get_settings()
        if error:
            return None, None, error

        # Obtener categorías configuradas
        text_category = (
            guild.get_channel(settings.text_category_id) if settings.text_category_id else None
        )
        voice_category = (
            guild.get_channel(settings.voice_category_id) if settings.voice_category_id else None
        )

        # Permisos
        overwrites: Mapping[Union[Role, Member, Object], PermissionOverwrite] = {
            guild.default_role: PermissionOverwrite(read_messages=False, connect=False),
            role: PermissionOverwrite(read_messages=True, connect=True),
        }

        # Crear canal de texto
        if text_category and isinstance(text_category, CategoryChannel):
            text_channel = await text_category.create_text_channel(name=name, overwrites=overwrites)
        else:
            text_channel = await guild.create_text_channel(name=name, overwrites=overwrites)

        # Crear canal de voz
        if voice_category and isinstance(voice_category, CategoryChannel):
            voice_channel = await voice_category.create_voice_channel(
                name=name, overwrites=overwrites
            )
        else:
            voice_channel = await guild.create_voice_channel(name=name, overwrites=overwrites)

        return text_channel, voice_channel, None
    except Forbidden as forbidden:
        logger.error("Error al crear canales del clan: %s", forbidden.text)
        return None, None, "No tengo permisos para crear los canales del clan"
    except HTTPException as http_exception:
        logger.error("Error al crear canales del clan: %s", http_exception.text)
        return None, None, "Ha habido un error al crear los canales del clan"
    except TypeError as type_error:
        logger.error("Error al crear canales del clan: %s", type_error)
        return None, None, "Ha habido un error al crear los canales del clan"


async def setup_clan_roles(guild: Guild, member: Member, role: Role) -> Optional[str]:
    try:
        settings_service = ClanSettingsService()
        settings, error = await settings_service.get_settings()
        if error:
            return error

        # Añadir rol del clan
        await member.add_roles(role)

        # Añadir rol de líder si está configurado
        if settings.leader_role_id:
            if leader_role := guild.get_role(settings.leader_role_id):
                await member.add_roles(leader_role)

        # Añadir roles adicionales configurados
        for role_id in settings.additional_roles:
            if additional_role := guild.get_role(role_id):
                await member.add_roles(additional_role)

        return None
    except Forbidden as forbbiden:
        logger.error("Error al configurar roles del clan: %s", forbbiden.text)
        return f"No tengo permisos para añadir el role {role.id} al usuario {member.id}"
    except HTTPException as http_exception:
        logger.error("Error al configurar roles del clan: %s", http_exception.text)
        return f"Ha habido un error al añadir el rol {role.id} al usuario {member.id}"


async def is_in_clan(member_id: int) -> bool:
    service = ClanService()
    clans, _ = await service.get_clans_by_user_id(member_id)
    return clans is not None and len(clans) > 0


async def is_clan_leader(member_id: int) -> bool:
    service = ClanService()
    clan, error = await service.get_leader_clan(member_id)
    if error or not clan:
        return False
    return True


async def add_member_to_clan(guild: Guild, member_id: int, clan_id: str) -> Optional[str]:
    service = ClanService()
    # Obtener rol del clan
    role, error = await service.get_clan_role(guild, clan_id)
    if error or not role:
        return "Error al obtener el rol del clan"

    member = await guild.fetch_member(member_id)
    if not member:
        return "El miembro no existe"
    if member.bot:
        return "No se puede añadir un bot al clan"
    # Añadir rol al miembro
    await member.add_roles(role)

    # Añadir miembro al clan
    error = await service.add_member_to_clan(member_id, clan_id)
    if error:
        await member.remove_roles(role)
        return "Error al añadir el miembro al clan"

    return None


async def logica_salir_del_clan(id_usuario: int, id_clan: str, guild: Guild) -> Optional[str]:
    """Lógica para que un usuario salga de un clan."""
    try:
        servicio = ClanService()
        
        # Verificar que el usuario está en el clan
        clanes, error = await servicio.get_clans_by_user_id(id_usuario)
        if error or not clanes:
            return "No perteneces a ningún clan"
        
        clan_a_abandonar = next((c for c in clanes if c.id == id_clan), None)
        if not clan_a_abandonar:
            return "No perteneces a este clan"
        
        # No permitir que el líder se salga si es el único líder
        from .models import ClanMemberRole
        lideres = [m for m in clan_a_abandonar.members if m.role == ClanMemberRole.LEADER.value]
        if len(lideres) <= 1:
            es_lider, _ = await servicio.is_clan_leader(id_usuario, id_clan)
            if es_lider:
                return "No puedes salir del clan siendo el único líder. Transfiere el liderazgo primero."
        
        # Eliminar del clan en la base de datos
        error = await servicio.remove_member_from_clan(id_usuario, id_clan)
        if error:
            return f"Error al salir del clan: {error}"
        
        # Quitar rol del clan
        try:
            miembro = await guild.fetch_member(id_usuario)
            rol_clan = await guild.fetch_role(clan_a_abandonar.role_id)
            if miembro and rol_clan:
                await miembro.remove_roles(rol_clan)
        except Exception:
            pass  # Continuar aunque no se pueda quitar el rol
        
        return None
        
    except Exception as e:
        logger.error(f"Error en logica_salir_del_clan: {str(e)}")
        return f"Error inesperado al salir del clan: {str(e)}"


async def crear_canal_adicional(
    interaction, 
    nombre: str, 
    tipo_canal: str
) -> Tuple[bool, str]:
    """
    Lógica común para crear canales adicionales.
    Retorna (éxito, mensaje)
    """
    from datetime import datetime
    from .models import ClanChannel, ChannelType
    
    servicio = ClanService()
    
    try:
        # Verificar que es un canal de clan
        clan, error = await servicio.get_clan_by_channel_id(interaction.channel.id)
        if error or not clan:
            return False, "Este canal no pertenece a ningún clan."
        
        # Verificar que es líder del clan
        es_lider, error = await servicio.is_clan_leader(interaction.user.id, clan.id)
        if error or not es_lider:
            return False, "No tienes permisos para crear canales en este clan."

        # Obtener configuración para verificar límites
        servicio_configuracion = ClanSettingsService()
        configuracion, error = await servicio_configuracion.get_settings()
        if error:
            return False, "Error al obtener la configuración."

        # Contar canales existentes del tipo solicitado
        canales_existentes = [c for c in clan.channels if c.type == tipo_canal]
        max_canales = (configuracion.max_text_channels 
                      if tipo_canal == "text" 
                      else configuracion.max_voice_channels)
        
        if len(canales_existentes) >= max_canales:
            return False, f"El clan ya tiene el máximo de canales de {tipo_canal} ({max_canales})."

        # Obtener el rol del clan para los permisos
        rol_clan = await interaction.guild.fetch_role(clan.role_id)
        if not rol_clan:
            return False, "Error: No se encontró el rol del clan."

        # Obtener categorías configuradas
        if tipo_canal == "text":
            id_categoria = configuracion.text_category_id
        else:
            id_categoria = configuracion.voice_category_id
        
        categoria = interaction.guild.get_channel(id_categoria) if id_categoria else None

        # Configurar permisos
        permisos = {
            interaction.guild.default_role: PermissionOverwrite(
                read_messages=False if tipo_canal == "text" else None,
                connect=False if tipo_canal == "voice" else None
            ),
            rol_clan: PermissionOverwrite(
                read_messages=True if tipo_canal == "text" else None,
                connect=True if tipo_canal == "voice" else None
            ),
        }

        # Crear el canal
        if tipo_canal == "text":
            if categoria:
                nuevo_canal = await categoria.create_text_channel(name=nombre, overwrites=permisos)
            else:
                nuevo_canal = await interaction.guild.create_text_channel(name=nombre, overwrites=permisos)
        else:  # voice
            if categoria:
                nuevo_canal = await categoria.create_voice_channel(name=nombre, overwrites=permisos)
            else:
                nuevo_canal = await interaction.guild.create_voice_channel(name=nombre, overwrites=permisos)

        # Guardar en la base de datos
        canal_obj = ClanChannel(
            channel_id=nuevo_canal.id,
            name=nuevo_canal.name,
            type=ChannelType.TEXT.value if tipo_canal == "text" else ChannelType.VOICE.value,
            clan_id=clan.id,
            created_at=datetime.now()
        )
        
        error = await servicio.save_clan_channel(canal_obj)
        if error:
            # Si hay error al guardar, eliminar el canal creado
            await nuevo_canal.delete()
            return False, f"Error al guardar el canal: {error}"

        return True, f"Canal de {tipo_canal} **{nombre}** creado exitosamente: {nuevo_canal.mention}"

    except Exception as e:
        logger.error(f"Error en crear_canal_adicional: {str(e)}")
        return False, f"Error al crear el canal: {str(e)}"
