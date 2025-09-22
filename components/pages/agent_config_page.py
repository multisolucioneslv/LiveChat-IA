# Página de configuración de agentes IA
# Panel para gestionar agentes y sus configuraciones

import customtkinter as ctk
import json
import os
import threading
from tkinter import messagebox
from typing import Dict, Any, Optional
from ..ui.frame import Frame, CardFrame
from ..ui.label import TitleLabel, SubtitleLabel
from ..ui.input import Input
from ..ui.button import PrimaryButton, SecondaryButton
from ..ui.input import TextArea
from models.agent_model import AgentModel
from agents import AgentFactory
from utils.logger import app_logger


class AgentConfigPage:
    """
    Página de configuración de agentes IA
    Permite crear, editar y probar agentes
    """

    def __init__(self, parent):
        self.parent = parent
        self.agent_model = AgentModel()
        self.current_agent_id = None
        self.agents_list = []

        # Colores del tema
        self.primary_color = "#2E86AB"
        self.secondary_color = "#F5F5F5"
        self.success_color = "#28A745"
        self.error_color = "#DC3545"

        self.create_config_page()
        self.load_agents_list()

    def create_config_page(self):
        """Crea la página de configuración de agentes"""
        # Frame principal
        self.main_frame = Frame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        title = TitleLabel(
            self.main_frame.get_widget(),
            text="⚙️ Configuración de Agentes IA"
        )
        title.pack(pady=(0, 20))

        # Crear layout de dos columnas
        self.create_layout()

        # Crear secciones
        self.create_agents_list_section()
        self.create_agent_form_section()

    def create_layout(self):
        """Crea el layout de columnas"""
        # Frame contenedor horizontal
        container = Frame(self.main_frame.get_widget(), fg_color="transparent")
        container.pack(fill="both", expand=True)

        # Columna izquierda - Lista de agentes
        self.left_frame = CardFrame(container.get_widget())
        self.left_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))
        self.left_frame.get_widget().configure(width=350)

        # Columna derecha - Formulario
        self.right_frame = CardFrame(container.get_widget())
        self.right_frame.pack(side="right", fill="both", expand=True)

    def create_agents_list_section(self):
        """Crea la sección de lista de agentes"""
        # Título de la sección
        list_title = SubtitleLabel(
            self.left_frame.get_widget(),
            text="📋 Agentes Configurados"
        )
        list_title.pack(pady=(10, 15))

        # Frame para lista y botones
        list_container = Frame(self.left_frame.get_widget(), fg_color="transparent")
        list_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Lista de agentes (simulada con TextArea)
        self.agents_listbox = TextArea(
            list_container.get_widget(),
            height=250,
            fg_color="white",
            text_color="#333333"
        )
        self.agents_listbox.pack(fill="both", expand=True, pady=(0, 10))

        # Frame para botones de lista
        buttons_frame = Frame(list_container.get_widget(), fg_color="transparent")
        buttons_frame.pack(fill="x")

        # Botón nuevo agente
        new_btn = PrimaryButton(
            buttons_frame.get_widget(),
            text="➕ Nuevo",
            command=self.new_agent,
            width=100,
            height=35
        )
        new_btn.pack(side="left", padx=(0, 5))

        # Botón editar agente
        edit_btn = SecondaryButton(
            buttons_frame.get_widget(),
            text="✏️ Editar",
            command=self.edit_agent,
            width=100,
            height=35
        )
        edit_btn.pack(side="left", padx=5)

        # Botón eliminar agente
        delete_btn = SecondaryButton(
            buttons_frame.get_widget(),
            text="🗑️ Eliminar",
            command=self.delete_agent,
            width=100,
            height=35
        )
        delete_btn.pack(side="left", padx=(5, 0))

    def create_agent_form_section(self):
        """Crea la sección del formulario"""
        # Título de la sección
        form_title = SubtitleLabel(
            self.right_frame.get_widget(),
            text="🔧 Configuración del Agente"
        )
        form_title.pack(pady=(10, 20))

        # Frame del formulario
        form_frame = Frame(self.right_frame.get_widget(), fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Campos del formulario
        self.create_form_fields(form_frame)

        # Botones de acción
        self.create_form_buttons(form_frame)

    def create_form_fields(self, parent):
        """Crea los campos del formulario"""
        # Nombre del agente
        ctk.CTkLabel(parent.get_widget(), text="Nombre del Agente:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.name_entry = Input(parent.get_widget(), placeholder_text="Ej: GPT-4o Personal")
        self.name_entry.pack(fill="x", pady=(0, 15))

        # Proveedor
        ctk.CTkLabel(parent.get_widget(), text="Proveedor:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.provider_combo = ctk.CTkComboBox(
            parent.get_widget(),
            values=["openai", "anthropic", "google", "ollama", "groq", "together"],
            command=self.on_provider_change
        )
        self.provider_combo.pack(fill="x", pady=(0, 15))

        # Modelo
        ctk.CTkLabel(parent.get_widget(), text="Modelo:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.model_combo = ctk.CTkComboBox(parent.get_widget(), values=[])
        self.model_combo.pack(fill="x", pady=(0, 15))

        # Nombre para mostrar
        ctk.CTkLabel(parent.get_widget(), text="Nombre para mostrar:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.display_name_entry = Input(parent.get_widget(), placeholder_text="Nombre que aparecerá en la UI")
        self.display_name_entry.pack(fill="x", pady=(0, 15))

        # API Key
        ctk.CTkLabel(parent.get_widget(), text="API Key:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.api_key_entry = Input(parent.get_widget(), placeholder_text="Tu API key", show="*")
        self.api_key_entry.pack(fill="x", pady=(0, 15))

        # Configuración avanzada en dos columnas
        advanced_frame = Frame(parent.get_widget(), fg_color="transparent")
        advanced_frame.pack(fill="x", pady=(0, 15))

        # Columna izquierda
        left_col = Frame(advanced_frame.get_widget(), fg_color="transparent")
        left_col.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(left_col.get_widget(), text="Temperatura:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.temperature_entry = Input(left_col.get_widget(), placeholder_text="0.7")
        self.temperature_entry.pack(fill="x")

        # Columna derecha
        right_col = Frame(advanced_frame.get_widget(), fg_color="transparent")
        right_col.pack(side="right", fill="x", expand=True)

        ctk.CTkLabel(right_col.get_widget(), text="Max Tokens:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.max_tokens_entry = Input(right_col.get_widget(), placeholder_text="2048")
        self.max_tokens_entry.pack(fill="x")

        # Descripción
        ctk.CTkLabel(parent.get_widget(), text="Descripción:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(15, 5))
        self.description_text = TextArea(
            parent.get_widget(),
            height=80,
            placeholder_text="Descripción del agente..."
        )
        self.description_text.pack(fill="x", pady=(0, 15))

    def create_form_buttons(self, parent):
        """Crea los botones del formulario"""
        buttons_frame = Frame(parent.get_widget(), fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))

        # Botón probar conexión
        test_btn = SecondaryButton(
            buttons_frame.get_widget(),
            text="🔌 Probar Conexión",
            command=self.test_connection,
            height=40
        )
        test_btn.pack(side="left", padx=(0, 10))

        # Botón limpiar
        clear_btn = SecondaryButton(
            buttons_frame.get_widget(),
            text="🧹 Limpiar",
            command=self.clear_form,
            height=40
        )
        clear_btn.pack(side="left", padx=(0, 10))

        # Botón guardar
        save_btn = PrimaryButton(
            buttons_frame.get_widget(),
            text="💾 Guardar Agente",
            command=self.save_agent,
            height=40
        )
        save_btn.pack(side="right")

    def on_provider_change(self, provider):
        """Actualiza los modelos disponibles según el proveedor"""
        models_by_provider = {
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
            "google": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
            "ollama": ["llama3.1", "codestral", "mistral", "phi3", "qwen2.5"],
            "groq": ["llama-3.1-70b-versatile", "mixtral-8x7b-32768", "gemma-7b-it"],
            "together": ["meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", "Qwen/Qwen2.5-72B-Instruct-Turbo"]
        }

        models = models_by_provider.get(provider, [])
        self.model_combo.configure(values=models)
        if models:
            self.model_combo.set(models[0])

    def load_agents_list(self):
        """Carga la lista de agentes desde la base de datos"""
        try:
            self.agents_list = self.agent_model.get_active_agents()
            self.update_agents_display()
        except Exception as e:
            app_logger.log_exception("Error cargando lista de agentes", e)
            messagebox.showerror("Error", f"Error cargando agentes: {str(e)}")

    def update_agents_display(self):
        """Actualiza la visualización de la lista de agentes"""
        self.agents_listbox.delete("1.0", "end")

        if not self.agents_list:
            self.agents_listbox.insert("1.0", "No hay agentes configurados")
            return

        for i, agent in enumerate(self.agents_list):
            status = "🟢" if agent.get('is_default') else "⚪"
            provider_icon = self.get_provider_icon(agent.get('provider', ''))

            line = f"{status} {provider_icon} {agent.get('display_name', agent.get('name', 'Sin nombre'))}\n"
            line += f"   Modelo: {agent.get('model_name', 'N/A')}\n"
            line += f"   Proveedor: {agent.get('provider', 'N/A')}\n\n"

            self.agents_listbox.insert("end", line)

    def get_provider_icon(self, provider):
        """Obtiene el icono del proveedor"""
        icons = {
            "openai": "🤖",
            "anthropic": "🧠",
            "google": "🎯",
            "ollama": "🏠",
            "groq": "⚡",
            "together": "🤝"
        }
        return icons.get(provider, "🔧")

    def new_agent(self):
        """Crea un nuevo agente"""
        self.current_agent_id = None
        self.clear_form()

    def edit_agent(self):
        """Edita el agente seleccionado"""
        if not self.agents_list:
            messagebox.showwarning("Advertencia", "No hay agentes para editar")
            return

        # Implementar selección de agente (simplificado por ahora)
        messagebox.showinfo("Info", "Función de edición en desarrollo")

    def delete_agent(self):
        """Elimina el agente seleccionado"""
        if not self.agents_list:
            messagebox.showwarning("Advertencia", "No hay agentes para eliminar")
            return

        # Implementar eliminación de agente
        messagebox.showinfo("Info", "Función de eliminación en desarrollo")

    def clear_form(self):
        """Limpia el formulario"""
        self.name_entry.delete(0, "end")
        self.display_name_entry.delete(0, "end")
        self.api_key_entry.delete(0, "end")
        self.temperature_entry.delete(0, "end")
        self.max_tokens_entry.delete(0, "end")
        self.description_text.delete("1.0", "end")
        self.provider_combo.set("openai")
        self.on_provider_change("openai")

    def test_connection(self):
        """Prueba la conexión con el agente"""
        if not self.validate_form():
            return

        config = self.get_form_data()

        # Mostrar mensaje de carga
        loading_msg = messagebox.showinfo("Probando", "Probando conexión con el agente...")

        def test_in_thread():
            try:
                result = AgentFactory.test_agent_connection(config['provider'], config)

                if result.get('success'):
                    messagebox.showinfo("Éxito", f"✅ {result.get('message', 'Conexión exitosa')}")
                else:
                    messagebox.showerror("Error", f"❌ {result.get('error', 'Error de conexión')}")

            except Exception as e:
                messagebox.showerror("Error", f"Error probando conexión: {str(e)}")

        threading.Thread(target=test_in_thread, daemon=True).start()

    def save_agent(self):
        """Guarda el agente en la base de datos"""
        if not self.validate_form():
            return

        try:
            config = self.get_form_data()

            if self.current_agent_id:
                # Actualizar agente existente
                success = self.agent_model.update_agent(self.current_agent_id, **config)
                action = "actualizado"
            else:
                # Crear nuevo agente
                agent_id = self.agent_model.create_agent(**config)
                success = agent_id is not None
                action = "creado"

            if success:
                messagebox.showinfo("Éxito", f"Agente {action} exitosamente")
                self.load_agents_list()
                self.clear_form()
            else:
                messagebox.showerror("Error", f"Error {action.replace('o', 'ando')} agente")

        except Exception as e:
            app_logger.log_exception("Error guardando agente", e)
            messagebox.showerror("Error", f"Error guardando agente: {str(e)}")

    def validate_form(self):
        """Valida el formulario"""
        if not self.name_entry.get().strip():
            messagebox.showerror("Error", "El nombre del agente es requerido")
            return False

        if not self.provider_combo.get():
            messagebox.showerror("Error", "Debe seleccionar un proveedor")
            return False

        if not self.model_combo.get():
            messagebox.showerror("Error", "Debe seleccionar un modelo")
            return False

        provider = self.provider_combo.get()
        if provider != "ollama" and not self.api_key_entry.get().strip():
            messagebox.showerror("Error", "API Key es requerida para este proveedor")
            return False

        return True

    def get_form_data(self):
        """Obtiene los datos del formulario"""
        try:
            temperature = float(self.temperature_entry.get() or "0.7")
            max_tokens = int(self.max_tokens_entry.get() or "2048")
        except ValueError:
            temperature = 0.7
            max_tokens = 2048

        return {
            'name': self.name_entry.get().strip(),
            'provider': self.provider_combo.get(),
            'model_name': self.model_combo.get(),
            'display_name': self.display_name_entry.get().strip() or self.name_entry.get().strip(),
            'description': self.description_text.get("1.0", "end").strip(),
            'api_key': self.api_key_entry.get().strip(),
            'temperature': temperature,
            'max_tokens': max_tokens,
            'is_active': True
        }

    def get_widget(self):
        """Retorna el widget principal"""
        return self.main_frame.get_widget()