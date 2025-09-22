# Modelo base para todas las entidades
# Contiene la configuración común de conexión a la base de datos
# y métodos básicos de CRUD (Crear, Leer, Actualizar, Eliminar)

import mysql.connector
from config.database import DatabaseConfig


class BaseModel:
    """
    Clase base para todos los modelos de la aplicación.
    Proporciona funcionalidades comunes de conexión a la base de datos.
    """

    def __init__(self):
        # Inicializa la conexión a la base de datos usando la configuración
        self.db_config = DatabaseConfig()
        self.connection = None

    def connect(self):
        """Establece conexión con la base de datos MySQL"""
        try:
            self.connection = mysql.connector.connect(**self.db_config.get_config())
            return self.connection
        except mysql.connector.Error as error:
            print(f"Error al conectar con la base de datos: {error}")
            return None

    def disconnect(self):
        """Cierra la conexión con la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query, params=None):
        """
        Ejecuta una consulta en la base de datos
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
        Returns:
            Resultado de la consulta o None si hay error
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except mysql.connector.Error as error:
            print(f"Error al ejecutar consulta: {error}")
            return None