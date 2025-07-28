"""
Constantes de mensajes para el módulo de configuración de clanes
"""

# Mensajes de error
ERROR_INVALID_COLOR = "❌ El color de roles debe ser un valor hexadecimal válido."
ERROR_GETTING_SETTINGS = "❌ Error al obtener la configuración"
ERROR_SAVING_SETTINGS = "❌ Error al guardar la configuración"
ERROR_ROLE_ALREADY_EXISTS = "❌ El rol {role} ya está en la lista de roles adicionales."
ERROR_ROLE_NOT_IN_LIST = "❌ El rol {role} no está en la lista de roles adicionales."
ERROR_NO_CLANS_TO_PROCESS = "❌ No hay clanes para procesar."
ERROR_NO_VALID_ADDITIONAL_ROLES = "❌ No se encontraron roles adicionales válidos en el servidor."

# Mensajes de éxito
SUCCESS_CONFIG_UPDATED = "✅ Configuración actualizada con éxito."
SUCCESS_ADDITIONAL_ROLE_ADDED = "✅ Rol adicional {role} agregado con éxito. Se asignará automáticamente a todos los nuevos miembros de clanes."
SUCCESS_ADDITIONAL_ROLE_REMOVED = "🗑️ Rol adicional {role} removido con éxito. Ya no se asignará a los nuevos miembros de clanes."
SUCCESS_ALL_ADDITIONAL_ROLES_CLEARED = "🧹 Todos los roles adicionales han sido removidos."
SUCCESS_ROLES_APPLIED = "✅ Proceso completado. Se procesaron {total_members} miembros. Se asignaron roles adicionales exitosamente a {successful_members} miembros."

# Mensajes informativos
NO_ADDITIONAL_ROLES_CONFIGURED = "📭 No hay roles adicionales configurados."

# Labels y títulos para embeds
TITLE_CLAN_CONFIG = "⚙️ Configuración de Clanes"
FIELD_CATEGORIES = "📂 Categorías"
FIELD_MAX_CHANNELS = "📊 Máx. Canales"
FIELD_ADDITIONAL_ROLES = "🎭 Roles Adicionales"
FIELD_LEADER_ROLE = "👑 Rol de Líder"
FIELD_ROLE_COLOR = "🎨 Color de Roles"
FIELD_LIMITS = "📏 Límites"

# Valores para embeds
VALUE_NOT_CONFIGURED = "⚪ No configurado"
VALUE_NO_ADDITIONAL_ROLES = "📭 No configurados"
VALUE_CATEGORIES_FORMAT = "📝 Texto: <#{text_category}>\n🔊 Voz: <#{voice_category}>"
VALUE_MAX_CHANNELS_FORMAT = "📝 Texto: {max_text}\n🔊 Voz: {max_voice}"
VALUE_LIMITS_FORMAT = "👥 Máx. Miembros: {max_members}\n🔄 Múltiples Clanes: {multiple_clans}\n👑 Múltiples Líderes: {multiple_leaders}"
VALUE_YES = "✅ Sí"
VALUE_NO = "❌ No"
EMBED_DESCRIPTION = "⚙️ Configuración actual de los clanes"

# Descripciones de comandos
COMMAND_CONFIG_DESC = "⚙️ Configurar ajustes generales de clanes"
COMMAND_INFO_DESC = "ℹ️ Ver configuración actual de clanes"
COMMAND_ADD_ROLE_DESC = "➕ Añadir rol adicional para miembros de clan"
COMMAND_REMOVE_ROLE_DESC = "🗑️ Quitar rol adicional"
COMMAND_CLEAR_ROLES_DESC = "🧹 Limpiar todos los roles adicionales"
COMMAND_APPLY_ROLES_DESC = "🔄 Aplicar roles adicionales a miembros existentes"

# Descripciones de parámetros
PARAM_TEXT_CATEGORY_DESC = "📝 Categoría para canales de texto de clanes"
PARAM_VOICE_CATEGORY_DESC = "🔊 Categoría para canales de voz de clanes"
PARAM_MAX_MEMBERS_DESC = "👥 Máximo de miembros por clan"
PARAM_LEADER_ROLE_DESC = "👑 Rol que se asigna a líderes de clan"
PARAM_ROLE_COLOR_DESC = "🎨 Color hexadecimal para roles de clan"
PARAM_MULTIPLE_CLANS_DESC = "🔄 Permitir que usuarios estén en múltiples clanes"
PARAM_MULTIPLE_LEADERS_DESC = "👑 Permitir múltiples líderes por clan"
PARAM_MAX_TEXT_DESC = "📝 Máximo de canales de texto por clan"
PARAM_MAX_VOICE_DESC = "🔊 Máximo de canales de voz por clan"
PARAM_ADDITIONAL_ROLE_DESC = "🎭 Rol adicional a asignar a todos los miembros de clanes"
PARAM_REMOVE_ROLE_DESC = "🗑️ Rol adicional a remover de la lista"
