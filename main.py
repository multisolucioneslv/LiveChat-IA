# Archivo principal de la aplicación
# Punto de entrada del programa con interfaz gráfica
# Ventana de 1200x800 con contenido ajustado y padding del 10%

import customtkinter as ctk
import sys
import os

# Configurar el appearance mode y color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Agregar las rutas de los módulos al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.app_config import AppConfig
from components.layout.navbar import Navbar
from components.layout.footer import AnimatedFooter
from components.ui.chat_interface import ChatInterface
from components.pages.agent_config_page import AgentConfigPage
from testing.test_agent import TestAgent


class LiveChatApp:
    """
    Aplicación principal con interfaz gráfica
    Ventana de 1200x800 con diseño ejecutivo y moderno
    """

    def __init__(self):
        # Configuración de la aplicación
        self.app_config = AppConfig()
        self.current_section = "Inicio"

        # Configuración de la ventana principal
        self.setup_main_window()

        # Inicializar agente de pruebas
        self.test_agent = TestAgent()

        # Crear componentes de la interfaz
        self.create_components()

        # Crear footer animado
        self.footer = AnimatedFooter(self.main_frame)

        # Mostrar sección inicial
        self.show_section("Inicio")

    def setup_main_window(self):
        """Configura la ventana principal de la aplicación"""
        self.root = ctk.CTk()
        self.root.title(self.app_config.get_app_name())
        self.root.geometry("1200x800")
        self.root.minsize(1200, 800)
        self.root.maxsize(1200, 800)  # Fijar tamaño exacto

        # Centrar la ventana en la pantalla
        self.center_window()

        # Configurar el cierre de la ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Frame principal sin padding
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color="#F8F9FA",
            corner_radius=0
        )
        self.main_frame.pack(
            fill="both",
            expand=True
        )

    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - 1200) // 2
        y = (screen_height - 800) // 2

        self.root.geometry(f"1200x800+{x}+{y}")

    def create_components(self):
        """Crea todos los componentes de la interfaz"""
        # Barra de navegación
        self.navbar = Navbar(self.main_frame, self.on_menu_change)

        # Frame para el contenido principal
        self.content_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.content_frame.pack(fill="both", expand=True)

        # Crear las diferentes secciones
        self.create_sections()

    def create_sections(self):
        """Crea las diferentes secciones de la aplicación"""
        self.sections = {}

        # Sección Inicio - Chat
        self.sections["Inicio"] = self.create_inicio_section()

        # Sección Configuraciones
        self.sections["Configuraciones"] = self.create_configuraciones_section()

        # Sección Administración
        self.sections["Administración"] = self.create_administracion_section()

    def create_inicio_section(self):
        """Crea la sección de inicio con el chat"""
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        # Interfaz de chat
        self.chat_interface = ChatInterface(frame, self.test_agent)

        return frame

    def create_configuraciones_section(self):
        """Crea la sección de configuraciones"""
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        # Página de configuración de agentes
        self.agent_config_page = AgentConfigPage(frame)

        return frame

    def create_administracion_section(self):
        """Crea la sección de administración"""
        frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10)

        # Título de la sección
        title_label = ctk.CTkLabel(
            frame,
            text="👨‍💼 Administración",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#2E86AB"
        )
        title_label.pack(pady=30)

        # Contenido de administración
        admin_label = ctk.CTkLabel(
            frame,
            text="Panel de administración\n\nFunciones disponibles:\n• Gestión de usuarios\n• Monitoreo del sistema\n• Logs y estadísticas\n• Configuración avanzada",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        admin_label.pack(pady=20)

        return frame

    def on_menu_change(self, menu_name):
        """Maneja el cambio de menú en la navegación"""
        self.show_section(menu_name)

    def show_section(self, section_name):
        """Muestra la sección seleccionada y oculta las demás"""
        # Ocultar todas las secciones
        for section in self.sections.values():
            section.pack_forget()

        # Mostrar la sección seleccionada
        if section_name in self.sections:
            self.sections[section_name].pack(fill="both", expand=True)
            self.current_section = section_name

    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        print("Cerrando aplicación...")
        self.root.quit()
        self.root.destroy()

    def run(self):
        """Inicia la aplicación"""
        print(f"=== Iniciando {self.app_config.get_app_name()} ===")
        print(f"Entorno: {self.app_config.get_environment()}")
        print(f"Ventana: 1200x800 con padding del 10%")
        print("=== Aplicación iniciada ===")

        self.root.mainloop()


def main():
    """
    Función principal de la aplicación
    Crea e inicia la aplicación con interfaz gráfica
    """
    try:
        app = LiveChatApp()
        app.run()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        input("Presiona Enter para salir...")


if __name__ == "__main__":
    main()