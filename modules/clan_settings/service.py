"""service for clan settings module"""

from typing import Optional, Tuple
from database import db
from modules.core import logger
from .models import ClanSettings, ClanSetting

class ClanSettingsService:
    """Servicio para gestionar la configuración de clanes"""

    @staticmethod
    async def get_settings() -> Tuple[ClanSettings, Optional[str]]:
        """Obtener configuración actual"""
        settings, error = db.select(
            model=ClanSetting,
            table="clan_settings",
            columns=["key", "value"]
        )
        if error:
            return ClanSettings.get_default(), error
        if not settings:
            default_settings = ClanSettings.get_default()
            await ClanSettingsService.save_settings(default_settings)
            return default_settings, None

        settings_dict = {}
        for setting in settings:
            settings_dict[setting.key] = setting.value

        try:
            settings = ClanSettings.from_dict(settings_dict)
            return settings, None
        except:
            logger.error("Error al cargar la configuración de clanes")
            return ClanSettings.get_default(), "Error al cargar la configuración de clanes"


    @staticmethod
    async def save_settings(settings: ClanSettings) -> Optional[str]:
        """Guardar configuración"""
        settings_dict = settings.to_dict()
        for key, value in settings_dict.items():
            _, error = db.upsert(
                table="clan_settings",
                data={"key": key, "value": value},
                primary_key="key"
            )
            if error:
                logger.error("Error al guardar configuración: %s", error)
                return error
        return None
