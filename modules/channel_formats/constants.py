"""
Constantes de mensajes para el módulo de formatos de canales
"""

# Mensajes de error
ERROR_INVALID_REGEX = "❌ Formato inválido. Asegúrate de que sea una expresión regular válida"
ERROR_FORMAT_NOT_FOUND = "❌ No se ha encontrado el formato de canal con ID {id}"
ERROR_GETTING_FORMATS = "❌ Error al obtener los formatos de canal"
ERROR_DELETING_FORMAT = "❌ Error al eliminar el formato de canal"
ERROR_UPDATING_FORMAT = "❌ Error al actualizar el formato de canal"

# Mensajes de éxito
SUCCESS_FORMAT_ADDED = "✅ Formato de canal añadido: {channel} - `{format}`"
SUCCESS_FORMAT_DELETED = "🗑️ Formato de canal eliminado: `{id}`"
SUCCESS_FORMAT_EDITED = "✏️ Formato de canal editado exitosamente"

# Mensajes informativos
NO_FORMATS_FOUND = "📭 No hay formatos de canal configurados"
SHOWING_FORMATS = "📋 Mostrando {count} formatos de canal"

# Labels y títulos
TITLE_FORMAT_ID = "📝 Formato de canal {id}"
FIELD_CHANNEL = "📢 Canal"
FIELD_FORMAT = "🔧 Formato"

# Descripciones de comandos
COMMAND_CREATE_DESC = "➕ Añade un nuevo formato de canal"
COMMAND_LIST_DESC = "📋 Lista todos los formatos de canal"
COMMAND_DELETE_DESC = "🗑️ Elimina un formato de canal"
COMMAND_EDIT_DESC = "✏️ Edita un formato de canal"

# Descripciones de parámetros
PARAM_CHANNEL_DESC = "📢 Canal donde se aplicará el formato"
PARAM_FORMAT_DESC = "🔧 Formato que se aplicará al canal"
PARAM_FORMAT_ID_DESC = (
    "🆔 ID del formato de canal (opcional - se mostrará lista si no se proporciona)"
)
PARAM_LIST_CHANNEL_DESC = "📢 Listar formatos por canal"
PARAM_PERSISTENT_DESC = "📌 Hacer persistente"

# Constantes para vistas interactivas
VIEW_SELECT_FORMAT_TITLE = "🎯 Seleccionar Formato de Canal"
VIEW_SELECT_FORMAT_DESC = "👆 Selecciona el formato de canal que deseas gestionar:"

# Constantes para confirmaciones
CONFIRMATION_DELETE_TITLE = "✅ Formato Eliminado"
CONFIRMATION_DELETE_DESC = "🗑️ El formato de canal **{id}** ha sido eliminado exitosamente."
CONFIRMATION_EDIT_TITLE = "✅ Formato Editado"
CONFIRMATION_EDIT_DESC = "✏️ El formato de canal **{id}** ha sido editado exitosamente."

# Constantes para paginación
PAGE_PREVIOUS = "◀️ Anterior"
PAGE_NEXT = "Siguiente ▶️"
PAGE_INDICATOR = "📄 Página {current}/{total}"
PAGE_INFO = "📊 Página {current} de {total} | Mostrando {showing} de {total_items} formatos"
