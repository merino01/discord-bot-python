"""Servicio de clanes"""

from uuid import uuid4
from datetime import datetime
from typing import Optional, List
from discord import TextChannel, VoiceChannel, Role, Guild
from database import db
from modules.clan_settings import ClanSettingsService
from .models import Clan, ClanMember, ClanChannel, ClanMemberRole, ChannelType, FullClan

class ClanService:
    """Lógica de negocio para clanes"""

    @staticmethod
    async def create_clan(
        name: str,
        leader_id: int,
        role_id: int,
        text_channel: TextChannel,
        voice_channel: VoiceChannel,
        max_members: int
    ) -> tuple[Optional[Clan], Optional[str]]:
        """Crea un nuevo clan"""
        # Crear clan
        clan = Clan(
            id=str(uuid4()),
            name=name,
            role_id=role_id,
            created_at=datetime.now(),
            member_count=1,
            max_members=max_members,
        )
        # Guardar clan en la base de datos
        db.insert(table="clans", data=clan.__dict__)

        # Añadir líder como primer miembro
        member = ClanMember(
            user_id=leader_id,
            clan_id=clan.id,
            role=ClanMemberRole.LEADER.value,
            joined_at=datetime.now(),
        )
        # Guardar miembro en la base de datos
        db.insert(table="clan_members", data=member.__dict__)

        # Crear canales de texto y voz
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

        # Guardar canales en la base de datos
        db.insert(table="clan_channels", data=_text_channel.__dict__)
        db.insert(table="clan_channels", data=_voice_channel.__dict__)

        return clan, None


    @staticmethod
    async def get_all() -> tuple[Optional[List[FullClan]], Optional[str]]:
        """Obtiene todos los clanes"""
        clans, error = db.select(
            model=Clan,
            table="clans",
            columns=["*"]
        )
        if error:
            return None, error

        if not clans:
            return None, "No hay clanes"

        full_clans = []
        for clan in clans:
            members, error = db.select(
                model=ClanMember,
                table="clan_members",
                columns=["*"],
                conditions={"clan_id": clan.id}
            )
            if error or not members:
                return None, "El clan no tiene miembros"

            channels, error = db.select(
                model=ClanChannel,
                table="clan_channels",
                columns=["*"],
                conditions={"clan_id": clan.id}
            )
            if error or not channels:
                return None, "El clan no tiene canales"

            full_clan = FullClan(
                clan=clan,
                members=members,
                channels=channels
            )
            full_clans.append(full_clan)

        return full_clans, None


    @staticmethod
    async def get_clan_by_id(clan_id: str) -> tuple[Optional[FullClan], Optional[str]]:
        """Obtiene un clan por su ID"""
        clan, error = db.select_one(
            model=Clan,
            table="clans",
            columns=["*"],
            conditions={"id": clan_id}
        )
        if error or not clan:
            return None, "El clan no existe"

        members, error = db.select(
            model=ClanMember,
            table="clan_members",
            columns=["*"],
            conditions={"clan_id": clan_id},
        )
        if error or not members:
            return None, "El clan no tiene miembros"

        channels, error = db.select(
            model=ClanChannel,
            table="clan_channels",
            columns=["*"],
            conditions={"clan_id": clan_id},
        )
        if error or not channels:
            return None, "El clan no tiene canales"

        full_clan = FullClan(clan=clan, members=members, channels=channels)
        return full_clan, None


    @staticmethod
    async def delete(clan_id: str) -> tuple[Optional[int], Optional[str]]:
        """Elimina un clan"""
        # Validar

        # Eliminar clan
        _, error = db.delete(
            table="clans",
            key="id",
            value=clan_id
        )
        if error:
            return None, error

        return _, None


    @staticmethod
    async def get_member_clans(
        member_id: int
    ) -> tuple[Optional[List[Clan]], Optional[str]]:
        """Obtiene el clan al que pertenece un miembro"""
        member, error = db.select_one(
            model=ClanMember,
            table="clan_members",
            columns=["*"],
            conditions={"user_id": member_id}
        )
        if error or not member:
            return None, "El miembro no pertenece a ningún clan"

        clans, error = db.select(
            model=Clan,
            table="clans",
            columns=["*"],
            conditions={"id": member.clan_id}
        )
        if error or not clans:
            return None, "El miembro no pertenece a ningún clan"

        return clans, None


    @staticmethod
    async def get_leader_clan(
        member_id: int
    ) -> tuple[Optional[Clan], Optional[str]]:
        """Obtiene el clan al que pertenece un líder"""
        leader, error = db.select_one(
            model=ClanMember,
            table="clan_members",
            columns=["*"],
            conditions={"user_id": member_id, "role": ClanMemberRole.LEADER.value}
        )
        if error or not leader:
            return None, "El usuario no es líder de ningún clan"

        clan, error = db.select_one(
            model=Clan,
            table="clans",
            columns=["*"],
            conditions={"id": leader.clan_id}
        )
        if error or not clan:
            return None, "El usuario no es líder de ningún clan"

        return clan, None


    @staticmethod
    async def get_clan_role(guild: Guild, clan_id: str) -> tuple[Optional[Role], Optional[str]]:
        """Obtiene el rol del clan"""
        clan, error = db.select_one(
            model=Clan,
            table="clans",
            columns=["*"],
            conditions={"id": clan_id}
        )
        if error or not clan:
            return None, "El clan no existe"

        # Obtener rol del clan
        role = await guild.fetch_role(clan.role_id)
        if not role:
            return None, "El rol del clan no existe"

        return role, None


    @staticmethod
    async def add_member_to_clan(
        member_id: int,
        clan_id: str
    ) -> Optional[str]:
        """Añade un miembro a un clan"""
        settings, error = await ClanSettingsService.get_settings()
        if error or not settings:
            return "Error al obtener la configuración de clanes"
        # Validar si el clan existe
        clan, error = db.select_one(
            model=Clan,
            table="clans",
            columns=["*"],
            conditions={"id": clan_id}
        )
        if error or not clan:
            return "El clan no existe"

        # Validar si el miembro ya pertenece a un clan
        member, error = db.select_one(
            model=ClanMember,
            table="clan_members",
            columns=["*"],
            conditions={"user_id": member_id}
        )
        if error:
            return "Error al obtener el miembro"

        if member and member.clan_id != clan_id and settings.allow_multiple_clans is False:
            return "El miembro ya pertenece a otro clan"

        if member and member.clan_id == clan_id:
            return "El miembro ya pertenece a este clan"

        return None
