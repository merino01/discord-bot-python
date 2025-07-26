from typing import Optional, Tuple
from database import Database
from modules.core import logger
from .models import ClanSettings


class ClanSettingsService:
    def __init__(self):
        self.db = Database()

    async def get_settings(self) -> Tuple[ClanSettings, Optional[str]]:
        try:
            rows = self.db.select("SELECT key, value FROM clan_settings")
            if not rows:
                default_settings = ClanSettings.get_default()
                await self.save_settings(default_settings)
                return default_settings, None

            settings_dict = {row["key"]: row["value"] for row in rows}
            try:
                settings = ClanSettings.from_dict(settings_dict)
                return settings, None
            except Exception:
                logger.error("Error al cargar la configuración de clanes")
                return ClanSettings.get_default(), "Error al cargar la configuración de clanes"
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener la configuración de clanes: %s", error)
            return ClanSettings.get_default(), None

    async def save_settings(self, settings: ClanSettings) -> Optional[str]:
        try:
            settings_dict = settings.to_dict()
            for key, value in settings_dict.items():
                # Usar INSERT OR REPLACE para simplificar la lógica
                sql = "INSERT OR REPLACE INTO clan_settings (key, value) VALUES (?, ?)"
                self.db.execute(sql, (key, value))
            return None
        except Exception as e:
            error = str(e)
            logger.error("Error al guardar configuración: %s", error)
            return error
