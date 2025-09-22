# Componente de interfaz de chat
# Proporciona la interfaz para comunicarse con los agentes

import customtkinter as ctk
from tkinter import scrolledtext
import threading
import time
from datetime import datetime
from .frame import Frame, CardFrame
from .label import TitleLabel
from .input import Input, TextArea
from .button import PrimaryButton
from utils.logger import app_logger
from utils.report_generator import ReportGenerator
from models.history_model import HistoryModel
from models.agent_model import AgentModel
from agents import AgentFactory
from agents.specialized.token_tracker_agent import TokenTrackerAgent


class ChatInterface:
    """
    Componente de interfaz de chat
    Permite la comunicación con agentes de IA
    """

    def __init__(self, parent, agent_handler=None, user_id=None, session_id=None):
        self.parent = parent
        self.agent_handler = agent_handler
        self.chat_history = []
        self.user_id = user_id
        self.session_id = session_id
        self.current_agent = None

        # Configuración de colores
        self.primary_color = "#2E86AB"
        self.secondary_color = "#F5F5F5"
        self.user_color = "#A23B72"
        self.agent_color = "#F18F01"

        # Instancias para logging y reportes
        self.report_generator = ReportGenerator()
        self.history_model = HistoryModel()
        self.agent_model = AgentModel()
        self.token_tracker = TokenTrackerAgent()

        self.create_chat_interface()

    def create_chat_interface(self):
        """Crea la interfaz completa del chat"""
        # Frame principal del chat usando componente (sin padding para usar todo el espacio)
        self.chat_frame = CardFrame(self.parent)
        self.chat_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Selector de agentes
        self.create_agent_selector()

        # Área de mensajes (ocupa todo el espacio disponible)
        self.create_messages_area()

        # Área de entrada de texto
        self.create_input_area()

        # Cargar agentes y mensaje de bienvenida
        self.load_agents()
        self.add_agent_message("¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?")

    def create_agent_selector(self):
        """Crea el selector de agentes"""
        # Frame para selector
        selector_frame = Frame(
            self.chat_frame.get_widget(),
            fg_color="transparent"
        )
        selector_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Label del selector
        ctk.CTkLabel(
            selector_frame.get_widget(),
            text="🤖 Agente:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.primary_color
        ).pack(side="left", padx=(0, 10))

        # ComboBox de agentes
        self.agent_selector = ctk.CTkComboBox(
            selector_frame.get_widget(),
            values=["Cargando agentes..."],
            command=self.on_agent_change,
            width=250,
            font=ctk.CTkFont(size=11),
            dropdown_font=ctk.CTkFont(size=11)
        )
        self.agent_selector.pack(side="left", padx=(0, 10))

        # Estado del agente
        self.agent_status_label = ctk.CTkLabel(
            selector_frame.get_widget(),
            text="⚪ No configurado",
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        )
        self.agent_status_label.pack(side="left")

    def create_messages_area(self):
        """Crea el área donde se muestran los mensajes"""
        # Frame contenedor usando componente
        self.messages_frame = Frame(
            self.chat_frame.get_widget(),
            fg_color=self.secondary_color
        )
        self.messages_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Área de texto usando componente
        self.messages_text = TextArea(
            self.messages_frame.get_widget(),
            font=ctk.CTkFont(size=12),
            fg_color="white",
            text_color="#333333",
            corner_radius=5,
            scrollbar_button_color=self.primary_color,
            scrollbar_button_hover_color=self.user_color
        )
        self.messages_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Configurar tags para diferentes tipos de mensajes
        self.messages_text.get_widget()._textbox.tag_configure(
            "user_message",
            foreground=self.user_color,
            font=("Arial", 11, "bold")
        )
        self.messages_text.get_widget()._textbox.tag_configure(
            "agent_message",
            foreground=self.agent_color,
            font=("Arial", 11, "bold")
        )
        self.messages_text.get_widget()._textbox.tag_configure(
            "timestamp",
            foreground="#666666",
            font=("Arial", 9)
        )

    def create_input_area(self):
        """Crea el área de entrada de texto y botón de envío"""
        # Frame para entrada usando componente
        self.input_frame = Frame(
            self.chat_frame.get_widget(),
            fg_color="transparent"
        )
        self.input_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Campo de texto usando componente
        self.message_entry = Input(
            self.input_frame.get_widget(),
            placeholder_text="Escribe tu mensaje aquí...",
            height=40
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Bind para enviar con Enter
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        # Botón de envío usando componente
        self.send_button = PrimaryButton(
            self.input_frame.get_widget(),
            text="Enviar 📤",
            command=self.send_message,
            width=100,
            height=40
        )
        self.send_button.pack(side="right")

    def send_message(self):
        """Envía un mensaje al agente"""
        message = self.message_entry.get().strip()
        if not message:
            return

        # Limpiar campo de entrada
        self.message_entry.delete(0, "end")

        # Agregar mensaje del usuario
        self.add_user_message(message)

        # Procesar mensaje en hilo separado para no bloquear la UI
        threading.Thread(
            target=self.process_message,
            args=(message,),
            daemon=True
        ).start()

    def process_message(self, message):
        """Procesa el mensaje y obtiene respuesta del agente"""
        start_time = time.time()

        try:
            # Log del mensaje del usuario
            app_logger.info(f"Mensaje recibido: {message[:100]}..." if len(message) > 100 else message)

            if self.current_agent and self.current_agent.provider == 'ollama':
                # Ollama no requiere API key
                response = self.current_agent.get_response(message)
            elif self.current_agent and hasattr(self.current_agent, 'api_key') and self.current_agent.api_key:
                response = self.current_agent.get_response(message)
            elif self.agent_handler:
                response = self.agent_handler.get_response(message)
            else:
                # Mensaje indicando que necesita configurar API key
                if self.current_agent:
                    provider = self.current_agent.config.get('provider', 'desconocido')
                    response = f"⚠️ Para usar este agente de {provider.upper()}, necesitas configurar tu API Key en la sección 'Configuraciones'."
                else:
                    response = f"⚠️ No hay agente configurado. Ve a 'Configuraciones' para configurar un agente IA."

            # Calcular tiempo de respuesta
            response_time_ms = int((time.time() - start_time) * 1000)

            # Log de la interacción completa
            app_logger.log_chat_interaction(
                self.user_id,
                self.session_id,
                message,
                response,
                response_time_ms
            )

            # Registrar uso de tokens si el agente lo proporciona
            self.track_token_usage(message, response)

            # Guardar en base de datos
            self.save_interaction_to_db(message, response, response_time_ms)

            # Generar reporte de la interacción
            self.generate_interaction_report(message, response, response_time_ms)

            # Agregar respuesta del agente en el hilo principal
            self.parent.after(0, lambda: self.add_agent_message(response))

        except Exception as e:
            error_msg = f"Error: No se pudo procesar el mensaje. {str(e)}"

            # Log del error
            app_logger.log_exception("Error procesando mensaje", e)

            # Generar reporte de error
            self.generate_error_report(message, e)

            self.parent.after(0, lambda: self.add_agent_message(error_msg))

    def add_user_message(self, message):
        """Agrega un mensaje del usuario al chat"""
        timestamp = datetime.now().strftime("%H:%M")

        self.messages_text.insert("end", f"[{timestamp}] ", "timestamp")
        self.messages_text.insert("end", "Tú: ", "user_message")
        self.messages_text.insert("end", f"{message}\n\n")

        self.messages_text.see("end")
        self.chat_history.append({"type": "user", "message": message, "timestamp": timestamp})

    def add_agent_message(self, message):
        """Agrega un mensaje del agente al chat"""
        timestamp = datetime.now().strftime("%H:%M")

        self.messages_text.insert("end", f"[{timestamp}] ", "timestamp")
        self.messages_text.insert("end", "Agente: ", "agent_message")
        self.messages_text.insert("end", f"{message}\n\n")

        self.messages_text.see("end")
        self.chat_history.append({"type": "agent", "message": message, "timestamp": timestamp})

    def clear_chat(self):
        """Limpia el historial del chat"""
        self.messages_text.delete("1.0", "end")
        self.chat_history.clear()
        self.add_agent_message("Chat limpiado. ¿En qué puedo ayudarte?")

    def get_widget(self):
        """Retorna el widget principal del chat"""
        return self.chat_frame.get_widget()

    def save_interaction_to_db(self, user_message, agent_response, response_time_ms):
        """Guarda la interacción en la base de datos"""
        try:
            metadata = {
                'agent_name': getattr(self.agent_handler, 'name', 'Agente de Pruebas'),
                'timestamp': datetime.now().isoformat(),
                'message_length': len(user_message),
                'response_length': len(agent_response)
            }

            self.history_model.create_interaction(
                user_id=self.user_id,
                session_id=self.session_id,
                interaction_type='chat',
                user_message=user_message,
                agent_response=agent_response,
                response_time_ms=response_time_ms,
                tokens_used=None,  # Se puede agregar si el agente proporciona esta info
                metadata=metadata
            )

        except Exception as e:
            app_logger.log_exception("Error guardando interacción en BD", e)

    def generate_interaction_report(self, user_message, agent_response, response_time_ms):
        """Genera un reporte de la interacción"""
        try:
            metadata = {
                'username': f"Usuario_{self.user_id}" if self.user_id else "Anónimo",
                'session_id': self.session_id,
                'agent_name': getattr(self.agent_handler, 'name', 'Agente de Pruebas'),
                'timestamp': datetime.now().isoformat()
            }

            report_path = self.report_generator.create_chat_interaction_report(
                user_message=user_message,
                agent_response=agent_response,
                response_time_ms=response_time_ms,
                tokens_used=None,
                metadata=metadata
            )

            app_logger.log_report_generation("chat_interaction", report_path, True)

        except Exception as e:
            app_logger.log_exception("Error generando reporte de interacción", e)

    def generate_error_report(self, user_message, error):
        """Genera un reporte de error"""
        try:
            context = {
                'user_message': user_message,
                'user_id': self.user_id,
                'session_id': self.session_id,
                'agent_name': getattr(self.agent_handler, 'name', 'Agente de Pruebas'),
                'timestamp': datetime.now().isoformat()
            }

            report_path = self.report_generator.create_error_report(
                error_type="ChatProcessingError",
                error_message=str(error),
                stack_trace=None,
                context=context
            )

            app_logger.log_report_generation("error", report_path, True)

        except Exception as e:
            app_logger.log_exception("Error generando reporte de error", e)

    def set_user_session(self, user_id, session_id):
        """Establece el usuario y sesión para logging"""
        self.user_id = user_id
        self.session_id = session_id
        app_logger.info(f"Chat configurado para usuario {user_id}, sesión {session_id}")

    def set_agent_handler(self, agent_handler):
        """Establece el manejador de agentes"""
        self.agent_handler = agent_handler
        agent_name = getattr(agent_handler, 'name', 'Agente Desconocido')
        app_logger.info(f"Agente configurado: {agent_name}")

    def load_agents(self):
        """Carga los agentes disponibles desde la base de datos"""
        try:
            agents = self.agent_model.get_active_agents()

            if not agents:
                self.agent_selector.configure(values=["No hay agentes configurados"])
                self.agent_selector.set("No hay agentes configurados")
                return

            # Preparar lista para el combobox
            agent_options = []
            for agent in agents:
                provider_icon = self.get_provider_icon(agent.get('provider', ''))
                display_text = f"{provider_icon} {agent.get('display_name', agent.get('name', 'Sin nombre'))}"
                agent_options.append(display_text)

            self.agent_selector.configure(values=agent_options)

            # Seleccionar agente por defecto
            default_agent = next((agent for agent in agents if agent.get('is_default')), agents[0])
            if default_agent:
                provider_icon = self.get_provider_icon(default_agent.get('provider', ''))
                default_text = f"{provider_icon} {default_agent.get('display_name', default_agent.get('name', 'Sin nombre'))}"
                self.agent_selector.set(default_text)
                self.load_agent_by_id(default_agent['id'])

        except Exception as e:
            app_logger.log_exception("Error cargando agentes", e)
            self.agent_selector.configure(values=["Error cargando agentes"])
            self.agent_selector.set("Error cargando agentes")

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

    def on_agent_change(self, selection):
        """Maneja el cambio de agente seleccionado"""
        try:
            # Extraer nombre del agente de la selección
            if "🤖" in selection or "🧠" in selection or "🎯" in selection or "🏠" in selection or "⚡" in selection or "🤝" in selection or "🔧" in selection:
                agent_name = selection.split(" ", 1)[1] if " " in selection else selection

                # Buscar agente por display_name o name
                agents = self.agent_model.get_active_agents()
                selected_agent = None

                for agent in agents:
                    if (agent.get('display_name') == agent_name or
                        agent.get('name') == agent_name):
                        selected_agent = agent
                        break

                if selected_agent:
                    self.load_agent_by_id(selected_agent['id'])
                else:
                    self.agent_status_label.configure(text="❌ Agente no encontrado")

        except Exception as e:
            app_logger.log_exception("Error cambiando agente", e)
            self.agent_status_label.configure(text="❌ Error")

    def load_agent_by_id(self, agent_id):
        """Carga un agente específico por su ID"""
        try:
            agent_data = self.agent_model.get_agent_by_id(agent_id)

            if not agent_data:
                self.agent_status_label.configure(text="❌ Agente no encontrado")
                return

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

            # Crear instancia del agente (sin validar API key durante carga inicial)
            self.current_agent = AgentFactory.create_agent(
                agent_data.get('provider'),
                config,
                validate_api_key=False
            )

            if self.current_agent:
                # Verificar si tiene API key configurada o es Ollama (local)
                is_ollama = agent_data.get('provider') == 'ollama'
                has_api_key = bool(agent_data.get('api_key')) or is_ollama

                if is_ollama:
                    default_indicator = "🟢" if agent_data.get('is_default') else "🏠"
                    status_text = f"{default_indicator} {agent_data.get('model_name')} - Local"
                elif has_api_key:
                    default_indicator = "🟢" if agent_data.get('is_default') else "🔵"
                    status_text = f"{default_indicator} {agent_data.get('model_name')} - Listo"
                else:
                    status_text = f"⚠️ {agent_data.get('model_name')} - Sin API Key"

                self.agent_status_label.configure(text=status_text)

                # Mensaje de cambio de agente
                provider_icon = self.get_provider_icon(agent_data.get('provider'))
                agent_name = agent_data.get('display_name', agent_data.get('name'))

                if is_ollama:
                    self.add_system_message(f"Agente cambiado a: {provider_icon} {agent_name} (Local - Sin costo)")
                elif has_api_key:
                    self.add_system_message(f"Agente cambiado a: {provider_icon} {agent_name}")
                else:
                    self.add_system_message(f"Agente seleccionado: {provider_icon} {agent_name} (⚠️ Configurar API Key en Configuraciones)")

                app_logger.info(f"Agente cargado: {agent_name} ({agent_data.get('provider')})")
            else:
                self.agent_status_label.configure(text="❌ Error al cargar agente")

        except Exception as e:
            error_msg = f"Error cargando agente {agent_id}: {str(e)}"
            app_logger.log_exception("Error cargando agente por ID", e)
            self.agent_status_label.configure(text="❌ Error al cargar agente")

            # Mostrar error más específico en un mensaje del sistema
            self.add_system_message(f"❌ Error cargando agente: {str(e)[:100]}")

    def add_system_message(self, message):
        """Agrega un mensaje del sistema al chat"""
        timestamp = datetime.now().strftime("%H:%M")

        self.messages_text.insert("end", f"[{timestamp}] ", "timestamp")
        self.messages_text.insert("end", "Sistema: ", "system_message")
        self.messages_text.insert("end", f"{message}\n\n")

        # Configurar tag para mensajes del sistema si no existe
        try:
            self.messages_text.get_widget()._textbox.tag_configure(
                "system_message",
                foreground="#6C757D",
                font=("Arial", 10, "italic")
            )
        except:
            pass

        self.messages_text.see("end")
        self.chat_history.append({"type": "system", "message": message, "timestamp": timestamp})

    def track_token_usage(self, user_message: str, agent_response: str):
        """Registra el uso de tokens en el token tracker"""
        try:
            if not self.current_agent:
                return

            # Obtener información del agente actual
            provider = getattr(self.current_agent, 'provider', 'unknown')
            model = getattr(self.current_agent, 'model_name', 'unknown')

            # Estimar tokens (aproximación simple)
            # 1 token ≈ 4 caracteres para modelos estándar
            input_tokens = len(user_message) // 4
            output_tokens = len(agent_response) // 4

            # Si el agente tiene método para obtener uso real de tokens, usarlo
            if hasattr(self.current_agent, 'get_last_token_usage'):
                try:
                    usage = self.current_agent.get_last_token_usage()
                    if usage:
                        input_tokens = usage.get('input_tokens', input_tokens)
                        output_tokens = usage.get('output_tokens', output_tokens)
                except:
                    pass  # Usar estimación si falla

            # Registrar en el token tracker
            self.token_tracker.record_usage(
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                session_id=self.session_id
            )

            app_logger.info(f"Token usage tracked: {provider}:{model} - {input_tokens + output_tokens} tokens")

        except Exception as e:
            app_logger.error(f"Error tracking token usage: {e}")