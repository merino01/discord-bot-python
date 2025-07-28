"""
Constantes de mensajes para el módulo de mensajes automáticos
"""

# Mensajes de error
ERROR_CREATING_MESSAGE = "❌ Error al crear el mensaje automático"
ERROR_GETTING_MESSAGES = "❌ Error al obtener los mensajes automáticos"
ERROR_MESSAGE_NOT_FOUND = "❌ No se ha encontrado el mensaje automático con ID {id}"
ERROR_DELETING_MESSAGE = "❌ No se ha podido eliminar el mensaje automático con ID {id}"
ERROR_MUST_SPECIFY_CHANNEL_OR_CATEGORY = "❌ Debes especificar un **canal** o una **categoría**, pero no ambos."
ERROR_CANNOT_SPECIFY_BOTH = "❌ No puedes especificar tanto **canal** como **categoría**. Elige solo uno."

# Mensajes de éxito
SUCCESS_MESSAGE_CREATED = "✅ Mensaje automático creado en el canal {channel}"
SUCCESS_CATEGORY_MESSAGE_CREATED = "✅ Mensaje automático configurado para la categoría {category} - Se enviará al crear nuevos canales"
SUCCESS_MESSAGE_DELETED = "🗑️ Mensaje automático con ID **{id}** eliminado exitosamente"

# Mensajes informativos
NO_MESSAGES_FOUND = "📭 No hay mensajes automáticos configurados"
SHOWING_MESSAGES = "📋 Mostrando {count} mensajes automáticos"

# Labels y títulos
TITLE_MESSAGE_ID = "🤖 Mensaje automático {id}"
TITLE_MESSAGE_WITH_NAME = "🤖 {name}"
FIELD_CHANNEL = "📢 Canal"
FIELD_CATEGORY = "📁 Categoría" 
FIELD_MESSAGE = "💬 Mensaje"
FIELD_NAME = "🏷️ Nombre"
FIELD_INTERVAL = "⏰ Intervalo"
FIELD_TIME = "🕐 Hora"
FIELD_TYPE = "🎯 Tipo"

# Formato de texto
INTERVAL_FORMAT = "⏰ Cada {interval} {unit}"
TIME_FORMAT = "🕐 {hour}:{minute}"
TYPE_CHANNEL = "📢 Canal programado"
TYPE_CATEGORY = "📁 Al crear canal en categoría"

# Descripciones de comandos
COMMAND_CREATE_DESC = "➕ Crea un mensaje automático"
COMMAND_LIST_DESC = "📋 Lista todos los mensajes automáticos"
COMMAND_DELETE_DESC = "🗑️ Elimina un mensaje automático"

# Descripciones de parámetros
PARAM_CHANNEL_DESC = "📢 Canal donde se enviará el mensaje automático"
PARAM_CATEGORY_DESC = "📁 Categoría donde se enviará el mensaje al crear nuevos canales"
PARAM_MESSAGE_DESC = "💬 Mensaje automático a enviar"
PARAM_NAME_DESC = "🏷️ Nombre identificativo para el mensaje automático"
PARAM_INTERVAL_DESC = "⏰ Intervalo de tiempo entre mensajes"
PARAM_INTERVAL_TYPE_DESC = "⌚ Tipo de intervalo (segundos, minutos, horas)"
PARAM_HOUR_DESC = "🕐 Hora en la que se enviará el mensaje automático"
PARAM_MINUTE_DESC = "⏲️ Minuto en el que se enviará el mensaje automático"
PARAM_LIST_CHANNEL_DESC = "📢 Ver mensaje automático por canal"
PARAM_PERSISTENT_DESC = "📌 Hacer persistente"
PARAM_MESSAGE_ID_DESC = "🆔 ID del mensaje automático a eliminar (opcional - se mostrará lista si no se proporciona)"

# Traducciones de unidades de tiempo
TIME_TRANSLATIONS = {
    "seconds": "⚡ segundos",
    "minutes": "⏰ minutos", 
    "hours": "🕐 horas",
}

# Opciones de comando
CHOICE_SECONDS = "⚡ segundos"
CHOICE_MINUTES = "⏰ minutos"
CHOICE_HOURS = "🕐 horas"

# Constantes para vistas interactivas
VIEW_SELECT_MESSAGE_TITLE = "🎯 Seleccionar Mensaje Automático"
VIEW_SELECT_MESSAGE_DESC = "👆 Selecciona el mensaje automático que deseas gestionar:"

# Constantes para confirmaciones
CONFIRMATION_DELETE_TITLE = "✅ Mensaje Eliminado"
CONFIRMATION_DELETE_DESC = "🗑️ El mensaje automático **{id}** ha sido eliminado exitosamente."

# Constantes para paginación
PAGE_PREVIOUS = "◀️ Anterior"
PAGE_NEXT = "Siguiente ▶️"
PAGE_INDICATOR = "📄 Página {current}/{total}"
PAGE_INFO = "📊 Página {current} de {total} | Mostrando {showing} de {total_items} mensajes"
