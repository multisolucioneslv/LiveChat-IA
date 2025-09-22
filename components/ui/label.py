# Componente de etiqueta reutilizable
# Labels personalizables para toda la aplicación

import customtkinter as ctk


class Label:
    """
    Componente de etiqueta reutilizable
    Proporciona etiquetas consistentes en toda la aplicación
    """

    def __init__(self, parent, text="", **kwargs):
        self.parent = parent
        self.text = text

        # Configuración por defecto
        self.default_config = {
            "font": ctk.CTkFont(size=12),
            "text_color": "#333333",
            "fg_color": "transparent"
        }

        # Combinar configuración por defecto con kwargs
        self.config = {**self.default_config, **kwargs}

        self.create_label()

    def create_label(self):
        """Crea la etiqueta con la configuración especificada"""
        self.label = ctk.CTkLabel(
            self.parent,
            text=self.text,
            **self.config
        )

    def pack(self, **kwargs):
        """Empaqueta la etiqueta"""
        self.label.pack(**kwargs)

    def place(self, **kwargs):
        """Posiciona la etiqueta"""
        self.label.place(**kwargs)

    def grid(self, **kwargs):
        """Coloca la etiqueta en grid"""
        self.label.grid(**kwargs)

    def configure(self, **kwargs):
        """Configura propiedades de la etiqueta"""
        self.label.configure(**kwargs)

    def get_widget(self):
        """Retorna el widget de la etiqueta"""
        return self.label

    def destroy(self):
        """Destruye la etiqueta"""
        self.label.destroy()


class TitleLabel(Label):
    """Etiqueta de título con estilo predefinido"""

    def __init__(self, parent, text="", **kwargs):
        title_style = {
            "font": ctk.CTkFont(size=24, weight="bold"),
            "text_color": "#2E86AB"
        }
        super().__init__(parent, text, **{**title_style, **kwargs})


class SubtitleLabel(Label):
    """Etiqueta de subtítulo con estilo predefinido"""

    def __init__(self, parent, text="", **kwargs):
        subtitle_style = {
            "font": ctk.CTkFont(size=18, weight="bold"),
            "text_color": "#A23B72"
        }
        super().__init__(parent, text, **{**subtitle_style, **kwargs})


class BodyLabel(Label):
    """Etiqueta de cuerpo con estilo predefinido"""

    def __init__(self, parent, text="", **kwargs):
        body_style = {
            "font": ctk.CTkFont(size=14),
            "text_color": "#666666"
        }
        super().__init__(parent, text, **{**body_style, **kwargs})


class CaptionLabel(Label):
    """Etiqueta de caption con estilo predefinido"""

    def __init__(self, parent, text="", **kwargs):
        caption_style = {
            "font": ctk.CTkFont(size=11),
            "text_color": "#999999"
        }
        super().__init__(parent, text, **{**caption_style, **kwargs})


class ErrorLabel(Label):
    """Etiqueta de error con estilo predefinido"""

    def __init__(self, parent, text="", **kwargs):
        error_style = {
            "font": ctk.CTkFont(size=12, weight="bold"),
            "text_color": "#E74C3C"
        }
        super().__init__(parent, text, **{**error_style, **kwargs})


class SuccessLabel(Label):
    """Etiqueta de éxito con estilo predefinido"""

    def __init__(self, parent, text="", **kwargs):
        success_style = {
            "font": ctk.CTkFont(size=12, weight="bold"),
            "text_color": "#27AE60"
        }
        super().__init__(parent, text, **{**success_style, **kwargs})