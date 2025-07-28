from datetime import datetime, time
from typing import Dict
from discord.ext import tasks
from modules.core import logger, send_message_to_channel
from .service import AutomaticMessagesService
from .models import AutomaticMessage
from .text_processor import process_message_text

message_tasks: Dict[str, tasks.Loop] = {}


def create_message_task(client, message_config: AutomaticMessage):
    if message_config.is_category_based:
        return None
    
    # Preparar los argumentos del decorador basados en la configuración
    decorator_kwargs = {}

    if message_config.interval is not None:
        # Si se define un intervalo, usamos el decorador con el parámetro adecuado
        interval_unit = message_config.interval_unit

        # Asegurarnos de que el intervalo sea un tipo válido
        if interval_unit and interval_unit not in ["seconds", "minutes", "hours"]:
            logger.error(f"Tipo de intervalo no válido: {interval_unit}")
            return None

        decorator_kwargs[interval_unit] = message_config.interval

        @tasks.loop(**decorator_kwargs)
        async def send_message_interval():
            channel = await client.fetch_channel(message_config.channel_id)
            if not channel or not channel.permissions_for(channel.guild.me).send_messages:
                return

            # Procesar el texto para interpretar \n como saltos de línea
            processed_text = process_message_text(message_config.text)
            await send_message_to_channel(channel, content=processed_text)
            logger.info("Mensaje automático enviado a %s (intervalo)", channel.name)

    else:
        # Si no se define un intervalo, usamos la hora exacta
        if message_config.hour is None or message_config.minute is None:
            return

        target_time = time(
            hour=message_config.hour,
            minute=message_config.minute
        )

        @tasks.loop(seconds=31)
        async def send_message_at_specified_time():
            now = datetime.now().time()
            if now.hour == target_time.hour and now.minute == target_time.minute:
                channel = await client.fetch_channel(message_config.channel_id)
                if not channel or not channel.permissions_for(channel.guild.me).send_messages:
                    return

                # Procesar el texto para interpretar \n como saltos de línea
                processed_text = process_message_text(message_config.text)
                await send_message_to_channel(channel, content=processed_text)
                logger.info(f"Mensaje automático enviado a {channel.name} (hora exacta)")

    if hasattr(message_config, "interval"):
        return send_message_interval
    else:
        return send_message_at_specified_time


def stop_all_tasks():
    for task_id, task in message_tasks.items():
        if task.is_running():
            task.stop()
            logger.info("Tarea %s detenida", task_id)

    message_tasks.clear()  # Limpiar el diccionario de tareas
    logger.info("Todas las tareas automáticas han sido detenidas")


def stop_task_by_id(task_id: str):
    task = message_tasks.get(task_id)
    if task and task.is_running():
        task.stop()
        logger.info("Tarea %s detenida", task_id)
        del message_tasks[task_id]
    else:
        logger.warning("No se encontró la tarea %s o ya está detenida", task_id)


def start_task(client, automatic_message_config: AutomaticMessage):
    if automatic_message_config.is_category_based:
        return
    
    task = create_message_task(client, automatic_message_config)

    if task is None:
        return

    message_tasks[str(automatic_message_config.id)] = task

    # Iniciar la tarea
    task.start()

    log_info = {
        "channel_id": automatic_message_config.channel_id,
        "message_content": automatic_message_config.text,
    }
    if automatic_message_config.interval:
        interval_log_text = f"{automatic_message_config.interval} "
        interval_log_text += f"{automatic_message_config.interval_unit}"
        log_info["interval"] = interval_log_text
    else:
        log_info["time"] = f"{automatic_message_config.hour}:{automatic_message_config.minute}"
    logger.info("Mensaje automático programado")
    logger.info(log_info)


def setup_automatic_messages(client):
    service = AutomaticMessagesService()
    automatic_messages, error = service.get_all()
    if error:
        logger.error("Error al obtener los mensajes automáticos: %s", error)
        return
    if not automatic_messages:
        logger.info("No hay mensajes automáticos configurados")
        return

    for msg_config in automatic_messages:
        start_task(client, msg_config)
