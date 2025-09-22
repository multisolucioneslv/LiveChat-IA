# Clase base para agentes de IA
# Define la interfaz común para todos los agentes

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from utils.logger import app_logger


class BaseAgent(ABC):
    """
    Clase abstracta base para todos los agentes de IA
    Define la interfaz común que deben implementar todos los agentes
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'Agente Desconocido')
        self.provider = config.get('provider', '')
        self.model_name = config.get('model_name', '')
        self.api_key = config.get('api_key', '')
        self.api_url = config.get('api_url', '')
        self.max_tokens = config.get('max_tokens', 2048)
        self.temperature = config.get('temperature', 0.7)
        self.default_params = config.get('default_params', {})


    @abstractmethod
    def get_response(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """
        Obtiene una respuesta del agente
        Args:
            message: Mensaje del usuario
            context: Contexto de la conversación (opcional)
        Returns:
            Respuesta del agente
        """
        pass

    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con el servicio del agente
        Returns:
            Diccionario con el resultado de la prueba
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Obtiene la lista de modelos disponibles
        Returns:
            Lista de nombres de modelos
        """
        pass

    def validate_config(self) -> bool:
        """
        Valida la configuración del agente
        Returns:
            True si la configuración es válida
        """
        required_fields = ['name', 'provider', 'model_name']

        for field in required_fields:
            if not self.config.get(field):
                app_logger.error(f"Campo requerido faltante: {field}")
                return False

        if not self.api_key and self.provider != 'ollama':
            app_logger.error("API key requerida para este proveedor")
            return False

        return True

    def log_interaction(self, message: str, response: str, response_time_ms: int):
        """
        Registra una interacción con el agente
        """
        app_logger.info(f"Agente {self.name} - Tiempo: {response_time_ms}ms")
        app_logger.log_chat_interaction(
            user_id=None,
            session_id=None,
            message=message,
            response=response,
            response_time_ms=response_time_ms,
            agent_name=self.name
        )

    def get_info(self) -> Dict[str, Any]:
        """
        Obtiene información del agente
        Returns:
            Diccionario con información del agente
        """
        return {
            'name': self.name,
            'provider': self.provider,
            'model_name': self.model_name,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'status': 'configured' if self.validate_config() else 'error'
        }