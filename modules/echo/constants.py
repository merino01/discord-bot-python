"""Constantes para el módulo Echo"""

# Descripciones de comandos
COMMAND_ECHO_DESC = "Envía un mensaje a un canal específico"
PARAM_TEXT_DESC = "El texto que se enviará al canal"
PARAM_CHANNEL_DESC = "El canal donde se enviará el mensaje"

# Mensajes de respuesta
SUCCESS_MESSAGE_SENT = "✅ Mensaje enviado correctamente al canal {channel}"
ERROR_NO_PERMISSIONS = "❌ No tienes permisos para enviar mensajes en este canal"
ERROR_SENDING_MESSAGE = "❌ Error al enviar el mensaje: {error}"
ERROR_INVALID_CHANNEL = "❌ El canal especificado no es válido"
ERROR_MESSAGE_TOO_LONG = "❌ El mensaje es demasiado largo (máximo 2000 caracteres)"
