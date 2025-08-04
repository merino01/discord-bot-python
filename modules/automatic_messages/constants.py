"""
Constantes técnicas para el módulo de mensajes automáticos
Solo contiene valores de configuración, límites e identificadores técnicos.
Todos los textos user-facing están en las traducciones.
"""

# Identificadores de tipos de programación (no cambiar)
SCHEDULE_TYPE_INTERVAL = "interval"
SCHEDULE_TYPE_DAILY = "daily"
SCHEDULE_TYPE_WEEKLY = "weekly"
SCHEDULE_TYPE_ON_CHANNEL_CREATE = "on_channel_create"
SCHEDULE_TYPE_CUSTOM = "custom"

# Unidades de tiempo válidas (no cambiar)
VALID_INTERVAL_UNITS = ["seconds", "minutes", "hours"]

# Días de la semana (para manejo interno)
WEEKDAYS_MAP = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}

# Límites técnicos
MAX_MESSAGE_LENGTH = 2000
MAX_NAME_LENGTH = 100
MAX_MESSAGES_PER_PAGE = 10
MIN_INTERVAL = 1
MAX_INTERVAL = 86400  # 24 horas en segundos
MIN_HOUR = 0
MAX_HOUR = 23
MIN_MINUTE = 0
MAX_MINUTE = 59

# Rangos válidos
VALID_HOURS = range(0, 24)
VALID_MINUTES = range(0, 60)
VALID_WEEKDAYS = range(0, 7)

# Configuración de paginación
DEFAULT_PAGE_SIZE = 10

# Configuración de timeout
DEFAULT_TIMEOUT = 600  # 10 minutos

# Configuración de colores por defecto
COLOR_SUCCESS = 0x00FF00
COLOR_ERROR = 0xFF0000
COLOR_WARNING = 0xFFAA00
COLOR_INFO = 0x0099FF
DEFAULT_EMBED_COLOR = 0x00FF00  # Verde

# Estados de mensaje
MESSAGE_STATUS_ACTIVE = "active"
MESSAGE_STATUS_INACTIVE = "inactive"
MESSAGE_STATUS_ERROR = "error"

# Tipos de canal válidos
VALID_CHANNEL_TYPES = ["text", "voice", "category"]

# Configuración de embeds
MAX_EMBED_TITLE_LENGTH = 256
MAX_EMBED_DESCRIPTION_LENGTH = 4096
MAX_EMBED_FIELDS = 25

# Valores de respuesta del bot
INTERACTION_RESPONSE_TIMEOUT = 3  # segundos
