-- Migración para añadir soporte a programación semanal de mensajes automáticos
-- Añade los campos necesarios para programaciones más flexibles

ALTER TABLE automatic_messages ADD COLUMN schedule_type TEXT DEFAULT 'interval';
ALTER TABLE automatic_messages ADD COLUMN weekdays TEXT; -- JSON array de días de la semana
ALTER TABLE automatic_messages ADD COLUMN cron_expression TEXT; -- Para programaciones personalizadas

-- Actualizar constraint para incluir los nuevos valores
-- Eliminar el constraint anterior si existe
-- DROP CONSTRAINT IF EXISTS valid_interval_unit;

-- Añadir nuevo constraint mejorado
-- ALTER TABLE automatic_messages ADD CONSTRAINT valid_interval_unit CHECK (interval_unit IN ('seconds', 'minutes', 'hours') OR interval_unit IS NULL);
-- ALTER TABLE automatic_messages ADD CONSTRAINT valid_schedule_type CHECK (schedule_type IN ('interval', 'daily', 'weekly', 'custom') OR schedule_type IS NULL);
