"""Constantes para el módulo Echo"""

# Descripciones de comandos
COMMAND_ECHO_DESC = "Envía un mensaje a un canal específico o al canal actual"
PARAM_TEXT_DESC = "El texto que se enviará al canal (o JSON del embed si enviar_embed=True)"
PARAM_CHANNEL_DESC = "El canal donde se enviará el mensaje (opcional, por defecto el canal actual)"
PARAM_EMBED_DESC = "Si el mensaje se enviará como un embed usando JSON (opcional)"

# Mensajes de respuesta
SUCCESS_MESSAGE_SENT = "✅ Mensaje enviado correctamente al canal {channel}"
SUCCESS_EMBED_SENT = "✅ Embed enviado correctamente al canal {channel}"
ERROR_NO_PERMISSIONS = "❌ No tienes permisos para enviar mensajes en este canal"
ERROR_SENDING_MESSAGE = "❌ Error al enviar el mensaje: {error}"
ERROR_INVALID_CHANNEL = "❌ El canal especificado no es válido"
ERROR_MESSAGE_TOO_LONG = "❌ El mensaje es demasiado largo (máximo 2000 caracteres)"
ERROR_INVALID_JSON = "❌ El JSON del embed no es válido. Formato esperado: {\"title\":\"...\",\"description\":\"...\",\"color\":123456}"
ERROR_EMBED_CREATION = "❌ Error al crear el embed: {error}"
