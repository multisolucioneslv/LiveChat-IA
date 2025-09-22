# Agente Groq
# Implementación específica para modelos ejecutados por Groq (API compatible con OpenAI)

import json
import time
import requests
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
from utils.logger import app_logger


class GroqAgent(BaseAgent):
    """
    Agente para modelos de Groq (Llama, Mixtral, Gemma)
    Usa API compatible con OpenAI
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = self.api_url or "https://api.groq.com/openai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_response(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """
        Obtiene respuesta de Groq
        """
        start_time = time.time()

        try:
            # Preparar mensajes
            messages = []

            if context:
                messages.extend(context)

            messages.append({"role": "user", "content": message})

            # Preparar parámetros
            payload = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                **self.default_params
            }

            # Realizar petición
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            # Extraer respuesta
            if 'choices' in data and len(data['choices']) > 0:
                response_text = data['choices'][0]['message']['content']

                # Calcular tiempo de respuesta
                response_time_ms = int((time.time() - start_time) * 1000)

                # Log de la interacción
                self.log_interaction(message, response_text, response_time_ms)

                return response_text.strip()
            else:
                raise Exception("Respuesta inválida de Groq")

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión con Groq: {str(e)}"
            app_logger.error(error_msg)
            return f"Error: {error_msg}"

        except Exception as e:
            error_msg = f"Error procesando respuesta de Groq: {str(e)}"
            app_logger.error(error_msg)
            return f"Error: {error_msg}"

    def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con Groq
        """
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Conexión exitosa con Groq",
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "error": f"Error HTTP {response.status_code}",
                    "message": response.text
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "No se pudo conectar con Groq"
            }

    def get_available_models(self) -> List[str]:
        """
        Obtiene modelos disponibles de Groq
        """
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    models = [model['id'] for model in data['data']]
                    return sorted(models)

            # Modelos conocidos de Groq si la API no responde
            return [
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
                "gemma-7b-it"
            ]

        except Exception as e:
            app_logger.error(f"Error obteniendo modelos de Groq: {e}")
            return [
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
                "gemma-7b-it"
            ]

    def estimate_cost(self, message: str, response: str) -> float:
        """
        Estima el costo de la interacción
        """
        # Estimación básica basada en caracteres
        input_chars = len(message)
        output_chars = len(response)

        # Conversión aproximada a tokens (1 token ≈ 4 caracteres)
        input_tokens = input_chars // 4
        output_tokens = output_chars // 4

        # Costos por modelo (por 1K tokens) - Groq es muy económico
        costs = {
            "llama-3.1-70b-versatile": {"input": 0.00059, "output": 0.00079},
            "llama-3.1-8b-instant": {"input": 0.00005, "output": 0.00008},
            "mixtral-8x7b-32768": {"input": 0.00024, "output": 0.00024},
            "gemma-7b-it": {"input": 0.00007, "output": 0.00007}
        }

        model_costs = costs.get(self.model_name, costs["llama-3.1-70b-versatile"])

        input_cost = (input_tokens / 1000) * model_costs["input"]
        output_cost = (output_tokens / 1000) * model_costs["output"]

        return input_cost + output_cost

    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información específica del modelo Groq
        """
        model_info = {
            "llama-3.1-70b-versatile": {
                "context_length": 131072,
                "description": "Modelo Llama 3.1 70B optimizado por Groq para velocidad"
            },
            "llama-3.1-8b-instant": {
                "context_length": 131072,
                "description": "Modelo Llama 3.1 8B ultrarrápido"
            },
            "mixtral-8x7b-32768": {
                "context_length": 32768,
                "description": "Modelo Mixtral 8x7B con contexto extendido"
            },
            "gemma-7b-it": {
                "context_length": 8192,
                "description": "Modelo Gemma 7B instruction-tuned"
            }
        }

        return model_info.get(self.model_name, {
            "context_length": 8192,
            "description": "Modelo de Groq"
        })