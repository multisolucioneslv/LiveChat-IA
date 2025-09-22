# Configuración general de la aplicación
# Maneja las variables de entorno y configuraciones globales
# Incluye zona horaria, modo debug y otras configuraciones

import os
import pytz
from dotenv import load_dotenv
from datetime import datetime

# Carga las variables de entorno desde el archivo .env
load_dotenv()


class AppConfig:
    """
    Clase para manejar la configuración general de la aplicación.
    Lee variables de entorno y proporciona configuraciones globales.
    """

    def __init__(self):
        # Configuración del entorno de la aplicación
        self.app_name = os.getenv('APP_NAME', 'LiveChat-IA')
        self.environment = os.getenv('APP_ENV', 'development')
        self.debug = os.getenv('APP_DEBUG', 'false').lower() == 'true'
        self.timezone_str = os.getenv('TIMEZONE', 'UTC')

        # Configuración de zona horaria
        try:
            self.timezone = pytz.timezone(self.timezone_str)
        except pytz.UnknownTimeZoneError:
            print(f"Zona horaria desconocida: {self.timezone_str}. Usando UTC por defecto.")
            self.timezone = pytz.UTC

    def get_environment(self):
        """
        Obtiene el entorno actual de la aplicación
        Returns:
            String con el entorno (development, production, testing)
        """
        return self.environment

    def is_debug_mode(self):
        """
        Verifica si la aplicación está en modo debug
        Returns:
            Boolean indicando si está en modo debug
        """
        return self.debug

    def get_timezone(self):
        """
        Obtiene la zona horaria configurada
        Returns:
            Objeto timezone de pytz
        """
        return self.timezone

    def get_timezone_name(self):
        """
        Obtiene el nombre de la zona horaria
        Returns:
            String con el nombre de la zona horaria
        """
        return self.timezone_str

    def get_current_datetime(self):
        """
        Obtiene la fecha y hora actual en la zona horaria configurada
        Returns:
            Objeto datetime con la fecha y hora actual
        """
        utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        return utc_now.astimezone(self.timezone)

    def is_production(self):
        """
        Verifica si la aplicación está en entorno de producción
        Returns:
            Boolean indicando si está en producción
        """
        return self.environment.lower() == 'production'

    def get_app_name(self):
        """
        Obtiene el nombre de la aplicación
        Returns:
            String con el nombre de la aplicación
        """
        return self.app_name