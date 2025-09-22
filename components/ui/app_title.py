# Componente del título de la aplicación
# Muestra el nombre de la aplicación en la esquina superior

import customtkinter as ctk
from config.app_config import AppConfig


class AppTitle:
    """
    Componente para mostrar el título de la aplicación
    Se posiciona en la esquina superior de la ventana
    """

    def __init__(self, parent):
        self.parent = parent
        self.app_config = AppConfig()

        # Obtener el nombre de la aplicación desde las variables de entorno
        self.app_name = self.app_config.get_app_name()

        self.create_title()

    def create_title(self):
        """Crea y configura el título de la aplicación"""
        self.title_label = ctk.CTkLabel(
            self.parent,
            text=self.app_name,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#2E86AB"  # Color azul corporativo
        )

        # Posicionar en la esquina superior izquierda
        self.title_label.place(x=20, y=20)

    def get_widget(self):
        """Retorna el widget del título"""
        return self.title_label

    def update_title(self, new_title):
        """Actualiza el texto del título"""
        self.title_label.configure(text=new_title)