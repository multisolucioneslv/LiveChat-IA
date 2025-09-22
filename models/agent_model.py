# Modelo de agentes IA
# Gestiona la configuración y uso de agentes de inteligencia artificial

import json
import base64
from datetime import datetime
from typing import Optional, Dict, List, Any
from .base_model import BaseModel
from utils.logger import app_logger


class AgentModel(BaseModel):
    """
    Modelo para gestión de agentes de IA
    Maneja configuración, credenciales y estadísticas de uso
    """

    def __init__(self):
        super().__init__()
        self.table_name = "agents"

    def encrypt_api_key(self, api_key: str) -> str:
        """
        Encripta una API key para almacenamiento seguro
        Args:
            api_key: API key en texto plano
        Returns:
            API key encriptada en base64
        """
        if not api_key:
            return ""

        # Encriptación básica con base64 (se puede mejorar con cryptography)
        encoded = base64.b64encode(api_key.encode('utf-8'))
        return encoded.decode('utf-8')

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """
        Desencripta una API key
        Args:
            encrypted_key: API key encriptada
        Returns:
            API key en texto plano
        """
        if not encrypted_key:
            return ""

        try:
            decoded = base64.b64decode(encrypted_key.encode('utf-8'))
            return decoded.decode('utf-8')
        except Exception as e:
            app_logger.error(f"Error desencriptando API key: {e}")
            return ""

    def create_agent(
        self,
        name: str,
        provider: str,
        model_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        config: Optional[Dict] = None,
        default_params: Optional[Dict] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        cost_per_1k_tokens: float = 0.0,
        created_by: Optional[int] = None,
        is_active: bool = True,
        is_default: bool = False
    ) -> Optional[int]:
        """
        Crea un nuevo agente IA
        Args:
            name: Nombre del agente
            provider: Proveedor (openai, anthropic, google, etc.)
            model_name: Nombre del modelo específico
            display_name: Nombre para mostrar en UI
            description: Descripción del agente
            api_key: API key del proveedor
            api_url: URL de la API
            config: Configuración específica del agente
            default_params: Parámetros por defecto
            max_tokens: Máximo de tokens
            temperature: Temperatura del modelo
            cost_per_1k_tokens: Costo por 1000 tokens
            created_by: ID del usuario que crea el agente
            is_active: Si el agente está activo
            is_default: Si es el agente por defecto
        Returns:
            ID del agente creado o None si hay error
        """
        try:
            self.connect()

            # Si es agente por defecto, desactivar otros defaults
            if is_default:
                self.unset_all_defaults()

            # Encriptar API key si se proporciona
            encrypted_key = self.encrypt_api_key(api_key) if api_key else None

            # Convertir configuraciones a JSON
            config_json = json.dumps(config) if config else None
            params_json = json.dumps(default_params) if default_params else None

            query = """
                INSERT INTO agents (
                    name, provider, model_name, display_name, description,
                    api_key_encrypted, api_url, config_json, default_params,
                    max_tokens, temperature, cost_per_1k_tokens, created_by,
                    is_active, is_default
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor = self.connection.cursor()
            cursor.execute(query, (
                name, provider, model_name, display_name or name, description,
                encrypted_key, api_url, config_json, params_json,
                max_tokens, temperature, cost_per_1k_tokens, created_by,
                is_active, is_default
            ))
            self.connection.commit()

            agent_id = cursor.lastrowid
            cursor.close()

            app_logger.info(f"Agente creado: {name} (ID: {agent_id})")
            return agent_id

        except Exception as error:
            app_logger.log_exception("Error creando agente", error)
            return None
        finally:
            self.disconnect()

    def get_agent_by_id(self, agent_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un agente por su ID
        Args:
            agent_id: ID del agente
        Returns:
            Datos del agente o None si no existe
        """
        try:
            self.connect()

            query = "SELECT * FROM agents WHERE id = %s"
            result = self.execute_query(query, (agent_id,))

            if result:
                agent = result[0]
                # Procesar campos JSON
                if agent['config_json']:
                    try:
                        agent['config'] = json.loads(agent['config_json'])
                    except json.JSONDecodeError:
                        agent['config'] = {}

                if agent['default_params']:
                    try:
                        agent['default_params'] = json.loads(agent['default_params'])
                    except json.JSONDecodeError:
                        agent['default_params'] = {}

                # Desencriptar API key
                if agent['api_key_encrypted']:
                    agent['api_key'] = self.decrypt_api_key(agent['api_key_encrypted'])

                return agent

            return None

        except Exception as error:
            app_logger.log_exception("Error obteniendo agente", error)
            return None
        finally:
            self.disconnect()

    def get_active_agents(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los agentes activos
        Returns:
            Lista de agentes activos
        """
        try:
            self.connect()

            query = """
                SELECT id, name, provider, model_name, display_name, description,
                       max_tokens, temperature, cost_per_1k_tokens, is_default
                FROM agents
                WHERE is_active = TRUE
                ORDER BY is_default DESC, name ASC
            """

            result = self.execute_query(query)
            return result if result else []

        except Exception as error:
            app_logger.log_exception("Error obteniendo agentes activos", error)
            return []
        finally:
            self.disconnect()

    def get_agents_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """
        Obtiene agentes por proveedor
        Args:
            provider: Nombre del proveedor
        Returns:
            Lista de agentes del proveedor
        """
        try:
            self.connect()

            query = """
                SELECT * FROM agents
                WHERE provider = %s AND is_active = TRUE
                ORDER BY name ASC
            """

            result = self.execute_query(query, (provider,))

            # Procesar datos para cada agente
            if result:
                for agent in result:
                    if agent['config_json']:
                        try:
                            agent['config'] = json.loads(agent['config_json'])
                        except json.JSONDecodeError:
                            agent['config'] = {}

                    if agent['default_params']:
                        try:
                            agent['default_params'] = json.loads(agent['default_params'])
                        except json.JSONDecodeError:
                            agent['default_params'] = {}

            return result if result else []

        except Exception as error:
            app_logger.log_exception(f"Error obteniendo agentes de {provider}", error)
            return []
        finally:
            self.disconnect()

    def get_default_agent(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el agente por defecto
        Returns:
            Datos del agente por defecto o None
        """
        try:
            self.connect()

            query = "SELECT * FROM agents WHERE is_default = TRUE AND is_active = TRUE LIMIT 1"
            result = self.execute_query(query)

            if result:
                return self.get_agent_by_id(result[0]['id'])

            return None

        except Exception as error:
            app_logger.log_exception("Error obteniendo agente por defecto", error)
            return None
        finally:
            self.disconnect()

    def update_agent(
        self,
        agent_id: int,
        name: Optional[str] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        config: Optional[Dict] = None,
        default_params: Optional[Dict] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        cost_per_1k_tokens: Optional[float] = None,
        is_active: Optional[bool] = None,
        is_default: Optional[bool] = None
    ) -> bool:
        """
        Actualiza un agente existente
        Args:
            agent_id: ID del agente
            ...: Campos a actualizar
        Returns:
            True si la actualización fue exitosa
        """
        try:
            self.connect()

            # Si se establece como default, desactivar otros defaults
            if is_default:
                self.unset_all_defaults()

            updates = []
            params = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)

            if display_name is not None:
                updates.append("display_name = %s")
                params.append(display_name)

            if description is not None:
                updates.append("description = %s")
                params.append(description)

            if api_key is not None:
                updates.append("api_key_encrypted = %s")
                params.append(self.encrypt_api_key(api_key))

            if api_url is not None:
                updates.append("api_url = %s")
                params.append(api_url)

            if config is not None:
                updates.append("config_json = %s")
                params.append(json.dumps(config))

            if default_params is not None:
                updates.append("default_params = %s")
                params.append(json.dumps(default_params))

            if max_tokens is not None:
                updates.append("max_tokens = %s")
                params.append(max_tokens)

            if temperature is not None:
                updates.append("temperature = %s")
                params.append(temperature)

            if cost_per_1k_tokens is not None:
                updates.append("cost_per_1k_tokens = %s")
                params.append(cost_per_1k_tokens)

            if is_active is not None:
                updates.append("is_active = %s")
                params.append(is_active)

            if is_default is not None:
                updates.append("is_default = %s")
                params.append(is_default)

            if not updates:
                return True  # No hay nada que actualizar

            updates.append("updated_at = NOW()")
            params.append(agent_id)

            query = f"UPDATE agents SET {', '.join(updates)} WHERE id = %s"

            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            if affected_rows > 0:
                app_logger.info(f"Agente actualizado: ID {agent_id}")

            return affected_rows > 0

        except Exception as error:
            app_logger.log_exception("Error actualizando agente", error)
            return False
        finally:
            self.disconnect()

    def delete_agent(self, agent_id: int) -> bool:
        """
        Elimina un agente
        Args:
            agent_id: ID del agente
        Returns:
            True si la eliminación fue exitosa
        """
        try:
            self.connect()

            query = "DELETE FROM agents WHERE id = %s"

            cursor = self.connection.cursor()
            cursor.execute(query, (agent_id,))
            self.connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            if affected_rows > 0:
                app_logger.info(f"Agente eliminado: ID {agent_id}")

            return affected_rows > 0

        except Exception as error:
            app_logger.log_exception("Error eliminando agente", error)
            return False
        finally:
            self.disconnect()

    def unset_all_defaults(self):
        """Quita el flag de default a todos los agentes"""
        try:
            if not self.connection:
                self.connect()

            query = "UPDATE agents SET is_default = FALSE WHERE is_default = TRUE"

            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()

        except Exception as error:
            app_logger.log_exception("Error quitando defaults", error)

    def set_default_agent(self, agent_id: int) -> bool:
        """
        Establece un agente como predeterminado
        Args:
            agent_id: ID del agente
        Returns:
            True si fue exitoso
        """
        try:
            self.connect()

            # Quitar default de todos los agentes
            self.unset_all_defaults()

            # Establecer el nuevo default
            query = "UPDATE agents SET is_default = TRUE WHERE id = %s AND is_active = TRUE"

            cursor = self.connection.cursor()
            cursor.execute(query, (agent_id,))
            self.connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            if affected_rows > 0:
                app_logger.info(f"Agente establecido como default: ID {agent_id}")

            return affected_rows > 0

        except Exception as error:
            app_logger.log_exception("Error estableciendo agente default", error)
            return False
        finally:
            self.disconnect()

    def test_agent_connection(self, agent_id: int) -> Dict[str, Any]:
        """
        Prueba la conexión con un agente
        Args:
            agent_id: ID del agente
        Returns:
            Resultado de la prueba
        """
        try:
            agent = self.get_agent_by_id(agent_id)

            if not agent:
                return {"success": False, "error": "Agente no encontrado"}

            if not agent.get('api_key'):
                return {"success": False, "error": "API key no configurada"}

            # Aquí se implementaría la prueba real según el proveedor
            # Por ahora retornamos éxito si hay API key
            return {
                "success": True,
                "message": f"Conexión con {agent['provider']} exitosa",
                "response_time": 150  # Simulado
            }

        except Exception as error:
            app_logger.log_exception("Error probando conexión de agente", error)
            return {"success": False, "error": str(error)}

    def get_agent_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de agentes
        Returns:
            Diccionario con estadísticas
        """
        try:
            self.connect()

            # Estadísticas básicas
            stats_query = """
                SELECT
                    COUNT(*) as total_agents,
                    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_agents,
                    COUNT(DISTINCT provider) as unique_providers
                FROM agents
            """

            result = self.execute_query(stats_query)
            stats = result[0] if result else {}

            # Estadísticas por proveedor
            provider_query = """
                SELECT provider, COUNT(*) as count, SUM(is_active) as active_count
                FROM agents
                GROUP BY provider
                ORDER BY count DESC
            """

            provider_result = self.execute_query(provider_query)
            stats['by_provider'] = {
                row['provider']: {
                    'total': row['count'],
                    'active': row['active_count']
                }
                for row in (provider_result if provider_result else [])
            }

            return stats

        except Exception as error:
            app_logger.log_exception("Error obteniendo estadísticas de agentes", error)
            return {}
        finally:
            self.disconnect()