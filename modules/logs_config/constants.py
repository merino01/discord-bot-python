"""
Constantes de mensajes para el módulo de configuración de logs
"""

# Mensajes de error
ERROR_NO_CHANNEL_FOR_ACTIVATION = "❌ No puedes activar los logs sin especificar un canal"
ERROR_UPDATING_LOG_CONFIG = "❌ Error al actualizar la configuración de logs"
ERROR_GETTING_LOG_CONFIGS = "❌ Error al obtener la configuración de logs"
ERROR_ACTIVATING_LOG = "❌ Ha habido un error al activar el {log_type}log"

# Mensajes de éxito
SUCCESS_LOG_ACTIVATED = "✅ {log_type}log activado en el canal <#{channel_id}>"
SUCCESS_LOG_DEACTIVATED = "🔇 {log_type}log desactivado exitosamente"

# Mensajes informativos
NO_LOGS_CONFIGURED = "📭 No hay logs configurados"

# Labels y títulos para embeds
TITLE_LOG_TYPE = "📊 {log_type}log"
FIELD_CHANNEL = "📢 Canal"
FIELD_STATUS = "🔄 Estado"

# Valores para embeds
VALUE_ENABLED = "🟢 activado"
VALUE_DISABLED = "🔴 desactivado"

# Descripciones de comandos
COMMAND_CONFIG_DESC = "⚙️ Configura los logs del servidor"
COMMAND_LIST_DESC = "📋 Muestra la configuración de los logs"

# Descripciones de parámetros
PARAM_LOG_TYPE_DESC = "📊 Tipo de log a configurar"
PARAM_ACTIVATE_DESC = "🔄 Activar o desactivar los logs"
PARAM_CHANNEL_DESC = "📢 Canal donde se enviarán los logs"
PARAM_PERSISTENT_DESC = "📌 Hacer la respuesta persistente"

# Opciones de tipos de log
CHOICE_CHAT = "💬 Mensajes"
CHOICE_VOICE = "🔊 Voz"
CHOICE_MEMBERS = "👥 Miembros"
CHOICE_JOIN_LEAVE = "🚪 Entradas/Salidas"

# Valores de tipos de log
LOG_TYPE_CHAT = "💬 chat"
LOG_TYPE_VOICE = "🔊 voice"
LOG_TYPE_MEMBERS = "👥 members"
LOG_TYPE_JOIN_LEAVE = "🚪 join_leave"
