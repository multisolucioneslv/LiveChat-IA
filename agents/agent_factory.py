# Factory para crear agentes de IA
# Gestiona la creación e instanciación de diferentes tipos de agentes

from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from .openai_agent import OpenAIAgent
from .claude_agent import ClaudeAgent
from .gemini_agent import GeminiAgent
from .ollama_agent import OllamaAgent
from .groq_agent import GroqAgent
from utils.logger import app_logger


class AgentFactory:
    """
    Factory para crear instancias de agentes de IA
    """

    # Registro de agentes disponibles
    AGENT_CLASSES = {
        'openai': OpenAIAgent,
        'anthropic': ClaudeAgent,
        'google': GeminiAgent,
        'ollama': OllamaAgent,
        'groq': GroqAgent
    }

    @classmethod
    def create_agent(cls, provider: str, config: Dict[str, Any], validate_api_key: bool = True) -> Optional[BaseAgent]:
        """
        Crea una instancia de agente según el proveedor

        Args:
            provider: Nombre del proveedor (openai, anthropic, google, ollama)
            config: Configuración del agente
            validate_api_key: Si validar API key o crear agente sin validar

        Returns:
            Instancia del agente o None si hay error
        """
        try:
            agent_class = cls.AGENT_CLASSES.get(provider.lower())

            if not agent_class:
                app_logger.warning(f"Proveedor no soportado: {provider}")
                return None

            # Validar configuración básica
            if not cls._validate_config(provider, config, validate_api_key):
                if validate_api_key:
                    return None
                else:
                    # Crear agente sin validación completa para mostrar en UI
                    app_logger.warning(f"Agente {config.get('name', 'Sin nombre')} creado sin API key válida")

            # Crear instancia del agente
            agent = agent_class(config)

            # Solo validar configuración si se requiere validación de API key
            if validate_api_key and not agent.validate_config():
                app_logger.warning(f"Configuración inválida para agente {provider}")
                return None

            app_logger.info(f"Agente {provider} creado: {config.get('name', 'Sin nombre')}")
            return agent

        except Exception as e:
            app_logger.log_exception(f"Error creando agente {provider}", e)
            return None

    @classmethod
    def _validate_config(cls, provider: str, config: Dict[str, Any], validate_api_key: bool = True) -> bool:
        """
        Valida la configuración básica según el proveedor
        """
        required_fields = ['name', 'model_name']

        # Campos requeridos para cada proveedor
        provider_requirements = {
            'openai': ['api_key'],
            'anthropic': ['api_key'],
            'google': ['api_key'],
            'groq': ['api_key'],
            'ollama': []  # Ollama no requiere API key para localhost
        }

        # Verificar campos básicos
        for field in required_fields:
            if not config.get(field):
                app_logger.warning(f"Campo requerido faltante: {field}")
                return False

        # Solo verificar API key si se requiere validación
        if validate_api_key:
            provider_fields = provider_requirements.get(provider.lower(), [])
            for field in provider_fields:
                if not config.get(field):
                    app_logger.warning(f"Campo requerido para {provider}: {field}")
                    return False

        return True

    @classmethod
    def get_supported_providers(cls) -> list:
        """
        Obtiene la lista de proveedores soportados
        """
        return list(cls.AGENT_CLASSES.keys())

    @classmethod
    def test_agent_connection(cls, provider: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prueba la conexión de un agente sin crear una instancia permanente
        """
        try:
            agent = cls.create_agent(provider, config)

            if not agent:
                return {
                    "success": False,
                    "error": "No se pudo crear el agente",
                    "provider": provider
                }

            return agent.test_connection()

        except Exception as e:
            app_logger.log_exception(f"Error probando conexión {provider}", e)
            return {
                "success": False,
                "error": str(e),
                "provider": provider
            }

    @classmethod
    def register_agent_class(cls, provider: str, agent_class):
        """
        Registra una nueva clase de agente personalizada
        """
        if not issubclass(agent_class, BaseAgent):
            raise ValueError("La clase debe heredar de BaseAgent")

        cls.AGENT_CLASSES[provider.lower()] = agent_class
        app_logger.info(f"Agente personalizado registrado: {provider}")

    @classmethod
    def get_agent_info(cls, provider: str) -> Dict[str, Any]:
        """
        Obtiene información sobre un proveedor específico
        """
        agent_class = cls.AGENT_CLASSES.get(provider.lower())

        if not agent_class:
            return {"error": f"Proveedor {provider} no soportado"}

        return {
            "provider": provider,
            "class_name": agent_class.__name__,
            "module": agent_class.__module__,
            "supported": True
        }


class AgentManager:
    """
    Gestor de instancias de agentes activos
    """

    def __init__(self):
        self.active_agents = {}
        self.default_agent = None

    def add_agent(self, agent_id: str, agent: BaseAgent):
        """
        Agrega un agente al gestor
        """
        self.active_agents[agent_id] = agent
        app_logger.info(f"Agente {agent_id} agregado al gestor")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Obtiene un agente por su ID
        """
        return self.active_agents.get(agent_id)

    def remove_agent(self, agent_id: str):
        """
        Remueve un agente del gestor
        """
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]
            app_logger.info(f"Agente {agent_id} removido del gestor")

    def set_default_agent(self, agent_id: str):
        """
        Establece un agente como predeterminado
        """
        if agent_id in self.active_agents:
            self.default_agent = agent_id
            app_logger.info(f"Agente {agent_id} establecido como predeterminado")

    def get_default_agent(self) -> Optional[BaseAgent]:
        """
        Obtiene el agente predeterminado
        """
        if self.default_agent and self.default_agent in self.active_agents:
            return self.active_agents[self.default_agent]
        return None

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Lista todos los agentes activos
        """
        return {
            agent_id: agent.get_info()
            for agent_id, agent in self.active_agents.items()
        }

    def clear_agents(self):
        """
        Limpia todos los agentes activos
        """
        self.active_agents.clear()
        self.default_agent = None
        app_logger.info("Todos los agentes fueron removidos del gestor")