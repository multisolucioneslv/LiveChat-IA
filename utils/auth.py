# Utilidades de autenticación
# Proporciona funciones para manejo de autenticación y sesiones

from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from models.user_model import UserModel
from models.session_model import SessionModel
from utils.logger import app_logger


class AuthManager:
    """
    Gestor de autenticación y sesiones
    Centraliza la lógica de autenticación del sistema
    """

    def __init__(self):
        self.user_model = UserModel()
        self.session_model = SessionModel()
        self.current_user = None
        self.current_session = None

    def login(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Inicia sesión de usuario
        Args:
            username: Nombre de usuario
            password: Contraseña
            ip_address: Dirección IP del cliente
            user_agent: User agent del cliente
        Returns:
            Tuple (éxito, datos_usuario, session_id)
        """
        try:
            # Autenticar usuario
            user = self.user_model.authenticate_user(username, password)

            if not user:
                app_logger.log_authentication(username, False, ip_address)
                return False, None, None

            # Crear nueva sesión
            session_id = self.session_model.create_session(
                user_id=user['id'],
                ip_address=ip_address,
                user_agent=user_agent
            )

            if not session_id:
                app_logger.error(f"Error al crear sesión para usuario {username}")
                return False, None, None

            # Establecer usuario y sesión actuales
            self.current_user = user
            self.current_session = session_id

            app_logger.log_authentication(username, True, ip_address)
            app_logger.log_session_event(session_id, "INICIO", user['id'])
            app_logger.log_user_action(user['id'], "LOGIN", f"IP: {ip_address}")

            return True, user, session_id

        except Exception as e:
            app_logger.log_exception("Error en login", e)
            return False, None, None

    def logout(self, session_id: Optional[str] = None) -> bool:
        """
        Cierra sesión de usuario
        Args:
            session_id: ID de la sesión a cerrar (opcional, usa la actual si no se especifica)
        Returns:
            True si el logout fue exitoso
        """
        try:
            target_session = session_id or self.current_session

            if not target_session:
                return False

            # Expirar la sesión
            success = self.session_model.expire_session(target_session)

            if success:
                if self.current_user:
                    app_logger.log_user_action(
                        self.current_user['id'],
                        "LOGOUT",
                        f"Sesión: {target_session}"
                    )

                app_logger.log_session_event(target_session, "CIERRE")

                # Limpiar datos actuales si es la sesión actual
                if target_session == self.current_session:
                    self.current_user = None
                    self.current_session = None

            return success

        except Exception as e:
            app_logger.log_exception("Error en logout", e)
            return False

    def validate_session(self, session_id: str) -> bool:
        """
        Valida si una sesión es válida
        Args:
            session_id: ID de la sesión
        Returns:
            True si la sesión es válida
        """
        try:
            # Limpiar sesiones expiradas primero
            self.session_model.cleanup_expired_sessions()

            # Validar la sesión específica
            session = self.session_model.get_session(session_id)

            if session:
                # Actualizar actividad de la sesión
                self.session_model.update_session_activity(session_id)
                return True

            return False

        except Exception as e:
            app_logger.log_exception("Error al validar sesión", e)
            return False

    def get_current_user(self, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene el usuario de la sesión actual
        Args:
            session_id: ID de la sesión (opcional, usa la actual si no se especifica)
        Returns:
            Datos del usuario o None si no hay sesión válida
        """
        try:
            target_session = session_id or self.current_session

            if not target_session:
                return None

            if not self.validate_session(target_session):
                return None

            session = self.session_model.get_session(target_session)

            if session and session['user_id']:
                user = self.user_model.get_user_by_id(session['user_id'])
                return user

            return None

        except Exception as e:
            app_logger.log_exception("Error al obtener usuario actual", e)
            return None

    def require_authentication(self, session_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Requiere autenticación válida
        Args:
            session_id: ID de la sesión
        Returns:
            Tuple (autenticado, datos_usuario)
        """
        if not self.validate_session(session_id):
            return False, None

        user = self.get_current_user(session_id)
        return user is not None, user

    def require_admin(self, session_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Requiere permisos de administrador
        Args:
            session_id: ID de la sesión
        Returns:
            Tuple (es_admin, datos_usuario)
        """
        authenticated, user = self.require_authentication(session_id)

        if not authenticated or not user:
            return False, None

        is_admin = user.get('is_admin', False)

        if not is_admin:
            app_logger.log_user_action(
                user['id'],
                "ACCESO_DENEGADO",
                "Intento de acceso a función de administrador"
            )

        return is_admin, user

    def extend_session(self, session_id: str, additional_hours: int = 24) -> bool:
        """
        Extiende la duración de una sesión
        Args:
            session_id: ID de la sesión
            additional_hours: Horas adicionales
        Returns:
            True si la extensión fue exitosa
        """
        try:
            additional_seconds = additional_hours * 60 * 60
            success = self.session_model.extend_session(session_id, additional_seconds)

            if success:
                app_logger.log_session_event(
                    session_id,
                    "EXTENDIDA",
                    f"Por {additional_hours} horas"
                )

            return success

        except Exception as e:
            app_logger.log_exception("Error al extender sesión", e)
            return False

    def change_password(
        self,
        session_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Cambia la contraseña del usuario actual
        Args:
            session_id: ID de la sesión
            current_password: Contraseña actual
            new_password: Nueva contraseña
        Returns:
            True si el cambio fue exitoso
        """
        try:
            # Verificar autenticación
            authenticated, user = self.require_authentication(session_id)
            if not authenticated or not user:
                return False

            # Verificar contraseña actual
            if not self.user_model.verify_password(current_password, user.get('password_hash', '')):
                app_logger.log_user_action(
                    user['id'],
                    "CAMBIO_PASSWORD_FALLIDO",
                    "Contraseña actual incorrecta"
                )
                return False

            # Actualizar contraseña
            success = self.user_model.update_password(user['id'], new_password)

            if success:
                app_logger.log_user_action(user['id'], "CAMBIO_PASSWORD", "Exitoso")

                # Expirar otras sesiones del usuario por seguridad
                self.session_model.expire_user_sessions(user['id'], session_id)

            return success

        except Exception as e:
            app_logger.log_exception("Error al cambiar contraseña", e)
            return False

    def get_user_sessions(self, user_id: int) -> list:
        """
        Obtiene las sesiones activas de un usuario
        Args:
            user_id: ID del usuario
        Returns:
            Lista de sesiones activas
        """
        try:
            return self.session_model.get_user_sessions(user_id, active_only=True)
        except Exception as e:
            app_logger.log_exception("Error al obtener sesiones de usuario", e)
            return []

    def terminate_user_sessions(self, user_id: int, except_session: Optional[str] = None) -> int:
        """
        Termina todas las sesiones de un usuario
        Args:
            user_id: ID del usuario
            except_session: Sesión a excluir de la terminación
        Returns:
            Número de sesiones terminadas
        """
        try:
            terminated = self.session_model.expire_user_sessions(user_id, except_session)

            if terminated > 0:
                app_logger.log_user_action(
                    user_id,
                    "SESIONES_TERMINADAS",
                    f"{terminated} sesiones cerradas"
                )

            return terminated

        except Exception as e:
            app_logger.log_exception("Error al terminar sesiones", e)
            return 0

    def cleanup_expired_sessions(self) -> int:
        """
        Limpia sesiones expiradas del sistema
        Returns:
            Número de sesiones limpiadas
        """
        try:
            cleaned = self.session_model.cleanup_expired_sessions()

            if cleaned > 0:
                app_logger.log_system_event(
                    "LIMPIEZA_SESIONES",
                    {'sesiones_eliminadas': cleaned}
                )

            return cleaned

        except Exception as e:
            app_logger.log_exception("Error al limpiar sesiones", e)
            return 0

    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de sesiones
        Returns:
            Diccionario con estadísticas
        """
        try:
            return self.session_model.get_session_statistics()
        except Exception as e:
            app_logger.log_exception("Error al obtener estadísticas de sesiones", e)
            return {}

    def initialize_default_admin(self) -> bool:
        """
        Inicializa el usuario administrador por defecto
        Returns:
            True si se inicializó correctamente
        """
        try:
            success = self.user_model.create_default_admin()

            if success:
                app_logger.log_system_event(
                    "ADMIN_INICIALIZADO",
                    "Usuario administrador por defecto creado/verificado"
                )

            return success

        except Exception as e:
            app_logger.log_exception("Error al inicializar administrador por defecto", e)
            return False


# Instancia global del gestor de autenticación
auth_manager = AuthManager()


# Funciones de conveniencia para usar directamente
def login(username: str, password: str, ip_address: str = None, user_agent: str = None):
    return auth_manager.login(username, password, ip_address, user_agent)


def logout(session_id: str = None):
    return auth_manager.logout(session_id)


def validate_session(session_id: str):
    return auth_manager.validate_session(session_id)


def get_current_user(session_id: str = None):
    return auth_manager.get_current_user(session_id)


def require_authentication(session_id: str):
    return auth_manager.require_authentication(session_id)


def require_admin(session_id: str):
    return auth_manager.require_admin(session_id)