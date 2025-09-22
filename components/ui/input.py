# Componente de input reutilizable
# Campo de entrada personalizable para toda la aplicación

import customtkinter as ctk


class Input:
    """
    Componente de input reutilizable
    Proporciona campos de entrada consistentes en toda la aplicación
    """

    def __init__(self, parent, placeholder_text="", **kwargs):
        self.parent = parent
        self.placeholder_text = placeholder_text

        # Configuración por defecto
        self.default_config = {
            "font": ctk.CTkFont(size=12),
            "height": 40,
            "corner_radius": 20,
            "border_width": 2,
            "fg_color": "white",
            "border_color": "#2E86AB",
            "text_color": "#333333",
            "placeholder_text_color": "#999999"
        }

        # Combinar configuración por defecto con kwargs
        self.config = {**self.default_config, **kwargs}

        self.create_input()

    def create_input(self):
        """Crea el input con la configuración especificada"""
        self.input = ctk.CTkEntry(
            self.parent,
            placeholder_text=self.placeholder_text,
            **self.config
        )

    def pack(self, **kwargs):
        """Empaqueta el input"""
        self.input.pack(**kwargs)

    def place(self, **kwargs):
        """Posiciona el input"""
        self.input.place(**kwargs)

    def grid(self, **kwargs):
        """Coloca el input en grid"""
        self.input.grid(**kwargs)

    def get(self):
        """Obtiene el valor del input"""
        return self.input.get()

    def set(self, value):
        """Establece el valor del input"""
        self.input.delete(0, "end")
        self.input.insert(0, value)

    def delete(self, first, last=None):
        """Elimina texto del input"""
        self.input.delete(first, last)

    def insert(self, index, string):
        """Inserta texto en el input"""
        self.input.insert(index, string)

    def configure(self, **kwargs):
        """Configura propiedades del input"""
        self.input.configure(**kwargs)

    def bind(self, sequence, func):
        """Vincula eventos al input"""
        self.input.bind(sequence, func)

    def focus(self):
        """Enfoca el input"""
        self.input.focus()

    def get_widget(self):
        """Retorna el widget del input"""
        return self.input

    def destroy(self):
        """Destruye el input"""
        self.input.destroy()


class SearchInput(Input):
    """Input de búsqueda con estilo predefinido"""

    def __init__(self, parent, **kwargs):
        search_style = {
            "placeholder_text": "Buscar...",
            "width": 250,
            "border_color": "#A23B72"
        }
        super().__init__(parent, **{**search_style, **kwargs})


class PasswordInput(Input):
    """Input de contraseña con texto oculto"""

    def __init__(self, parent, **kwargs):
        password_style = {
            "placeholder_text": "Contraseña",
            "show": "*",
            "width": 200
        }
        super().__init__(parent, **{**password_style, **kwargs})


class EmailInput(Input):
    """Input de email con validación visual"""

    def __init__(self, parent, **kwargs):
        email_style = {
            "placeholder_text": "correo@ejemplo.com",
            "width": 250,
            "border_color": "#F18F01"
        }
        super().__init__(parent, **{**email_style, **kwargs})


class TextArea:
    """
    Componente de área de texto (textbox) reutilizable
    Para texto multilínea
    """

    def __init__(self, parent, **kwargs):
        self.parent = parent

        # Configuración por defecto
        self.default_config = {
            "font": ctk.CTkFont(size=12),
            "corner_radius": 10,
            "border_width": 2,
            "fg_color": "white",
            "border_color": "#2E86AB",
            "text_color": "#333333",
            "scrollbar_button_color": "#2E86AB",
            "scrollbar_button_hover_color": "#A23B72"
        }

        # Combinar configuración por defecto con kwargs
        self.config = {**self.default_config, **kwargs}

        self.create_textarea()

    def create_textarea(self):
        """Crea el textarea con la configuración especificada"""
        # Filtrar parámetros no soportados por CTkTextbox
        filtered_config = {k: v for k, v in self.config.items()
                          if k not in ['placeholder_text']}

        self.textarea = ctk.CTkTextbox(
            self.parent,
            **filtered_config
        )

    def pack(self, **kwargs):
        """Empaqueta el textarea"""
        self.textarea.pack(**kwargs)

    def place(self, **kwargs):
        """Posiciona el textarea"""
        self.textarea.place(**kwargs)

    def grid(self, **kwargs):
        """Coloca el textarea en grid"""
        self.textarea.grid(**kwargs)

    def get(self, start="1.0", end="end"):
        """Obtiene el contenido del textarea"""
        return self.textarea.get(start, end)

    def insert(self, index, text, tags=None):
        """Inserta texto en el textarea"""
        if tags:
            self.textarea.insert(index, text, tags)
        else:
            self.textarea.insert(index, text)

    def delete(self, start, end=None):
        """Elimina texto del textarea"""
        self.textarea.delete(start, end)

    def see(self, index):
        """Hace scroll hacia una posición específica"""
        self.textarea.see(index)

    def configure(self, **kwargs):
        """Configura propiedades del textarea"""
        self.textarea.configure(**kwargs)

    def get_widget(self):
        """Retorna el widget del textarea"""
        return self.textarea

    def destroy(self):
        """Destruye el textarea"""
        self.textarea.destroy()