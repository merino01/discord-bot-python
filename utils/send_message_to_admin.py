"""Send a message to the admin."""
from discord.ext import commands
from utils.logger import logger
from settings import admin_id, send_to_admin

async def send_message_to_admin(client: commands.Bot, message: str):
    """
    Send a message to the admin.
    """
    if not send_to_admin:
        return

    try:
        admin = await client.fetch_user(admin_id)
        if admin:
            await admin.send(message)
            logger.info("Mensaje enviado al admin: %s", message)
        else:
            logger.error("No se pudo encontrar al admin con ID %s", admin_id)
    except Exception as e:
        logger.error("Error al enviar el mensaje al admin: %s", e)
