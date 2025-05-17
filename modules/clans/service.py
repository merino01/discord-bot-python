"""Servicio de clanes"""

from uuid import uuid4
from datetime import datetime
from typing import Optional
from discord import TextChannel, VoiceChannel
from database import db
from .models import Clan, ClanMember, ClanChannel, ClanMemberRole, ChannelType, FullClan
from .validators import ClanValidator


class ClanService:
    """Lógica de negocio para clanes"""

    @staticmethod
    async def create_clan(
        name: str,
        leader_id: int,
        role_id: int,
        text_channel: TextChannel,
        voice_channel: VoiceChannel,
    ) -> tuple[Optional[Clan], Optional[str]]:
        """Crea un nuevo clan"""
        # Validar
        can_create, error = ClanValidator.can_create_clan(name)
        if not can_create:
            return None, error

        # Crear clan
        clan = Clan(
            id=str(uuid4()),
            name=name,
            role_id=role_id,
            created_at=datetime.now(),
            member_count=1,
            max_members=30,
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
    async def get_clan_by_id(clan_id: str) -> tuple[Optional[FullClan], Optional[str]]:
        """Obtiene un clan por su ID"""
        clan, error = db.select_one(
            model=Clan, table="clans", columns=["*"], contitions={"id": clan_id}
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
