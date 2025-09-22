# Componente de botón reutilizable
# Botón personalizable para toda la aplicación

import customtkinter as ctk


class Button:
    """
    Componente de botón reutilizable
    Proporciona botones consistentes en toda la aplicación
    """

    def __init__(self, parent, text, command=None, **kwargs):
        self.parent = parent
        self.text = text
        self.command = command

        # Configuración por defecto
        self.default_config = {
            "font": ctk.CTkFont(size=12, weight="bold"),
            "width": 100,
            "height": 40,
            "corner_radius": 20,
            "fg_color": "#2E86AB",
            "hover_color": "#A23B72",
            "text_color": "white"
        }

        # Combinar configuración por defecto con kwargs
        self.config = {**self.default_config, **kwargs}

        self.create_button()

    def create_button(self):
        """Crea el botón con la configuración especificada"""
        self.button = ctk.CTkButton(
            self.parent,
            text=self.text,
            command=self.command,
            **self.config
        )

    def pack(self, **kwargs):
        """Empaqueta el botón"""
        self.button.pack(**kwargs)

    def place(self, **kwargs):
        """Posiciona el botón"""
        self.button.place(**kwargs)

    def grid(self, **kwargs):
        """Coloca el botón en grid"""
        self.button.grid(**kwargs)

    def configure(self, **kwargs):
        """Configura propiedades del botón"""
        self.button.configure(**kwargs)

    def get_widget(self):
        """Retorna el widget del botón"""
        return self.button

    def destroy(self):
        """Destruye el botón"""
        self.button.destroy()


class PrimaryButton(Button):
    """Botón primario con estilo predefinido"""

    def __init__(self, parent, text, command=None, **kwargs):
        primary_style = {
            "fg_color": "#2E86AB",
            "hover_color": "#1E5F7A",
            "width": 120,
            "height": 45
        }
        super().__init__(parent, text, command, **{**primary_style, **kwargs})


class SecondaryButton(Button):
    """Botón secundario con estilo predefinido"""

    def __init__(self, parent, text, command=None, **kwargs):
        secondary_style = {
            "fg_color": "#A23B72",
            "hover_color": "#7A2D56",
            "width": 120,
            "height": 45
        }
        super().__init__(parent, text, command, **{**secondary_style, **kwargs})


class AccentButton(Button):
    """Botón de acento con estilo predefinido"""

    def __init__(self, parent, text, command=None, **kwargs):
        accent_style = {
            "fg_color": "#F18F01",
            "hover_color": "#C7740A",
            "width": 120,
            "height": 45
        }
        super().__init__(parent, text, command, **{**accent_style, **kwargs})