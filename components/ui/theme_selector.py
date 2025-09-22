# Theme Selector Component
# Componente para seleccionar y cambiar temas de la aplicación

import customtkinter as ctk
import tkinter as tk
from typing import Dict, Any, Callable, Optional
from .themes import theme_system, get_current_theme, get_theme_color, get_theme_font
from utils.logger import app_logger

class ThemeSelector(ctk.CTkFrame):
    """
    Componente selector de temas
    Permite al usuario cambiar entre diferentes temas disponibles
    """

    def __init__(self, parent, on_theme_change: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.on_theme_change = on_theme_change
        self.current_theme_id = theme_system.current_theme

        self.setup_ui()
        self.load_theme_previews()

    def setup_ui(self):
        """Configurar interfaz del selector"""
        # Título
        title_label = ctk.CTkLabel(
            self,
            text="🎨 Selector de Temas",
            font=get_theme_font("lg", "bold")
        )
        title_label.pack(pady=(16, 8))

        # Descripción
        desc_label = ctk.CTkLabel(
            self,
            text="Elige un tema para personalizar la apariencia de LiveChat-IA",
            font=get_theme_font("sm"),
            text_color="gray"
        )
        desc_label.pack(pady=(0, 16))

        # Frame scrollable para los temas
        self.themes_scroll = ctk.CTkScrollableFrame(self, height=400)
        self.themes_scroll.pack(fill="both", expand=True, padx=16, pady=8)

        # Frame para controles
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(fill="x", padx=16, pady=8)

        # Botón aplicar
        self.apply_button = ctk.CTkButton(
            controls_frame,
            text="✅ Aplicar Tema",
            command=self.apply_selected_theme,
            font=get_theme_font("md", "bold")
        )
        self.apply_button.pack(side="right", padx=8)

        # Botón preview
        self.preview_button = ctk.CTkButton(
            controls_frame,
            text="👁️ Vista Previa",
            command=self.preview_selected_theme,
            font=get_theme_font("md"),
            fg_color="gray"
        )
        self.preview_button.pack(side="right", padx=8)

        # Label de estado
        self.status_label = ctk.CTkLabel(
            controls_frame,
            text=f"Tema actual: {theme_system.get_theme()['name']}",
            font=get_theme_font("sm")
        )
        self.status_label.pack(side="left", padx=8)

    def load_theme_previews(self):
        """Cargar previews de todos los temas disponibles"""
        # Variable para mantener selección
        self.theme_selection = tk.StringVar(value=self.current_theme_id)

        available_themes = theme_system.get_available_themes()

        for theme_info in available_themes:
            self.create_theme_preview(theme_info)

    def create_theme_preview(self, theme_info: Dict[str, str]):
        """Crear preview de un tema específico"""
        theme_id = theme_info["id"]
        theme_data = theme_system.get_theme(theme_id)

        # Frame principal del preview
        preview_frame = ctk.CTkFrame(self.themes_scroll, corner_radius=12)
        preview_frame.pack(fill="x", pady=8, padx=8)

        # Frame header con radio button y nombre
        header_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(16, 8))

        # Radio button para selección
        radio_button = ctk.CTkRadioButton(
            header_frame,
            text="",
            variable=self.theme_selection,
            value=theme_id,
            command=self.on_selection_changed
        )
        radio_button.pack(side="left")

        # Información del tema
        theme_info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        theme_info_frame.pack(side="left", fill="x", expand=True, padx=(12, 0))

        # Nombre del tema
        name_label = ctk.CTkLabel(
            theme_info_frame,
            text=theme_info["name"],
            font=get_theme_font("md", "bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")

        # Descripción del tema
        desc_label = ctk.CTkLabel(
            theme_info_frame,
            text=theme_info["description"],
            font=get_theme_font("sm"),
            text_color="gray",
            anchor="w"
        )
        desc_label.pack(anchor="w")

        # Preview visual del tema
        self.create_visual_preview(preview_frame, theme_data)

    def create_visual_preview(self, parent, theme_data: Dict[str, Any]):
        """Crear preview visual de los colores del tema"""
        colors = theme_data["colors"]

        # Frame para el preview visual
        visual_frame = ctk.CTkFrame(parent, corner_radius=8)
        visual_frame.pack(fill="x", padx=16, pady=(0, 16))

        # Frame para paleta de colores principales
        colors_frame = ctk.CTkFrame(visual_frame, fg_color="transparent")
        colors_frame.pack(fill="x", padx=12, pady=12)

        # Título del preview
        preview_title = ctk.CTkLabel(
            colors_frame,
            text="Vista Previa de Colores:",
            font=get_theme_font("sm", "bold")
        )
        preview_title.pack(anchor="w", pady=(0, 8))

        # Frame para las muestras de color
        color_samples_frame = ctk.CTkFrame(colors_frame, fg_color="transparent")
        color_samples_frame.pack(fill="x")

        # Colores principales a mostrar
        main_colors = [
            ("Primario", colors.get("primary", "#000000")),
            ("Secundario", colors.get("secondary", "#000000")),
            ("Acento", colors.get("accent", "#000000")),
            ("Fondo", colors.get("background", "#ffffff")),
            ("Superficie", colors.get("surface", "#ffffff")),
            ("Éxito", colors.get("success", "#00ff00")),
            ("Error", colors.get("error", "#ff0000"))
        ]

        # Crear muestras de color en grid
        for i, (color_name, color_value) in enumerate(main_colors):
            self.create_color_sample(color_samples_frame, color_name, color_value, i)

    def create_color_sample(self, parent, color_name: str, color_value: str, index: int):
        """Crear muestra individual de color"""
        # Calcular posición en grid (4 columnas)
        row = index // 4
        col = index % 4

        # Frame para la muestra
        sample_frame = ctk.CTkFrame(parent, fg_color="transparent")
        sample_frame.grid(row=row, column=col, padx=4, pady=4, sticky="w")

        # Crear un frame pequeño con el color
        color_box = ctk.CTkFrame(
            sample_frame,
            width=24,
            height=24,
            corner_radius=4,
            fg_color=color_value
        )
        color_box.pack(side="left", padx=(0, 8))

        # Configurar el grid para que se ajuste
        color_box.pack_propagate(False)

        # Label con el nombre del color
        color_label = ctk.CTkLabel(
            sample_frame,
            text=color_name,
            font=get_theme_font("xs"),
            anchor="w"
        )
        color_label.pack(side="left")

    def on_selection_changed(self):
        """Manejar cambio de selección de tema"""
        selected_theme = self.theme_selection.get()
        theme_data = theme_system.get_theme(selected_theme)

        self.status_label.configure(text=f"Seleccionado: {theme_data['name']}")

        app_logger.info(f"Theme selection changed to: {selected_theme}")

    def preview_selected_theme(self):
        """Vista previa del tema seleccionado"""
        selected_theme = self.theme_selection.get()

        if selected_theme == self.current_theme_id:
            self.status_label.configure(text="Este tema ya está activo")
            return

        # Aplicar temporalmente el tema
        theme_system.set_theme(selected_theme)

        # Crear ventana de preview
        self.create_preview_window(selected_theme)

        # Restaurar tema anterior
        theme_system.set_theme(self.current_theme_id)

    def create_preview_window(self, theme_id: str):
        """Crear ventana de vista previa del tema"""
        theme_data = theme_system.get_theme(theme_id)

        # Crear ventana toplevel
        preview_window = ctk.CTkToplevel(self)
        preview_window.title(f"Vista Previa - {theme_data['name']}")
        preview_window.geometry("600x400")

        # Aplicar colores del tema a la ventana
        colors = theme_data["colors"]
        preview_window.configure(fg_color=colors.get("background", "#ffffff"))

        # Contenido de ejemplo
        main_frame = ctk.CTkFrame(
            preview_window,
            fg_color=colors.get("surface", "#ffffff"),
            corner_radius=12
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Vista Previa: {theme_data['name']}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=colors.get("text_primary", "#000000")
        )
        title_label.pack(pady=20)

        # Botones de ejemplo
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=20)

        # Botón primario
        primary_btn = ctk.CTkButton(
            buttons_frame,
            text="Botón Primario",
            fg_color=colors.get("primary", "#0000ff"),
            hover_color=colors.get("primary_hover", "#0000cc")
        )
        primary_btn.pack(side="left", padx=8)

        # Botón secundario
        secondary_btn = ctk.CTkButton(
            buttons_frame,
            text="Botón Secundario",
            fg_color=colors.get("button_secondary", "#f0f0f0"),
            text_color=colors.get("text_primary", "#000000")
        )
        secondary_btn.pack(side="left", padx=8)

        # Texto de ejemplo
        text_example = ctk.CTkLabel(
            main_frame,
            text="Este es un ejemplo de cómo se vería el texto en este tema.\nIncluye texto primario y secundario para mostrar el contraste.",
            font=ctk.CTkFont(size=14),
            text_color=colors.get("text_primary", "#000000"),
            justify="center"
        )
        text_example.pack(pady=20)

        # Botón cerrar
        close_btn = ctk.CTkButton(
            main_frame,
            text="Cerrar Vista Previa",
            command=preview_window.destroy,
            fg_color=colors.get("button_danger", "#ff0000")
        )
        close_btn.pack(pady=20)

    def apply_selected_theme(self):
        """Aplicar el tema seleccionado"""
        selected_theme = self.theme_selection.get()

        if selected_theme == self.current_theme_id:
            self.status_label.configure(text="Este tema ya está activo")
            return

        try:
            # Cambiar tema
            theme_system.set_theme(selected_theme)
            theme_system.save_theme_preference(selected_theme)

            self.current_theme_id = selected_theme
            theme_data = theme_system.get_theme(selected_theme)

            self.status_label.configure(text=f"✅ Aplicado: {theme_data['name']}")

            app_logger.info(f"Theme applied: {selected_theme}")

            # Notificar callback si existe
            if self.on_theme_change:
                self.on_theme_change(selected_theme, theme_data)

            # Mostrar mensaje de reinicio recomendado
            self.show_restart_message()

        except Exception as e:
            app_logger.error(f"Error applying theme: {e}")
            self.status_label.configure(text="❌ Error aplicando tema")

    def show_restart_message(self):
        """Mostrar mensaje recomendando reiniciar la aplicación"""
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Tema Aplicado")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()

        # Centrar la ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")

        # Contenido
        content_frame = ctk.CTkFrame(dialog)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Icono y mensaje
        message_label = ctk.CTkLabel(
            content_frame,
            text="✅ Tema aplicado correctamente",
            font=get_theme_font("lg", "bold")
        )
        message_label.pack(pady=(20, 10))

        info_label = ctk.CTkLabel(
            content_frame,
            text="Se recomienda reiniciar la aplicación\npara ver todos los cambios aplicados.",
            font=get_theme_font("md"),
            justify="center"
        )
        info_label.pack(pady=10)

        # Botón OK
        ok_button = ctk.CTkButton(
            content_frame,
            text="Entendido",
            command=dialog.destroy,
            width=120
        )
        ok_button.pack(pady=20)

    def refresh_theme_display(self):
        """Refrescar la visualización del selector con el tema actual"""
        # Limpiar contenido actual
        for widget in self.themes_scroll.winfo_children():
            widget.destroy()

        # Recargar previews
        self.load_theme_previews()

        # Actualizar status
        current_theme_data = theme_system.get_theme()
        self.status_label.configure(text=f"Tema actual: {current_theme_data['name']}")