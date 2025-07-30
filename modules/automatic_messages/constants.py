"""
Constantes de mensajes para el módulo de mensajes automáticos
"""

# Mensajes de error
ERROR_CREATING_MESSAGE = "❌ Error al crear el mensaje automático"
ERROR_GETTING_MESSAGES = "❌ Error al obtener los mensajes automáticos"
ERROR_MESSAGE_NOT_FOUND = "❌ No se ha encontrado el mensaje automático con ID {id}"
ERROR_DELETING_MESSAGE = "❌ Error al eliminar el mensaje automático"
ERROR_UPDATING_MESSAGE = "❌ Error al actualizar el mensaje automático"
ERROR_INVALID_INTERVAL = "❌ El intervalo debe ser un número positivo"
ERROR_INVALID_TIME = "❌ La hora debe estar entre 0-23 y los minutos entre 0-59"
ERROR_INVALID_CHANNEL_OR_CATEGORY = "❌ Debes especificar un canal o una categoría, pero no ambos"
ERROR_MISSING_REQUIRED_FIELDS = "❌ Faltan campos obligatorios para este tipo de programación"
ERROR_INVALID_CRON = "❌ Expresión cron inválida"
ERROR_PERMISSION_DENIED = "❌ No tienes permisos para usar este comando"

# Mensajes de éxito
SUCCESS_MESSAGE_CREATED = "✅ Mensaje automático creado exitosamente"
SUCCESS_MESSAGE_DELETED = "🗑️ Mensaje automático eliminado correctamente"
SUCCESS_MESSAGE_EDITED = "✏️ Mensaje automático editado con éxito"

# Mensajes informativos
NO_MESSAGES_FOUND = "📭 No hay mensajes automáticos configurados"
SHOWING_MESSAGES = "📋 Lista de mensajes automáticos ({count})"
CONFIRM_DELETE = "⚠️ ¿Estás seguro de que quieres eliminar este mensaje automático?"
SELECT_MESSAGE_TO_DELETE = "🗑️ Selecciona el mensaje automático que deseas eliminar:"
SELECT_MESSAGE_TO_VIEW = "👁️ Selecciona el mensaje automático que deseas ver:"

# Traducciones de tipos de programación
SCHEDULE_TYPE_TRANSLATIONS = {
    "interval": "⏰ Por intervalo",
    "daily": "📅 Diario",
    "weekly": "📆 Semanal", 
    "custom": "🔧 Personalizado (cron)",
    "on_channel_create": "🆕 Al crear canal"
}

# Traducciones de unidades de intervalo
INTERVAL_UNIT_TRANSLATIONS = {
    "seconds": "segundos",
    "minutes": "minutos",
    "hours": "horas"
}

# Traducciones de días de la semana
WEEKDAY_TRANSLATIONS = {
    0: "Lunes",
    1: "Martes", 
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"
}

# Labels y títulos para embeds
TITLE_MESSAGE_ID = "📨 Mensaje {name}"
FIELD_CHANNEL = "📢 Canal"
FIELD_CATEGORY = "📁 Categoría"
FIELD_TEXT = "💬 Texto"
FIELD_SCHEDULE_TYPE = "⏰ Tipo de programación"
FIELD_INTERVAL = "⏳ Intervalo"
FIELD_TIME = "🕐 Hora"
FIELD_WEEKDAYS = "📅 Días de la semana"
FIELD_CRON = "⚙️ Expresión cron"

# Valores para embeds
VALUE_NONE = "-"
VALUE_INVALID = "inválido"
VALUE_EVERY_X = "Cada {interval} {unit}"
VALUE_AT_TIME = "A las {hour:02d}:{minute:02d}"
VALUE_DAILY_AT = "Todos los días a las {hour:02d}:{minute:02d}"
VALUE_WEEKLY_AT = "Los {days} a las {hour:02d}:{minute:02d}"
EMBED_DESCRIPTION = "Detalles del mensaje automático"

# Descripciones de comandos
COMMAND_PROGRAM_DESC = "➕ Programa un nuevo mensaje automático"
COMMAND_LIST_DESC = "📋 Lista los mensajes automáticos configurados"
COMMAND_DELETE_DESC = "🗑️ Elimina un mensaje automático"

# Descripciones de parámetros
PARAM_NAME_DESC = "Nombre descriptivo para el mensaje automático"
PARAM_TEXT_DESC = "Texto del mensaje que se enviará"
PARAM_CHANNEL_DESC = "Canal donde se enviará el mensaje"
PARAM_CATEGORY_DESC = "Categoría donde se enviará el mensaje al crear canales"
PARAM_SCHEDULE_TYPE_DESC = "Tipo de programación del mensaje"
PARAM_INTERVAL_DESC = "Intervalo numérico (para tipo intervalo)"
PARAM_INTERVAL_UNIT_DESC = "Unidad del intervalo (segundos, minutos, horas)"
PARAM_HOUR_DESC = "Hora del día (0-23)"
PARAM_MINUTE_DESC = "Minuto de la hora (0-59)"
PARAM_CRON_DESC = "Expresión cron personalizada"

# Opciones para selects
SELECT_PLACEHOLDER_DELETE = "Selecciona un mensaje para eliminar..."
SELECT_PLACEHOLDER_VIEW = "Selecciona un mensaje para ver..."

# Botones
BUTTON_CONFIRM_DELETE = "✅ Confirmar eliminación"
BUTTON_CANCEL_DELETE = "❌ Cancelar"

# Labels para inputs comunes
INPUT_HOUR_LABEL = "Hora (0-23)"
INPUT_MINUTE_LABEL = "Minuto (0-59)"
INPUT_MINUTE_PLACEHOLDER = "Ej: 30"

# Límites
MAX_MESSAGE_LENGTH = 2000
MAX_NAME_LENGTH = 100
MAX_MESSAGES_PER_PAGE = 10

# Emojis
EMOJI_SUCCESS = "✅"
EMOJI_ERROR = "❌"
EMOJI_WARNING = "⚠️"
EMOJI_INFO = "ℹ️"
EMOJI_LOADING = "⏳"
EMOJI_MESSAGE = "📨"
EMOJI_CHANNEL = "📢"
EMOJI_CATEGORY = "📁"
EMOJI_TIME = "🕐"
EMOJI_CALENDAR = "📅"

# Textos de interfaz - MessageBuilderView
TITLE_CONFIGURE_MESSAGE = "🎨 Configurar Mensaje Automático"
DESC_CONFIGURE_MESSAGE = "Personaliza tu mensaje automático añadiendo contenido:"
FIELD_CURRENT_CONFIG = "📋 Configuración Actual"
FIELD_INSTRUCTIONS = "📖 Instrucciones"

# Textos para configuración actual
TEXT_DESTINATION = "**📍 Destino:** {destination}"
TEXT_TYPE = "**⏰ Tipo:** {type}"
TEXT_NAME = "**📝 Nombre:** {name}"
TEXT_NO_NAME = "Sin nombre"
TEXT_STATUS = "**Estado:** {status}"
TEXT_NO_CONTENT = "Sin contenido configurado"

# Instrucciones de botones
INSTRUCTION_ADD_TEXT = "1. **📝 Añadir Texto** - Contenido principal del mensaje"
INSTRUCTION_ADD_EMBED = "2. **🎨 Añadir Embed** - Mensaje con formato enriquecido (incluye imagen del embed)"
INSTRUCTION_ADD_IMAGE = "3. **🖼️ Imagen Attachment** - Imagen independiente como adjunto"
INSTRUCTION_COMPLETE = "4. **✅ Completar** - Finalizar y programar el mensaje"

# Nombres de tipos de programación (app_commands.Choice)
CHOICE_INTERVAL = "⏰ Cada cierto tiempo"
CHOICE_DAILY = "📅 Todos los días"
CHOICE_WEEKLY = "📆 Días específicos"
CHOICE_ON_CHANNEL_CREATE = "🆕 Al crear canales"

# Traducciones de tipos para display
DISPLAY_INTERVAL = "⏰ Cada cierto tiempo"
DISPLAY_DAILY = "📅 Todos los días"
DISPLAY_WEEKLY = "📆 Días específicos"
DISPLAY_ON_CHANNEL_CREATE = "🆕 Al crear canales"

# Parámetros y descripciones
DESC_DESTINATION_PARAM = "Canal o categoría donde se enviará el mensaje"
ERROR_NAME_TOO_LONG = "El nombre no puede exceder {max_length} caracteres"
ERROR_INVALID_DESTINATION = "El destino debe ser un canal de texto o una categoría."
ERROR_CATEGORY_REQUIRED = "Para 'Al crear canales' debes seleccionar una categoría, no un canal."
ERROR_INVALID_INTERVAL_UNIT = "Unidad de intervalo inválida"

# Textos de modales y vistas
TITLE_MESSAGE_TEXT_MODAL = "📝 Texto del mensaje automático"
LABEL_MESSAGE_TEXT = "Texto del mensaje"
PLACEHOLDER_MESSAGE_TEXT = "Escribe aquí el texto del mensaje automático..."

# Textos de botones
BUTTON_ADD_TEXT = "📝 Añadir Texto"
BUTTON_ADD_EMBED = "🎨 Añadir Embed"
BUTTON_ADD_IMAGE = "🖼️ Imagen Attachment"
BUTTON_COMPLETE = "✅ Completar"

# Textos de MessageBuilderView
BUTTON_SIMPLE_MESSAGE = "📝 Mensaje Simple"
BUTTON_CREATE_EMBED = "🎨 Crear Embed"
BUTTON_ADD_IMAGE_OLD = "🖼️ Añadir Imagen"
BUTTON_EMBED_IMAGE = "✨ Embed + Imagen"

# Textos de configuración de mensajes
TITLE_CONFIGURE_MESSAGE_TYPE = "🎨 Configurar mensaje"
DESC_MESSAGE_PREVIEW = "**Texto del mensaje:**\n```{preview}```"
TEXT_NO_TEXT_PREVIEW = "(Sin texto - solo embed/imagen)"

# Textos de programación
TITLE_CONFIGURE_SCHEDULE = "⚙️ Configurar programación"
DESC_SCHEDULE_CONFIG = "**Texto del mensaje:**\n```{preview}```\n\nAhora configura cuándo se debe enviar el mensaje:"
TEXT_AUTO_SEND_CHANNEL_CREATE = "🆕 Se enviará automáticamente en cada canal nuevo creado en la categoría."

# Textos de mensajes de fallback
MSG_FALLBACK_DEFAULT_NAME = "Mensaje {id}"
ERROR_CREATING_MESSAGE_GENERIC = "Error creando el mensaje: {error}"

# Textos para validación
ERROR_MISSING_CONTENT = "El mensaje debe tener al menos texto, embed o imagen"
ERROR_EMBED_MISSING_CONTENT = "El embed debe tener al menos un título o descripción"

# Textos para resumen de configuración
SUMMARY_TEXT_CONTENT = "📝 **Texto:** {preview}"
SUMMARY_EMBED_CONTENT = "🎨 **Embed:** {title}{image_indicator}"
SUMMARY_ATTACHMENT_IMAGE = "🖼️ **Imagen Attachment:** Configurada"
SUMMARY_EMBED_IMAGE_INDICATOR = " + imagen"
SUMMARY_NO_CONTENT = "❌ **Sin contenido configurado**"
TEXT_READY_TO_SCHEDULE = "¡Listo para programar!"

# Textos para modales de configuración
TITLE_EMBED_BUILDER = "🎨 Configurar Embed"
LABEL_EMBED_TITLE = "Título del embed"
PLACEHOLDER_EMBED_TITLE = "Título principal del embed"
LABEL_EMBED_DESCRIPTION = "Descripción del embed"
PLACEHOLDER_EMBED_DESCRIPTION = "Contenido del embed..."
LABEL_EMBED_COLOR = "Color del embed"
PLACEHOLDER_EMBED_COLOR = "blue, red, green, #FF0000..."
LABEL_EMBED_IMAGE = "Imagen del embed (URL)"
PLACEHOLDER_EMBED_IMAGE = "https://ejemplo.com/imagen.png"

TITLE_IMAGE_BUILDER = "🖼️ Configurar Imagen Attachment"
LABEL_IMAGE_URL = "URL de la imagen"
PLACEHOLDER_IMAGE_URL = "https://ejemplo.com/imagen.png"

# Textos para botones de intervalo
BUTTON_INTERVAL_1MIN = "1 minuto"
BUTTON_INTERVAL_5MIN = "5 minutos"
BUTTON_INTERVAL_10MIN = "10 minutos"
BUTTON_INTERVAL_30MIN = "30 minutos"
BUTTON_INTERVAL_1HOUR = "1 hora"
BUTTON_INTERVAL_CUSTOM = "⚙️ Personalizado"

TITLE_CUSTOM_INTERVAL = "Intervalo Personalizado"
LABEL_INTERVAL_NUMBER = "Número"
PLACEHOLDER_INTERVAL_NUMBER = "Ej: 45"
LABEL_INTERVAL_UNIT = "Unidad"

# Textos para configuración de tiempo
TITLE_TIME_CONFIG = "🕐 Configurar Hora"
LABEL_HOUR = "Hora (0-23)"
PLACEHOLDER_HOUR = "Ej: 14"
LABEL_MINUTE = "Minuto (0-59)"
PLACEHOLDER_MINUTE = "Ej: 30"

# Textos para días de la semana
TITLE_WEEKLY_CONFIG = "📅 Configurar Días de la Semana"
DESC_WEEKLY_CONFIG = "Selecciona los días en que se enviará el mensaje:"
BUTTON_MONDAY = "Lunes"
BUTTON_TUESDAY = "Martes"
BUTTON_WEDNESDAY = "Miércoles"
BUTTON_THURSDAY = "Jueves"
BUTTON_FRIDAY = "Viernes"
BUTTON_SATURDAY = "Sábado"
BUTTON_SUNDAY = "Domingo"

# Textos adicionales para completar views.py
PLACEHOLDER_EMBED_DESCRIPTION_FULL = "Descripción completa del embed..."
TITLE_SCHEDULE_MESSAGE = "Programar Mensaje Automático"
PLACEHOLDER_MESSAGE_TEXT = "Escribe aquí el texto que se enviará..."
LABEL_INTERVAL_NUMBER_SIMPLE = "Intervalo (número)"
CATEGORY_UNKNOWN = "Categoría desconocida"
CATEGORY_PREFIX = "Categoría: "

# Títulos de error estándar
TITLE_ERROR_EMOJI = "❌ Error"
BUTTON_CONFIRM_DAYS = "✅ Confirmar días"

# Mensajes de éxito con formato
SUCCESS_INTERVAL_MESSAGE = "⏰ Se enviará cada {interval} {unit}"
SUCCESS_DAILY_MESSAGE = "📅 Se enviará todos los días a las {hour:02d}:{minute:02d}"
SUCCESS_WEEKLY_MESSAGE = "📆 Se enviará los {days} a las {hour:02d}:{minute:02d}"

# Textos de error comunes
ERROR_MODAL_SUBMIT = "❌ Error: {error}"

# Títulos de modales faltantes
TITLE_INTERVAL_CONFIG = "Configurar Intervalo"
TITLE_DAILY_CONFIG = "Configurar Programación Diaria"
TITLE_TIME_CONFIG_MODAL = "Configurar Hora"
TITLE_WEEKLY_CONFIG_MODAL = "Configurar Programación Semanal"
TITLE_SELECT_DAYS = "Seleccionar Días"
TITLE_CONFIG_COMPLETED = "✅ Configuración Completada"
TITLE_CONFIG_PROGRAMMING = "⚙️ Configurar Programación"
TITLE_CONFIG_CANCELLED = "❌ Configuración Cancelada"
TITLE_MESSAGE_BUILDER = "🎨 Configurar Mensaje Automático"
TITLE_TEXT_CONFIG = "📝 Configurar Texto del Mensaje"
TITLE_EMBED_CONFIG_MODAL = "🎨 Configurar Embed"
TITLE_IMAGE_CONFIG = "🖼️ Configurar Imagen (Attachment)"

# Labels faltantes
LABEL_MESSAGE_NAME = "Nombre del mensaje"
LABEL_MESSAGE_TEXT = "Texto del mensaje"
LABEL_SECONDS = "Segundos"
LABEL_MINUTES = "Minutos"
LABEL_HOURS = "Horas"
LABEL_ADD_TEXT = "📝 Añadir Texto"
LABEL_ADD_EMBED = "🎨 Añadir Embed"
LABEL_IMAGE_ATTACHMENT = "🖼️ Imagen Attachment"
LABEL_COMPLETE = "✅ Completar"
LABEL_CANCEL = "❌ Cancelar"
LABEL_EMBED_TITLE_OPTIONAL = "Título del embed (opcional)"
LABEL_EMBED_DESCRIPTION = "Descripción del embed"
LABEL_EMBED_COLOR = "Color del embed"
LABEL_EMBED_IMAGE_URL = "Imagen del embed (URL)"
LABEL_IMAGE_URL_ATTACHMENT = "URL de la imagen (attachment)"

# Placeholders faltantes
PLACEHOLDER_EMBED_TITLE_EXAMPLE = "Ej: ¡Anuncio Importante!"
PLACEHOLDER_MESSAGE_NAME = "Nombre descriptivo para el mensaje"
PLACEHOLDER_INTERVAL_EXAMPLE = "Ej: 5, 30, 120"
PLACEHOLDER_TIME_UNIT = "Selecciona la unidad de tiempo..."
PLACEHOLDER_HOUR_EXAMPLE = "Ej: 14 para las 2 PM"
PLACEHOLDER_MESSAGE_TEXT_FULL = "Escribe aquí el texto del mensaje automático..."
PLACEHOLDER_WELCOME_EMBED = "Ej: ¡Bienvenido al servidor!"
PLACEHOLDER_EMBED_DESCRIPTION_MODAL = "Escribe aquí la descripción del embed..."
PLACEHOLDER_EMBED_COLOR_OPTIONS = "blue, red, green, #FF0000, etc."

# Descriptions faltantes
DESC_CONFIG_COMPLETED = "El mensaje ha sido configurado correctamente. Ahora procederemos con la programación."
DESC_CONFIG_CANCELLED = "Se ha cancelado la configuración del mensaje automático."
DESC_MESSAGE_BUILDER = "Personaliza tu mensaje automático añadiendo contenido:"

# Textos de status del contenido
STATUS_TEXT_CONFIGURED = "✅ Texto configurado"
STATUS_NO_TEXT = "❌ Sin texto"
STATUS_EMBED_CONFIGURED = "✅ Embed configurado"
STATUS_NO_EMBED = "❌ Sin embed"
STATUS_IMAGE_CONFIGURED = "✅ Imagen configurada"
STATUS_NO_IMAGE = "❌ Sin imagen"

# Secciones del resumen
SECTION_BASIC_CONFIG = "📋 Configuración Básica"
SECTION_CONTENT_STATUS = "📊 Estado del Contenido"
SECTION_PREVIEW = "👁️ Vista Previa"
SECTION_SUMMARY = "📋 Resumen del mensaje:"

# Textos de destino y tipo
TEXT_DESTINATION = "📍 Destino:"
TEXT_TYPE = "⏰ Tipo:"
TEXT_NAME = "📝 Nombre:"
TEXT_NO_NAME = "Sin nombre"

# Tipos de programación en formato amigable
SCHEDULE_INTERVAL_DISPLAY = "⏰ Cada cierto tiempo"
SCHEDULE_DAILY_DISPLAY = "📅 Todos los días"
SCHEDULE_WEEKLY_DISPLAY = "📆 Días específicos"
SCHEDULE_CHANNEL_CREATE_DISPLAY = "🆕 Al crear canales"

# Mensajes de error de validación
ERROR_MESSAGE_NO_CONTENT = "El mensaje debe tener al menos texto, embed o imagen"
ERROR_EMBED_NO_CONTENT = "El embed debe tener al menos un título o descripción"
ERROR_NO_CONTENT_BEFORE_COMPLETE = "Debes añadir al menos texto, embed o imagen antes de completar."

# Nombres de secciones en embeds
FIELD_NAME_SUMMARY = "📋 Resumen"
FIELD_NAME_BASIC_CONFIG = "📋 Configuración Básica"
FIELD_NAME_CONTENT_STATUS = "📊 Estado del Contenido"
FIELD_NAME_PREVIEW = "👁️ Vista Previa"

# Mensajes de confirmación
MESSAGE_AUTO_CONFIGURED = "¡Mensaje automático configurado correctamente!"
MESSAGE_TEXT_CONFIGURED = "✅ Texto configurado correctamente."
MESSAGE_EMBED_CONFIGURED = "✅ Embed configurado correctamente."
MESSAGE_IMAGE_CONFIGURED = "✅ Imagen configurada correctamente."
TEXT_MODAL_WORKING = "✅ Modal funcionando!\n**Tipo:** {type}\n**Texto:** {text}..."

# Textos adicionales para limpieza
TEXT_CONTINUE_ELLIPSIS = "..."

# Mensajes de error adicionales
ERROR_CRON_REQUIRED = "La expresión cron es obligatoria para programación personalizada"

# Textos para interfaces adicionales
TEXT_NO_MESSAGES_TO_DELETE = "No se encontraron mensajes automáticos para eliminar."
TEXT_MESSAGES_FOUND_DELETE = "Se encontraron {count} mensajes automáticos."
TEXT_OPERATION_CANCELLED = "Operación cancelada"
TEXT_NO_MESSAGE_DELETED = "No se ha eliminado ningún mensaje automático"
TEXT_UNEXPECTED_ERROR = "Ocurrió un error inesperado. Por favor, inténtalo de nuevo."

# Docstrings (no se traducen pero las incluimos para consistencia)
DOCSTRING_PROGRAM_MESSAGE = "Programa un nuevo mensaje automático"
DOCSTRING_LIST_MESSAGES = "Lista todos los mensajes automáticos configurados"
DOCSTRING_DELETE_MESSAGE = "Elimina un mensaje automático"

# Textos adicionales para views.py
TEXT_MODAL_DEBUG = "✅ Modal funcionando!\n**Tipo:** {type}\n**Texto:** {text}..."
TEXT_ERROR_PREFIX = "❌ Error: {error}"
DESC_HOW_TO_SEND = "¿Cómo quieres enviar este mensaje?"
TEXT_NO_TEXT_ONLY_EMBED = "(Sin texto - solo embed/imagen)"
DESC_SCHEDULE_NOW = "Ahora configura cuándo se debe enviar el mensaje:"
TEXT_AUTO_CHANNEL_CREATE = "🆕 Se enviará automáticamente en cada canal nuevo creado en la categoría."
ERROR_CREATING_MSG = "Error creando el mensaje: {error}"
TEXT_DEFAULT_MSG_NAME = "Mensaje {id}"

# Botones adicionales
BUTTON_CANCEL = "❌ Cancelar"
BUTTON_SELECT_INTERVAL = "Seleccionar intervalo"
BUTTON_CONFIGURE_DAYS = "⚙️ Configurar días"
BUTTON_SET_TIME = "🕐 Configurar hora"

# Status del contenido
TEXT_NO_TEXT_STATUS = "❌ Sin texto"
TEXT_HAS_TEXT_STATUS = "📝 **Texto:** {preview}"
TEXT_HAS_EMBED_STATUS = "🎨 **Embed:** {title}{image}"
TEXT_HAS_ATTACHMENT_STATUS = "🖼️ **Imagen Attachment:** Configurada"
TEXT_READY_STATUS = "¡Listo para programar!"
TEXT_NO_CONTENT_STATUS = "❌ **Sin contenido configurado**"

# Textos para validaciones
VALIDATION_INTERVAL_UNIT_ERROR = "Unidad inválida. Usa 'seconds', 'minutes' o 'hours'"
VALIDATION_DAYS_REQUIRED = "Debes seleccionar al menos un día"
VALIDATION_VALID_HOUR = "La hora debe estar entre 0 y 23"
VALIDATION_VALID_MINUTE = "Los minutos deben estar entre 0 y 59"

# Textos para configuración de intervalo
CHOICE_SECONDS = "segundos"
CHOICE_MINUTES = "minutos" 
CHOICE_HOURS = "horas"

# Placeholders adicionales
PLACEHOLDER_CUSTOM_INTERVAL = "Ej: 45"
PLACEHOLDER_CUSTOM_UNIT = "seconds, minutes, hours"

# Constantes adicionales para completar views.py
TITLE_EMBED_CONFIG = "🎨 Configurar Embed"
TITLE_IMAGE_CONFIG = "🖼️ Configurar Imagen"
TITLE_FULL_EMBED_CONFIG = "✨ Configurar Embed + Imagen"
TITLE_CONFIGURE_SCHEDULE = "⚙️ Configurar programación"
TITLE_CONFIGURE_INTERVAL = "⏰ Configurar Intervalo"
TITLE_DAILY_HOUR_CONFIG = "📅 Configurar Hora Diaria"
TITLE_WEEKLY_CONFIG = "📆 Configurar Programación Semanal"
TITLE_SELECT_DAYS = "Seleccionar Días"
TITLE_DAYS_SELECTED = "Días seleccionados"
TITLE_OPERATION_CANCELLED = "Operación cancelada"
TITLE_ERROR = "❌ Error"

# Labels para inputs de modales
LABEL_EMBED_TITLE_OPTIONAL = "Título del embed (opcional)"
LABEL_EMBED_DESCRIPTION = "Descripción del embed"
LABEL_EMBED_COLOR = "Color del embed"
LABEL_IMAGE_URL_REQUIRED = "URL de la imagen"
LABEL_INTERVAL_NUMBER = "Intervalo (número)"
LABEL_UNIT_INTERVAL = "Unidad"

# Placeholders para inputs
PLACEHOLDER_EMBED_TITLE = "Ej: ¡Bienvenido al servidor!"
PLACEHOLDER_EMBED_DESCRIPTION = "Escribe aquí la descripción del embed..."
PLACEHOLDER_EMBED_COLOR = "blue, red, green, #FF0000, etc."
PLACEHOLDER_IMAGE_URL = "https://ejemplo.com/imagen.png"
PLACEHOLDER_INTERVAL_NUMBER = "Ej: 5, 30, 120"
PLACEHOLDER_UNIT_SELECT = "seconds, minutes o hours"
PLACEHOLDER_DAILY_HOUR = "Ej: 14 para las 2 PM"
PLACEHOLDER_WEEKLY_HOUR = "Ej: 18 para las 6 PM"

# Labels de botones específicos
BUTTON_SIMPLE_MESSAGE = "📝 Mensaje Simple"
BUTTON_CREATE_EMBED = "🎨 Crear Embed"
BUTTON_ADD_IMAGE_BTN = "🖼️ Añadir Imagen"
BUTTON_EMBED_AND_IMAGE = "✨ Embed + Imagen"
BUTTON_CONFIGURE_HOUR = "🕐 Configurar Hora"
BUTTON_CONFIGURE_TIME = "Configurar hora"
BUTTON_CUSTOM_INTERVAL = "Intervalo personalizado"
BUTTON_CONFIRM_WEEKDAYS = "Confirmar selección"

# Descripciones y mensajes
DESC_CONFIGURE_INTERVAL = "Selecciona cada cuánto tiempo se enviará el mensaje:"
DESC_DAILY_CONFIG = "Configura a qué hora se enviará el mensaje todos los días:"
DESC_WEEKLY_CONFIG = "Configura la hora y después selecciona los días:"
DESC_WEEKDAY_SELECTION = "Selecciona los días de la semana..."
DESC_TIME_CONFIGURED = "Hora configurada: {hour:02d}:{minute:02d}\n\nAhora selecciona los días:"
DESC_CONFIRM_DAYS = "**{days}**\n\nHaz clic en 'Confirmar selección' para continuar."

# Selectores y opciones
SELECT_TYPE_PLACEHOLDER = "Selecciona el tipo de programación..."
SELECT_INTERVAL_PLACEHOLDER = "Elige un intervalo común..."
SELECT_UNIT_PLACEHOLDER = "Selecciona la unidad de tiempo..."

# Opciones de select para tipos de programación
OPTION_INTERVAL_LABEL = "Por intervalo"
OPTION_INTERVAL_DESC = "Enviar cada X segundos/minutos/horas"
OPTION_DAILY_LABEL = "Diario"
OPTION_DAILY_DESC = "Enviar todos los días a una hora específica"
OPTION_WEEKLY_LABEL = "Semanal"
OPTION_WEEKLY_DESC = "Enviar ciertos días de la semana"
OPTION_CHANNEL_CREATE_LABEL = "Al crear canal"
OPTION_CHANNEL_CREATE_DESC = "Enviar cuando se cree un canal en la categoría"

# Opciones de intervalos comunes
OPTION_30_SECONDS = "Cada 30 segundos"
OPTION_1_MINUTE = "Cada minuto"
OPTION_5_MINUTES = "Cada 5 minutos"
OPTION_15_MINUTES = "Cada 15 minutos"
OPTION_30_MINUTES = "Cada 30 minutos"
OPTION_1_HOUR = "Cada hora"
OPTION_2_HOURS = "Cada 2 horas"
OPTION_6_HOURS = "Cada 6 horas"

# Opciones de unidades de tiempo
OPTION_SECONDS = "Segundos"
OPTION_MINUTES = "Minutos"
OPTION_HOURS = "Horas"

# Días de la semana para selectores
WEEKDAY_MONDAY = "Lunes"
WEEKDAY_TUESDAY = "Martes"
WEEKDAY_WEDNESDAY = "Miércoles"
WEEKDAY_THURSDAY = "Jueves"
WEEKDAY_FRIDAY = "Viernes"
WEEKDAY_SATURDAY = "Sábado"
WEEKDAY_SUNDAY = "Domingo"

# Mensajes de error específicos
ERROR_IMAGE_URL_REQUIRED = "La URL de la imagen es requerida"
ERROR_POSITIVE_INTERVAL = "El intervalo debe ser positivo"
ERROR_VALID_UNIT = "La unidad debe ser seconds, minutes o hours"
ERROR_HOUR_MINUTE_INVALID = "Hora o minuto inválidos (0-23 y 0-59)"
ERROR_SELECT_ONE_DAY = "Debes seleccionar al menos un día de la semana"
ERROR_UNEXPECTED = "Error inesperado: {error}"

# Mensajes de configuración de embeds
ERROR_CONFIGURING_EMBED = "Error configurando embed: {error}"
ERROR_CONFIGURING_IMAGE = "Error configurando imagen: {error}"
ERROR_CONFIGURING_FULL_EMBED = "Error configurando embed completo: {error}"

# Textos de confirmación y éxito
TEXT_MESSAGE_CONFIGURED = "¡Mensaje automático configurado correctamente!"
TEXT_MESSAGE_DELETED = "Se ha eliminado el mensaje automático **{name}**"
TEXT_NO_MESSAGE_DELETED = "No se ha eliminado ningún mensaje automático"
TEXT_UNIT_TIME = "Selecciona la unidad de tiempo:"

# Formatos de tiempo y programación
FORMAT_DAILY_TIME = "📅 Se enviará todos los días a las {hour:02d}:{minute:02d}"
FORMAT_WEEKLY_SCHEDULE = "📅 Días: {days}\n🕐 Hora: {hour:02d}:{minute:02d}"

# Mensajes de debug y fallback
TEXT_MODAL_COMPLETED = "Modal completado. Este callback será implementado en slash_commands."
