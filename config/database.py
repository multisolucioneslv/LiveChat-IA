# Configuración de la base de datos
# Maneja la conexión y parámetros de MySQL
# Lee las variables de entorno para la configuración de la base de datos

import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()


class DatabaseConfig:
    """
    Clase para manejar la configuración de la base de datos MySQL.
    Lee las variables de entorno y proporciona los parámetros de conexión.
    """

    def __init__(self):
        # Configuración de la base de datos desde variables de entorno
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.database = os.getenv('DB_NAME', 'test_db')
        self.username = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')

    def get_config(self):
        """
        Obtiene la configuración de conexión a la base de datos
        Returns:
            Diccionario con los parámetros de conexión
        """
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.username,
            'password': self.password,
            'charset': 'utf8mb4',
            'autocommit': True
        }

    def get_connection_string(self):
        """
        Genera la cadena de conexión para la base de datos
        Returns:
            String con la URL de conexión (sin incluir la contraseña por seguridad)
        """
        return f"mysql://{self.username}@{self.host}:{self.port}/{self.database}"