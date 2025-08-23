"""Constantes para el módulo Echo"""

# Descripciones de comandos
COMMAND_ECHO_DESC = "Envía un mensaje a un canal específico o al canal actual"
COMMAND_EDIT_DESC = "Edita un mensaje enviado previamente con echo"
PARAM_TEXT_DESC = "El texto que se enviará al canal (o JSON del embed si enviar_embed=True)"
PARAM_CHANNEL_DESC = "El canal donde se enviará el mensaje (opcional, por defecto el canal actual)"
PARAM_EMBED_DESC = "Si el mensaje se enviará como un embed usando JSON (opcional)"
PARAM_MESSAGE_ID_DESC = "Enlace del mensaje a editar (opcional, si no se proporciona se mostrará un selector)"
PARAM_NEW_TEXT_DESC = "El nuevo texto para el mensaje (o JSON del embed si enviar_embed=True)"
PARAM_NEW_EMBED_DESC = "Si el nuevo mensaje será un embed usando JSON (opcional)"

# Mensajes de respuesta
SUCCESS_MESSAGE_SENT = "✅ Mensaje enviado correctamente al canal {channel}"
SUCCESS_EMBED_SENT = "✅ Embed enviado correctamente al canal {channel}"
SUCCESS_MESSAGE_SAVED = "✅ Mensaje guardado para edición futura (ID: {message_id})"
ERROR_NO_PERMISSIONS = "❌ No tienes permisos para enviar mensajes en este canal"
ERROR_SENDING_MESSAGE = "❌ Error al enviar el mensaje: {error}"
ERROR_INVALID_CHANNEL = "❌ El canal especificado no es válido"
ERROR_MESSAGE_TOO_LONG = "❌ El mensaje es demasiado largo (máximo 2000 caracteres)"
ERROR_INVALID_JSON = "❌ El JSON del embed no es válido. Formato esperado: {\"title\":\"...\",\"description\":\"...\",\"color\":123456}"
ERROR_EMBED_CREATION = "❌ Error al crear el embed: {error}"
ERROR_NO_ECHO_MESSAGES = "❌ No hay mensajes echo para editar en este servidor"
ERROR_ECHO_MESSAGE_NOT_FOUND = "❌ No se encontró el mensaje echo especificado"
ERROR_INVALID_MESSAGE_LINK = "❌ El enlace del mensaje no es válido"
ERROR_MESSAGE_NOT_FROM_BOT = "❌ Solo puedes editar mensajes enviados por el bot"
ERROR_MESSAGE_NOT_IN_DISCORD = "❌ El mensaje ya no existe en Discord"
ERROR_EDITING_MESSAGE = "❌ Error al editar el mensaje: {error}"

# Títulos y descripciones para embeds
TITLE_SELECT_MESSAGE_TO_EDIT = "Seleccionar Mensaje para Editar"
DESCRIPTION_SELECT_MESSAGE_TO_EDIT = "Selecciona uno de los últimos 10 mensajes echo del servidor para editar:"

# Mensajes de ayuda
HELP_MESSAGE_LINK_FORMAT = """
📌 **Formatos de enlace soportados:**
• `https://discord.com/channels/guild_id/channel_id/message_id`
• `https://discordapp.com/channels/guild_id/channel_id/message_id`
• Solo el ID del mensaje (se editará en el canal actual)

💡 **Tip:** Haz clic derecho en cualquier mensaje > "Copiar enlace del mensaje"
"""
