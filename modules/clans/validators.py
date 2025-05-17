"""Módulo de validaciones para clanes"""

from typing import Optional
from discord import Member
from .models import Clan


class ClanValidator:
    """Validaciones para operaciones de clanes"""

    @staticmethod
    def can_create_clan(name: str) -> tuple[bool, Optional[str]]:
        """Valida si se puede crear un clan con ese nombre"""
        if len(name) < 3 or len(name) > 32:
            return False, "El nombre debe tener entre 3 y 32 caracteres"
        return True, None

    @staticmethod
    def can_join_clan(member: Member, clan: Clan) -> tuple[bool, Optional[str]]:
        """Valida si un miembro puede unirse al clan"""
        if clan.member_count >= clan.max_members:
            return False, "El clan está lleno"
        # Más validaciones...
        return True, None

    @staticmethod
    def can_manage_clan(member: Member, clan: Clan) -> tuple[bool, Optional[str]]:
        """Valida si un miembro puede gestionar el clan"""
        if member.id != clan.leader_id and not member.guild_permissions.administrator:
            return False, "No tienes permisos para gestionar este clan"
        return True, None
