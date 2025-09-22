-- Script de seeds para LiveChat-IA
-- Inserta datos iniciales necesarios para el funcionamiento del sistema

USE `livechat-ia`;

-- Insertar usuario administrador predeterminado
-- Nota: La contraseña "72900968" será hasheada por la aplicación
-- Este script solo crea el placeholder, el hash real se genera en código
INSERT IGNORE INTO `users` (
    `username`,
    `password_hash`,
    `email`,
    `full_name`,
    `is_active`,
    `is_admin`
) VALUES (
    'jscothserver',
    '$2b$12$placeholder_hash_will_be_replaced_by_application',
    'admin@livechat-ia.local',
    'Administrador del Sistema',
    TRUE,
    TRUE
);

-- Configuraciones iniciales del sistema
INSERT IGNORE INTO `system_config` (`config_key`, `config_value`, `config_type`, `description`, `is_public`) VALUES
('app_name', 'LiveChat-IA', 'string', 'Nombre de la aplicación', TRUE),
('app_version', '1.0.0', 'string', 'Versión actual de la aplicación', TRUE),
('max_session_duration', '86400', 'integer', 'Duración máxima de sesión en segundos (24 horas)', FALSE),
('max_chat_history', '1000', 'integer', 'Número máximo de mensajes en historial de chat', FALSE),
('enable_logging', 'true', 'boolean', 'Habilitar sistema de logging', FALSE),
('log_level', 'INFO', 'string', 'Nivel de logging (DEBUG, INFO, WARNING, ERROR)', FALSE),
('enable_reports', 'true', 'boolean', 'Habilitar generación automática de reportes', FALSE),
('report_retention_days', '30', 'integer', 'Días de retención de reportes', FALSE),
('timezone', 'America/Los_Angeles', 'string', 'Zona horaria del sistema', TRUE),
('date_format', '%Y-%m-%d %H:%M:%S', 'string', 'Formato de fecha por defecto', TRUE);

-- Crear índices adicionales (verificando si no existen)
SET @sql = IF((SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS WHERE table_schema = DATABASE() AND table_name = 'history' AND index_name = 'idx_history_created_date') = 0, 'CREATE INDEX idx_history_created_date ON history ((DATE(created_at)))', 'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = IF((SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS WHERE table_schema = DATABASE() AND table_name = 'reports' AND index_name = 'idx_reports_created_date') = 0, 'CREATE INDEX idx_reports_created_date ON reports ((DATE(created_at)))', 'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = IF((SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS WHERE table_schema = DATABASE() AND table_name = 'sessions' AND index_name = 'idx_sessions_created_date') = 0, 'CREATE INDEX idx_sessions_created_date ON sessions ((DATE(created_at)))', 'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Crear vista para estadísticas rápidas
CREATE OR REPLACE VIEW `user_stats` AS
SELECT
    u.id,
    u.username,
    u.created_at as user_created,
    u.last_login,
    COUNT(DISTINCT s.id) as total_sessions,
    COUNT(DISTINCT h.id) as total_interactions,
    MAX(s.last_activity) as last_activity
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id
LEFT JOIN history h ON u.id = h.user_id
GROUP BY u.id, u.username, u.created_at, u.last_login;

-- Crear vista para reportes recientes
CREATE OR REPLACE VIEW `recent_reports` AS
SELECT
    r.id,
    r.report_type,
    r.title,
    r.file_path,
    r.created_at,
    u.username as created_by,
    r.is_auto_generated
FROM reports r
LEFT JOIN users u ON r.user_id = u.id
WHERE r.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY r.created_at DESC;