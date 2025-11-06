"""triggers util functions."""

import re
from asyncio import sleep
from typing import Optional
from discord import Forbidden, Embed, Color
from modules.core import logger
from .service import TriggersService
from .models import TriggerPosition, Trigger
from . import constants
from .views import TriggerSelectView, create_trigger_selection_embed


def _find_trigger(channel_id: int, text: str) -> Optional[Trigger]:
    """
    Searches for a trigger in the message.
    The function iterates through the triggers and checks if any of them match the message.
    If a trigger is found, it returns the trigger.
    If no trigger is found, it returns None.

    Args:
        channel_id (int): The ID of the channel where the message was sent.
        text (str): The message content to check.
    Returns:
        Optional[dict]: The trigger that was found, or None if no trigger was found.
    """

    def activates_trigger(trigger: Trigger) -> bool:
        position = trigger.position
        key = trigger.key

        if position == TriggerPosition.CONTAINS.value:
            return key in text
        if position == TriggerPosition.STARTS_WITH.value:
            return text.startswith(key)
        if position == TriggerPosition.ENDS_WITH.value:
            return text.endswith(key)
        if position == TriggerPosition.EXACT_MATCH.value:
            return text == key
        if position == TriggerPosition.TEXT_BETWEEN.value:
            words = [word for word in key.split() if word.strip()]
            pattern = ".*".join(words)
            return bool(re.search(pattern, text, re.IGNORECASE))
        if position == TriggerPosition.REGEX.value:
            return bool(re.search(key, text, re.IGNORECASE))

        return False

    service = TriggersService()
    triggers, error = service.get_all_by_channel_id(channel_id)
    if error:
        logger.error("Error al obtener los triggers: %s", error)
        return None

    if not triggers:
        return None

    for trigger in triggers:
        if activates_trigger(trigger):
            return trigger

    return None


async def check_trigger(message) -> None:
    """
    Comprueba si el mensaje es un trigger.

    Args:
        message (str): The message to check.

    Returns:
        None
    """
    matched_trigger = _find_trigger(message.channel.id, message.content)
    if not matched_trigger:
        return

    log_info = {
        "user_id": message.author.id,
        "user_name": message.author.name,
        "content": message.content,
        "channel_id": message.channel.id,
        "channel_name": message.channel.name,
    }
    logger.info("Trigger activado")
    logger.info(log_info)

    _delete_message = matched_trigger.delete_message
    _reply = matched_trigger.response
    _reply_timeout = matched_trigger.response_timeout

    async def delete_message(message):
        try:
            await message.delete()
        except Forbidden:
            logger.warning("No tengo permisos para eliminar el mensaje")

    if not _reply and _delete_message:
        if _reply_timeout:
            await sleep(_reply_timeout)
        await delete_message(message)
        return
    if not _reply:
        return

    if _reply_timeout:
        await sleep(_reply_timeout)

    await message.reply(content=_reply)
    if _delete_message:
        await delete_message(message)


async def show_trigger_selection_for_delete(interaction, service: TriggersService):
    """Mostrar vista de selección para eliminar trigger"""
    triggers, error = service.get_all_by_channel_id(interaction.channel_id)
    if error:
        await interaction.response.send_message(content=error, ephemeral=True)
        return

    if not triggers:
        await interaction.response.send_message(
            content=constants.NO_TRIGGERS_TO_SELECT, ephemeral=True
        )
        return

    async def delete_callback(button_interaction, trigger_id: str):
        # Eliminar el trigger seleccionado
        _, error = service.delete_by_id(trigger_id)
        if error:
            await button_interaction.response.send_message(content=error, ephemeral=True)
            return

        # Crear embed de confirmación
        success_embed = Embed(
            title=constants.CONFIRMATION_TRIGGER_DELETED,
            description=constants.SUCCESS_TRIGGER_DELETED,
            color=Color.green(),
        )

        # Editar el mensaje original con la confirmación
        await button_interaction.response.edit_message(
            embed=success_embed, view=None  # Eliminar la vista con botones
        )

    # Crear vista con botones
    view = TriggerSelectView(triggers, delete_callback, constants.SELECT_TRIGGER_TO_DELETE)
    embed = create_trigger_selection_embed(triggers, constants.SELECT_TRIGGER_TO_DELETE)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def show_trigger_selection_for_edit(interaction, service: TriggersService, **edit_params):
    """Mostrar vista de selección para editar trigger"""
    triggers, error = service.get_all_by_channel_id(interaction.channel_id)
    if error:
        await interaction.response.send_message(content=error, ephemeral=True)
        return

    if not triggers:
        await interaction.response.send_message(
            content=constants.NO_TRIGGERS_TO_SELECT, ephemeral=True
        )
        return

    async def edit_callback(button_interaction, trigger_id: str):
        # Editar el trigger seleccionado
        result = _edit_trigger_internal(service, trigger_id, **edit_params)

        if result["success"]:
            # Crear embed de confirmación
            success_embed = Embed(
                title=constants.CONFIRMATION_TRIGGER_EDITED,
                description=result["message"],
                color=Color.green(),
            )

            # Editar el mensaje original con la confirmación
            await button_interaction.response.edit_message(
                embed=success_embed, view=None  # Eliminar la vista con botones
            )
        else:
            # Si hay error, mostrar mensaje de error
            await button_interaction.response.send_message(content=result["error"], ephemeral=True)

    # Crear vista con botones
    view = TriggerSelectView(triggers, edit_callback, constants.SELECT_TRIGGER_TO_EDIT)
    embed = create_trigger_selection_embed(triggers, constants.SELECT_TRIGGER_TO_EDIT)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def edit_trigger_by_id(interaction, service: TriggersService, id_trigger: str, **edit_params):
    """Editar un trigger específico por ID (comando directo)"""
    result = _edit_trigger_internal(service, id_trigger, **edit_params)

    if result["success"]:
        await interaction.response.send_message(content=result["message"], ephemeral=True)
    else:
        await interaction.response.send_message(content=result["error"], ephemeral=True)


def _edit_trigger_internal(service: TriggersService, id_trigger: str, **edit_params):
    """Función interna para editar trigger sin manejar la respuesta de interaction"""
    trigger, error = service.get_by_id(id_trigger)
    if error:
        return {"success": False, "error": error}
    if not trigger:
        return {"success": False, "error": constants.ERROR_TRIGGER_NOT_FOUND.format(id=id_trigger)}

    # Actualizamos los campos que se han pasado como parámetros
    canal = edit_params.get('canal')
    borrar_mensaje = edit_params.get('borrar_mensaje')
    respuesta = edit_params.get('respuesta')
    clave = edit_params.get('clave')
    posicion = edit_params.get('posicion')
    tiempo_respuesta = edit_params.get('tiempo_respuesta')

    if canal:
        trigger.channel_id = canal.id
    if borrar_mensaje is not None:
        trigger.delete_message = borrar_mensaje
    if respuesta:
        trigger.response = respuesta
    if clave:
        trigger.key = clave
    if posicion:
        trigger.position = posicion
    if tiempo_respuesta:
        trigger.response_timeout = tiempo_respuesta

    _, error = service.update(trigger)
    if error:
        return {"success": False, "error": error}

    return {"success": True, "message": constants.SUCCESS_TRIGGER_EDITED}
