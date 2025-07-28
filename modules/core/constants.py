"""
Constantes de mensajes para el módulo core (utilidades generales)
"""

# Mensajes de error
ERROR_NO_PERMISSIONS_SEND = "No tengo permisos para enviar mensajes en {channel_name}"
ERROR_SENDING_MESSAGE = "Error al enviar mensaje a {channel_name}. Error: {error}"
ERROR_SENDING_TO_ADMIN = "Error al enviar el mensaje al admin: {error}"
ERROR_NO_ADMIN_PERMISSIONS = "No tengo permisos para enviar mensajes al admin"
ERROR_ADMIN_NOT_FOUND = "No se pudo encontrar al admin con ID {admin_id}"
ERROR_SENDING_PAGINATED = "Error al enviar el mensaje: {error}"
ERROR_COULD_NOT_SEND = "No se pudo enviar el mensaje."

# Mensajes informativos
INFO_NO_INFORMATION = "No hay información para mostrar."
INFO_MESSAGE_SENT_TO_ADMIN = "Mensaje enviado al admin: {message}"
INFO_NO_SEND_TO_ADMIN_WARNING = "No tengo permisos para enviar mensajes en {channel_name}"

# Mensajes de error generales
ERROR_PREFIX = "Error: {error}"
