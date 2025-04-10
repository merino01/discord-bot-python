"""triggers_service.py"""

from typing import List, Optional
from database import db
from modules.core import logger
from .models import Trigger

class TriggersService:
    """Service class for managing triggers."""

    @staticmethod
    def get_all() -> tuple[Optional[List[Trigger]], Optional[str]]:
        """
        Fetch all triggers from the database.
        :return: List of triggers.
        """
        triggers, error = db.select(
            model=Trigger,
            table="triggers",
            columns=["*"]
        )
        if error:
            logger.error("Error al obtener los triggers: %s", error)
            return None, error
        return triggers, None


    @staticmethod
    def get_by_id(trigger_id: str) -> tuple[Optional[Trigger], Optional[str]]:
        """
        Fetch trigger by ID.
        :param trigger_id: The ID of the trigger.
        :return: Trigger object if found, None otherwise.
        """
        trigger, error = db.select_one(
            model=Trigger,
            table="triggers",
            columns=["*"],
            conditions={"id": trigger_id}
        )
        if error:
            logger.error("Error al obtener el trigger: %s", error)
            return None, error
        return trigger, None


    @staticmethod
    def get_one_by_channel_id(channel_id: int) -> tuple[Optional[Trigger], Optional[str]]:
        """
        Fetch triggers by channel ID.
        :param channel_id: The ID of the channel.
        :return: List of triggers for the specified channel.
        """
        trigger, error = db.select_one(
            model=Trigger,
            table="triggers",
            columns=["*"],
            conditions={"channel_id": channel_id}
        )
        if error:
            logger.error("Error al obtener el trigger: %s", error)
            return None, error
        return trigger, None


    @staticmethod
    def get_all_by_channel_id(channel_id: int) -> tuple[Optional[List[Trigger]], Optional[str]]:
        """
        Fetch triggers by channel ID.
        :param channel_id: The ID of the channel.
        :return: List of triggers for the specified channel.
        """
        triggers, error = db.select(
            model=Trigger,
            table="triggers",
            columns=["*"],
            conditions={"channel_id": channel_id}
        )
        if error:
            logger.error("Error al obtener los triggers: %s", error)
            return None, error
        return triggers, None


    @staticmethod
    def add(trigger: Trigger) -> tuple[Optional[Trigger], Optional[str]]:
        """
        Add a new trigger to the database.
        :param trigger: trigger to add.
        """
        _, error = db.insert(
            table="triggers",
            data=trigger.__dict__
        )
        if error:
            logger.error("Error al crear el trigger: %s", error)
            return None, error
        return trigger, None


    @staticmethod
    def delete_by_id(trigger_id: str) -> tuple[Optional[str], Optional[str]]:
        """
        Delete a trigger from the database.
        :param trigger: Trigger to delete.
        """
        # Check if trigger exists
        trigger, error = TriggersService.get_by_id(trigger_id)
        if error:
            logger.error("Error al obtener el trigger: %s", error)
            return None, error
        if not trigger:
            logger.error("Trigger no encontrado")
            return None, "Trigger no encontrado"

        _, error = db.delete(
            table="triggers",
            key="id",
            value=trigger_id
        )
        if error:
            logger.error("Error al eliminar el trigger: %s", error)
            return None, error
        return trigger_id, None


    @staticmethod
    def update(trigger: Trigger) -> tuple[Optional[Trigger], Optional[str]]:
        """
        Update a trigger in the database.
        :param trigger: Trigger to update.
        """
        _, error = db.upsert(
            table="triggers",
            data=trigger.__dict__,
            primary_key="id"
        )
        if error:
            logger.error("Error al actualizar el trigger: %s", error)
            return None, error
        return trigger, None
