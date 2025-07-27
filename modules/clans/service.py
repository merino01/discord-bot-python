from uuid import uuid4
from datetime import datetime
from typing import Optional, List
from discord import TextChannel, VoiceChannel, Role, Guild
from database import Database
from modules.clan_settings.service import ClanSettingsService
from modules.core import logger
from .models import Clan, ClanMember, ClanChannel, ClanMemberRole, ChannelType, FullClan


class ClanService:
    CLAN_NOT_FOUND_MSG = "El miembro no pertenece a ningún clan"
    CLAN_SELECT_BY_ID_SQL = "SELECT * FROM clans WHERE id = ?"

    def __init__(self):
        self.db = Database()
        self.clan_settings_service = ClanSettingsService()

    async def update_clan_config(
        self, 
        clan_id: str, 
        max_text_channels: Optional[int] = None, 
        max_voice_channels: Optional[int] = None
    ) -> Optional[str]:
        """
        Actualiza la configuración personalizada de un clan.
        """
        try:
            # Verificar que el clan existe
            clan_sql = "SELECT id FROM clans WHERE id = ? AND deleted = 0"
            clan_row = self.db.single(clan_sql, (clan_id,))
            if not clan_row:
                return "Clan no encontrado"

            # Construir query dinámico solo para campos no nulos
            update_fields = []
            params = []
            
            if max_text_channels is not None:
                update_fields.append("max_text_channels = ?")
                params.append(max_text_channels)
            
            if max_voice_channels is not None:
                update_fields.append("max_voice_channels = ?")
                params.append(max_voice_channels)
            
            if not update_fields:
                return "No se especificaron campos para actualizar"
            
            params.append(clan_id)
            update_sql = f"UPDATE clans SET {', '.join(update_fields)} WHERE id = ?"
            self.db.execute(update_sql, tuple(params))
            
            logger.info(f"Configuración del clan {clan_id} actualizada: texto={max_text_channels}, voz={max_voice_channels}")
            return None
        except Exception as e:
            logger.error(f"Error al actualizar configuración del clan {clan_id}: {str(e)}")
            return f"Error al actualizar la configuración: {str(e)}"

    async def create_clan(
        self,
        name: str,
        leader_id: int,
        role_id: int,
        text_channel: TextChannel,
        voice_channel: VoiceChannel,
        max_members: int,
        max_text_channels: Optional[int] = None,
        max_voice_channels: Optional[int] = None,
    ) -> tuple[Optional[Clan], Optional[str]]:
        
        # Si no se proporcionan límites específicos, usar la configuración global
        if max_text_channels is None or max_voice_channels is None:
            global_settings, error = await self.clan_settings_service.get_settings()
            if error:
                return None, f"Error al obtener configuración: {error}"
            
            if max_text_channels is None:
                max_text_channels = global_settings.max_text_channels
            if max_voice_channels is None:
                max_voice_channels = global_settings.max_voice_channels
        
        clan = Clan(
            id=str(uuid4()),
            name=name,
            role_id=role_id,
            created_at=datetime.now(),
            member_count=1,
            max_members=max_members,
            max_text_channels=max_text_channels,
            max_voice_channels=max_voice_channels,
        )
        sql = """--sql
            INSERT INTO clans (id, name, role_id, created_at, member_count, max_members, max_text_channels, max_voice_channels)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute(
            sql,
            (
                clan.id,
                clan.name,
                clan.role_id,
                clan.created_at,
                clan.member_count,
                clan.max_members,
                clan.max_text_channels,
                clan.max_voice_channels,
            ),
        )

        member = ClanMember(
            user_id=leader_id,
            clan_id=clan.id,
            role=ClanMemberRole.LEADER.value,
            joined_at=datetime.now(),
        )
        sql = """--sql
            INSERT INTO clan_members (user_id, clan_id, role, joined_at)
            VALUES (?, ?, ?, ?)
        """
        self.db.execute(
            sql, (member.user_id, member.clan_id, member.role, member.joined_at)
        )

        insert_channel_sql = """--sql
            INSERT INTO clan_channels (channel_id, name, type, clan_id, created_at)
            VALUES (?, ?, ?, ?, ?)
        """
        _text_channel = ClanChannel(
            channel_id=text_channel.id,
            name=text_channel.name,
            type=ChannelType.TEXT.value,
            clan_id=clan.id,
            created_at=datetime.now(),
        )
        _voice_channel = ClanChannel(
            channel_id=voice_channel.id,
            name=voice_channel.name,
            type=ChannelType.VOICE.value,
            clan_id=clan.id,
            created_at=datetime.now(),
        )
        self.db.execute(
            insert_channel_sql,
            (
                _text_channel.channel_id,
                _text_channel.name,
                _text_channel.type,
                _text_channel.clan_id,
                _text_channel.created_at,
            ),
        )
        self.db.execute(
            insert_channel_sql,
            (
                _voice_channel.channel_id,
                _voice_channel.name,
                _voice_channel.type,
                _voice_channel.clan_id,
                _voice_channel.created_at,
            ),
        )

        return clan, None

    async def delete(self, clan_id: str) -> tuple[Optional[int], Optional[str]]:
        delete_sql = "DELETE FROM clans WHERE id = ?"
        deleted = self.db.execute(delete_sql, (clan_id,))
        if not deleted:
            return None, f"No se pudo eliminar el clan con id {clan_id}"
        return clan_id, None

    async def get_member_clans(self, member_id: int) -> tuple[Optional[List[Clan]], Optional[str]]:
        try:
            sql = """--sql
                SELECT c.*
                FROM clans c
                INNER JOIN clan_members m ON c.id = m.clan_id
                WHERE
                    m.user_id = ?
                    AND c.deleted = 0
            """
            clans_rows = self.db.select(sql, (member_id,))
            if not clans_rows:
                return None, ClanService.CLAN_NOT_FOUND_MSG

            clans = [Clan(**row) for row in clans_rows]
            return clans, None
        except Exception as e:
            return None, f"Error al obtener los clanes del miembro: {str(e)}"

    async def get_leader_clan(self, member_id: int) -> tuple[Optional[Clan], Optional[str]]:
        sql = "SELECT * FROM clan_members WHERE user_id = ? AND role = ?"
        leader = self.db.single(sql, (member_id, ClanMemberRole.LEADER.value))
        if not leader:
            return None, "El usuario no es líder de ningún clan"

        clan = self.db.single(ClanService.CLAN_SELECT_BY_ID_SQL, (leader["clan_id"],))
        if not clan:
            return None, "El usuario no es líder de ningún clan"

        return Clan(**clan), None

    async def get_clan_role(self, guild: Guild, clan_id: str) -> tuple[Optional[Role], Optional[str]]:
        clan = self.db.single(ClanService.CLAN_SELECT_BY_ID_SQL, (clan_id,))
        if not clan:
            return None, "El clan no existe"

        role = await guild.fetch_role(clan["role_id"])
        if not role:
            return None, "El rol del clan no existe"

        return role, None

    async def add_member_to_clan(self, member_id: int, clan_id: str) -> Optional[str]:
        try:
            settings, error = await self.clan_settings_service.get_settings()
            if error or not settings:
                logger.error(f"Error al obtener configuración de clanes: {error}")
                return "Error al obtener la configuración de clanes"
                
            # Verificar que el clan existe
            clan = self.db.single(ClanService.CLAN_SELECT_BY_ID_SQL, (clan_id,))
            if not clan:
                logger.error(f"Clan con ID {clan_id} no encontrado")
                return "El clan no existe"

            # Verificar si el miembro ya está en algún clan
            select_member_sql = "SELECT * FROM clan_members WHERE user_id = ?"
            member = self.db.single(select_member_sql, (member_id,))
            
            if member and member["clan_id"] != clan_id and settings.allow_multiple_clans is False:
                logger.info(f"Miembro {member_id} ya pertenece a otro clan {member['clan_id']}")
                return "El miembro ya pertenece a otro clan"

            if member and member["clan_id"] == clan_id:
                logger.info(f"Miembro {member_id} ya pertenece al clan {clan_id}")
                return "El miembro ya pertenece a este clan"

            # Verificar límite de miembros del clan
            count_members_sql = "SELECT COUNT(*) as count FROM clan_members WHERE clan_id = ?"
            count_result = self.db.single(count_members_sql, (clan_id,))
            current_members = count_result["count"] if count_result else 0
            
            if current_members >= clan["max_members"]:
                logger.info(f"Clan {clan_id} ha alcanzado el límite máximo de miembros ({clan['max_members']})")
                return f"El clan ha alcanzado el límite máximo de miembros ({clan['max_members']})"

            # Insertar el miembro en la base de datos
            insert_member_sql = """
                INSERT INTO clan_members (user_id, clan_id, role, joined_at) 
                VALUES (?, ?, ?, ?)
            """
            
            logger.info(f"Intentando añadir miembro {member_id} al clan {clan_id}")
            result = self.db.execute(insert_member_sql, (member_id, clan_id, "member", datetime.now()))
            
            if result:
                logger.info(f"Miembro {member_id} añadido exitosamente al clan {clan_id}")
                return None
            else:
                logger.error(f"Error: No se pudo insertar el miembro {member_id} en el clan {clan_id}")
                return "Error al insertar el miembro en la base de datos"
                
        except Exception as e:
            logger.error(f"Excepción al añadir miembro {member_id} al clan {clan_id}: {str(e)}")
            return f"Error inesperado al añadir el miembro: {str(e)}"

    async def kick_member_from_clan(self, member_id: int, clan_id: str) -> Optional[str]:
        settings, error = await self.clan_settings_service.get_settings()
        if error or not settings:
            return "Error al obtener la configuración de clanes"
        
        # Validar si el clan existe
        clan_sql = "SELECT * FROM clans WHERE id = ?"
        clan_row = self.db.single(clan_sql, (clan_id,))
        if not clan_row:
            return "El clan no existe"

        # Validar si el miembro ya pertenece a un clan
        member_sql = "SELECT * FROM clan_members WHERE user_id = ?"
        member_row = self.db.single(member_sql, (member_id,))
        if not member_row:
            return "El miembro no pertenece a ningún clan"
        
        member = ClanMember(**member_row)
        if member.clan_id != clan_id and settings.allow_multiple_clans is False:
            return "El miembro pertenece a otro clan"

        if member.clan_id != clan_id:
            return "El miembro no pertenece a este clan"

        # Eliminar el miembro del clan
        delete_sql = "DELETE FROM clan_members WHERE user_id = ? AND clan_id = ?"
        self.db.execute(delete_sql, (member_id, clan_id))
        
        return None

    async def get_clan_by_id(self, clan_id: str) -> tuple[Optional[FullClan], Optional[str]]:
        try:
            # Obtener datos básicos del clan
            clan_sql = "SELECT * FROM clans WHERE id = ? AND deleted = 0"
            clan_row = self.db.single(clan_sql, (clan_id,))
            if not clan_row:
                return None, "Clan no encontrado"
            
            clan = Clan(**clan_row)
            
            # Obtener miembros del clan
            members_sql = "SELECT * FROM clan_members WHERE clan_id = ?"
            members_rows = self.db.select(members_sql, (clan_id,))
            members = [ClanMember(**row) for row in members_rows] if members_rows else []
            
            # Obtener canales del clan
            channels_sql = "SELECT * FROM clan_channels WHERE clan_id = ?"
            channels_rows = self.db.select(channels_sql, (clan_id,))
            channels = [ClanChannel(**row) for row in channels_rows] if channels_rows else []
            
            # Crear el objeto FullClan
            full_clan = FullClan(
                id=clan.id,
                name=clan.name,
                role_id=clan.role_id,
                created_at=clan.created_at,
                member_count=clan.member_count,
                max_members=clan.max_members,
                max_text_channels=clan.max_text_channels,
                max_voice_channels=clan.max_voice_channels,
                members=members,
                channels=channels
            )
            
            return full_clan, None
        except Exception as e:
            return None, f"Error al obtener el clan: {str(e)}"

    async def get_all_clans(self) -> tuple[Optional[List[FullClan]], Optional[str]]:
        try:
            # Obtener todos los clanes
            clans_sql = "SELECT * FROM clans WHERE deleted = 0"
            clans_rows = self.db.select(clans_sql)
            if not clans_rows:
                return [], None
            
            full_clans = []
            for clan_row in clans_rows:
                clan = Clan(**clan_row)
                
                # Obtener miembros del clan
                members_sql = "SELECT * FROM clan_members WHERE clan_id = ?"
                members_rows = self.db.select(members_sql, (clan.id,))
                members = [ClanMember(**row) for row in members_rows] if members_rows else []
                
                # Obtener canales del clan
                channels_sql = "SELECT * FROM clan_channels WHERE clan_id = ?"
                channels_rows = self.db.select(channels_sql, (clan.id,))
                channels = [ClanChannel(**row) for row in channels_rows] if channels_rows else []
                
                # Crear el objeto FullClan
                full_clan = FullClan(
                    id=clan.id,
                    name=clan.name,
                    role_id=clan.role_id,
                    created_at=clan.created_at,
                    member_count=clan.member_count,
                    max_members=clan.max_members,
                    max_text_channels=clan.max_text_channels,
                    max_voice_channels=clan.max_voice_channels,
                    members=members,
                    channels=channels
                )
                full_clans.append(full_clan)
            
            return full_clans, None
        except Exception as e:
            return None, f"Error al obtener los clanes: {str(e)}"

    async def delete_clan(self, clan_id: str) -> Optional[str]:
        try:
            # Marcar el clan como eliminado
            delete_sql = "UPDATE clans SET deleted = 1 WHERE id = ?"
            result = self.db.execute(delete_sql, (clan_id,))
            if not result:
                return "No se pudo eliminar el clan"
            
            # Eliminar todos los miembros del clan eliminado
            delete_members_sql = "DELETE FROM clan_members WHERE clan_id = ?"
            self.db.execute(delete_members_sql, (clan_id,))
            
            logger.info(f"Clan {clan_id} eliminado y sus miembros removidos")
            return None
        except Exception as e:
            logger.error(f"Error al eliminar el clan {clan_id}: {str(e)}")
            return f"Error al eliminar el clan: {str(e)}"

    async def get_clan_by_role_id(self, role_id: int) -> tuple[Optional[FullClan], Optional[str]]:
        try:
            # Obtener el clan por role_id
            clan_sql = "SELECT * FROM clans WHERE role_id = ? AND deleted = 0"
            clan_row = self.db.single(clan_sql, (role_id,))
            if not clan_row:
                return None, "No se encontró un clan con ese rol"
            
            # Usar get_clan_by_id para obtener todos los datos
            return await self.get_clan_by_id(clan_row["id"])
        except Exception as e:
            return None, f"Error al obtener el clan por rol: {str(e)}"

    async def get_clan_by_channel_id(self, channel_id: int) -> tuple[Optional[FullClan], Optional[str]]:
        try:
            # Obtener el clan a través del canal
            clan_sql = """--sql
                SELECT c.* FROM clans c
                INNER JOIN clan_channels cc ON c.id = cc.clan_id
                WHERE cc.channel_id = ? AND c.deleted = 0
            """
            clan_row = self.db.single(clan_sql, (channel_id,))
            if not clan_row:
                return None, "No se encontró un clan asociado a este canal"
            
            # Usar get_clan_by_id para obtener todos los datos
            return await self.get_clan_by_id(clan_row["id"])
        except Exception as e:
            return None, f"Error al obtener el clan por canal: {str(e)}"

    async def is_clan_leader(self, user_id: int, clan_id: str) -> tuple[bool, Optional[str]]:
        try:
            sql = "SELECT * FROM clan_members WHERE user_id = ? AND clan_id = ? AND role = ?"
            member = self.db.single(sql, (user_id, clan_id, ClanMemberRole.LEADER.value))
            return member is not None, None
        except Exception as e:
            return False, f"Error al verificar liderazgo: {str(e)}"

    def save_clan_channel(self, channel: ClanChannel) -> Optional[str]:
        """Guardar un canal de clan en la base de datos"""
        try:
            sql = """--sql
                INSERT INTO clan_channels (channel_id, name, type, clan_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """
            self.db.execute(
                sql,
                (
                    channel.channel_id,
                    channel.name,
                    channel.type,
                    channel.clan_id,
                    channel.created_at,
                ),
            )
            return None
        except Exception as e:
            logger.error(f"Error al guardar canal de clan: {str(e)}")
            return f"Error al guardar el canal: {str(e)}"

    def promote_member_to_leader(self, user_id: int, clan_id: str) -> Optional[str]:
        """Promover un miembro a líder del clan"""
        try:
            # Verificar que el miembro existe en el clan
            member_sql = "SELECT * FROM clan_members WHERE user_id = ? AND clan_id = ?"
            member = self.db.single(member_sql, (user_id, clan_id))
            if not member:
                return "El usuario no es miembro de este clan"
            
            if member["role"] == ClanMemberRole.LEADER.value:
                return "El usuario ya es líder de este clan"
            
            # Promover a líder
            update_sql = "UPDATE clan_members SET role = ? WHERE user_id = ? AND clan_id = ?"
            self.db.execute(update_sql, (ClanMemberRole.LEADER.value, user_id, clan_id))
            
            return None
        except Exception as e:
            logger.error(f"Error al promover miembro a líder: {str(e)}")
            return f"Error al promover el miembro: {str(e)}"
