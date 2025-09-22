# Vista base para todas las interfaces de usuario
# Contiene métodos comunes para el formateo y presentación de datos
# Maneja la renderización de respuestas y mensajes al usuario

import json
from datetime import datetime
from config.app_config import AppConfig


class BaseView:
    """
    Clase base para todas las vistas de la aplicación.
    Proporciona funcionalidades comunes de presentación y formateo.
    """

    def __init__(self):
        # Inicializa la configuración de la aplicación
        self.app_config = AppConfig()
        self.timezone = self.app_config.get_timezone()

    def format_response(self, data, status="success", message=""):
        """
        Formatea una respuesta estándar para la aplicación
        Args:
            data: Datos a incluir en la respuesta
            status: Estado de la respuesta (success, error, warning)
            message: Mensaje descriptivo
        Returns:
            Diccionario con la respuesta formateada
        """
        return {
            "status": status,
            "message": message,
            "data": data,
            "timestamp": self.get_current_timestamp()
        }

    def format_error(self, error_message, error_code=None):
        """
        Formatea una respuesta de error
        Args:
            error_message: Mensaje de error
            error_code: Código de error (opcional)
        Returns:
            Diccionario con el error formateado
        """
        error_data = {
            "error_message": error_message,
            "error_code": error_code,
            "timestamp": self.get_current_timestamp()
        }
        return self.format_response(error_data, "error", "Ha ocurrido un error")

    def get_current_timestamp(self):
        """
        Obtiene la marca de tiempo actual en la zona horaria configurada
        Returns:
            String con la fecha y hora actual
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def render_json(self, data):
        """
        Convierte los datos a formato JSON
        Args:
            data: Datos a convertir
        Returns:
            String JSON formateado
        """
        return json.dumps(data, ensure_ascii=False, indent=2)