# Componente de navegación
# Barra de navegación con opciones: Inicio, Configuraciones, Administración

import customtkinter as ctk
from ..ui.frame import Frame, TransparentFrame
from ..ui.button import Button


class Navbar:
    """
    Componente de barra de navegación
    Contiene las opciones principales del menú centradas y con diseño ejecutivo
    """

    def __init__(self, parent, on_menu_change):
        self.parent = parent
        self.on_menu_change = on_menu_change  # Callback para cambio de menú
        self.current_menu = "Inicio"  # Menú activo por defecto

        # Configuración de colores y estilos
        self.primary_color = "#2E86AB"
        self.secondary_color = "#A23B72"
        self.accent_color = "#F18F01"
        self.bg_color = "#F5F5F5"
        self.text_color = "#333333"

        self.create_navbar()

    def create_navbar(self):
        """Crea la barra de navegación con diseño centrado"""
        # Frame principal del navbar
        self.navbar_frame = ctk.CTkFrame(
            self.parent,
            height=80,
            fg_color=self.bg_color,
            corner_radius=0
        )
        self.navbar_frame.pack(fill="x", padx=0, pady=0)

        # Frame contenedor para centrar los botones usando componente
        self.buttons_frame = TransparentFrame(self.navbar_frame)
        self.buttons_frame.pack(expand=True)

        # Crear botones del menú
        self.menu_buttons = {}
        menu_items = [
            ("Inicio", "🏠"),
            ("Beam", "⚡"),
            ("Dashboard", "📊"),
            ("Configuraciones", "⚙️"),
            ("Administración", "👨‍💼")
        ]

        for i, (menu_name, icon) in enumerate(menu_items):
            self.create_menu_button(menu_name, icon, i)

        # Marcar el primer botón como activo
        self.set_active_menu("Inicio")

    def create_menu_button(self, menu_name, icon, index):
        """Crea un botón de menú individual usando componente"""
        button = Button(
            self.buttons_frame.get_widget(),
            text=f"{icon} {menu_name}",
            command=lambda: self.menu_clicked(menu_name),
            font=ctk.CTkFont(size=16, weight="bold"),
            width=180,
            height=50,
            corner_radius=25,
            fg_color=self.primary_color,
            hover_color=self.secondary_color,
            text_color="white"
        )

        # Posicionar botones horizontalmente centrados
        button.pack(side="left", padx=15, pady=15)
        self.menu_buttons[menu_name] = button

    def menu_clicked(self, menu_name):
        """Maneja el clic en un botón de menú"""
        if menu_name != self.current_menu:
            self.set_active_menu(menu_name)
            if self.on_menu_change:
                self.on_menu_change(menu_name)

    def set_active_menu(self, menu_name):
        """Establece el menú activo y actualiza el estilo visual"""
        # Resetear todos los botones al color normal
        for button in self.menu_buttons.values():
            button.configure(fg_color=self.primary_color)

        # Resaltar el botón activo
        if menu_name in self.menu_buttons:
            self.menu_buttons[menu_name].configure(fg_color=self.accent_color)
            self.current_menu = menu_name

    def get_widget(self):
        """Retorna el widget principal del navbar"""
        return self.navbar_frame

    def get_current_menu(self):
        """Retorna el menú actualmente seleccionado"""
        return self.current_menu