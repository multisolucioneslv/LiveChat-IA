# Agente Google Gemini
# Implementación específica para modelos de Google Gemini

import json
import time
import requests
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
from utils.logger import app_logger


class GeminiAgent(BaseAgent):
    """
    Agente para modelos de Google Gemini
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = self.api_url or "https://generativelanguage.googleapis.com/v1"

    def get_response(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """
        Obtiene respuesta de Gemini
        """
        start_time = time.time()

        try:
            # Preparar contenido para Gemini
            contents = []

            if context:
                # Convertir contexto a formato Gemini
                for msg in context:
                    role = "user" if msg.get('role') == 'user' else "model"
                    contents.append({
                        "role": role,
                        "parts": [{"text": msg['content']}]
                    })

            contents.append({
                "role": "user",
                "parts": [{"text": message}]
            })

            # Preparar parámetros
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": self.max_tokens,
                    **self.default_params
                }
            }

            # URL con API key
            url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"

            # Realizar petición
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            # Extraer respuesta
            if 'candidates' in data and len(data['candidates']) > 0:
                candidate = data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    response_text = candidate['content']['parts'][0]['text']

                    # Calcular tiempo de respuesta
                    response_time_ms = int((time.time() - start_time) * 1000)

                    # Log de la interacción
                    self.log_interaction(message, response_text, response_time_ms)

                    return response_text.strip()
                else:
                    raise Exception("Estructura de respuesta inválida de Gemini")
            else:
                raise Exception("Respuesta inválida de Gemini")

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión con Gemini: {str(e)}"
            app_logger.error(error_msg)
            return f"Error: {error_msg}"

        except Exception as e:
            error_msg = f"Error procesando respuesta de Gemini: {str(e)}"
            app_logger.error(error_msg)
            return f"Error: {error_msg}"

    def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con Gemini
        """
        try:
            # Probar con mensaje simple
            test_payload = {
                "contents": [{
                    "role": "user",
                    "parts": [{"text": "Test"}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 10
                }
            }

            url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"

            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=test_payload,
                timeout=10
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Conexión exitosa con Gemini",
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
                "message": "No se pudo conectar con Gemini"
            }

    def get_available_models(self) -> List[str]:
        """
        Obtiene modelos disponibles de Gemini
        """
        try:
            url = f"{self.base_url}/models?key={self.api_key}"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'models' in data:
                    models = []
                    for model in data['models']:
                        model_name = model.get('name', '').replace('models/', '')
                        # Filtrar solo modelos de generación
                        if 'generateContent' in model.get('supportedGenerationMethods', []):
                            models.append(model_name)
                    return sorted(models)

            return ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]

        except Exception as e:
            app_logger.error(f"Error obteniendo modelos de Gemini: {e}")
            return ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]

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
            "gemini-1.5-pro": {"input": 0.0035, "output": 0.0105},
            "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
            "gemini-pro": {"input": 0.0005, "output": 0.0015}
        }

        model_costs = costs.get(self.model_name, costs["gemini-1.5-flash"])

        input_cost = (input_tokens / 1000) * model_costs["input"]
        output_cost = (output_tokens / 1000) * model_costs["output"]

        return input_cost + output_cost

    def format_safety_settings(self) -> List[Dict[str, Any]]:
        """
        Configuraciones de seguridad para Gemini
        """
        return [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]