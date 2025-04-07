"""triggers_service.py"""

from typing import List, Optional
from database import db
from database.models import Trigger
from utils.logger import logger

class TriggersService:
    """Service class for managing triggers."""

    @staticmethod
    def get_all() -> List[Trigger]:
        """
        Fetch all triggers from the database.
        :return: List of triggers.
        """
        return db.query(
            model=Trigger,
            query="SELECT * FROM triggers"
        )

    @staticmethod
    def get_by_id(trigger_id: str) -> Optional[Trigger]:
        """
        Fetch trigger by ID.
        :param trigger_id: The ID of the trigger.
        :return: Trigger object if found, None otherwise.
        """
        triggers = db.query(
            model=Trigger,
            query="SELECT * FROM triggers WHERE id = ?",
            params=(trigger_id,)
        )
        return triggers[0] if len(triggers) > 0 else None

    @staticmethod
    def get_one_by_channel_id(channel_id: int) -> Optional[Trigger]:
        """
        Fetch triggers by channel ID.
        :param channel_id: The ID of the channel.
        :return: List of triggers for the specified channel.
        """
        triggers = db.query(
            model=Trigger,
            query="SELECT * FROM triggers WHERE channel_id = ?",
            params=(channel_id,)
        )
        return triggers[0] if len(triggers) > 0 else None

    @staticmethod
    def get_all_by_channel_id(channel_id: int) -> List[Trigger]:
        """
        Fetch triggers by channel ID.
        :param channel_id: The ID of the channel.
        :return: List of triggers for the specified channel.
        """
        triggers = db.query(
            model=Trigger,
            query="SELECT * FROM triggers WHERE channel_id = ?",
            params=(channel_id,)
        )
        return triggers

    @staticmethod
    def add(trigger: Trigger) -> None:
        """
        Add a new trigger to the database.
        :param trigger: trigger to add.
        """
        data = trigger.__dict__.copy()
        data["id"] = str(data["id"])
        # Eliminar campos None para que SQLite use los defaults
        data = {k: v for k, v in data.items() if v is not None}
        ok = db.insert(
            table="triggers",
            data=data
        )
        if ok:
            logger.info(f"Trigger añadido: {trigger}")
        else:
            logger.error("Error al añadir el trigger: %s", trigger)

    @staticmethod
    def delete_by_id(trigger_id: str) -> bool:
        """
        Delete a trigger from the database.
        :param trigger: Trigger to delete.
        """
        ok = db.delete(
            table="triggers",
            key="id",
            value=trigger_id
        )
        if ok:
            logger.info("Trigger eliminado: %s", trigger_id)
        else:
            logger.error("Error al eliminar el trigger: %s", trigger_id)
        return ok
