-- Migración para sistema de agentes IA
-- Crea tablas para gestión de agentes externos

USE `livechat-ia`;

-- Tabla de agentes IA configurados
CREATE TABLE IF NOT EXISTS `agents` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `provider` VARCHAR(50) NOT NULL,
    `model_name` VARCHAR(100) NOT NULL,
    `display_name` VARCHAR(150),
    `description` TEXT,
    `api_key_encrypted` TEXT,
    `api_url` VARCHAR(500),
    `config_json` JSON,
    `default_params` JSON,
    `is_active` BOOLEAN DEFAULT TRUE,
    `is_default` BOOLEAN DEFAULT FALSE,
    `max_tokens` INT DEFAULT 2048,
    `temperature` DECIMAL(3,2) DEFAULT 0.70,
    `cost_per_1k_tokens` DECIMAL(10,6) DEFAULT 0.000000,
    `created_by` INT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`created_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_provider` (`provider`),
    INDEX `idx_active` (`is_active`),
    INDEX `idx_default` (`is_default`),
    UNIQUE KEY `unique_agent_model` (`provider`, `model_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de uso de agentes (estadísticas y costos)
CREATE TABLE IF NOT EXISTS `agent_usage` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `agent_id` INT NOT NULL,
    `user_id` INT,
    `session_id` VARCHAR(36),
    `interaction_id` INT,
    `tokens_used` INT DEFAULT 0,
    `prompt_tokens` INT DEFAULT 0,
    `completion_tokens` INT DEFAULT 0,
    `cost_usd` DECIMAL(10,6) DEFAULT 0.000000,
    `response_time_ms` INT,
    `status` ENUM('success', 'error', 'timeout') DEFAULT 'success',
    `error_message` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`agent_id`) REFERENCES `agents`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`session_id`) REFERENCES `sessions`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`interaction_id`) REFERENCES `history`(`id`) ON DELETE SET NULL,
    INDEX `idx_agent_id` (`agent_id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_session_id` (`session_id`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de configuraciones de proveedores de IA
CREATE TABLE IF NOT EXISTS `ai_providers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) UNIQUE NOT NULL,
    `display_name` VARCHAR(100) NOT NULL,
    `base_url` VARCHAR(500),
    `auth_type` ENUM('api_key', 'oauth', 'token') DEFAULT 'api_key',
    `supported_models` JSON,
    `default_params` JSON,
    `rate_limit_rpm` INT DEFAULT 60,
    `rate_limit_tpm` INT DEFAULT 10000,
    `is_active` BOOLEAN DEFAULT TRUE,
    `documentation_url` VARCHAR(500),
    `pricing_url` VARCHAR(500),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_name` (`name`),
    INDEX `idx_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de configuraciones de agentes por usuario
CREATE TABLE IF NOT EXISTS `user_agent_preferences` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `preferred_agent_id` INT,
    `custom_params` JSON,
    `usage_limit_daily` INT DEFAULT 1000,
    `usage_limit_monthly` INT DEFAULT 30000,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`preferred_agent_id`) REFERENCES `agents`(`id`) ON DELETE SET NULL,
    UNIQUE KEY `unique_user_prefs` (`user_id`),
    INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar proveedores de IA populares
INSERT IGNORE INTO `ai_providers` (`name`, `display_name`, `base_url`, `auth_type`, `supported_models`, `default_params`, `rate_limit_rpm`, `rate_limit_tpm`, `documentation_url`, `pricing_url`) VALUES
('openai', 'OpenAI', 'https://api.openai.com/v1', 'api_key',
 JSON_ARRAY('gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'),
 JSON_OBJECT('temperature', 0.7, 'max_tokens', 2048, 'top_p', 1.0),
 3500, 200000, 'https://platform.openai.com/docs', 'https://openai.com/pricing'),

('anthropic', 'Anthropic Claude', 'https://api.anthropic.com/v1', 'api_key',
 JSON_ARRAY('claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-haiku-20240307'),
 JSON_OBJECT('temperature', 0.7, 'max_tokens', 2048),
 4000, 400000, 'https://docs.anthropic.com', 'https://www.anthropic.com/pricing'),

('google', 'Google Gemini', 'https://generativelanguage.googleapis.com/v1', 'api_key',
 JSON_ARRAY('gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro'),
 JSON_OBJECT('temperature', 0.7, 'maxOutputTokens', 2048),
 1500, 120000, 'https://ai.google.dev/docs', 'https://ai.google.dev/pricing'),

('groq', 'Groq', 'https://api.groq.com/openai/v1', 'api_key',
 JSON_ARRAY('llama-3.1-70b-versatile', 'mixtral-8x7b-32768', 'gemma-7b-it'),
 JSON_OBJECT('temperature', 0.7, 'max_tokens', 2048),
 14400, 14400, 'https://console.groq.com/docs', 'https://groq.com/pricing'),

('together', 'Together AI', 'https://api.together.xyz/v1', 'api_key',
 JSON_ARRAY('meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', 'Qwen/Qwen2.5-72B-Instruct-Turbo', 'deepseek-ai/deepseek-coder-33b-instruct'),
 JSON_OBJECT('temperature', 0.7, 'max_tokens', 2048),
 600, 600, 'https://docs.together.ai', 'https://www.together.ai/pricing'),

('ollama', 'Ollama (Local)', 'http://localhost:11434', 'token',
 JSON_ARRAY('llama3.1', 'codestral', 'mistral', 'phi3', 'qwen2.5'),
 JSON_OBJECT('temperature', 0.7, 'num_predict', 2048),
 NULL, NULL, 'https://ollama.com/docs', NULL);

-- Insertar algunos agentes por defecto
INSERT IGNORE INTO `agents` (`name`, `provider`, `model_name`, `display_name`, `description`, `default_params`, `is_default`, `max_tokens`, `temperature`, `cost_per_1k_tokens`) VALUES
('GPT-4o Mini', 'openai', 'gpt-4o-mini', 'GPT-4o Mini', 'Modelo rápido y económico de OpenAI para tareas generales',
 JSON_OBJECT('temperature', 0.7, 'max_tokens', 2048), TRUE, 2048, 0.70, 0.000150),

('Claude 3.5 Sonnet', 'anthropic', 'claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet', 'Modelo balanceado de Anthropic para conversaciones inteligentes',
 JSON_OBJECT('temperature', 0.7, 'max_tokens', 2048), FALSE, 2048, 0.70, 0.003000),

('Gemini 1.5 Flash', 'google', 'gemini-1.5-flash', 'Gemini 1.5 Flash', 'Modelo rápido de Google para respuestas eficientes',
 JSON_OBJECT('temperature', 0.7, 'maxOutputTokens', 2048), FALSE, 2048, 0.70, 0.000075),

('Llama 3.1 70B', 'groq', 'llama-3.1-70b-versatile', 'Llama 3.1 70B', 'Modelo versátil de Meta ejecutado por Groq',
 JSON_OBJECT('temperature', 0.7, 'max_tokens', 2048), FALSE, 2048, 0.70, 0.000590),

('Llama 3.1 Local', 'ollama', 'llama3.1', 'Llama 3.1 (Ollama)', 'Modelo local sin costo, ejecutado con Ollama',
 JSON_OBJECT('temperature', 0.7, 'num_predict', 2048), FALSE, 2048, 0.70, 0.000000);

-- Crear vista para estadísticas de agentes
CREATE OR REPLACE VIEW `agent_stats` AS
SELECT
    a.id,
    a.name,
    a.provider,
    a.model_name,
    a.is_active,
    COUNT(au.id) as total_uses,
    COALESCE(SUM(au.tokens_used), 0) as total_tokens,
    COALESCE(SUM(au.cost_usd), 0) as total_cost,
    COALESCE(AVG(au.response_time_ms), 0) as avg_response_time,
    COUNT(DISTINCT au.user_id) as unique_users,
    MAX(au.created_at) as last_used
FROM agents a
LEFT JOIN agent_usage au ON a.id = au.agent_id
GROUP BY a.id, a.name, a.provider, a.model_name, a.is_active
ORDER BY total_uses DESC;

-- Crear vista para uso diario de agentes
CREATE OR REPLACE VIEW `daily_agent_usage` AS
SELECT
    DATE(au.created_at) as usage_date,
    a.name as agent_name,
    a.provider,
    COUNT(au.id) as daily_uses,
    SUM(au.tokens_used) as daily_tokens,
    SUM(au.cost_usd) as daily_cost,
    COUNT(DISTINCT au.user_id) as daily_users
FROM agent_usage au
JOIN agents a ON au.agent_id = a.id
WHERE au.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(au.created_at), a.id, a.name, a.provider
ORDER BY usage_date DESC, daily_uses DESC;