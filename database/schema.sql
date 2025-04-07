-- Tabla para los logs
CREATE TABLE IF NOT EXISTS logs (
    type TEXT PRIMARY KEY,
    channel_id INTEGER NOT NULL,
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