# Token Tracker Agent
# Agente especializado para rastreo y análisis de consumo de tokens

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkinter
import numpy as np
from utils.logger import app_logger

class TokenTrackerAgent:
    """
    Agente especializado para tracking y análisis de tokens
    Genera estadísticas, gráficos y alertas de consumo
    """

    def __init__(self):
        self.data_file = "data/token_usage.json"
        self.config_file = "data/token_config.json"
        self.usage_data = self.load_usage_data()
        self.config = self.load_config()
        self.ensure_directories()

        # Configuración por defecto de costos (USD por 1K tokens)
        self.default_costs = {
            'openai': {
                'gpt-4': {'input': 0.03, 'output': 0.06},
                'gpt-3.5-turbo': {'input': 0.001, 'output': 0.002},
                'gpt-4-turbo': {'input': 0.01, 'output': 0.03}
            },
            'anthropic': {
                'claude-3-opus': {'input': 0.015, 'output': 0.075},
                'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
                'claude-3-haiku': {'input': 0.00025, 'output': 0.00125}
            },
            'google': {
                'gemini-pro': {'input': 0.0005, 'output': 0.0015},
                'gemini-pro-vision': {'input': 0.0005, 'output': 0.0015}
            },
            'groq': {
                'llama-3.1-70b': {'input': 0.0005, 'output': 0.0008},
                'mixtral-8x7b': {'input': 0.0002, 'output': 0.0002}
            },
            'ollama': {
                'llama3.1': {'input': 0.0, 'output': 0.0},  # Local = gratis
                'codellama': {'input': 0.0, 'output': 0.0}
            }
        }

    def ensure_directories(self):
        """Crear directorios necesarios"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

    def load_usage_data(self) -> Dict[str, Any]:
        """Cargar datos de uso de tokens"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {
                "sessions": [],
                "daily_stats": {},
                "provider_stats": {},
                "model_stats": {},
                "total_tokens": 0,
                "total_cost": 0.0
            }
        except Exception as e:
            app_logger.error(f"Error cargando datos de tokens: {e}")
            return {"sessions": [], "daily_stats": {}, "provider_stats": {}, "model_stats": {}, "total_tokens": 0, "total_cost": 0.0}

    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración de alertas y límites"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {
                "daily_limit": 100000,  # tokens por día
                "cost_limit": 10.0,     # USD por día
                "alert_threshold": 0.8,  # 80% del límite
                "auto_optimize": True
            }
        except Exception as e:
            app_logger.error(f"Error cargando configuración: {e}")
            return {"daily_limit": 100000, "cost_limit": 10.0, "alert_threshold": 0.8, "auto_optimize": True}

    def save_data(self):
        """Guardar datos de uso"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            app_logger.error(f"Error guardando datos de tokens: {e}")

    def record_usage(self, provider: str, model: str, input_tokens: int, output_tokens: int, session_id: str = None):
        """Registrar uso de tokens"""
        timestamp = datetime.now().isoformat()
        today = datetime.now().strftime("%Y-%m-%d")

        # Calcular costo
        cost = self.calculate_cost(provider, model, input_tokens, output_tokens)

        # Registrar sesión
        session_data = {
            "timestamp": timestamp,
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": cost,
            "session_id": session_id
        }

        self.usage_data["sessions"].append(session_data)

        # Actualizar estadísticas diarias
        if today not in self.usage_data["daily_stats"]:
            self.usage_data["daily_stats"][today] = {
                "tokens": 0,
                "cost": 0.0,
                "sessions": 0
            }

        self.usage_data["daily_stats"][today]["tokens"] += input_tokens + output_tokens
        self.usage_data["daily_stats"][today]["cost"] += cost
        self.usage_data["daily_stats"][today]["sessions"] += 1

        # Actualizar estadísticas por proveedor
        if provider not in self.usage_data["provider_stats"]:
            self.usage_data["provider_stats"][provider] = {
                "tokens": 0,
                "cost": 0.0,
                "sessions": 0
            }

        self.usage_data["provider_stats"][provider]["tokens"] += input_tokens + output_tokens
        self.usage_data["provider_stats"][provider]["cost"] += cost
        self.usage_data["provider_stats"][provider]["sessions"] += 1

        # Actualizar estadísticas por modelo
        model_key = f"{provider}:{model}"
        if model_key not in self.usage_data["model_stats"]:
            self.usage_data["model_stats"][model_key] = {
                "tokens": 0,
                "cost": 0.0,
                "sessions": 0
            }

        self.usage_data["model_stats"][model_key]["tokens"] += input_tokens + output_tokens
        self.usage_data["model_stats"][model_key]["cost"] += cost
        self.usage_data["model_stats"][model_key]["sessions"] += 1

        # Actualizar totales
        self.usage_data["total_tokens"] += input_tokens + output_tokens
        self.usage_data["total_cost"] += cost

        self.save_data()

        # Verificar alertas
        self.check_alerts(today)

        app_logger.info(f"Token usage recorded: {provider}:{model} - {input_tokens + output_tokens} tokens, ${cost:.4f}")

    def calculate_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calcular costo basado en tokens"""
        try:
            if provider in self.default_costs and model in self.default_costs[provider]:
                rates = self.default_costs[provider][model]
                input_cost = (input_tokens / 1000) * rates['input']
                output_cost = (output_tokens / 1000) * rates['output']
                return input_cost + output_cost
            return 0.0  # Modelo desconocido o gratuito
        except Exception as e:
            app_logger.error(f"Error calculando costo: {e}")
            return 0.0

    def check_alerts(self, today: str):
        """Verificar y generar alertas"""
        if today not in self.usage_data["daily_stats"]:
            return

        daily_data = self.usage_data["daily_stats"][today]
        token_usage = daily_data["tokens"]
        cost_usage = daily_data["cost"]

        # Alerta de tokens
        if token_usage >= self.config["daily_limit"] * self.config["alert_threshold"]:
            percentage = (token_usage / self.config["daily_limit"]) * 100
            app_logger.warning(f"ALERTA TOKENS: {percentage:.1f}% del límite diario alcanzado ({token_usage:,} tokens)")

        # Alerta de costo
        if cost_usage >= self.config["cost_limit"] * self.config["alert_threshold"]:
            percentage = (cost_usage / self.config["cost_limit"]) * 100
            app_logger.warning(f"ALERTA COSTO: {percentage:.1f}% del límite diario alcanzado (${cost_usage:.2f})")

    def get_daily_stats(self, days: int = 7) -> Dict[str, Any]:
        """Obtener estadísticas de los últimos días"""
        stats = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if date in self.usage_data["daily_stats"]:
                day_data = self.usage_data["daily_stats"][date].copy()
                day_data["date"] = date
                stats.append(day_data)
            else:
                stats.append({
                    "date": date,
                    "tokens": 0,
                    "cost": 0.0,
                    "sessions": 0
                })

        return {"daily_stats": sorted(stats, key=lambda x: x["date"])}

    def get_provider_comparison(self) -> Dict[str, Any]:
        """Comparar uso por proveedor"""
        providers = []
        for provider, stats in self.usage_data["provider_stats"].items():
            avg_cost_per_token = stats["cost"] / max(stats["tokens"], 1)
            providers.append({
                "provider": provider,
                "tokens": stats["tokens"],
                "cost": stats["cost"],
                "sessions": stats["sessions"],
                "avg_cost_per_token": avg_cost_per_token
            })

        return {"providers": sorted(providers, key=lambda x: x["cost"], reverse=True)}

    def get_efficiency_analysis(self) -> Dict[str, Any]:
        """Análisis de eficiencia por modelo"""
        models = []
        for model_key, stats in self.usage_data["model_stats"].items():
            provider, model = model_key.split(":", 1)
            avg_tokens_per_session = stats["tokens"] / max(stats["sessions"], 1)
            avg_cost_per_session = stats["cost"] / max(stats["sessions"], 1)

            models.append({
                "provider": provider,
                "model": model,
                "total_tokens": stats["tokens"],
                "total_cost": stats["cost"],
                "sessions": stats["sessions"],
                "avg_tokens_per_session": avg_tokens_per_session,
                "avg_cost_per_session": avg_cost_per_session,
                "efficiency_score": stats["tokens"] / max(stats["cost"], 0.001)  # tokens por dólar
            })

        return {"models": sorted(models, key=lambda x: x["efficiency_score"], reverse=True)}

    def create_usage_chart(self, chart_type: str = "daily", days: int = 7) -> plt.Figure:
        """Crear gráfico de uso"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        if chart_type == "daily":
            daily_stats = self.get_daily_stats(days)["daily_stats"]
            dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in daily_stats]
            tokens = [d["tokens"] for d in daily_stats]
            costs = [d["cost"] for d in daily_stats]

            # Gráfico de tokens
            ax1.plot(dates, tokens, marker='o', linewidth=2, markersize=6)
            ax1.set_title("Uso Diario de Tokens", fontsize=14, fontweight='bold')
            ax1.set_ylabel("Tokens", fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

            # Gráfico de costos
            ax2.plot(dates, costs, marker='s', color='red', linewidth=2, markersize=6)
            ax2.set_title("Costo Diario", fontsize=14, fontweight='bold')
            ax2.set_ylabel("Costo (USD)", fontsize=12)
            ax2.set_xlabel("Fecha", fontsize=12)
            ax2.grid(True, alpha=0.3)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

        elif chart_type == "provider":
            comparison = self.get_provider_comparison()["providers"]
            providers = [p["provider"] for p in comparison]
            tokens = [p["tokens"] for p in comparison]
            costs = [p["cost"] for p in comparison]

            # Gráfico de barras para tokens
            bars1 = ax1.bar(providers, tokens, alpha=0.7)
            ax1.set_title("Tokens por Proveedor", fontsize=14, fontweight='bold')
            ax1.set_ylabel("Tokens", fontsize=12)
            ax1.tick_params(axis='x', rotation=45)

            # Gráfico de barras para costos
            bars2 = ax2.bar(providers, costs, color='red', alpha=0.7)
            ax2.set_title("Costo por Proveedor", fontsize=14, fontweight='bold')
            ax2.set_ylabel("Costo (USD)", fontsize=12)
            ax2.set_xlabel("Proveedor", fontsize=12)
            ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        return fig

    def generate_report(self) -> str:
        """Generar reporte completo de uso"""
        report = []
        report.append("# REPORTE DE USO DE TOKENS")
        report.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Resumen general
        report.append("## RESUMEN GENERAL")
        report.append(f"- Total de tokens consumidos: {self.usage_data['total_tokens']:,}")
        report.append(f"- Costo total: ${self.usage_data['total_cost']:.2f}")
        report.append(f"- Sesiones totales: {len(self.usage_data['sessions'])}")
        report.append("")

        # Estadísticas por proveedor
        report.append("## USO POR PROVEEDOR")
        comparison = self.get_provider_comparison()["providers"]
        for provider in comparison:
            report.append(f"### {provider['provider'].upper()}")
            report.append(f"- Tokens: {provider['tokens']:,}")
            report.append(f"- Costo: ${provider['cost']:.2f}")
            report.append(f"- Sesiones: {provider['sessions']}")
            report.append(f"- Costo promedio por token: ${provider['avg_cost_per_token']:.6f}")
            report.append("")

        # Análisis de eficiencia
        report.append("## ANÁLISIS DE EFICIENCIA")
        efficiency = self.get_efficiency_analysis()["models"]
        for model in efficiency[:5]:  # Top 5 más eficientes
            report.append(f"### {model['provider']}:{model['model']}")
            report.append(f"- Tokens por sesión: {model['avg_tokens_per_session']:.0f}")
            report.append(f"- Costo por sesión: ${model['avg_cost_per_session']:.3f}")
            report.append(f"- Eficiencia: {model['efficiency_score']:.0f} tokens/USD")
            report.append("")

        # Estadísticas de los últimos 7 días
        report.append("## ÚLTIMOS 7 DÍAS")
        daily_stats = self.get_daily_stats(7)["daily_stats"]
        for day in daily_stats:
            if day["tokens"] > 0:
                report.append(f"- {day['date']}: {day['tokens']:,} tokens, ${day['cost']:.2f}, {day['sessions']} sesiones")

        return "\n".join(report)

    def optimize_recommendations(self) -> List[Dict[str, Any]]:
        """Generar recomendaciones de optimización"""
        recommendations = []

        # Análisis de eficiencia
        efficiency = self.get_efficiency_analysis()["models"]
        if efficiency:
            most_efficient = efficiency[0]
            least_efficient = efficiency[-1] if len(efficiency) > 1 else None

            recommendations.append({
                "type": "EFFICIENCY",
                "priority": "HIGH",
                "title": "Modelo más eficiente",
                "description": f"Considera usar más {most_efficient['provider']}:{most_efficient['model']} - {most_efficient['efficiency_score']:.0f} tokens/USD"
            })

            if least_efficient and least_efficient['efficiency_score'] < most_efficient['efficiency_score'] * 0.5:
                recommendations.append({
                    "type": "COST_OPTIMIZATION",
                    "priority": "MEDIUM",
                    "title": "Modelo costoso",
                    "description": f"Reduce el uso de {least_efficient['provider']}:{least_efficient['model']} - Solo {least_efficient['efficiency_score']:.0f} tokens/USD"
                })

        # Análisis de uso diario
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.usage_data["daily_stats"]:
            daily_data = self.usage_data["daily_stats"][today]
            if daily_data["cost"] > self.config["cost_limit"] * 0.5:
                recommendations.append({
                    "type": "BUDGET_ALERT",
                    "priority": "HIGH",
                    "title": "Alto consumo diario",
                    "description": f"Has gastado ${daily_data['cost']:.2f} hoy. Considera modelos más económicos."
                })

        return recommendations