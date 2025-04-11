"""Módulo de validaciones para clanes"""

from typing import Optional
from discord import Member
from modules.clan_settings import ClanSettingsService
from .models import Clan
from .utils import is_in_clan, is_clan_leader

class ClanValidator:
    """Validaciones para operaciones de clanes"""

    @staticmethod
    async def can_create_clan(
        name: str,
        leader: Member
    ) -> tuple[bool, Optional[str]]:
        """Valida si se puede crear un clan con ese nombre"""
        settings, error = await ClanSettingsService.get_settings()
        if error:
            return False, "Error al obtener la configuración de clanes"

        if not settings.allow_multiple_clans and await is_in_clan(leader.id):
            return False, "El líder ya pertenece a un clan"
        if not settings.allow_multiple_leaders and await is_clan_leader(leader.id):
            return False, "El líder ya es líder de otro clan"
        if len(name) < 3 or len(name) > 32:
            return False, "El nombre debe tener entre 3 y 32 caracteres"
        return True, None


    @staticmethod
    async def can_manage_clan(member: Member, clan: Clan) -> tuple[bool, Optional[str]]:
        """Valida si un miembro puede gestionar el clan"""
        return True, None
