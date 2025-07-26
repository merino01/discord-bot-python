from typing import Optional, Tuple, Mapping, Union
from datetime import datetime
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
from .models import ClanMemberRole, ClanChannel, ChannelType


async def create_clan_role(guild: Guild, name: str) -> Tuple[Optional[Role], Optional[str]]:
    try:
        settings_service = ClanSettingsService()
        settings, error = await settings_service.get_settings()
        if error:
            return None, error

        # Validar y corregir el color
        try:
            # Intentar usar el color configurado
            color_str = settings.default_role_color
            # Asegurar que tenga exactamente 6 caracteres hexadecimales
            if len(color_str) != 6 or not all(c in '0123456789ABCDEFabcdef' for c in color_str):
                logger.warning(f"Color inválido en configuración: {color_str}, usando color por defecto")
                color_str = "7289da"  # Color azul de Discord por defecto
            
            role_color = Color.from_str(f"#{color_str}")
        except Exception as color_error:
            logger.warning(f"Error al procesar color {settings.default_role_color}: {color_error}, usando color por defecto")
            role_color = Color.from_str("#7289da")  # Color azul de Discord por defecto

        role = await guild.create_role(name=name, color=role_color)
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

        # Permisos para canales de texto
        text_overwrites: Mapping[Union[Role, Member, Object], PermissionOverwrite] = {
            guild.default_role: PermissionOverwrite(
                view_channel=False,
                read_messages=False,
                send_messages=False
            ),
            role: PermissionOverwrite(
                view_channel=True,
                read_messages=True,
                send_messages=True,
                add_reactions=True,
                attach_files=True,
                embed_links=True,
                read_message_history=True,
                use_external_emojis=True
            ),
        }

        # Permisos para canales de voz
        voice_overwrites: Mapping[Union[Role, Member, Object], PermissionOverwrite] = {
            guild.default_role: PermissionOverwrite(
                view_channel=False,
                connect=False
            ),
            role: PermissionOverwrite(
                view_channel=True,
                connect=True,
                speak=True,
                stream=True,
                use_voice_activation=True
            ),
        }

        # Crear canal de texto
        if text_category and isinstance(text_category, CategoryChannel):
            text_channel = await text_category.create_text_channel(name=name, overwrites=text_overwrites)
        else:
            text_channel = await guild.create_text_channel(name=name, overwrites=text_overwrites)

        # Crear canal de voz
        if voice_category and isinstance(voice_category, CategoryChannel):
            voice_channel = await voice_category.create_voice_channel(
                name=name, overwrites=voice_overwrites
            )
        else:
            voice_channel = await guild.create_voice_channel(name=name, overwrites=voice_overwrites)

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
    clans, _ = await service.get_member_clans(member_id)
    return clans is not None and len(clans) > 0


async def is_clan_leader(member_id: int) -> bool:
    service = ClanService()
    clan, error = await service.get_leader_clan(member_id)
    if error or not clan:
        return False
    return True


async def remove_clan_roles_from_member(
    guild: Guild, 
    member_id: int, 
    clan_role_id: int, 
    should_check_other_clans: bool = True
) -> None:
    """
    Función reutilizable para quitar roles de clan de un miembro.
    
    Args:
        guild: El servidor de Discord
        member_id: ID del miembro
        clan_role_id: ID del rol del clan a quitar
        should_check_other_clans: Si debe verificar si está en otros clanes antes de quitar roles adicionales
    """
    try:
        # Obtener miembro de Discord
        try:
            miembro = await guild.fetch_member(member_id)
        except Exception:
            return  # Si no se puede obtener el miembro, salir silenciosamente
        
        if not miembro:
            return
            
        # Quitar rol del clan
        try:
            rol_clan = await guild.fetch_role(clan_role_id)
            if rol_clan and rol_clan in miembro.roles:
                await miembro.remove_roles(rol_clan)
        except Exception:
            pass  # Continuar aunque no se pueda quitar el rol
        
        # Si no se debe verificar otros clanes, quitar roles adicionales directamente
        if not should_check_other_clans:
            await _remove_additional_and_leader_roles(guild, miembro, member_id, force_remove=True)
            return
        
        # Verificar si el usuario está en otros clanes
        servicio = ClanService()
        clanes_restantes, _ = await servicio.get_member_clans(member_id)
        usuario_en_otros_clanes = clanes_restantes and len(clanes_restantes) > 0
        
        # Si no está en otros clanes, quitar roles adicionales y rol de líder
        if not usuario_en_otros_clanes:
            await _remove_additional_and_leader_roles(guild, miembro, member_id)
            
    except Exception as e:
        logger.error(f"Error en remove_clan_roles_from_member: {str(e)}")


async def _remove_additional_and_leader_roles(
    guild: Guild, 
    miembro: Member, 
    member_id: int, 
    force_remove: bool = False
) -> None:
    """
    Función auxiliar para quitar roles adicionales y de líder.
    
    Args:
        guild: El servidor de Discord
        miembro: El miembro de Discord
        member_id: ID del miembro
        force_remove: Si debe forzar la remoción sin verificar otros clanes
    """
    try:
        settings_service = ClanSettingsService()
        settings, settings_error = await settings_service.get_settings()
        if settings_error or not settings:
            return
        
        # Quitar roles adicionales
        for role_id in settings.additional_roles:
            if additional_role := guild.get_role(role_id):
                if additional_role in miembro.roles:
                    try:
                        await miembro.remove_roles(additional_role)
                    except Exception:
                        pass  # Continuar aunque no se pueda quitar el rol
        
        # Quitar rol de líder si corresponde
        if settings.leader_role_id:
            should_remove_leader_role = force_remove
            
            if not force_remove:
                # Verificar si es líder de algún otro clan
                servicio = ClanService()
                clanes_restantes, _ = await servicio.get_member_clans(member_id)
                if clanes_restantes:
                    es_lider_de_otro_clan = False
                    for clan_restante in clanes_restantes:
                        es_lider, _ = await servicio.is_clan_leader(member_id, clan_restante.id)
                        if es_lider:
                            es_lider_de_otro_clan = True
                            break
                    should_remove_leader_role = not es_lider_de_otro_clan
                else:
                    should_remove_leader_role = True
            
            if should_remove_leader_role:
                if leader_role := guild.get_role(settings.leader_role_id):
                    if leader_role in miembro.roles:
                        try:
                            await miembro.remove_roles(leader_role)
                        except Exception:
                            pass  # Continuar aunque no se pueda quitar el rol
                            
    except Exception as e:
        logger.error(f"Error en _remove_additional_and_leader_roles: {str(e)}")


async def add_member_to_clan(guild: Guild, member_id: int, clan_id: str) -> Optional[str]:
    service = ClanService()
    settings_service = ClanSettingsService()
    
    # Obtener rol del clan
    role, error = await service.get_clan_role(guild, clan_id)
    if error or not role:
        return "Error al obtener el rol del clan"

    member = await guild.fetch_member(member_id)
    if not member:
        return "El miembro no existe"
    if member.bot:
        return "No se puede añadir un bot al clan"
    
    # Obtener la configuración para roles adicionales
    settings, settings_error = await settings_service.get_settings()
    if settings_error:
        return f"Error al obtener configuración: {settings_error}"
    
    # Añadir rol del clan
    await member.add_roles(role)
    
    # Añadir roles adicionales configurados
    additional_roles_added = []
    try:
        for role_id in settings.additional_roles:
            if additional_role := guild.get_role(role_id):
                await member.add_roles(additional_role)
                additional_roles_added.append(additional_role)
    except Exception as e:
        # Si hay error al añadir roles adicionales, revertir todo
        await member.remove_roles(role)
        for added_role in additional_roles_added:
            try:
                await member.remove_roles(added_role)
            except:
                pass
        logger.error(f"Error al añadir roles adicionales: {str(e)}")
        return "Error al asignar roles adicionales"

    # Añadir miembro al clan
    error = await service.add_member_to_clan(member_id, clan_id)
    if error:
        # Revertir todos los roles si hay error en la base de datos
        await member.remove_roles(role)
        for added_role in additional_roles_added:
            try:
                await member.remove_roles(added_role)
            except:
                pass
        return "Error al añadir el miembro al clan"

    return None


async def logica_salir_del_clan(id_usuario: int, id_clan: str, guild: Guild) -> Optional[str]:
    """Lógica para que un usuario salga de un clan."""
    try:
        servicio = ClanService()
        
        # Obtener el clan completo con sus miembros
        clan_completo, error = await servicio.get_clan_by_id(id_clan)
        if error or not clan_completo:
            return f"Error al obtener información del clan: {error}"
        
        # Verificar que el usuario está en el clan
        usuario_en_clan = any(m.user_id == id_usuario for m in clan_completo.members)
        if not usuario_en_clan:
            return "No perteneces a este clan"
        
        # No permitir que el líder se salga si es el único líder
        lideres = [m for m in clan_completo.members if m.role == ClanMemberRole.LEADER.value]
        # TODO: Descomentar esto cuando se pueda pasar el liderazgo del clan
        # if len(lideres) <= 1:
        #     usuario_es_lider = any(m.user_id == id_usuario and m.role == ClanMemberRole.LEADER.value for m in clan_completo.members)
        #     if usuario_es_lider:
        #         return "No puedes salir del clan siendo el único líder. Transfiere el liderazgo primero."
        
        # Eliminar del clan en la base de datos
        error = await servicio.kick_member_from_clan(id_usuario, id_clan)
        if error:
            return f"Error al salir del clan: {error}"
        
        # Quitar roles usando la función reutilizable
        await remove_clan_roles_from_member(guild, id_usuario, clan_completo.role_id)
        
        return None
        
    except Exception as e:
        logger.error(f"Error en logica_salir_del_clan: {str(e)}")
        return f"Error inesperado al salir del clan: {str(e)}"


async def logica_expulsar_del_clan(id_usuario: int, id_clan: str, guild: Guild) -> Optional[str]:
    """Lógica para expulsar a un usuario de un clan."""
    try:
        servicio = ClanService()
        
        # Verificar que el usuario está en el clan
        clanes, error = await servicio.get_member_clans(id_usuario)
        if error or not clanes:
            return "El usuario no pertenece a ningún clan"
        
        clan_del_que_expulsar = next((c for c in clanes if c.id == id_clan), None)
        if not clan_del_que_expulsar:
            return "El usuario no pertenece a este clan"
        
        # Expulsar del clan en la base de datos
        error = await servicio.kick_member_from_clan(id_usuario, id_clan)
        if error:
            return f"Error al expulsar del clan: {error}"
        
        # Quitar roles usando la función reutilizable
        await remove_clan_roles_from_member(guild, id_usuario, clan_del_que_expulsar.role_id)
        
        return None
        
    except Exception as e:
        logger.error(f"Error en logica_expulsar_del_clan: {str(e)}")
        return f"Error inesperado al expulsar del clan: {str(e)}"


async def crear_canal_adicional(
    interaction, 
    nombre: str, 
    tipo_canal: str
) -> Tuple[bool, str]:
    """
    Lógica común para crear canales adicionales.
    Retorna (éxito, mensaje)
    """
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
