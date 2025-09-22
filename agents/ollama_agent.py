# Agente Ollama (Local)
# Implementación específica para modelos locales ejecutados con Ollama

import json
import time
import requests
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
from utils.logger import app_logger


class OllamaAgent(BaseAgent):
    """
    Agente para modelos locales ejecutados con Ollama
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = self.api_url or "http://localhost:11434"
        # Ollama no requiere API key para localhost

    def get_response(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """
        Obtiene respuesta de Ollama
        """
        start_time = time.time()

        try:
            # Preparar contexto si existe
            prompt = message
            if context:
                context_text = "\n".join([
                    f"Usuario: {msg['content']}" if msg.get('role') == 'user'
                    else f"Asistente: {msg['content']}"
                    for msg in context
                ])
                prompt = f"{context_text}\nUsuario: {message}\nAsistente:"

            # Preparar parámetros
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                    **self.default_params
                }
            }

            # Realizar petición
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60  # Ollama puede ser más lento
            )

            response.raise_for_status()
            data = response.json()

            # Extraer respuesta
            if 'response' in data:
                response_text = data['response']

                # Calcular tiempo de respuesta
                response_time_ms = int((time.time() - start_time) * 1000)

                # Log de la interacción
                self.log_interaction(message, response_text, response_time_ms)

                return response_text.strip()
            else:
                raise Exception("Respuesta inválida de Ollama")

        except requests.exceptions.ConnectionError:
            error_msg = "Error: Ollama no está ejecutándose. Inicia Ollama con 'ollama serve'"
            app_logger.error(error_msg)
            return error_msg

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión con Ollama: {str(e)}"
            app_logger.error(error_msg)
            return f"Error: {error_msg}"

        except Exception as e:
            error_msg = f"Error procesando respuesta de Ollama: {str(e)}"
            app_logger.error(error_msg)
            return f"Error: {error_msg}"

    def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con Ollama
        """
        try:
            # Verificar si Ollama está ejecutándose
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]

                if self.model_name in models:
                    return {
                        "success": True,
                        "message": f"Conexión exitosa con Ollama. Modelo {self.model_name} disponible",
                        "available_models": models
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Modelo {self.model_name} no encontrado",
                        "message": f"Modelos disponibles: {', '.join(models)}",
                        "available_models": models
                    }
            else:
                return {
                    "success": False,
                    "error": f"Error HTTP {response.status_code}",
                    "message": "Ollama responde pero hay un error"
                }

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Ollama no está ejecutándose",
                "message": "Ejecuta 'ollama serve' para iniciar Ollama"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "No se pudo conectar con Ollama"
            }

    def get_available_models(self) -> List[str]:
        """
        Obtiene modelos disponibles en Ollama
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                return sorted(models)

            return ["llama3.1", "codestral", "mistral", "phi3", "qwen2.5"]

        except Exception as e:
            app_logger.error(f"Error obteniendo modelos de Ollama: {e}")
            return ["llama3.1", "codestral", "mistral", "phi3", "qwen2.5"]

    def pull_model(self, model_name: str) -> Dict[str, Any]:
        """
        Descarga un modelo en Ollama
        """
        try:
            payload = {"name": model_name}

            response = requests.post(
                f"{self.base_url}/api/pull",
                json=payload,
                timeout=300  # 5 minutos para descarga
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "message": f"Modelo {model_name} descargado exitosamente"
                }
            else:
                return {
                    "success": False,
                    "error": f"Error descargando modelo: {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"No se pudo descargar el modelo {model_name}"
            }

    def estimate_cost(self, message: str, response: str) -> float:
        """
        Ollama es gratuito (local)
        """
        return 0.0

    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """
        Obtiene información de un modelo específico
        """
        model = model_name or self.model_name

        try:
            payload = {"name": model}

            response = requests.post(
                f"{self.base_url}/api/show",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Modelo {model} no encontrado"}

        except Exception as e:
            return {"error": str(e)}