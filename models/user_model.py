# Modelo de usuarios
# Gestiona la autenticación y datos de usuarios del sistema

import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from .base_model import BaseModel


class UserModel(BaseModel):
    """
    Modelo para gestión de usuarios
    Maneja autenticación, registro y datos de usuario
    """

    def __init__(self):
        super().__init__()
        self.table_name = "users"

    def hash_password(self, password: str) -> str:
        """
        Encripta una contraseña usando bcrypt
        Args:
            password: Contraseña en texto plano
        Returns:
            Hash de la contraseña
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verifica una contraseña contra su hash
        Args:
            password: Contraseña en texto plano
            hashed: Hash almacenado
        Returns:
            True si la contraseña es correcta
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def create_user(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        is_admin: bool = False
    ) -> Optional[int]:
        """
        Crea un nuevo usuario
        Args:
            username: Nombre de usuario único
            password: Contraseña en texto plano
            email: Email del usuario
            full_name: Nombre completo
            is_admin: Si es administrador
        Returns:
            ID del usuario creado o None si hay error
        """
        try:
            self.connect()

            # Verificar si el usuario ya existe
            if self.get_user_by_username(username):
                print(f"Error: El usuario '{username}' ya existe")
                return None

            password_hash = self.hash_password(password)

            query = """
                INSERT INTO users (username, password_hash, email, full_name, is_admin)
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor = self.connection.cursor()
            cursor.execute(query, (username, password_hash, email, full_name, is_admin))
            self.connection.commit()

            user_id = cursor.lastrowid
            cursor.close()

            print(f"Usuario '{username}' creado exitosamente con ID: {user_id}")
            return user_id

        except Exception as error:
            print(f"Error al crear usuario: {error}")
            return None
        finally:
            self.disconnect()

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
        Returns:
            Datos del usuario si la autenticación es exitosa
        """
        try:
            self.connect()

            user = self.get_user_by_username(username)
            if not user:
                return None

            if not user['is_active']:
                print(f"Usuario '{username}' está inactivo")
                return None

            if self.verify_password(password, user['password_hash']):
                # Actualizar último login
                self.update_last_login(user['id'])

                # Remover la contraseña del resultado
                user.pop('password_hash', None)
                return user
            else:
                print(f"Contraseña incorrecta para el usuario '{username}'")
                return None

        except Exception as error:
            print(f"Error en autenticación: {error}")
            return None
        finally:
            self.disconnect()

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por su nombre de usuario
        Args:
            username: Nombre de usuario
        Returns:
            Datos del usuario o None si no existe
        """
        try:
            if not self.connection:
                self.connect()

            query = "SELECT * FROM users WHERE username = %s"
            result = self.execute_query(query, (username,))

            return result[0] if result else None

        except Exception as error:
            print(f"Error al obtener usuario: {error}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por su ID
        Args:
            user_id: ID del usuario
        Returns:
            Datos del usuario o None si no existe
        """
        try:
            self.connect()

            query = "SELECT * FROM users WHERE id = %s"
            result = self.execute_query(query, (user_id,))

            if result:
                user = result[0]
                user.pop('password_hash', None)  # No devolver el hash
                return user
            return None

        except Exception as error:
            print(f"Error al obtener usuario por ID: {error}")
            return None
        finally:
            self.disconnect()

    def update_user(
        self,
        user_id: int,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """
        Actualiza los datos de un usuario
        Args:
            user_id: ID del usuario
            email: Nuevo email
            full_name: Nuevo nombre completo
            is_active: Nuevo estado activo
        Returns:
            True si la actualización fue exitosa
        """
        try:
            self.connect()

            updates = []
            params = []

            if email is not None:
                updates.append("email = %s")
                params.append(email)

            if full_name is not None:
                updates.append("full_name = %s")
                params.append(full_name)

            if is_active is not None:
                updates.append("is_active = %s")
                params.append(is_active)

            if not updates:
                return True  # No hay nada que actualizar

            updates.append("updated_at = NOW()")
            params.append(user_id)

            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"

            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            return affected_rows > 0

        except Exception as error:
            print(f"Error al actualizar usuario: {error}")
            return False
        finally:
            self.disconnect()

    def update_password(self, user_id: int, new_password: str) -> bool:
        """
        Actualiza la contraseña de un usuario
        Args:
            user_id: ID del usuario
            new_password: Nueva contraseña en texto plano
        Returns:
            True si la actualización fue exitosa
        """
        try:
            self.connect()

            password_hash = self.hash_password(new_password)

            query = "UPDATE users SET password_hash = %s, updated_at = NOW() WHERE id = %s"

            cursor = self.connection.cursor()
            cursor.execute(query, (password_hash, user_id))
            self.connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            return affected_rows > 0

        except Exception as error:
            print(f"Error al actualizar contraseña: {error}")
            return False
        finally:
            self.disconnect()

    def update_last_login(self, user_id: int) -> bool:
        """
        Actualiza el último login del usuario
        Args:
            user_id: ID del usuario
        Returns:
            True si la actualización fue exitosa
        """
        try:
            if not self.connection:
                self.connect()

            query = "UPDATE users SET last_login = NOW() WHERE id = %s"

            cursor = self.connection.cursor()
            cursor.execute(query, (user_id,))
            self.connection.commit()
            cursor.close()

            return True

        except Exception as error:
            print(f"Error al actualizar último login: {error}")
            return False

    def get_all_users(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Obtiene todos los usuarios
        Args:
            include_inactive: Si incluir usuarios inactivos
        Returns:
            Lista de usuarios
        """
        try:
            self.connect()

            query = "SELECT id, username, email, full_name, is_active, is_admin, last_login, created_at FROM users"

            if not include_inactive:
                query += " WHERE is_active = TRUE"

            query += " ORDER BY created_at DESC"

            result = self.execute_query(query)
            return result if result else []

        except Exception as error:
            print(f"Error al obtener usuarios: {error}")
            return []
        finally:
            self.disconnect()

    def deactivate_user(self, user_id: int) -> bool:
        """
        Desactiva un usuario
        Args:
            user_id: ID del usuario
        Returns:
            True si la desactivación fue exitosa
        """
        return self.update_user(user_id, is_active=False)

    def activate_user(self, user_id: int) -> bool:
        """
        Activa un usuario
        Args:
            user_id: ID del usuario
        Returns:
            True si la activación fue exitosa
        """
        return self.update_user(user_id, is_active=True)

    def create_default_admin(self) -> bool:
        """
        Crea el usuario administrador por defecto si no existe
        Returns:
            True si se creó o ya existía el usuario
        """
        try:
            # Verificar si ya existe el usuario admin
            if self.get_user_by_username('jscothserver'):
                print("Usuario administrador ya existe")
                return True

            # Crear usuario administrador
            user_id = self.create_user(
                username='jscothserver',
                password='72900968',
                email='admin@livechat-ia.local',
                full_name='Administrador del Sistema',
                is_admin=True
            )

            if user_id:
                print("Usuario administrador creado exitosamente")
                return True
            else:
                print("Error al crear usuario administrador")
                return False

        except Exception as error:
            print(f"Error al crear usuario administrador por defecto: {error}")
            return False