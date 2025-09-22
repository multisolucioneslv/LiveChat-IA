# Agente Anthropic Claude
# Implementación específica para modelos de Claude

import json
import time
import requests
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
from utils.logger import app_logger


class ClaudeAgent(BaseAgent):
    """
    Agente para modelos de Anthropic Claude
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = self.api_url or "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

    def get_response(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """
        Obtiene respuesta de Claude
        """
        start_time = time.time()

        try:
            # Preparar mensajes para Claude
            messages = []

            if context:
                # Convertir contexto a formato Claude
                for msg in context:
                    if msg.get('role') == 'user':
                        messages.append({"role": "user", "content": msg['content']})
                    elif msg.get('role') == 'assistant':
                        messages.append({"role": "assistant", "content": msg['content']})

            messages.append({"role": "user", "content": message})

            # Preparar parámetros
            payload = {
                "model": self.model_name,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": messages,
                **self.default_params
            }

            # Realizar petición
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            # Extraer respuesta
            if 'content' in data and len(data['content']) > 0:
                response_text = data['content'][0]['text']

                # Calcular tiempo de respuesta
                response_time_ms = int((time.time() - start_time) * 1000)

                # Log de la interacción
                self.log_interaction(message, response_text, response_time_ms)

                return response_text.strip()
            else:
                raise Exception("Respuesta inválida de Claude")

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión con Claude: {str(e)}"
            app_logger.error(error_msg)
            return f"Error: {error_msg}"

        except Exception as e:
            error_msg = f"Error procesando respuesta de Claude: {str(e)}"
            app_logger.error(error_msg)
            return f"Error: {error_msg}"

    def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con Claude
        """
        try:
            # Claude no tiene endpoint de modelos, probamos con mensaje simple
            test_payload = {
                "model": self.model_name,
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Test"}]
            }

            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=test_payload,
                timeout=10
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Conexión exitosa con Claude",
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
                "message": "No se pudo conectar con Claude"
            }

    def get_available_models(self) -> List[str]:
        """
        Obtiene modelos disponibles de Claude
        """
        # Claude no tiene endpoint público de modelos, retornamos los conocidos
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
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

        # Costos por modelo (por 1K tokens)
        costs = {
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125}
        }

        model_costs = costs.get(self.model_name, costs["claude-3-5-sonnet-20241022"])

        input_cost = (input_tokens / 1000) * model_costs["input"]
        output_cost = (output_tokens / 1000) * model_costs["output"]

        return input_cost + output_cost

    def format_system_prompt(self, system_message: str) -> Dict[str, Any]:
        """
        Formatea un mensaje de sistema para Claude
        """
        return {
            "system": system_message
        }