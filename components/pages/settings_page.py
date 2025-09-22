# Settings Page
# Página de configuraciones generales incluyendo agentes y temas

import customtkinter as ctk
from typing import Dict, Any, Optional
from ..ui.theme_selector import ThemeSelector
from .agent_config_page import AgentConfigPage
from ..ui.themes import get_theme_font, get_theme_color
from utils.logger import app_logger

class SettingsPage:
    """
    Página de configuraciones generales
    Incluye configuración de agentes, temas y otras preferencias
    """

    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz de configuraciones"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

        # Título de la página
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="⚙️ Configuraciones",
            font=get_theme_font("title", "bold")
        )
        title_label.pack(pady=(20, 10))

        # Crear notebook para diferentes secciones
        self.notebook = ctk.CTkTabview(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Crear tabs
        self.create_agents_tab()
        self.create_themes_tab()
        self.create_general_tab()

    def create_agents_tab(self):
        """Crear tab de configuración de agentes"""
        agents_tab = self.notebook.add("🤖 Agentes IA")

        # Integrar la página de configuración de agentes existente
        self.agent_config = AgentConfigPage(agents_tab)

    def create_themes_tab(self):
        """Crear tab de configuración de temas"""
        themes_tab = self.notebook.add("🎨 Temas")

        # Agregar selector de temas
        self.theme_selector = ThemeSelector(
            themes_tab,
            on_theme_change=self.on_theme_changed
        )
        self.theme_selector.pack(fill="both", expand=True, padx=16, pady=16)

    def create_general_tab(self):
        """Crear tab de configuraciones generales"""
        general_tab = self.notebook.add("🔧 General")

        # Frame principal para configuraciones generales
        general_frame = ctk.CTkFrame(general_tab, corner_radius=12)
        general_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # Título
        general_title = ctk.CTkLabel(
            general_frame,
            text="⚙️ Configuraciones Generales",
            font=get_theme_font("lg", "bold")
        )
        general_title.pack(pady=(20, 16))

        # Sección de aplicación
        self.create_app_settings_section(general_frame)

        # Sección de logging
        self.create_logging_settings_section(general_frame)

        # Sección de performance
        self.create_performance_settings_section(general_frame)

    def create_app_settings_section(self, parent):
        """Crear sección de configuraciones de la aplicación"""
        # Frame para configuraciones de app
        app_section = ctk.CTkFrame(parent, corner_radius=8)
        app_section.pack(fill="x", padx=16, pady=8)

        # Título de sección
        app_title = ctk.CTkLabel(
            app_section,
            text="📱 Aplicación",
            font=get_theme_font("md", "bold")
        )
        app_title.pack(anchor="w", padx=16, pady=(12, 8))

        # Frame para controles
        controls_frame = ctk.CTkFrame(app_section, fg_color="transparent")
        controls_frame.pack(fill="x", padx=16, pady=(0, 16))

        # Auto-save de configuraciones
        auto_save_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        auto_save_frame.pack(fill="x", pady=4)

        self.auto_save_var = ctk.BooleanVar(value=True)
        auto_save_checkbox = ctk.CTkCheckBox(
            auto_save_frame,
            text="Guardar configuraciones automáticamente",
            variable=self.auto_save_var,
            font=get_theme_font("sm")
        )
        auto_save_checkbox.pack(side="left")

        # Startup con última sesión
        startup_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        startup_frame.pack(fill="x", pady=4)

        self.restore_session_var = ctk.BooleanVar(value=True)
        restore_checkbox = ctk.CTkCheckBox(
            startup_frame,
            text="Restaurar última sesión al iniciar",
            variable=self.restore_session_var,
            font=get_theme_font("sm")
        )
        restore_checkbox.pack(side="left")

        # Minimizar a bandeja del sistema
        minimize_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        minimize_frame.pack(fill="x", pady=4)

        self.minimize_tray_var = ctk.BooleanVar(value=False)
        minimize_checkbox = ctk.CTkCheckBox(
            minimize_frame,
            text="Minimizar a bandeja del sistema",
            variable=self.minimize_tray_var,
            font=get_theme_font("sm")
        )
        minimize_checkbox.pack(side="left")

    def create_logging_settings_section(self, parent):
        """Crear sección de configuraciones de logging"""
        # Frame para logging
        logging_section = ctk.CTkFrame(parent, corner_radius=8)
        logging_section.pack(fill="x", padx=16, pady=8)

        # Título de sección
        logging_title = ctk.CTkLabel(
            logging_section,
            text="📝 Logging y Reportes",
            font=get_theme_font("md", "bold")
        )
        logging_title.pack(anchor="w", padx=16, pady=(12, 8))

        # Frame para controles
        logging_controls = ctk.CTkFrame(logging_section, fg_color="transparent")
        logging_controls.pack(fill="x", padx=16, pady=(0, 16))

        # Nivel de logging
        level_frame = ctk.CTkFrame(logging_controls, fg_color="transparent")
        level_frame.pack(fill="x", pady=4)

        level_label = ctk.CTkLabel(
            level_frame,
            text="Nivel de logging:",
            font=get_theme_font("sm")
        )
        level_label.pack(side="left", padx=(0, 8))

        self.log_level_selector = ctk.CTkOptionMenu(
            level_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            width=120
        )
        self.log_level_selector.set("INFO")
        self.log_level_selector.pack(side="left")

        # Auto-generar reportes
        reports_frame = ctk.CTkFrame(logging_controls, fg_color="transparent")
        reports_frame.pack(fill="x", pady=4)

        self.auto_reports_var = ctk.BooleanVar(value=True)
        reports_checkbox = ctk.CTkCheckBox(
            reports_frame,
            text="Generar reportes automáticamente",
            variable=self.auto_reports_var,
            font=get_theme_font("sm")
        )
        reports_checkbox.pack(side="left")

    def create_performance_settings_section(self, parent):
        """Crear sección de configuraciones de rendimiento"""
        # Frame para performance
        perf_section = ctk.CTkFrame(parent, corner_radius=8)
        perf_section.pack(fill="x", padx=16, pady=8)

        # Título de sección
        perf_title = ctk.CTkLabel(
            perf_section,
            text="⚡ Rendimiento",
            font=get_theme_font("md", "bold")
        )
        perf_title.pack(anchor="w", padx=16, pady=(12, 8))

        # Frame para controles
        perf_controls = ctk.CTkFrame(perf_section, fg_color="transparent")
        perf_controls.pack(fill="x", padx=16, pady=(0, 16))

        # Habilitar monitoreo de rendimiento
        monitoring_frame = ctk.CTkFrame(perf_controls, fg_color="transparent")
        monitoring_frame.pack(fill="x", pady=4)

        self.performance_monitoring_var = ctk.BooleanVar(value=True)
        monitoring_checkbox = ctk.CTkCheckBox(
            monitoring_frame,
            text="Habilitar monitoreo de rendimiento",
            variable=self.performance_monitoring_var,
            font=get_theme_font("sm")
        )
        monitoring_checkbox.pack(side="left")

        # Límite de historial de chat
        history_frame = ctk.CTkFrame(perf_controls, fg_color="transparent")
        history_frame.pack(fill="x", pady=4)

        history_label = ctk.CTkLabel(
            history_frame,
            text="Límite de historial de chat:",
            font=get_theme_font("sm")
        )
        history_label.pack(side="left", padx=(0, 8))

        self.history_limit_selector = ctk.CTkOptionMenu(
            history_frame,
            values=["100", "500", "1000", "5000", "Sin límite"],
            width=120
        )
        self.history_limit_selector.set("1000")
        self.history_limit_selector.pack(side="left")

        # Frame para botones de acción
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.pack(fill="x", padx=16, pady=16)

        # Botón guardar configuraciones
        save_button = ctk.CTkButton(
            actions_frame,
            text="💾 Guardar Configuraciones",
            command=self.save_settings,
            font=get_theme_font("md", "bold")
        )
        save_button.pack(side="right", padx=8)

        # Botón restaurar defaults
        reset_button = ctk.CTkButton(
            actions_frame,
            text="🔄 Restaurar Defaults",
            command=self.restore_defaults,
            font=get_theme_font("md"),
            fg_color="gray"
        )
        reset_button.pack(side="right", padx=8)

        # Label de estado
        self.settings_status_label = ctk.CTkLabel(
            actions_frame,
            text="Configuraciones cargadas",
            font=get_theme_font("sm")
        )
        self.settings_status_label.pack(side="left", padx=8)

    def on_theme_changed(self, theme_id: str, theme_data: Dict[str, Any]):
        """Manejar cambio de tema"""
        app_logger.info(f"Theme changed to: {theme_id}")

        # Actualizar configuraciones para reflejar el nuevo tema
        self.refresh_ui_with_theme()

        # Mostrar confirmación
        self.settings_status_label.configure(
            text=f"✅ Tema aplicado: {theme_data['name']}"
        )

        # Restaurar mensaje después de 3 segundos
        self.parent.after(3000, lambda: self.settings_status_label.configure(
            text="Configuraciones guardadas"
        ))

    def refresh_ui_with_theme(self):
        """Refrescar UI con el tema actual"""
        # Esta función se puede usar para aplicar cambios de tema
        # a componentes que no se actualizan automáticamente
        pass

    def save_settings(self):
        """Guardar todas las configuraciones"""
        try:
            settings = {
                "app": {
                    "auto_save": self.auto_save_var.get(),
                    "restore_session": self.restore_session_var.get(),
                    "minimize_to_tray": self.minimize_tray_var.get()
                },
                "logging": {
                    "level": self.log_level_selector.get(),
                    "auto_reports": self.auto_reports_var.get()
                },
                "performance": {
                    "monitoring_enabled": self.performance_monitoring_var.get(),
                    "history_limit": self.history_limit_selector.get()
                }
            }

            # Crear directorio de configuraciones
            config_dir = "config"
            import os
            os.makedirs(config_dir, exist_ok=True)

            # Guardar configuraciones
            import json
            with open("config/user_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            self.settings_status_label.configure(text="✅ Configuraciones guardadas")
            app_logger.info("User settings saved successfully")

        except Exception as e:
            self.settings_status_label.configure(text="❌ Error guardando configuraciones")
            app_logger.error(f"Error saving settings: {e}")

    def restore_defaults(self):
        """Restaurar configuraciones por defecto"""
        try:
            # Restaurar valores por defecto
            self.auto_save_var.set(True)
            self.restore_session_var.set(True)
            self.minimize_tray_var.set(False)
            self.log_level_selector.set("INFO")
            self.auto_reports_var.set(True)
            self.performance_monitoring_var.set(True)
            self.history_limit_selector.set("1000")

            self.settings_status_label.configure(text="✅ Configuraciones restauradas")
            app_logger.info("Settings restored to defaults")

        except Exception as e:
            self.settings_status_label.configure(text="❌ Error restaurando configuraciones")
            app_logger.error(f"Error restoring defaults: {e}")

    def load_settings(self):
        """Cargar configuraciones guardadas"""
        try:
            import json
            import os

            if os.path.exists("config/user_settings.json"):
                with open("config/user_settings.json", 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                # Aplicar configuraciones
                app_settings = settings.get("app", {})
                self.auto_save_var.set(app_settings.get("auto_save", True))
                self.restore_session_var.set(app_settings.get("restore_session", True))
                self.minimize_tray_var.set(app_settings.get("minimize_to_tray", False))

                logging_settings = settings.get("logging", {})
                self.log_level_selector.set(logging_settings.get("level", "INFO"))
                self.auto_reports_var.set(logging_settings.get("auto_reports", True))

                perf_settings = settings.get("performance", {})
                self.performance_monitoring_var.set(perf_settings.get("monitoring_enabled", True))
                self.history_limit_selector.set(perf_settings.get("history_limit", "1000"))

                app_logger.info("User settings loaded successfully")

        except Exception as e:
            app_logger.error(f"Error loading settings: {e}")

    def get_current_settings(self) -> Dict[str, Any]:
        """Obtener configuraciones actuales"""
        return {
            "app": {
                "auto_save": self.auto_save_var.get(),
                "restore_session": self.restore_session_var.get(),
                "minimize_to_tray": self.minimize_tray_var.get()
            },
            "logging": {
                "level": self.log_level_selector.get(),
                "auto_reports": self.auto_reports_var.get()
            },
            "performance": {
                "monitoring_enabled": self.performance_monitoring_var.get(),
                "history_limit": self.history_limit_selector.get()
            }
        }