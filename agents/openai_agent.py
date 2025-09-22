# Agente OpenAI
# Implementación específica para modelos de OpenAI

import json
import time
import requests
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
from utils.logger import app_logger


class OpenAIAgent(BaseAgent):
    """
    Agente para modelos de OpenAI (GPT-4o, GPT-4o-mini, GPT-3.5-turbo)
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = self.api_url or "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_response(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """
        Obtiene respuesta de OpenAI
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
                raise Exception("Respuesta inválida de OpenAI")

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión con OpenAI: {str(e)}"
            app_logger.error(error_msg)
            return f"Error: {error_msg}"

        except Exception as e:
            error_msg = f"Error procesando respuesta de OpenAI: {str(e)}"
            app_logger.error(error_msg)
            return f"Error: {error_msg}"

    def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con OpenAI
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
                    "message": "Conexión exitosa con OpenAI",
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
                "message": "No se pudo conectar con OpenAI"
            }

    def get_available_models(self) -> List[str]:
        """
        Obtiene modelos disponibles de OpenAI
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
                    # Filtrar solo modelos de chat relevantes
                    chat_models = [m for m in models if any(x in m for x in ['gpt-4', 'gpt-3.5'])]
                    return sorted(chat_models)

            return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]

        except Exception as e:
            app_logger.error(f"Error obteniendo modelos de OpenAI: {e}")
            return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]

    def estimate_cost(self, message: str, response: str) -> float:
        """
        Estima el costo de la interacción
        """
        # Estimación básica basada en caracteres (aproximado)
        input_chars = len(message)
        output_chars = len(response)

        # Conversión aproximada a tokens (1 token ≈ 4 caracteres)
        input_tokens = input_chars // 4
        output_tokens = output_chars // 4

        # Costos por modelo (por 1K tokens)
        costs = {
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
        }

        model_costs = costs.get(self.model_name, costs["gpt-4o-mini"])

        input_cost = (input_tokens / 1000) * model_costs["input"]
        output_cost = (output_tokens / 1000) * model_costs["output"]

        return input_cost + output_cost