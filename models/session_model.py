# Modelo de sesiones
# Gestiona las sesiones activas de usuarios en el sistema

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from .base_model import BaseModel


class SessionModel(BaseModel):
    """
    Modelo para gestión de sesiones de usuario
    Maneja creación, validación y limpieza de sesiones
    """

    def __init__(self):
        super().__init__()
        self.table_name = "sessions"
        self.default_session_duration = 24 * 60 * 60  # 24 horas en segundos

    def generate_session_id(self) -> str:
        """
        Genera un ID único para la sesión
        Returns:
            UUID único como string
        """
        return str(uuid.uuid4())

    def create_session(
        self,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        duration_seconds: Optional[int] = None
    ) -> Optional[str]:
        """
        Crea una nueva sesión para un usuario
        Args:
            user_id: ID del usuario
            ip_address: Dirección IP del cliente
            user_agent: User agent del navegador/cliente
            duration_seconds: Duración de la sesión en segundos
        Returns:
            ID de la sesión creada o None si hay error
        """
        try:
            self.connect()

            session_id = self.generate_session_id()
            duration = duration_seconds or self.default_session_duration
            expires_at = datetime.now() + timedelta(seconds=duration)

            query = """
                INSERT INTO sessions (id, user_id, ip_address, user_agent, expires_at)
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor = self.connection.cursor()
            cursor.execute(query, (session_id, user_id, ip_address, user_agent, expires_at))
            self.connection.commit()
            cursor.close()

            print(f"Sesión creada: {session_id} para usuario {user_id}")
            return session_id

        except Exception as error:
            print(f"Error al crear sesión: {error}")
            return None
        finally:
            self.disconnect()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de una sesión
        Args:
            session_id: ID de la sesión
        Returns:
            Datos de la sesión o None si no existe/expiró
        """
        try:
            self.connect()

            query = """
                SELECT s.*, u.username, u.is_active as user_is_active
                FROM sessions s
                LEFT JOIN users u ON s.user_id = u.id
                WHERE s.id = %s AND s.is_active = TRUE
            """

            result = self.execute_query(query, (session_id,))

            if not result:
                return None

            session = result[0]

            # Verificar si la sesión ha expirado
            if session['expires_at'] and session['expires_at'] < datetime.now():
                self.expire_session(session_id)
                return None

            # Verificar si el usuario está activo
            if not session['user_is_active']:
                self.expire_session(session_id)
                return None

            return session

        except Exception as error:
            print(f"Error al obtener sesión: {error}")
            return None
        finally:
            self.disconnect()

    def validate_session(self, session_id: str) -> bool:
        """
        Valida si una sesión es válida y activa
        Args:
            session_id: ID de la sesión
        Returns:
            True si la sesión es válida
        """
        session = self.get_session(session_id)
        return session is not None

    def update_session_activity(self, session_id: str) -> bool:
        """
        Actualiza la última actividad de una sesión
        Args:
            session_id: ID de la sesión
        Returns:
            True si la actualización fue exitosa
        """
        try:
            self.connect()

            query = """
                UPDATE sessions
                SET last_activity = NOW()
                WHERE id = %s AND is_active = TRUE
            """

            cursor = self.connection.cursor()
            cursor.execute(query, (session_id,))
            self.connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            return affected_rows > 0

        except Exception as error:
            print(f"Error al actualizar actividad de sesión: {error}")
            return False
        finally:
            self.disconnect()

    def extend_session(
        self,
        session_id: str,
        additional_seconds: int = None
    ) -> bool:
        """
        Extiende la duración de una sesión
        Args:
            session_id: ID de la sesión
            additional_seconds: Segundos adicionales (por defecto usa duración estándar)
        Returns:
            True si la extensión fue exitosa
        """
        try:
            self.connect()

            extension = additional_seconds or self.default_session_duration
            new_expires_at = datetime.now() + timedelta(seconds=extension)

            query = """
                UPDATE sessions
                SET expires_at = %s, last_activity = NOW()
                WHERE id = %s AND is_active = TRUE
            """

            cursor = self.connection.cursor()
            cursor.execute(query, (new_expires_at, session_id))
            self.connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            return affected_rows > 0

        except Exception as error:
            print(f"Error al extender sesión: {error}")
            return False
        finally:
            self.disconnect()

    def expire_session(self, session_id: str) -> bool:
        """
        Expira una sesión específica
        Args:
            session_id: ID de la sesión
        Returns:
            True si la expiración fue exitosa
        """
        try:
            self.connect()

            query = """
                UPDATE sessions
                SET is_active = FALSE, last_activity = NOW()
                WHERE id = %s
            """

            cursor = self.connection.cursor()
            cursor.execute(query, (session_id,))
            self.connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            print(f"Sesión expirada: {session_id}")
            return affected_rows > 0

        except Exception as error:
            print(f"Error al expirar sesión: {error}")
            return False
        finally:
            self.disconnect()

    def expire_user_sessions(self, user_id: int, except_session: Optional[str] = None) -> int:
        """
        Expira todas las sesiones de un usuario
        Args:
            user_id: ID del usuario
            except_session: ID de sesión a excluir de la expiración
        Returns:
            Número de sesiones expiradas
        """
        try:
            self.connect()

            if except_session:
                query = """
                    UPDATE sessions
                    SET is_active = FALSE, last_activity = NOW()
                    WHERE user_id = %s AND id != %s AND is_active = TRUE
                """
                params = (user_id, except_session)
            else:
                query = """
                    UPDATE sessions
                    SET is_active = FALSE, last_activity = NOW()
                    WHERE user_id = %s AND is_active = TRUE
                """
                params = (user_id,)

            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            print(f"Expiradas {affected_rows} sesiones para usuario {user_id}")
            return affected_rows

        except Exception as error:
            print(f"Error al expirar sesiones de usuario: {error}")
            return 0
        finally:
            self.disconnect()

    def cleanup_expired_sessions(self) -> int:
        """
        Limpia sesiones expiradas automáticamente
        Returns:
            Número de sesiones limpiadas
        """
        try:
            self.connect()

            query = """
                UPDATE sessions
                SET is_active = FALSE
                WHERE (expires_at < NOW() OR expires_at IS NULL)
                AND is_active = TRUE
            """

            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            if affected_rows > 0:
                print(f"Limpiadas {affected_rows} sesiones expiradas")

            return affected_rows

        except Exception as error:
            print(f"Error al limpiar sesiones expiradas: {error}")
            return 0
        finally:
            self.disconnect()

    def get_user_sessions(
        self,
        user_id: int,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las sesiones de un usuario
        Args:
            user_id: ID del usuario
            active_only: Si solo incluir sesiones activas
        Returns:
            Lista de sesiones del usuario
        """
        try:
            self.connect()

            query = """
                SELECT id, ip_address, user_agent, created_at, expires_at,
                       last_activity, is_active
                FROM sessions
                WHERE user_id = %s
            """

            if active_only:
                query += " AND is_active = TRUE"

            query += " ORDER BY last_activity DESC"

            result = self.execute_query(query, (user_id,))
            return result if result else []

        except Exception as error:
            print(f"Error al obtener sesiones de usuario: {error}")
            return []
        finally:
            self.disconnect()

    def get_active_sessions_count(self) -> int:
        """
        Obtiene el número de sesiones activas
        Returns:
            Número de sesiones activas
        """
        try:
            self.connect()

            query = """
                SELECT COUNT(*) as count
                FROM sessions
                WHERE is_active = TRUE AND expires_at > NOW()
            """

            result = self.execute_query(query)
            return result[0]['count'] if result else 0

        except Exception as error:
            print(f"Error al contar sesiones activas: {error}")
            return 0
        finally:
            self.disconnect()

    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de sesiones
        Returns:
            Diccionario con estadísticas
        """
        try:
            self.connect()

            # Consultas múltiples para obtener estadísticas
            queries = {
                'total_sessions': "SELECT COUNT(*) as count FROM sessions",
                'active_sessions': "SELECT COUNT(*) as count FROM sessions WHERE is_active = TRUE AND expires_at > NOW()",
                'expired_sessions': "SELECT COUNT(*) as count FROM sessions WHERE is_active = FALSE OR expires_at <= NOW()",
                'sessions_today': "SELECT COUNT(*) as count FROM sessions WHERE DATE(created_at) = CURDATE()",
                'unique_users_today': "SELECT COUNT(DISTINCT user_id) as count FROM sessions WHERE DATE(created_at) = CURDATE()"
            }

            stats = {}
            for key, query in queries.items():
                result = self.execute_query(query)
                stats[key] = result[0]['count'] if result else 0

            return stats

        except Exception as error:
            print(f"Error al obtener estadísticas de sesiones: {error}")
            return {}
        finally:
            self.disconnect()