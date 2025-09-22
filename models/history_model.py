# Modelo de historial
# Gestiona el historial de interacciones entre usuarios y agentes

import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from .base_model import BaseModel


class HistoryModel(BaseModel):
    """
    Modelo para gestión del historial de interacciones
    Registra todas las conversaciones y genera reportes
    """

    def __init__(self):
        super().__init__()
        self.table_name = "history"

    def create_interaction(
        self,
        user_id: Optional[int],
        session_id: Optional[str],
        interaction_type: str,
        user_message: Optional[str] = None,
        agent_response: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Registra una nueva interacción en el historial
        Args:
            user_id: ID del usuario (puede ser None para usuarios anónimos)
            session_id: ID de la sesión
            interaction_type: Tipo de interacción (chat, system, error, etc.)
            user_message: Mensaje del usuario
            agent_response: Respuesta del agente
            response_time_ms: Tiempo de respuesta en milisegundos
            tokens_used: Tokens utilizados en la respuesta
            metadata: Metadatos adicionales en formato JSON
        Returns:
            ID de la interacción creada o None si hay error
        """
        try:
            self.connect()

            query = """
                INSERT INTO history (
                    user_id, session_id, interaction_type, user_message,
                    agent_response, response_time_ms, tokens_used, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            metadata_json = json.dumps(metadata) if metadata else None

            cursor = self.connection.cursor()
            cursor.execute(query, (
                user_id, session_id, interaction_type, user_message,
                agent_response, response_time_ms, tokens_used, metadata_json
            ))
            self.connection.commit()

            interaction_id = cursor.lastrowid
            cursor.close()

            return interaction_id

        except Exception as error:
            print(f"Error al crear interacción: {error}")
            return None
        finally:
            self.disconnect()

    def get_user_interactions(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        interaction_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las interacciones de un usuario
        Args:
            user_id: ID del usuario
            limit: Número máximo de resultados
            offset: Desplazamiento para paginación
            interaction_type: Filtrar por tipo de interacción
        Returns:
            Lista de interacciones del usuario
        """
        try:
            self.connect()

            query = """
                SELECT id, session_id, interaction_type, user_message,
                       agent_response, response_time_ms, tokens_used,
                       metadata, created_at
                FROM history
                WHERE user_id = %s
            """
            params = [user_id]

            if interaction_type:
                query += " AND interaction_type = %s"
                params.append(interaction_type)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            result = self.execute_query(query, params)

            # Procesar metadatos JSON
            if result:
                for interaction in result:
                    if interaction['metadata']:
                        try:
                            interaction['metadata'] = json.loads(interaction['metadata'])
                        except json.JSONDecodeError:
                            interaction['metadata'] = {}

            return result if result else []

        except Exception as error:
            print(f"Error al obtener interacciones de usuario: {error}")
            return []
        finally:
            self.disconnect()

    def get_session_interactions(
        self,
        session_id: str,
        interaction_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las interacciones de una sesión específica
        Args:
            session_id: ID de la sesión
            interaction_type: Filtrar por tipo de interacción
        Returns:
            Lista de interacciones de la sesión
        """
        try:
            self.connect()

            query = """
                SELECT id, user_id, interaction_type, user_message,
                       agent_response, response_time_ms, tokens_used,
                       metadata, created_at
                FROM history
                WHERE session_id = %s
            """
            params = [session_id]

            if interaction_type:
                query += " AND interaction_type = %s"
                params.append(interaction_type)

            query += " ORDER BY created_at ASC"

            result = self.execute_query(query, params)

            # Procesar metadatos JSON
            if result:
                for interaction in result:
                    if interaction['metadata']:
                        try:
                            interaction['metadata'] = json.loads(interaction['metadata'])
                        except json.JSONDecodeError:
                            interaction['metadata'] = {}

            return result if result else []

        except Exception as error:
            print(f"Error al obtener interacciones de sesión: {error}")
            return []
        finally:
            self.disconnect()

    def get_interactions_by_date(
        self,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        interaction_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obtiene interacciones por rango de fechas
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin (por defecto hoy)
            interaction_type: Filtrar por tipo de interacción
            limit: Número máximo de resultados
        Returns:
            Lista de interacciones en el rango de fechas
        """
        try:
            self.connect()

            if not end_date:
                end_date = datetime.now()

            query = """
                SELECT h.*, u.username
                FROM history h
                LEFT JOIN users u ON h.user_id = u.id
                WHERE h.created_at BETWEEN %s AND %s
            """
            params = [start_date, end_date]

            if interaction_type:
                query += " AND h.interaction_type = %s"
                params.append(interaction_type)

            query += " ORDER BY h.created_at DESC LIMIT %s"
            params.append(limit)

            result = self.execute_query(query, params)

            # Procesar metadatos JSON
            if result:
                for interaction in result:
                    if interaction['metadata']:
                        try:
                            interaction['metadata'] = json.loads(interaction['metadata'])
                        except json.JSONDecodeError:
                            interaction['metadata'] = {}

            return result if result else []

        except Exception as error:
            print(f"Error al obtener interacciones por fecha: {error}")
            return []
        finally:
            self.disconnect()

    def get_interaction_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de interacciones
        Args:
            start_date: Fecha de inicio (por defecto últimos 30 días)
            end_date: Fecha de fin (por defecto hoy)
        Returns:
            Diccionario con estadísticas
        """
        try:
            self.connect()

            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)

            # Estadísticas básicas
            stats_query = """
                SELECT
                    COUNT(*) as total_interactions,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    AVG(response_time_ms) as avg_response_time,
                    SUM(tokens_used) as total_tokens,
                    AVG(tokens_used) as avg_tokens
                FROM history
                WHERE created_at BETWEEN %s AND %s
            """

            result = self.execute_query(stats_query, (start_date, end_date))
            stats = result[0] if result else {}

            # Estadísticas por tipo de interacción
            type_query = """
                SELECT interaction_type, COUNT(*) as count
                FROM history
                WHERE created_at BETWEEN %s AND %s
                GROUP BY interaction_type
                ORDER BY count DESC
            """

            type_result = self.execute_query(type_query, (start_date, end_date))
            stats['interaction_types'] = {
                row['interaction_type']: row['count']
                for row in (type_result if type_result else [])
            }

            # Estadísticas por día
            daily_query = """
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM history
                WHERE created_at BETWEEN %s AND %s
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 7
            """

            daily_result = self.execute_query(daily_query, (start_date, end_date))
            stats['daily_counts'] = {
                str(row['date']): row['count']
                for row in (daily_result if daily_result else [])
            }

            return stats

        except Exception as error:
            print(f"Error al obtener estadísticas: {error}")
            return {}
        finally:
            self.disconnect()

    def delete_old_interactions(self, days_to_keep: int = 90) -> int:
        """
        Elimina interacciones antiguas para mantener el tamaño de la base de datos
        Args:
            days_to_keep: Días de historial a mantener
        Returns:
            Número de interacciones eliminadas
        """
        try:
            self.connect()

            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            query = "DELETE FROM history WHERE created_at < %s"

            cursor = self.connection.cursor()
            cursor.execute(query, (cutoff_date,))
            self.connection.commit()

            deleted_count = cursor.rowcount
            cursor.close()

            if deleted_count > 0:
                print(f"Eliminadas {deleted_count} interacciones anteriores a {cutoff_date}")

            return deleted_count

        except Exception as error:
            print(f"Error al eliminar interacciones antiguas: {error}")
            return 0
        finally:
            self.disconnect()

    def get_popular_queries(
        self,
        limit: int = 10,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las consultas más populares
        Args:
            limit: Número máximo de consultas a retornar
            days: Número de días a considerar
        Returns:
            Lista de consultas populares
        """
        try:
            self.connect()

            start_date = datetime.now() - timedelta(days=days)

            query = """
                SELECT
                    SUBSTRING(user_message, 1, 100) as query_preview,
                    COUNT(*) as frequency,
                    AVG(response_time_ms) as avg_response_time
                FROM history
                WHERE created_at >= %s
                AND user_message IS NOT NULL
                AND user_message != ''
                AND interaction_type = 'chat'
                GROUP BY SUBSTRING(user_message, 1, 100)
                ORDER BY frequency DESC
                LIMIT %s
            """

            result = self.execute_query(query, (start_date, limit))
            return result if result else []

        except Exception as error:
            print(f"Error al obtener consultas populares: {error}")
            return []
        finally:
            self.disconnect()

    def update_interaction(
        self,
        interaction_id: int,
        agent_response: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Actualiza una interacción existente
        Args:
            interaction_id: ID de la interacción
            agent_response: Nueva respuesta del agente
            response_time_ms: Tiempo de respuesta actualizado
            tokens_used: Tokens utilizados actualizados
            metadata: Metadatos actualizados
        Returns:
            True si la actualización fue exitosa
        """
        try:
            self.connect()

            updates = []
            params = []

            if agent_response is not None:
                updates.append("agent_response = %s")
                params.append(agent_response)

            if response_time_ms is not None:
                updates.append("response_time_ms = %s")
                params.append(response_time_ms)

            if tokens_used is not None:
                updates.append("tokens_used = %s")
                params.append(tokens_used)

            if metadata is not None:
                updates.append("metadata = %s")
                params.append(json.dumps(metadata))

            if not updates:
                return True  # No hay nada que actualizar

            params.append(interaction_id)
            query = f"UPDATE history SET {', '.join(updates)} WHERE id = %s"

            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            return affected_rows > 0

        except Exception as error:
            print(f"Error al actualizar interacción: {error}")
            return False
        finally:
            self.disconnect()