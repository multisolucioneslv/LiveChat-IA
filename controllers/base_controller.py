# Controlador base para toda la lógica de negocio
# Coordina la interacción entre modelos y vistas
# Contiene métodos comunes para el manejo de peticiones y validaciones

from views.base_view import BaseView
from config.app_config import AppConfig


class BaseController:
    """
    Clase base para todos los controladores de la aplicación.
    Maneja la lógica de negocio y coordina modelos con vistas.
    """

    def __init__(self):
        # Inicializa la vista base para formatear respuestas
        self.view = BaseView()
        self.app_config = AppConfig()

    def validate_required_fields(self, data, required_fields):
        """
        Valida que los campos requeridos estén presentes en los datos
        Args:
            data: Diccionario con los datos a validar
            required_fields: Lista de campos requeridos
        Returns:
            Tuple (bool, list) - (es_válido, campos_faltantes)
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)

        return len(missing_fields) == 0, missing_fields

    def handle_validation_error(self, missing_fields):
        """
        Maneja errores de validación de campos requeridos
        Args:
            missing_fields: Lista de campos faltantes
        Returns:
            Respuesta de error formateada
        """
        error_message = f"Campos requeridos faltantes: {', '.join(missing_fields)}"
        return self.view.format_error(error_message, "VALIDATION_ERROR")

    def handle_database_error(self, error):
        """
        Maneja errores de base de datos
        Args:
            error: Excepción de base de datos
        Returns:
            Respuesta de error formateada
        """
        error_message = "Error en la base de datos. Intente nuevamente."
        if self.app_config.is_debug_mode():
            error_message += f" Detalles: {str(error)}"

        return self.view.format_error(error_message, "DATABASE_ERROR")

    def success_response(self, data, message="Operación exitosa"):
        """
        Genera una respuesta exitosa
        Args:
            data: Datos a incluir en la respuesta
            message: Mensaje de éxito
        Returns:
            Respuesta exitosa formateada
        """
        return self.view.format_response(data, "success", message)