# Performance Agent
# Agente especializado para análisis y optimización de rendimiento

import os
import time
import psutil
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
import cProfile
import pstats
from io import StringIO
from utils.logger import app_logger

class PerformanceAgent:
    """
    Agente especializado para monitoreo y optimización de rendimiento
    Analiza CPU, memoria, tiempo de respuesta y sugiere optimizaciones
    """

    def __init__(self):
        self.monitoring_active = False
        self.metrics_history = []
        self.performance_data = self.load_performance_data()
        self.thresholds = self.load_thresholds()
        self.profiling_results = {}
        self.ensure_directories()

    def ensure_directories(self):
        """Crear directorios necesarios"""
        os.makedirs("analysis/performance/", exist_ok=True)
        os.makedirs("analysis/performance/profiles/", exist_ok=True)

    def load_performance_data(self) -> Dict[str, Any]:
        """Cargar datos históricos de rendimiento"""
        data_file = "analysis/performance/performance_data.json"
        try:
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            app_logger.error(f"Error cargando datos de rendimiento: {e}")

        return {
            "sessions": [],
            "alerts": [],
            "optimizations": [],
            "benchmarks": {}
        }

    def load_thresholds(self) -> Dict[str, Any]:
        """Cargar umbrales de rendimiento"""
        return {
            "cpu_usage": {
                "warning": 70,  # 70%
                "critical": 90  # 90%
            },
            "memory_usage": {
                "warning": 80,  # 80%
                "critical": 95  # 95%
            },
            "response_time": {
                "warning": 2.0,   # 2 segundos
                "critical": 5.0   # 5 segundos
            },
            "api_latency": {
                "warning": 3.0,   # 3 segundos
                "critical": 10.0  # 10 segundos
            },
            "memory_leak": {
                "growth_rate": 10,  # MB por minuto
                "duration": 5       # minutos consecutivos
            }
        }

    def start_monitoring(self, interval: float = 1.0):
        """Iniciar monitoreo de rendimiento"""
        if self.monitoring_active:
            app_logger.warning("Monitoreo ya está activo")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        app_logger.info("Monitoreo de rendimiento iniciado")

    def stop_monitoring(self):
        """Detener monitoreo de rendimiento"""
        self.monitoring_active = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=2.0)
        app_logger.info("Monitoreo de rendimiento detenido")

    def _monitor_loop(self, interval: float):
        """Loop principal de monitoreo"""
        while self.monitoring_active:
            try:
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)

                # Mantener solo últimos 1000 registros
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]

                # Verificar alertas
                self.check_performance_alerts(metrics)

                time.sleep(interval)

            except Exception as e:
                app_logger.error(f"Error en monitoreo: {e}")
                time.sleep(interval)

    def collect_metrics(self) -> Dict[str, Any]:
        """Recopilar métricas del sistema"""
        try:
            # Información del proceso actual
            process = psutil.Process()

            # Métricas del sistema
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Métricas del proceso
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()

            metrics = {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available": memory.available,
                    "memory_used": memory.used,
                    "disk_percent": disk.percent,
                    "disk_free": disk.free
                },
                "process": {
                    "cpu_percent": process_cpu,
                    "memory_rss": process_memory.rss,
                    "memory_vms": process_memory.vms,
                    "threads": process.num_threads(),
                    "open_files": len(process.open_files()) if hasattr(process, 'open_files') else 0
                }
            }

            return metrics

        except Exception as e:
            app_logger.error(f"Error recopilando métricas: {e}")
            return {"timestamp": datetime.now().isoformat(), "error": str(e)}

    def check_performance_alerts(self, metrics: Dict[str, Any]):
        """Verificar alertas de rendimiento"""
        if "system" not in metrics:
            return

        system = metrics["system"]
        process = metrics.get("process", {})

        alerts = []

        # Alerta de CPU
        if system["cpu_percent"] >= self.thresholds["cpu_usage"]["critical"]:
            alerts.append({
                "type": "CPU_CRITICAL",
                "severity": "CRITICAL",
                "value": system["cpu_percent"],
                "threshold": self.thresholds["cpu_usage"]["critical"],
                "message": f"Uso crítico de CPU: {system['cpu_percent']:.1f}%"
            })
        elif system["cpu_percent"] >= self.thresholds["cpu_usage"]["warning"]:
            alerts.append({
                "type": "CPU_WARNING",
                "severity": "WARNING",
                "value": system["cpu_percent"],
                "threshold": self.thresholds["cpu_usage"]["warning"],
                "message": f"Alto uso de CPU: {system['cpu_percent']:.1f}%"
            })

        # Alerta de memoria
        if system["memory_percent"] >= self.thresholds["memory_usage"]["critical"]:
            alerts.append({
                "type": "MEMORY_CRITICAL",
                "severity": "CRITICAL",
                "value": system["memory_percent"],
                "threshold": self.thresholds["memory_usage"]["critical"],
                "message": f"Uso crítico de memoria: {system['memory_percent']:.1f}%"
            })
        elif system["memory_percent"] >= self.thresholds["memory_usage"]["warning"]:
            alerts.append({
                "type": "MEMORY_WARNING",
                "severity": "WARNING",
                "value": system["memory_percent"],
                "threshold": self.thresholds["memory_usage"]["warning"],
                "message": f"Alto uso de memoria: {system['memory_percent']:.1f}%"
            })

        # Detectar memory leaks
        leak_detected = self.detect_memory_leak()
        if leak_detected:
            alerts.append({
                "type": "MEMORY_LEAK",
                "severity": "HIGH",
                "message": "Posible memory leak detectado",
                "details": leak_detected
            })

        # Registrar alertas
        for alert in alerts:
            alert["timestamp"] = metrics["timestamp"]
            self.performance_data["alerts"].append(alert)
            app_logger.warning(f"ALERTA RENDIMIENTO: {alert['message']}")

    def detect_memory_leak(self) -> Optional[Dict[str, Any]]:
        """Detectar posibles memory leaks"""
        if len(self.metrics_history) < 5:  # Necesitamos al menos 5 mediciones
            return None

        # Analizar últimas 5 mediciones
        recent_metrics = self.metrics_history[-5:]
        memory_values = []

        for metric in recent_metrics:
            if "process" in metric and "memory_rss" in metric["process"]:
                memory_mb = metric["process"]["memory_rss"] / (1024 * 1024)  # Convertir a MB
                memory_values.append(memory_mb)

        if len(memory_values) < 5:
            return None

        # Calcular tendencia
        memory_growth = memory_values[-1] - memory_values[0]
        duration_minutes = 5 * 1.0 / 60  # 5 mediciones * 1 segundo / 60

        growth_rate = memory_growth / duration_minutes  # MB por minuto

        if growth_rate >= self.thresholds["memory_leak"]["growth_rate"]:
            return {
                "growth_rate_mb_per_min": growth_rate,
                "memory_start_mb": memory_values[0],
                "memory_end_mb": memory_values[-1],
                "total_growth_mb": memory_growth
            }

        return None

    def profile_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Perfilar ejecución de una función"""
        profiler = cProfile.Profile()

        start_time = time.time()
        profiler.enable()

        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)

        profiler.disable()
        end_time = time.time()

        # Analizar resultados
        stats_stream = StringIO()
        stats = pstats.Stats(profiler, stream=stats_stream)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 funciones

        profile_data = {
            "function_name": func.__name__,
            "execution_time": end_time - start_time,
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "stats": stats_stream.getvalue(),
            "call_count": stats.total_calls,
            "primitive_calls": stats.prim_calls
        }

        # Guardar perfil
        self.profiling_results[func.__name__] = profile_data

        return profile_data

    def benchmark_api_call(self, provider: str, model: str, call_func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Benchmark de llamada a API"""
        benchmark = {
            "provider": provider,
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "attempts": []
        }

        # Realizar 3 intentos para obtener promedio
        for attempt in range(3):
            start_time = time.time()
            start_metrics = self.collect_metrics()

            try:
                result = call_func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)

            end_time = time.time()
            end_metrics = self.collect_metrics()

            attempt_data = {
                "attempt": attempt + 1,
                "duration": end_time - start_time,
                "success": success,
                "error": error,
                "start_cpu": start_metrics.get("system", {}).get("cpu_percent", 0),
                "end_cpu": end_metrics.get("system", {}).get("cpu_percent", 0),
                "start_memory": start_metrics.get("process", {}).get("memory_rss", 0),
                "end_memory": end_metrics.get("process", {}).get("memory_rss", 0)
            }

            benchmark["attempts"].append(attempt_data)

            # Esperar un poco entre intentos
            if attempt < 2:
                time.sleep(0.5)

        # Calcular estadísticas
        successful_attempts = [a for a in benchmark["attempts"] if a["success"]]
        if successful_attempts:
            durations = [a["duration"] for a in successful_attempts]
            benchmark["statistics"] = {
                "success_rate": len(successful_attempts) / len(benchmark["attempts"]),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "total_attempts": len(benchmark["attempts"]),
                "successful_attempts": len(successful_attempts)
            }
        else:
            benchmark["statistics"] = {
                "success_rate": 0,
                "avg_duration": 0,
                "min_duration": 0,
                "max_duration": 0,
                "total_attempts": len(benchmark["attempts"]),
                "successful_attempts": 0
            }

        # Guardar benchmark
        provider_key = f"{provider}:{model}"
        if provider_key not in self.performance_data["benchmarks"]:
            self.performance_data["benchmarks"][provider_key] = []

        self.performance_data["benchmarks"][provider_key].append(benchmark)

        return benchmark

    def analyze_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Analizar tendencias de rendimiento"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filtrar métricas recientes
        recent_metrics = []
        for metric in self.metrics_history:
            try:
                metric_time = datetime.fromisoformat(metric["timestamp"])
                if metric_time >= cutoff_time:
                    recent_metrics.append(metric)
            except:
                continue

        if not recent_metrics:
            return {"error": "No hay datos suficientes para análisis"}

        # Calcular tendencias
        cpu_values = []
        memory_values = []
        timestamps = []

        for metric in recent_metrics:
            if "system" in metric:
                cpu_values.append(metric["system"]["cpu_percent"])
                memory_values.append(metric["system"]["memory_percent"])
                timestamps.append(metric["timestamp"])

        analysis = {
            "period_hours": hours,
            "data_points": len(recent_metrics),
            "cpu_trend": {
                "avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "min": min(cpu_values) if cpu_values else 0,
                "max": max(cpu_values) if cpu_values else 0,
                "current": cpu_values[-1] if cpu_values else 0
            },
            "memory_trend": {
                "avg": sum(memory_values) / len(memory_values) if memory_values else 0,
                "min": min(memory_values) if memory_values else 0,
                "max": max(memory_values) if memory_values else 0,
                "current": memory_values[-1] if memory_values else 0
            },
            "alerts_count": len([a for a in self.performance_data["alerts"]
                               if datetime.fromisoformat(a["timestamp"]) >= cutoff_time])
        }

        return analysis

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generar recomendaciones de optimización"""
        recommendations = []

        # Analizar tendencias recientes
        trends = self.analyze_performance_trends(2)  # Últimas 2 horas

        if trends.get("cpu_trend", {}).get("avg", 0) > 50:
            recommendations.append({
                "type": "CPU_OPTIMIZATION",
                "priority": "HIGH",
                "title": "Optimizar uso de CPU",
                "description": "El uso promedio de CPU es alto. Considerar optimizaciones.",
                "suggestions": [
                    "Implementar caching para reducir procesamiento",
                    "Optimizar loops y operaciones costosas",
                    "Usar threading para operaciones no bloqueantes",
                    "Considerar lazy loading para datos grandes"
                ]
            })

        if trends.get("memory_trend", {}).get("avg", 0) > 70:
            recommendations.append({
                "type": "MEMORY_OPTIMIZATION",
                "priority": "HIGH",
                "title": "Optimizar uso de memoria",
                "description": "El uso de memoria es elevado. Revisar gestión de recursos.",
                "suggestions": [
                    "Implementar garbage collection manual",
                    "Revisar variables globales y caches",
                    "Usar generators para procesar datos grandes",
                    "Liberar recursos explícitamente"
                ]
            })

        # Analizar benchmarks de API
        slow_apis = []
        for provider_model, benchmarks in self.performance_data["benchmarks"].items():
            if benchmarks:
                latest = benchmarks[-1]
                avg_duration = latest.get("statistics", {}).get("avg_duration", 0)
                if avg_duration > self.thresholds["api_latency"]["warning"]:
                    slow_apis.append((provider_model, avg_duration))

        if slow_apis:
            recommendations.append({
                "type": "API_OPTIMIZATION",
                "priority": "MEDIUM",
                "title": "Optimizar llamadas a API",
                "description": "Algunas APIs tienen latencia alta.",
                "slow_apis": slow_apis,
                "suggestions": [
                    "Implementar timeout más agresivos",
                    "Usar conexiones persistentes",
                    "Implementar retry con backoff",
                    "Considerar APIs más rápidas para tareas simples"
                ]
            })

        # Recomendaciones de profiling
        if self.profiling_results:
            slow_functions = []
            for func_name, profile in self.profiling_results.items():
                if profile["execution_time"] > 1.0:  # Más de 1 segundo
                    slow_functions.append((func_name, profile["execution_time"]))

            if slow_functions:
                recommendations.append({
                    "type": "FUNCTION_OPTIMIZATION",
                    "priority": "MEDIUM",
                    "title": "Optimizar funciones lentas",
                    "description": "Algunas funciones tienen tiempo de ejecución alto.",
                    "slow_functions": slow_functions,
                    "suggestions": [
                        "Perfilar funciones específicas",
                        "Optimizar algoritmos",
                        "Implementar caching",
                        "Paralelizar operaciones cuando sea posible"
                    ]
                })

        return recommendations

    def generate_performance_report(self) -> str:
        """Generar reporte completo de rendimiento"""
        trends = self.analyze_performance_trends(24)
        recommendations = self.get_optimization_recommendations()
        recent_alerts = [a for a in self.performance_data["alerts"][-10:]]

        report = []
        report.append("# REPORTE DE RENDIMIENTO")
        report.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Resumen de tendencias
        report.append("## TENDENCIAS (ÚLTIMAS 24 HORAS)")
        if "error" not in trends:
            report.append(f"- Puntos de datos: {trends['data_points']}")
            report.append(f"- CPU promedio: {trends['cpu_trend']['avg']:.1f}%")
            report.append(f"- CPU máximo: {trends['cpu_trend']['max']:.1f}%")
            report.append(f"- Memoria promedio: {trends['memory_trend']['avg']:.1f}%")
            report.append(f"- Memoria máxima: {trends['memory_trend']['max']:.1f}%")
            report.append(f"- Alertas generadas: {trends['alerts_count']}")
        else:
            report.append("- No hay datos suficientes para generar tendencias")
        report.append("")

        # Alertas recientes
        if recent_alerts:
            report.append("## ALERTAS RECIENTES")
            for alert in recent_alerts:
                report.append(f"- **{alert['type']}** ({alert['severity']}): {alert['message']}")
            report.append("")

        # Benchmarks de API
        if self.performance_data["benchmarks"]:
            report.append("## RENDIMIENTO DE APIs")
            for provider_model, benchmarks in self.performance_data["benchmarks"].items():
                if benchmarks:
                    latest = benchmarks[-1]
                    stats = latest.get("statistics", {})
                    report.append(f"### {provider_model}")
                    report.append(f"- Tiempo promedio: {stats.get('avg_duration', 0):.2f}s")
                    report.append(f"- Tasa de éxito: {stats.get('success_rate', 0)*100:.1f}%")
                    report.append(f"- Rango: {stats.get('min_duration', 0):.2f}s - {stats.get('max_duration', 0):.2f}s")
            report.append("")

        # Recomendaciones
        if recommendations:
            report.append("## RECOMENDACIONES DE OPTIMIZACIÓN")
            for rec in recommendations:
                report.append(f"### {rec['title']} ({rec['priority']})")
                report.append(f"{rec['description']}")
                report.append("**Sugerencias:**")
                for suggestion in rec["suggestions"]:
                    report.append(f"- {suggestion}")
                report.append("")

        return "\n".join(report)

    def save_performance_data(self):
        """Guardar datos de rendimiento"""
        data_file = "analysis/performance/performance_data.json"
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(self.performance_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            app_logger.error(f"Error guardando datos de rendimiento: {e}")

    def cleanup_old_data(self, days: int = 7):
        """Limpiar datos antiguos"""
        cutoff_time = datetime.now() - timedelta(days=days)

        # Limpiar alertas antiguas
        self.performance_data["alerts"] = [
            alert for alert in self.performance_data["alerts"]
            if datetime.fromisoformat(alert["timestamp"]) >= cutoff_time
        ]

        # Limpiar benchmarks antiguos
        for provider_model in self.performance_data["benchmarks"]:
            self.performance_data["benchmarks"][provider_model] = [
                benchmark for benchmark in self.performance_data["benchmarks"][provider_model]
                if datetime.fromisoformat(benchmark["timestamp"]) >= cutoff_time
            ]

        app_logger.info(f"Datos de rendimiento más antiguos que {days} días eliminados")