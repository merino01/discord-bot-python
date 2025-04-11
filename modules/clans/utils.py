"""utilities for clan module"""
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
    HTTPException
)
from modules.clan_settings.service import ClanSettingsService
from modules.core import logger
from .service import ClanService

async def create_clan_role(
    guild: Guild,
    name: str
) -> Tuple[Optional[Role], Optional[str]]:
    """
    Crear un rol para el clan usando la configuración
    """
    try:
        settings, error = await ClanSettingsService.get_settings()
        if error:
            return None, error

        role = await guild.create_role(
            name=name,
            color=Color.from_str(f"#{settings.default_role_color}")
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
    guild: Guild,
    name: str,
    role: Role
) -> Tuple[Optional[TextChannel], Optional[VoiceChannel], Optional[str]]:
    """
    Crear canales para el clan usando la configuración
    """
    try:
        settings, error = await ClanSettingsService.get_settings()
        if error:
            return None, None, error

        # Obtener categoría configurada
        category = guild.get_channel(settings.category_id) if settings.category_id else None

        # Permisos
        overwrites: Mapping[Union[Role, Member, Object], PermissionOverwrite] = {
            guild.default_role: PermissionOverwrite(read_messages=False, connect=False),
            role: PermissionOverwrite(read_messages=True, connect=True)
        }

        if category and isinstance(category, CategoryChannel):
            text_channel = await category.create_text_channel(
                name=name,
                overwrites=overwrites
            )

            voice_channel = await category.create_voice_channel(
                name=name,
                overwrites=overwrites
            )
        else:
            text_channel = await guild.create_text_channel(
                name=name,
                overwrites=overwrites
            )

            voice_channel = await guild.create_voice_channel(
                name=name,
                overwrites=overwrites
            )

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


async def setup_clan_roles(
    guild: Guild,
    member: Member,
    role: Role
) -> Optional[str]:
    """
    Configurar roles para un miembro del clan
    """
    try:
        settings, error = await ClanSettingsService.get_settings()
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
    """
    Verifica si un miembro pertenece a un clan
    """
    clans, error = await ClanService.get_member_clans(member_id)
    if error or not clans or len(clans) == 0:
        return False
    return True


async def is_clan_leader(member_id: int) -> bool:
    """
    Verifica si un miembro es líder de un clan
    """
    clan, error = await ClanService.get_leader_clan(member_id)
    if error or not clan:
        return False
    return True


async def add_member_to_clan(
    guild: Guild,
    member_id: int,
    clan_id: str
) -> Optional[str]:
    """
    Añade un miembro a un clan
    """
    # Obtener rol del clan
    role, error = await ClanService.get_clan_role(guild, clan_id)
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
    error = await ClanService.add_member_to_clan(member_id, clan_id)
    if error:
        await member.remove_roles(role)
        return "Error al añadir el miembro al clan"
