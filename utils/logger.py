# Sistema de logging personalizado
# Proporciona logging con rotación de archivos y colores en consola

import os
import logging
import colorlog
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional
from config.app_config import AppConfig


class Logger:
    """
    Sistema de logging personalizado con soporte para:
    - Rotación de archivos
    - Colores en consola
    - Múltiples niveles de log
    - Formateo personalizado
    """

    def __init__(self, name: str = "LiveChat-IA"):
        self.app_config = AppConfig()
        self.name = name
        self.logs_dir = "logs"
        self.logger = None
        self.setup_logger()

    def ensure_logs_directory(self):
        """Asegura que la carpeta de logs exista"""
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

    def setup_logger(self):
        """Configura el logger con handlers de archivo y consola"""
        self.ensure_logs_directory()

        # Crear logger principal
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)

        # Evitar duplicar handlers si ya existen
        if self.logger.handlers:
            return

        # Configurar formato para archivos
        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Configurar formato para consola con colores
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s | %(name)s | %(levelname)s | %(message)s%(reset)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )

        # Handler para archivo principal (todos los logs)
        main_log_file = os.path.join(self.logs_dir, f"{self.name.lower()}.log")
        main_handler = RotatingFileHandler(
            main_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setLevel(logging.DEBUG)
        main_handler.setFormatter(file_formatter)

        # Handler para errores (solo errores y críticos)
        error_log_file = os.path.join(self.logs_dir, f"{self.name.lower()}_errors.log")
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)

        # Handler para log diario
        daily_log_file = os.path.join(
            self.logs_dir,
            f"{self.name.lower()}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        daily_handler = RotatingFileHandler(
            daily_log_file,
            maxBytes=50*1024*1024,  # 50MB
            backupCount=1,
            encoding='utf-8'
        )
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(file_formatter)

        # Handler para consola (solo si está en modo debug)
        if self.app_config.is_debug_mode():
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        # Agregar handlers al logger
        self.logger.addHandler(main_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(daily_handler)

    def debug(self, message: str, extra: Optional[dict] = None):
        """Log nivel DEBUG"""
        self.logger.debug(message, extra=extra)

    def info(self, message: str, extra: Optional[dict] = None):
        """Log nivel INFO"""
        self.logger.info(message, extra=extra)

    def warning(self, message: str, extra: Optional[dict] = None):
        """Log nivel WARNING"""
        self.logger.warning(message, extra=extra)

    def error(self, message: str, extra: Optional[dict] = None):
        """Log nivel ERROR"""
        self.logger.error(message, extra=extra)

    def critical(self, message: str, extra: Optional[dict] = None):
        """Log nivel CRITICAL"""
        self.logger.critical(message, extra=extra)

    def log_exception(self, message: str, exception: Exception):
        """Log una excepción con detalles completos"""
        self.logger.error(f"{message}: {str(exception)}", exc_info=True)

    def log_user_action(self, user_id: int, action: str, details: Optional[str] = None):
        """Log específico para acciones de usuario"""
        message = f"Usuario {user_id} - {action}"
        if details:
            message += f" - {details}"
        self.info(message)

    def log_system_event(self, event: str, details: Optional[dict] = None):
        """Log específico para eventos del sistema"""
        message = f"Sistema - {event}"
        if details:
            message += f" - {details}"
        self.info(message)

    def log_chat_interaction(
        self,
        user_id: Optional[int],
        session_id: Optional[str],
        user_message: str,
        agent_response: str,
        response_time_ms: Optional[int] = None
    ):
        """Log específico para interacciones de chat"""
        message = f"Chat - Usuario: {user_id or 'Anónimo'}, Sesión: {session_id or 'N/A'}"
        if response_time_ms:
            message += f", Tiempo: {response_time_ms}ms"

        details = {
            'user_message_length': len(user_message),
            'agent_response_length': len(agent_response),
            'response_time_ms': response_time_ms
        }

        self.info(message, extra=details)

    def log_database_operation(self, operation: str, table: str, success: bool, details: Optional[str] = None):
        """Log específico para operaciones de base de datos"""
        status = "ÉXITO" if success else "ERROR"
        message = f"BD - {operation} en {table} - {status}"
        if details:
            message += f" - {details}"

        if success:
            self.info(message)
        else:
            self.error(message)

    def log_authentication(self, username: str, success: bool, ip_address: Optional[str] = None):
        """Log específico para intentos de autenticación"""
        status = "ÉXITO" if success else "FALLO"
        message = f"Auth - {username} - {status}"
        if ip_address:
            message += f" - IP: {ip_address}"

        if success:
            self.info(message)
        else:
            self.warning(message)

    def log_session_event(self, session_id: str, event: str, user_id: Optional[int] = None):
        """Log específico para eventos de sesión"""
        message = f"Sesión - {event} - ID: {session_id}"
        if user_id:
            message += f" - Usuario: {user_id}"

        self.info(message)

    def log_report_generation(self, report_type: str, file_path: str, success: bool):
        """Log específico para generación de reportes"""
        status = "GENERADO" if success else "ERROR"
        message = f"Reporte - {report_type} - {status} - {file_path}"

        if success:
            self.info(message)
        else:
            self.error(message)

    def log_startup(self, version: str, environment: str):
        """Log específico para inicio de aplicación"""
        message = f"INICIO - {self.app_config.get_app_name()} v{version} - Entorno: {environment}"
        self.info(message)

    def log_shutdown(self):
        """Log específico para cierre de aplicación"""
        message = f"CIERRE - {self.app_config.get_app_name()} cerrando correctamente"
        self.info(message)

    def get_log_files(self) -> list:
        """Obtiene la lista de archivos de log existentes"""
        log_files = []
        if os.path.exists(self.logs_dir):
            for file in os.listdir(self.logs_dir):
                if file.endswith('.log'):
                    file_path = os.path.join(self.logs_dir, file)
                    file_size = os.path.getsize(file_path)
                    log_files.append({
                        'name': file,
                        'path': file_path,
                        'size_bytes': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2)
                    })
        return log_files

    def cleanup_old_logs(self, days_to_keep: int = 7):
        """Limpia logs antiguos"""
        if not os.path.exists(self.logs_dir):
            return

        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        deleted_count = 0

        for file in os.listdir(self.logs_dir):
            if file.endswith('.log'):
                file_path = os.path.join(self.logs_dir, file)
                if os.path.getmtime(file_path) < cutoff_date:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        self.info(f"Log antiguo eliminado: {file}")
                    except OSError as e:
                        self.error(f"Error al eliminar log {file}: {e}")

        if deleted_count > 0:
            self.info(f"Limpieza completada: {deleted_count} logs eliminados")


# Instancia global del logger
app_logger = Logger()


# Funciones de conveniencia para usar directamente
def debug(message: str, extra: Optional[dict] = None):
    app_logger.debug(message, extra)


def info(message: str, extra: Optional[dict] = None):
    app_logger.info(message, extra)


def warning(message: str, extra: Optional[dict] = None):
    app_logger.warning(message, extra)


def error(message: str, extra: Optional[dict] = None):
    app_logger.error(message, extra)


def critical(message: str, extra: Optional[dict] = None):
    app_logger.critical(message, extra)


def log_exception(message: str, exception: Exception):
    app_logger.log_exception(message, exception)


def log_user_action(user_id: int, action: str, details: Optional[str] = None):
    app_logger.log_user_action(user_id, action, details)


def log_system_event(event: str, details: Optional[dict] = None):
    app_logger.log_system_event(event, details)


def log_chat_interaction(
    user_id: Optional[int],
    session_id: Optional[str],
    user_message: str,
    agent_response: str,
    response_time_ms: Optional[int] = None
):
    app_logger.log_chat_interaction(user_id, session_id, user_message, agent_response, response_time_ms)