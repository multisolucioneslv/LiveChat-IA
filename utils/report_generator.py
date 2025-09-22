# Generador de reportes en formato Markdown
# Crea y gestiona reportes del sistema de forma automática

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from config.app_config import AppConfig


class ReportGenerator:
    """
    Generador de reportes en formato Markdown
    Crea reportes estructurados y los guarda en la carpeta de reportes
    """

    def __init__(self):
        self.app_config = AppConfig()
        self.reports_dir = "reportes"
        self.ensure_reports_directory()

    def ensure_reports_directory(self):
        """Asegura que la carpeta de reportes exista"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def generate_timestamp(self) -> str:
        """Genera timestamp para nombres de archivo"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_readable_timestamp(self) -> str:
        """Genera timestamp legible para contenido del reporte"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def create_chat_interaction_report(
        self,
        user_message: str,
        agent_response: str,
        response_time_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Crea un reporte de interacción de chat
        Args:
            user_message: Mensaje del usuario
            agent_response: Respuesta del agente
            response_time_ms: Tiempo de respuesta en milisegundos
            tokens_used: Tokens utilizados
            metadata: Metadatos adicionales
        Returns:
            Path del archivo de reporte creado
        """
        timestamp = self.generate_timestamp()
        filename = f"chat_interaction_{timestamp}.md"
        filepath = os.path.join(self.reports_dir, filename)

        content = f"""# Reporte de Interacción de Chat

**Fecha y Hora:** {self.generate_readable_timestamp()}
**Tipo de Reporte:** Interacción de Chat
**ID de Reporte:** {timestamp}

## Información de la Sesión

- **Usuario:** {metadata.get('username', 'Anónimo') if metadata else 'Anónimo'}
- **Sesión ID:** {metadata.get('session_id', 'N/A') if metadata else 'N/A'}
- **Agente:** {metadata.get('agent_name', 'Agente de Pruebas') if metadata else 'Agente de Pruebas'}

## Detalles de la Interacción

### Mensaje del Usuario
```
{user_message}
```

### Respuesta del Agente
```
{agent_response}
```

## Métricas de Rendimiento

- **Tiempo de Respuesta:** {response_time_ms}ms
- **Tokens Utilizados:** {tokens_used if tokens_used else 'N/A'}
- **Longitud del Mensaje:** {len(user_message)} caracteres
- **Longitud de la Respuesta:** {len(agent_response)} caracteres

## Metadatos Técnicos

```json
{json.dumps(metadata if metadata else {}, indent=2, ensure_ascii=False)}
```

---
*Reporte generado automáticamente por {self.app_config.get_app_name()}*
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    def create_system_status_report(
        self,
        status_data: Dict[str, Any]
    ) -> str:
        """
        Crea un reporte de estado del sistema
        Args:
            status_data: Datos del estado del sistema
        Returns:
            Path del archivo de reporte creado
        """
        timestamp = self.generate_timestamp()
        filename = f"system_status_{timestamp}.md"
        filepath = os.path.join(self.reports_dir, filename)

        content = f"""# Reporte de Estado del Sistema

**Fecha y Hora:** {self.generate_readable_timestamp()}
**Tipo de Reporte:** Estado del Sistema
**ID de Reporte:** {timestamp}

## Información General

- **Aplicación:** {self.app_config.get_app_name()}
- **Entorno:** {self.app_config.get_environment()}
- **Modo Debug:** {self.app_config.is_debug_mode()}
- **Zona Horaria:** {self.app_config.get_timezone_name()}

## Estado de Componentes

### Base de Datos
- **Estado:** {status_data.get('database_status', 'Desconocido')}
- **Conexiones Activas:** {status_data.get('active_connections', 'N/A')}
- **Última Verificación:** {status_data.get('last_db_check', 'N/A')}

### Sistema de Archivos
- **Carpeta Logs:** {'✅ Disponible' if os.path.exists('logs') else '❌ No disponible'}
- **Carpeta Reportes:** {'✅ Disponible' if os.path.exists('reportes') else '❌ No disponible'}
- **Espacio en Disco:** {status_data.get('disk_space', 'N/A')}

### Memoria y Rendimiento
- **Uso de Memoria:** {status_data.get('memory_usage', 'N/A')}
- **Tiempo de Actividad:** {status_data.get('uptime', 'N/A')}
- **Sesiones Activas:** {status_data.get('active_sessions', 0)}

## Estadísticas de Uso

- **Total de Usuarios:** {status_data.get('total_users', 0)}
- **Interacciones Hoy:** {status_data.get('interactions_today', 0)}
- **Reportes Generados:** {status_data.get('reports_generated', 0)}

## Datos Técnicos

```json
{json.dumps(status_data, indent=2, ensure_ascii=False)}
```

---
*Reporte generado automáticamente por {self.app_config.get_app_name()}*
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    def create_error_report(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> str:
        """
        Crea un reporte de error
        Args:
            error_type: Tipo de error
            error_message: Mensaje de error
            stack_trace: Traza del error
            context: Contexto del error
        Returns:
            Path del archivo de reporte creado
        """
        timestamp = self.generate_timestamp()
        filename = f"error_report_{timestamp}.md"
        filepath = os.path.join(self.reports_dir, filename)

        content = f"""# Reporte de Error

**Fecha y Hora:** {self.generate_readable_timestamp()}
**Tipo de Reporte:** Error del Sistema
**ID de Reporte:** {timestamp}
**Nivel de Severidad:** {'CRÍTICO' if 'critical' in error_type.lower() else 'ERROR'}

## Información del Error

- **Tipo de Error:** {error_type}
- **Mensaje:** {error_message}
- **Aplicación:** {self.app_config.get_app_name()}
- **Entorno:** {self.app_config.get_environment()}

## Stack Trace

```
{stack_trace if stack_trace else 'No disponible'}
```

## Contexto del Error

```json
{json.dumps(context if context else {}, indent=2, ensure_ascii=False)}
```

## Acciones Recomendadas

1. Revisar los logs del sistema
2. Verificar la configuración de la aplicación
3. Comprobar la conectividad de la base de datos
4. Revisar el uso de recursos del sistema

---
*Reporte generado automáticamente por {self.app_config.get_app_name()}*
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    def create_daily_summary_report(
        self,
        summary_data: Dict[str, Any]
    ) -> str:
        """
        Crea un reporte de resumen diario
        Args:
            summary_data: Datos del resumen diario
        Returns:
            Path del archivo de reporte creado
        """
        timestamp = self.generate_timestamp()
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"daily_summary_{date_str}.md"
        filepath = os.path.join(self.reports_dir, filename)

        content = f"""# Resumen Diario - {date_str}

**Fecha y Hora de Generación:** {self.generate_readable_timestamp()}
**Tipo de Reporte:** Resumen Diario
**ID de Reporte:** {timestamp}

## Estadísticas del Día

### Actividad de Usuarios
- **Usuarios Activos:** {summary_data.get('active_users', 0)}
- **Nuevos Usuarios:** {summary_data.get('new_users', 0)}
- **Sesiones Iniciadas:** {summary_data.get('sessions_started', 0)}
- **Tiempo Promedio de Sesión:** {summary_data.get('avg_session_time', 'N/A')}

### Interacciones de Chat
- **Total de Mensajes:** {summary_data.get('total_messages', 0)}
- **Mensajes de Usuario:** {summary_data.get('user_messages', 0)}
- **Respuestas del Agente:** {summary_data.get('agent_responses', 0)}
- **Tiempo Promedio de Respuesta:** {summary_data.get('avg_response_time', 'N/A')}

### Sistema
- **Reportes Generados:** {summary_data.get('reports_generated', 0)}
- **Errores Registrados:** {summary_data.get('errors_logged', 0)}
- **Tiempo de Actividad:** {summary_data.get('system_uptime', 'N/A')}

## Tendencias

- **Hora de Mayor Actividad:** {summary_data.get('peak_hour', 'N/A')}
- **Agente Más Utilizado:** {summary_data.get('most_used_agent', 'N/A')}
- **Tipo de Consulta Más Común:** {summary_data.get('common_query_type', 'N/A')}

## Datos Completos

```json
{json.dumps(summary_data, indent=2, ensure_ascii=False)}
```

---
*Reporte generado automáticamente por {self.app_config.get_app_name()}*
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    def list_reports(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Lista los reportes existentes
        Args:
            limit: Límite de reportes a listar
        Returns:
            Lista de diccionarios con información de reportes
        """
        reports = []

        if not os.path.exists(self.reports_dir):
            return reports

        files = [f for f in os.listdir(self.reports_dir) if f.endswith('.md')]
        files.sort(reverse=True)  # Más recientes primero

        if limit:
            files = files[:limit]

        for filename in files:
            filepath = os.path.join(self.reports_dir, filename)
            try:
                stat = os.stat(filepath)
                reports.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
            except OSError:
                continue

        return reports

    def get_reports_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de todos los reportes
        Returns:
            Diccionario con resumen de reportes
        """
        reports = self.list_reports()

        total_size = sum(r['size'] for r in reports)
        report_types = {}

        for report in reports:
            report_type = report['filename'].split('_')[0]
            report_types[report_type] = report_types.get(report_type, 0) + 1

        return {
            'total_reports': len(reports),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'report_types': report_types,
            'latest_report': reports[0] if reports else None,
            'oldest_report': reports[-1] if reports else None
        }