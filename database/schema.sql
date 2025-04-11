-- Tabla para los logs
CREATE TABLE IF NOT EXISTS logs (
    type TEXT PRIMARY KEY,
    channel_id INTEGER,
    enabled INTEGER DEFAULT 1
);

-- Tabla para los triggers
CREATE TABLE IF NOT EXISTS triggers (
    id VARCHAR(36) PRIMARY KEY,
    channel_id INTEGER,
    delete_message INTEGER DEFAULT 0,
    response TEXT,
    key TEXT NOT NULL,
    position TEXT NOT NULL,
    response_timeout INTEGER
);

-- Tabla para los formatos de canal
CREATE TABLE IF NOT EXISTS channel_formats (
    id CHAR(36) PRIMARY KEY,
    channel_id INTEGER NOT NULL,
    regex TEXT NOT NULL
);

-- Tabla para mensajes automáticos
CREATE TABLE IF NOT EXISTS automatic_messages (
    id CHAR(36) PRIMARY KEY,
    channel_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    interval INTEGER,
    interval_unit TEXT,
    hour INTEGER,
    minute INTEGER
    CONSTRAINT valid_interval_unit CHECK (interval_unit IN ('seconds', 'minutes', 'hours'))
);

-- Tablas para los clanes
CREATE TABLE IF NOT EXISTS clan_channels (
    channel_id INTEGER NOT NULL PRIMARY KEY,
    clan_id CHAR(36) NOT NULL,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (clan_id) REFERENCES clans(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS clan_members (
    user_id INTEGER NOT NULL,
    clan_id CHAR(36) NOT NULL,
    role INTEGER NOT NULL,
    joined_at TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id, clan_id),
    FOREIGN KEY (clan_id) REFERENCES clans(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS clans (
    id CHAR(36) PRIMARY KEY,
    name TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    member_count INTEGER NOT NULL,
    max_members INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- Configuración global para los clanes
CREATE TABLE IF NOT EXISTS clan_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT OR IGNORE INTO clan_settings (key, value, description) VALUES
    ('category_id', '0', 'ID de la categoría donde se crean los clanes'),
    ('max_members', '50', 'Número máximo de miembros por clan'),
    ('multiple_clans', 'false', 'Si un usuario puede estar en varios clanes'),
    ('multiple_leaders', 'false', 'Si un clan puede tener múltiples líderes'),
    ('default_role_color', '0000FF', 'Color por defecto para roles de clan (hex)'),
    ('additional_roles', '[]', 'IDs de roles adicionales al unirse (JSON array)'),
    ('max_text_channels', '1', 'Número máximo de canales de texto por clan'),
    ('max_voice_channels', '1', 'Número máximo de canales de voz por clan'),
    ('leader_role_id', '0', 'ID del rol de líder de clan');