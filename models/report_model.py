# Modelo de reportes
# Gestiona los metadatos y archivos de reportes del sistema

import os
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from .base_model import BaseModel


class ReportModel(BaseModel):
    """
    Modelo para gestión de reportes y sus metadatos
    Registra información sobre reportes generados y facilita su recuperación
    """

    def __init__(self):
        super().__init__()
        self.table_name = "reports"

    def create_report_record(
        self,
        report_type: str,
        title: str,
        file_path: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        summary: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_auto_generated: bool = True
    ) -> Optional[int]:
        """
        Crea un registro de reporte en la base de datos
        Args:
            report_type: Tipo de reporte (chat_interaction, system_status, error, daily_summary)
            title: Título del reporte
            file_path: Ruta del archivo de reporte
            user_id: ID del usuario que generó el reporte
            session_id: ID de la sesión asociada
            summary: Resumen del contenido del reporte
            tags: Etiquetas para categorizar el reporte
            is_auto_generated: Si fue generado automáticamente
        Returns:
            ID del registro creado o None si hay error
        """
        try:
            self.connect()

            # Obtener el tamaño del archivo
            file_size = None
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)

            # Convertir tags a JSON
            tags_json = json.dumps(tags) if tags else None

            query = """
                INSERT INTO reports (
                    report_type, title, file_path, file_size, user_id,
                    session_id, summary, tags, is_auto_generated
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor = self.connection.cursor()
            cursor.execute(query, (
                report_type, title, file_path, file_size, user_id,
                session_id, summary, tags_json, is_auto_generated
            ))
            self.connection.commit()

            report_id = cursor.lastrowid
            cursor.close()

            return report_id

        except Exception as error:
            print(f"Error al crear registro de reporte: {error}")
            return None
        finally:
            self.disconnect()

    def get_report_by_id(self, report_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un reporte por su ID
        Args:
            report_id: ID del reporte
        Returns:
            Datos del reporte o None si no existe
        """
        try:
            self.connect()

            query = """
                SELECT r.*, u.username as created_by_username
                FROM reports r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.id = %s
            """

            result = self.execute_query(query, (report_id,))

            if result:
                report = result[0]
                # Procesar tags JSON
                if report['tags']:
                    try:
                        report['tags'] = json.loads(report['tags'])
                    except json.JSONDecodeError:
                        report['tags'] = []
                return report

            return None

        except Exception as error:
            print(f"Error al obtener reporte: {error}")
            return None
        finally:
            self.disconnect()

    def get_reports_by_type(
        self,
        report_type: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Obtiene reportes por tipo
        Args:
            report_type: Tipo de reporte
            limit: Número máximo de resultados
            offset: Desplazamiento para paginación
        Returns:
            Lista de reportes del tipo especificado
        """
        try:
            self.connect()

            query = """
                SELECT r.id, r.title, r.file_path, r.file_size, r.summary,
                       r.created_at, r.is_auto_generated, u.username as created_by
                FROM reports r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.report_type = %s
                ORDER BY r.created_at DESC
                LIMIT %s OFFSET %s
            """

            result = self.execute_query(query, (report_type, limit, offset))
            return result if result else []

        except Exception as error:
            print(f"Error al obtener reportes por tipo: {error}")
            return []
        finally:
            self.disconnect()

    def get_reports_by_date_range(
        self,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        report_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene reportes por rango de fechas
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin (por defecto hoy)
            report_type: Filtrar por tipo de reporte
        Returns:
            Lista de reportes en el rango de fechas
        """
        try:
            self.connect()

            if not end_date:
                end_date = datetime.now()

            query = """
                SELECT r.*, u.username as created_by_username
                FROM reports r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.created_at BETWEEN %s AND %s
            """
            params = [start_date, end_date]

            if report_type:
                query += " AND r.report_type = %s"
                params.append(report_type)

            query += " ORDER BY r.created_at DESC"

            result = self.execute_query(query, params)

            # Procesar tags JSON
            if result:
                for report in result:
                    if report['tags']:
                        try:
                            report['tags'] = json.loads(report['tags'])
                        except json.JSONDecodeError:
                            report['tags'] = []

            return result if result else []

        except Exception as error:
            print(f"Error al obtener reportes por fecha: {error}")
            return []
        finally:
            self.disconnect()

    def get_user_reports(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Obtiene reportes de un usuario específico
        Args:
            user_id: ID del usuario
            limit: Número máximo de resultados
            offset: Desplazamiento para paginación
        Returns:
            Lista de reportes del usuario
        """
        try:
            self.connect()

            query = """
                SELECT id, report_type, title, file_path, file_size,
                       summary, created_at, is_auto_generated
                FROM reports
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """

            result = self.execute_query(query, (user_id, limit, offset))
            return result if result else []

        except Exception as error:
            print(f"Error al obtener reportes de usuario: {error}")
            return []
        finally:
            self.disconnect()

    def search_reports(
        self,
        search_term: str,
        report_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Busca reportes por término de búsqueda
        Args:
            search_term: Término a buscar en título y resumen
            report_type: Filtrar por tipo de reporte
            tags: Filtrar por etiquetas
            limit: Número máximo de resultados
        Returns:
            Lista de reportes que coinciden con la búsqueda
        """
        try:
            self.connect()

            query = """
                SELECT r.*, u.username as created_by_username
                FROM reports r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE (r.title LIKE %s OR r.summary LIKE %s)
            """
            search_pattern = f"%{search_term}%"
            params = [search_pattern, search_pattern]

            if report_type:
                query += " AND r.report_type = %s"
                params.append(report_type)

            if tags:
                # Buscar reportes que contengan alguna de las etiquetas
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append("JSON_CONTAINS(r.tags, %s)")
                    params.append(json.dumps(tag))

                query += f" AND ({' OR '.join(tag_conditions)})"

            query += " ORDER BY r.created_at DESC LIMIT %s"
            params.append(limit)

            result = self.execute_query(query, params)

            # Procesar tags JSON
            if result:
                for report in result:
                    if report['tags']:
                        try:
                            report['tags'] = json.loads(report['tags'])
                        except json.JSONDecodeError:
                            report['tags'] = []

            return result if result else []

        except Exception as error:
            print(f"Error al buscar reportes: {error}")
            return []
        finally:
            self.disconnect()

    def get_report_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de reportes
        Returns:
            Diccionario con estadísticas
        """
        try:
            self.connect()

            # Estadísticas básicas
            basic_stats_query = """
                SELECT
                    COUNT(*) as total_reports,
                    SUM(file_size) as total_size_bytes,
                    AVG(file_size) as avg_size_bytes,
                    COUNT(DISTINCT user_id) as unique_users,
                    SUM(CASE WHEN is_auto_generated = 1 THEN 1 ELSE 0 END) as auto_generated,
                    SUM(CASE WHEN is_auto_generated = 0 THEN 1 ELSE 0 END) as manual_generated
                FROM reports
            """

            result = self.execute_query(basic_stats_query)
            stats = result[0] if result else {}

            # Estadísticas por tipo
            type_stats_query = """
                SELECT report_type, COUNT(*) as count, SUM(file_size) as total_size
                FROM reports
                GROUP BY report_type
                ORDER BY count DESC
            """

            type_result = self.execute_query(type_stats_query)
            stats['by_type'] = {
                row['report_type']: {
                    'count': row['count'],
                    'total_size': row['total_size']
                }
                for row in (type_result if type_result else [])
            }

            # Estadísticas diarias (últimos 7 días)
            daily_stats_query = """
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM reports
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """

            daily_result = self.execute_query(daily_stats_query)
            stats['daily_counts'] = {
                str(row['date']): row['count']
                for row in (daily_result if daily_result else [])
            }

            return stats

        except Exception as error:
            print(f"Error al obtener estadísticas de reportes: {error}")
            return {}
        finally:
            self.disconnect()

    def update_report(
        self,
        report_id: int,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Actualiza los metadatos de un reporte
        Args:
            report_id: ID del reporte
            title: Nuevo título
            summary: Nuevo resumen
            tags: Nuevas etiquetas
        Returns:
            True si la actualización fue exitosa
        """
        try:
            self.connect()

            updates = []
            params = []

            if title is not None:
                updates.append("title = %s")
                params.append(title)

            if summary is not None:
                updates.append("summary = %s")
                params.append(summary)

            if tags is not None:
                updates.append("tags = %s")
                params.append(json.dumps(tags))

            if not updates:
                return True  # No hay nada que actualizar

            params.append(report_id)
            query = f"UPDATE reports SET {', '.join(updates)} WHERE id = %s"

            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            return affected_rows > 0

        except Exception as error:
            print(f"Error al actualizar reporte: {error}")
            return False
        finally:
            self.disconnect()

    def delete_report(self, report_id: int, delete_file: bool = False) -> bool:
        """
        Elimina un reporte
        Args:
            report_id: ID del reporte
            delete_file: Si también eliminar el archivo físico
        Returns:
            True si la eliminación fue exitosa
        """
        try:
            # Obtener información del reporte antes de eliminar
            report = self.get_report_by_id(report_id)
            if not report:
                return False

            self.connect()

            # Eliminar registro de la base de datos
            query = "DELETE FROM reports WHERE id = %s"

            cursor = self.connection.cursor()
            cursor.execute(query, (report_id,))
            self.connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            # Eliminar archivo físico si se solicita
            if delete_file and affected_rows > 0:
                try:
                    if os.path.exists(report['file_path']):
                        os.remove(report['file_path'])
                        print(f"Archivo eliminado: {report['file_path']}")
                except OSError as e:
                    print(f"Error al eliminar archivo: {e}")

            return affected_rows > 0

        except Exception as error:
            print(f"Error al eliminar reporte: {error}")
            return False
        finally:
            self.disconnect()

    def cleanup_old_reports(
        self,
        days_to_keep: int = 30,
        delete_files: bool = True
    ) -> int:
        """
        Limpia reportes antiguos
        Args:
            days_to_keep: Días de reportes a mantener
            delete_files: Si también eliminar los archivos físicos
        Returns:
            Número de reportes eliminados
        """
        try:
            self.connect()

            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            # Obtener reportes a eliminar si necesitamos borrar archivos
            if delete_files:
                reports_query = "SELECT file_path FROM reports WHERE created_at < %s"
                reports_to_delete = self.execute_query(reports_query, (cutoff_date,))

            # Eliminar registros de la base de datos
            delete_query = "DELETE FROM reports WHERE created_at < %s"

            cursor = self.connection.cursor()
            cursor.execute(delete_query, (cutoff_date,))
            self.connection.commit()

            deleted_count = cursor.rowcount
            cursor.close()

            # Eliminar archivos físicos
            if delete_files and reports_to_delete:
                for report in reports_to_delete:
                    try:
                        if os.path.exists(report['file_path']):
                            os.remove(report['file_path'])
                    except OSError:
                        continue

            if deleted_count > 0:
                print(f"Eliminados {deleted_count} reportes anteriores a {cutoff_date}")

            return deleted_count

        except Exception as error:
            print(f"Error al limpiar reportes antiguos: {error}")
            return 0
        finally:
            self.disconnect()