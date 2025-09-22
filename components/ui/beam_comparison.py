# Beam Comparison Component
# Componente para comparar respuestas de múltiples modelos lado a lado
# Inspirado en NextChat Beam y Big-AGI

import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from agents import AgentFactory
from models.agent_model import AgentModel
from agents.specialized.token_tracker_agent import TokenTrackerAgent
from utils.logger import app_logger

class BeamComparison(ctk.CTkFrame):
    """
    Componente de comparación multi-modelo "Beam"
    Permite enviar el mismo prompt a múltiples modelos y comparar respuestas
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.agent_model = AgentModel()
        self.token_tracker = TokenTrackerAgent()
        self.active_agents = {}
        self.current_responses = {}
        self.comparison_history = []

        # Configuración de colores (tema moderno)
        self.colors = {
            "primary": "#1976d2",
            "secondary": "#388e3c",
            "warning": "#f57c00",
            "error": "#d32f2f",
            "surface": "#ffffff",
            "background": "#f5f5f5",
            "text": "#212121",
            "border": "#e0e0e0"
        }

        self.setup_ui()
        self.load_available_agents()

    def setup_ui(self):
        """Configurar interfaz del componente Beam"""
        # Frame principal con padding
        self.main_frame = ctk.CTkFrame(self, corner_radius=12)
        self.main_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # Título del componente
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="⚡ Beam - Comparación Multi-Modelo",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(16, 8))

        # Descripción
        self.desc_label = ctk.CTkLabel(
            self.main_frame,
            text="Envía el mismo prompt a múltiples modelos y compara sus respuestas lado a lado",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.desc_label.pack(pady=(0, 16))

        # Frame para selección de modelos
        self.setup_model_selection()

        # Frame para entrada de prompt
        self.setup_prompt_input()

        # Frame para comparación de respuestas
        self.setup_response_comparison()

        # Frame para controles y estadísticas
        self.setup_controls()

    def setup_model_selection(self):
        """Configurar selección de modelos"""
        selection_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        selection_frame.pack(fill="x", padx=16, pady=8)

        # Título
        selection_title = ctk.CTkLabel(
            selection_frame,
            text="🎯 Seleccionar Modelos para Comparar",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        selection_title.pack(pady=(12, 8))

        # Frame scrollable para checkboxes de modelos
        self.models_scroll = ctk.CTkScrollableFrame(selection_frame, height=120)
        self.models_scroll.pack(fill="x", padx=16, pady=(0, 16))

        # Diccionario para mantener checkboxes
        self.model_checkboxes = {}

    def setup_prompt_input(self):
        """Configurar entrada de prompt"""
        input_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        input_frame.pack(fill="x", padx=16, pady=8)

        # Título
        input_title = ctk.CTkLabel(
            input_frame,
            text="💬 Prompt para Comparar",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        input_title.pack(pady=(12, 8))

        # Frame para input y botón
        input_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_container.pack(fill="x", padx=16, pady=(0, 16))

        # TextBox para el prompt
        self.prompt_textbox = ctk.CTkTextbox(
            input_container,
            height=100,
            font=ctk.CTkFont(size=14),
            wrap="word"
        )
        self.prompt_textbox.pack(fill="x", pady=(0, 8))

        # Frame para botones
        buttons_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        buttons_frame.pack(fill="x")

        # Botón de enviar
        self.send_button = ctk.CTkButton(
            buttons_frame,
            text="🚀 Enviar a Modelos Seleccionados",
            command=self.send_beam_request,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=8
        )
        self.send_button.pack(side="left", padx=(0, 8))

        # Botón de limpiar
        self.clear_button = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Limpiar",
            command=self.clear_responses,
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8,
            fg_color="gray"
        )
        self.clear_button.pack(side="left", padx=8)

        # Label de estado
        self.status_label = ctk.CTkLabel(
            buttons_frame,
            text="Listo para comparar",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="right", padx=8)

    def setup_response_comparison(self):
        """Configurar área de comparación de respuestas"""
        comparison_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        comparison_frame.pack(fill="both", expand=True, padx=16, pady=8)

        # Título
        comparison_title = ctk.CTkLabel(
            comparison_frame,
            text="📊 Comparación de Respuestas",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        comparison_title.pack(pady=(12, 8))

        # Frame scrollable para las respuestas
        self.responses_scroll = ctk.CTkScrollableFrame(comparison_frame)
        self.responses_scroll.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Diccionario para mantener frames de respuestas
        self.response_frames = {}

    def setup_controls(self):
        """Configurar controles y estadísticas"""
        controls_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        controls_frame.pack(fill="x", padx=16, pady=8)

        # Frame para controles
        controls_container = ctk.CTkFrame(controls_frame, fg_color="transparent")
        controls_container.pack(fill="x", padx=16, pady=12)

        # Botón de exportar comparación
        self.export_button = ctk.CTkButton(
            controls_container,
            text="📄 Exportar Comparación",
            command=self.export_comparison,
            width=180
        )
        self.export_button.pack(side="left", padx=(0, 8))

        # Selector de modo de vista
        view_label = ctk.CTkLabel(controls_container, text="Vista:")
        view_label.pack(side="left", padx=(16, 8))

        self.view_mode = ctk.CTkOptionMenu(
            controls_container,
            values=["Columnas", "Pestañas", "Lista"],
            command=self.change_view_mode
        )
        self.view_mode.pack(side="left", padx=8)

        # Estadísticas básicas
        self.stats_label = ctk.CTkLabel(
            controls_container,
            text="Estadísticas: 0 modelos, 0 tokens",
            font=ctk.CTkFont(size=12)
        )
        self.stats_label.pack(side="right", padx=8)

    def load_available_agents(self):
        """Cargar agentes disponibles para selección"""
        try:
            agents = self.agent_model.get_active_agents()

            # Limpiar checkboxes existentes
            for widget in self.models_scroll.winfo_children():
                widget.destroy()
            self.model_checkboxes.clear()

            # Crear checkbox para cada agente
            for agent in agents:
                self.create_agent_checkbox(agent)

        except Exception as e:
            app_logger.error(f"Error cargando agentes: {e}")

    def create_agent_checkbox(self, agent_data: Dict[str, Any]):
        """Crear checkbox para un agente"""
        # Frame para el checkbox
        checkbox_frame = ctk.CTkFrame(self.models_scroll, fg_color="transparent")
        checkbox_frame.pack(fill="x", pady=2)

        # Variable para el checkbox
        var = tk.BooleanVar()

        # Crear checkbox
        checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="",
            variable=var,
            command=lambda: self.on_model_selection_changed()
        )
        checkbox.pack(side="left", padx=(8, 12))

        # Label con información del agente
        provider_icons = {
            "openai": "🤖",
            "anthropic": "🧠",
            "google": "🎯",
            "ollama": "🏠",
            "groq": "⚡",
            "together": "🤝"
        }

        provider = agent_data.get('provider', 'unknown')
        icon = provider_icons.get(provider, "🔧")
        name = agent_data.get('display_name', agent_data.get('name', 'Unnamed'))
        model = agent_data.get('model_name', 'Unknown')

        # Verificar si tiene API key o es local
        has_api_key = bool(agent_data.get('api_key')) or provider == 'ollama'
        status_indicator = "🟢" if has_api_key else "⚠️"

        label_text = f"{icon} {name} ({model}) {status_indicator}"

        label = ctk.CTkLabel(
            checkbox_frame,
            text=label_text,
            font=ctk.CTkFont(size=12)
        )
        label.pack(side="left", fill="x", expand=True)

        # Guardar referencia
        self.model_checkboxes[agent_data['id']] = {
            'checkbox': checkbox,
            'variable': var,
            'agent_data': agent_data,
            'frame': checkbox_frame
        }

    def on_model_selection_changed(self):
        """Manejar cambio en selección de modelos"""
        selected_count = sum(1 for cb in self.model_checkboxes.values() if cb['variable'].get())

        if selected_count == 0:
            self.send_button.configure(state="disabled")
            self.status_label.configure(text="Selecciona al menos un modelo")
        else:
            self.send_button.configure(state="normal")
            self.status_label.configure(text=f"{selected_count} modelo(s) seleccionado(s)")

    def send_beam_request(self):
        """Enviar prompt a todos los modelos seleccionados"""
        prompt = self.prompt_textbox.get("1.0", "end-1c").strip()

        if not prompt:
            self.status_label.configure(text="⚠️ Ingresa un prompt")
            return

        # Obtener modelos seleccionados
        selected_models = []
        for agent_id, cb_data in self.model_checkboxes.items():
            if cb_data['variable'].get():
                selected_models.append((agent_id, cb_data['agent_data']))

        if not selected_models:
            self.status_label.configure(text="⚠️ Selecciona al menos un modelo")
            return

        # Deshabilitar botón durante procesamiento
        self.send_button.configure(state="disabled")
        self.status_label.configure(text="🚀 Enviando a modelos...")

        # Limpiar respuestas anteriores
        self.clear_responses()

        # Crear frames para cada modelo
        for agent_id, agent_data in selected_models:
            self.create_response_frame(agent_id, agent_data)

        # Enviar requests en paralelo
        threading.Thread(
            target=self.process_beam_requests,
            args=(prompt, selected_models),
            daemon=True
        ).start()

    def process_beam_requests(self, prompt: str, selected_models: List):
        """Procesar requests a múltiples modelos en paralelo"""
        threads = []

        for agent_id, agent_data in selected_models:
            thread = threading.Thread(
                target=self.process_single_request,
                args=(agent_id, agent_data, prompt),
                daemon=True
            )
            threads.append(thread)
            thread.start()

        # Esperar a que terminen todos los threads
        for thread in threads:
            thread.join()

        # Actualizar UI en el hilo principal
        self.after(0, self.on_all_responses_complete)

    def process_single_request(self, agent_id: str, agent_data: Dict[str, Any], prompt: str):
        """Procesar request a un solo modelo"""
        start_time = time.time()

        try:
            # Actualizar estado
            self.after(0, lambda: self.update_response_status(agent_id, "🔄 Procesando..."))

            # Crear configuración para AgentFactory
            config = {
                'name': agent_data.get('name'),
                'provider': agent_data.get('provider'),
                'model_name': agent_data.get('model_name'),
                'api_key': agent_data.get('api_key'),
                'api_url': agent_data.get('api_url'),
                'max_tokens': agent_data.get('max_tokens', 2048),
                'temperature': agent_data.get('temperature', 0.7),
                'default_params': agent_data.get('default_params', {})
            }

            # Crear instancia del agente
            agent = AgentFactory.create_agent(
                agent_data.get('provider'),
                config,
                validate_api_key=False
            )

            if not agent:
                raise Exception("No se pudo crear el agente")

            # Verificar que tenga API key (excepto Ollama)
            if agent_data.get('provider') != 'ollama' and not agent_data.get('api_key'):
                raise Exception("API Key no configurada")

            # Obtener respuesta
            response = agent.get_response(prompt)

            # Calcular tiempo
            response_time = time.time() - start_time

            # Estimar tokens
            input_tokens = len(prompt) // 4
            output_tokens = len(response) // 4

            # Registrar uso de tokens
            self.token_tracker.record_usage(
                provider=agent_data.get('provider'),
                model=agent_data.get('model_name'),
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )

            # Guardar respuesta
            self.current_responses[agent_id] = {
                'response': response,
                'response_time': response_time,
                'tokens': input_tokens + output_tokens,
                'success': True,
                'error': None
            }

            # Actualizar UI
            self.after(0, lambda: self.update_response_content(agent_id, response, response_time, input_tokens + output_tokens))

        except Exception as e:
            error_msg = str(e)
            self.current_responses[agent_id] = {
                'response': None,
                'response_time': time.time() - start_time,
                'tokens': 0,
                'success': False,
                'error': error_msg
            }

            # Actualizar UI con error
            self.after(0, lambda: self.update_response_error(agent_id, error_msg))

    def create_response_frame(self, agent_id: str, agent_data: Dict[str, Any]):
        """Crear frame para respuesta de un modelo"""
        # Frame principal para esta respuesta
        response_frame = ctk.CTkFrame(self.responses_scroll, corner_radius=8)
        response_frame.pack(fill="x", pady=8, padx=8)

        # Header con información del modelo
        header_frame = ctk.CTkFrame(response_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(12, 8))

        # Icono y nombre del modelo
        provider_icons = {
            "openai": "🤖",
            "anthropic": "🧠",
            "google": "🎯",
            "ollama": "🏠",
            "groq": "⚡",
            "together": "🤝"
        }

        provider = agent_data.get('provider', 'unknown')
        icon = provider_icons.get(provider, "🔧")
        name = agent_data.get('display_name', agent_data.get('name', 'Unnamed'))

        model_label = ctk.CTkLabel(
            header_frame,
            text=f"{icon} {name}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        model_label.pack(side="left")

        # Status label
        status_label = ctk.CTkLabel(
            header_frame,
            text="⏳ Esperando...",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        status_label.pack(side="right")

        # TextBox para la respuesta
        response_textbox = ctk.CTkTextbox(
            response_frame,
            height=200,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        response_textbox.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Guardar referencias
        self.response_frames[agent_id] = {
            'frame': response_frame,
            'status_label': status_label,
            'textbox': response_textbox,
            'agent_data': agent_data
        }

    def update_response_status(self, agent_id: str, status: str):
        """Actualizar estado de una respuesta"""
        if agent_id in self.response_frames:
            self.response_frames[agent_id]['status_label'].configure(text=status)

    def update_response_content(self, agent_id: str, response: str, response_time: float, tokens: int):
        """Actualizar contenido de una respuesta"""
        if agent_id in self.response_frames:
            frame_data = self.response_frames[agent_id]

            # Actualizar textbox
            frame_data['textbox'].delete("1.0", "end")
            frame_data['textbox'].insert("1.0", response)

            # Actualizar status
            status_text = f"✅ {response_time:.1f}s • {tokens:,} tokens"
            frame_data['status_label'].configure(text=status_text, text_color="green")

    def update_response_error(self, agent_id: str, error: str):
        """Actualizar con error una respuesta"""
        if agent_id in self.response_frames:
            frame_data = self.response_frames[agent_id]

            # Mostrar error en textbox
            error_text = f"❌ Error: {error}"
            frame_data['textbox'].delete("1.0", "end")
            frame_data['textbox'].insert("1.0", error_text)

            # Actualizar status
            frame_data['status_label'].configure(text="❌ Error", text_color="red")

    def on_all_responses_complete(self):
        """Manejar cuando todas las respuestas están completas"""
        # Rehabilitar botón
        self.send_button.configure(state="normal")

        # Calcular estadísticas
        total_tokens = sum(r.get('tokens', 0) for r in self.current_responses.values())
        successful_count = sum(1 for r in self.current_responses.values() if r.get('success', False))
        total_count = len(self.current_responses)

        # Actualizar status
        self.status_label.configure(text=f"✅ Completado: {successful_count}/{total_count} modelos")

        # Actualizar estadísticas
        self.stats_label.configure(text=f"Estadísticas: {total_count} modelos, {total_tokens:,} tokens")

        app_logger.info(f"Beam comparison completed: {successful_count}/{total_count} successful, {total_tokens} tokens")

    def clear_responses(self):
        """Limpiar todas las respuestas"""
        # Limpiar frames de respuestas
        for widget in self.responses_scroll.winfo_children():
            widget.destroy()

        # Limpiar datos
        self.response_frames.clear()
        self.current_responses.clear()

        # Resetear estadísticas
        self.stats_label.configure(text="Estadísticas: 0 modelos, 0 tokens")

    def change_view_mode(self, mode: str):
        """Cambiar modo de vista"""
        # TODO: Implementar diferentes modos de vista
        app_logger.info(f"View mode changed to: {mode}")

    def export_comparison(self):
        """Exportar comparación actual"""
        try:
            if not self.current_responses:
                self.status_label.configure(text="⚠️ No hay respuestas para exportar")
                return

            # Generar reporte
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reportes/beam_comparison_{timestamp}.md"

            import os
            os.makedirs("reportes", exist_ok=True)

            prompt = self.prompt_textbox.get("1.0", "end-1c").strip()

            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Comparación Multi-Modelo (Beam)\n\n")
                f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Prompt:** {prompt}\n\n")
                f.write("---\n\n")

                for agent_id, response_data in self.current_responses.items():
                    if agent_id in self.response_frames:
                        agent_data = self.response_frames[agent_id]['agent_data']
                        name = agent_data.get('display_name', agent_data.get('name', 'Unnamed'))
                        provider = agent_data.get('provider', 'unknown')
                        model = agent_data.get('model_name', 'unknown')

                        f.write(f"## {name} ({provider}:{model})\n\n")

                        if response_data.get('success'):
                            f.write(f"**Tiempo:** {response_data['response_time']:.1f}s\n")
                            f.write(f"**Tokens:** {response_data['tokens']:,}\n\n")
                            f.write(f"**Respuesta:**\n```\n{response_data['response']}\n```\n\n")
                        else:
                            f.write(f"**Error:** {response_data.get('error', 'Unknown error')}\n\n")

                        f.write("---\n\n")

            app_logger.info(f"Beam comparison exported: {filename}")
            self.status_label.configure(text=f"✅ Exportado: {filename}")

        except Exception as e:
            app_logger.error(f"Error exportando comparación: {e}")
            self.status_label.configure(text="❌ Error exportando")