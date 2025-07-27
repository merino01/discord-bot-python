-- Migración: Añadir configuración personalizada por clan
-- Fecha: 2025-07-27
-- Descripción: Permite configurar límites de canales específicos para cada clan

-- Añadir columnas de configuración personalizada a la tabla clans
ALTER TABLE clans ADD COLUMN max_text_channels INTEGER DEFAULT 1;
ALTER TABLE clans ADD COLUMN max_voice_channels INTEGER DEFAULT 1;

-- Actualizar clanes existentes con los valores de la configuración global actual
-- Se toman los valores actuales configurados en el sistema
UPDATE clans SET max_text_channels = (
    SELECT CAST(value AS INTEGER) FROM clan_settings WHERE key = 'max_text_channels'
) WHERE max_text_channels IS NULL;

UPDATE clans SET max_voice_channels = (
    SELECT CAST(value AS INTEGER) FROM clan_settings WHERE key = 'max_voice_channels'  
) WHERE max_voice_channels IS NULL;

-- Comentarios para documentación
-- max_text_channels: Límite de canales de texto para este clan
-- max_voice_channels: Límite de canales de voz para este clan  
-- max_members: Límite de miembros para este clan (ya existe)
-- Todos los clanes tendrán valores específicos, inicializados con la configuración global
