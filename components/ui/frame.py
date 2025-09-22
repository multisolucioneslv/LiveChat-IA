# Componente de frame reutilizable
# Contenedores personalizables para toda la aplicación

import customtkinter as ctk


class Frame:
    """
    Componente de frame reutilizable
    Proporciona contenedores consistentes en toda la aplicación
    """

    def __init__(self, parent, **kwargs):
        self.parent = parent

        # Configuración por defecto
        self.default_config = {
            "fg_color": "white",
            "corner_radius": 10,
            "border_width": 0
        }

        # Combinar configuración por defecto con kwargs
        self.config = {**self.default_config, **kwargs}

        self.create_frame()

    def create_frame(self):
        """Crea el frame con la configuración especificada"""
        self.frame = ctk.CTkFrame(
            self.parent,
            **self.config
        )

    def pack(self, **kwargs):
        """Empaqueta el frame"""
        self.frame.pack(**kwargs)

    def place(self, **kwargs):
        """Posiciona el frame"""
        self.frame.place(**kwargs)

    def grid(self, **kwargs):
        """Coloca el frame en grid"""
        self.frame.grid(**kwargs)

    def configure(self, **kwargs):
        """Configura propiedades del frame"""
        self.frame.configure(**kwargs)

    def get_widget(self):
        """Retorna el widget del frame"""
        return self.frame

    def destroy(self):
        """Destruye el frame"""
        self.frame.destroy()


class CardFrame(Frame):
    """Frame tipo tarjeta con estilo predefinido"""

    def __init__(self, parent, **kwargs):
        card_style = {
            "fg_color": "white",
            "corner_radius": 15,
            "border_width": 1,
            "border_color": "#E0E0E0"
        }
        super().__init__(parent, **{**card_style, **kwargs})


class PanelFrame(Frame):
    """Frame tipo panel con estilo predefinido"""

    def __init__(self, parent, **kwargs):
        panel_style = {
            "fg_color": "#F8F9FA",
            "corner_radius": 10,
            "border_width": 0
        }
        super().__init__(parent, **{**panel_style, **kwargs})


class SidebarFrame(Frame):
    """Frame para sidebar con estilo predefinido"""

    def __init__(self, parent, **kwargs):
        sidebar_style = {
            "fg_color": "#2E86AB",
            "corner_radius": 0,
            "border_width": 0
        }
        super().__init__(parent, **{**sidebar_style, **kwargs})


class TransparentFrame(Frame):
    """Frame transparente con estilo predefinido"""

    def __init__(self, parent, **kwargs):
        transparent_style = {
            "fg_color": "transparent",
            "corner_radius": 0,
            "border_width": 0
        }
        super().__init__(parent, **{**transparent_style, **kwargs})