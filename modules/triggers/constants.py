"""
Constantes de mensajes para el módulo de triggers
"""

# Mensajes de error
ERROR_CREATING_TRIGGER = "❌ Error al crear el trigger"
ERROR_GETTING_TRIGGERS = "❌ Error al obtener los triggers"
ERROR_TRIGGER_NOT_FOUND = "❌ No se ha encontrado el trigger con ID {id}."
ERROR_DELETING_TRIGGER = "❌ Error al eliminar el trigger"
ERROR_UPDATING_TRIGGER = "❌ Error al actualizar el trigger"

# Mensajes de éxito
SUCCESS_TRIGGER_CREATED = "✅ Trigger creado exitosamente"
SUCCESS_TRIGGER_DELETED = "🗑️ Trigger eliminado correctamente"
SUCCESS_TRIGGER_EDITED = "✏️ Trigger editado con éxito"

# Mensajes informativos
NO_TRIGGERS_FOUND = "📭 No hay triggers configurados."
SHOWING_TRIGGERS = "📋 Lista de triggers ({count})"

# Traducciones de posiciones
TRIGGER_POSITIONS_TRANSLATIONS = {
    "contains": "🔍 Contiene",
    "starts_with": "▶️ Empieza por",
    "ends_with": "◀️ Termina por",
    "equal": "🎯 Igual a",
    "text_between": "↔️ Texto entre",
    "regex": "🔧 Expresión regular",
}

# Labels y títulos para embeds
TITLE_TRIGGER_ID = "🎯 Trigger {id}"
FIELD_CHANNEL = "📢 Canal"
FIELD_DELETE_MESSAGE = "🗑️ Borrar mensaje"
FIELD_RESPONSE = "💬 Respuesta"
FIELD_KEYWORD = "🔑 Palabra clave"
FIELD_POSITION = "📍 Posición"
FIELD_TIMEOUT = "⏱️ Tiempo de espera"

# Valores para embeds
VALUE_YES = "Sí"
VALUE_NO = "No"
VALUE_NONE = "-"
VALUE_INVALID = "invalido"
VALUE_TIMEOUT_SECONDS = "{timeout} segundos"
EMBED_DESCRIPTION = "Detalles del trigger"

# Descripciones de comandos
COMMAND_CREATE_DESC = "➕ Añade un trigger"
COMMAND_LIST_DESC = "📋 Lista de triggers"
COMMAND_DELETE_DESC = "🗑️ Eliminar un trigger"
COMMAND_EDIT_DESC = "✏️ Editar un trigger"

# Mensajes para selección interactiva
SELECT_TRIGGER_TO_DELETE = "🗑️ Seleccionar trigger para eliminar"
SELECT_TRIGGER_TO_EDIT = "✏️ Seleccionar trigger para editar"
NO_TRIGGERS_TO_SELECT = "📭 No hay triggers disponibles para seleccionar."
TRIGGER_SELECTION_EXPIRED = "⏰ La selección de trigger ha expirado."

# Mensajes de paginación
PAGE_INDICATOR = "📄 Página {current}/{total}"
PAGINATION_INFO = "📊 Página {current} de {total} | Total: {count} triggers"

# Mensajes para vistas interactivas
VIEW_SELECTION_DESCRIPTION = "👆 Haz clic en uno de los botones para seleccionar un trigger:"
VIEW_SUMMARY_TITLE = "📊 Resumen"
VIEW_SUMMARY_TEXT = "**Total de triggers:** {total}\n**En esta página:** {in_page}"
VIEW_PAGINATION_TITLE = "📄 Paginación"
VIEW_INSTRUCTIONS_TITLE = "ℹ️ Instrucciones"
VIEW_INSTRUCTIONS_TEXT = "• Usa los botones de **◀️Anterior/Siguiente▶️** para navegar\n• 👆 Haz clic en cualquier trigger para seleccionarlo"
VIEW_BUTTON_PREVIOUS = "◀️ Anterior"
VIEW_BUTTON_NEXT = "Siguiente ▶️"
VIEW_PAGE_TITLE = "{action} - 📄 Página {current}/{total}"

# Títulos de confirmación
CONFIRMATION_TRIGGER_DELETED = "✅ Trigger Eliminado"
CONFIRMATION_TRIGGER_EDITED = "✅ Trigger Editado"

# Descripciones de parámetros
PARAM_CHANNEL_DESC = "Canal donde se verificará el trigger"
PARAM_DELETE_MESSAGE_DESC = "Configurar si se debe borrar el mensaje que activa el trigger"
PARAM_RESPONSE_DESC = "Respuesta del bot al trigger"
PARAM_KEYWORD_DESC = "Palabra clave que activa el trigger"
PARAM_POSITION_DESC = "Posición de la palabra clave en el mensaje"
PARAM_TIMEOUT_DESC = "Tiempo de espera para la respuesta del bot"
PARAM_TRIGGER_ID_DESC = (
    "ID del trigger (opcional - si no se proporciona, se mostrará una lista para seleccionar)"
)
PARAM_TRIGGER_DELETE_ID_DESC = (
    "ID del trigger (opcional - si no se proporciona, se mostrará una lista para seleccionar)"
)
PARAM_LIST_CHANNEL_DESC = "Lista de triggers por canal"
PARAM_PERSISTENT_DESC = "Hacer la lista persistente"

# Nombres de opciones para las posiciones
CHOICE_CONTAINS = "🔍 Contiene"
CHOICE_STARTS_WITH = "▶️ Empieza por"
CHOICE_ENDS_WITH = "◀️ Termina por"
CHOICE_EXACT_MATCH = "🎯 Igual a"
CHOICE_TEXT_BETWEEN = "↔️ Texto entre"
CHOICE_REGEX = "🔧 Expresión regular"
