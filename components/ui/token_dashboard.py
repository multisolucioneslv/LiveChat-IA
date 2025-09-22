# Token Dashboard Component
# Dashboard visual para tracking de tokens con gráficos interactivos

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkinter
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import threading
import time
from agents.specialized.token_tracker_agent import TokenTrackerAgent
from utils.logger import app_logger

class TokenDashboard(ctk.CTkFrame):
    """
    Dashboard visual para monitoreo de tokens con gráficos en tiempo real
    Implementa las mejores prácticas de UI basadas en investigación de mercado
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.token_agent = TokenTrackerAgent()
        self.update_thread = None
        self.is_running = False

        # Configuración de colores (tema moderno)
        self.colors = {
            "primary": "#1976d2",
            "secondary": "#388e3c",
            "warning": "#f57c00",
            "error": "#d32f2f",
            "surface": "#ffffff",
            "background": "#f5f5f5"
        }

        self.setup_ui()
        self.start_real_time_updates()

    def setup_ui(self):
        """Configurar interfaz del dashboard"""
        # Frame principal con padding
        self.main_frame = ctk.CTkFrame(self, corner_radius=12)
        self.main_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # Título del dashboard
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="📊 Dashboard de Tokens",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(16, 8))

        # Frame para estadísticas rápidas
        self.stats_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        self.stats_frame.pack(fill="x", padx=16, pady=8)

        self.create_stats_cards()

        # Notebook para diferentes vistas
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=8)

        # Crear tabs
        self.create_overview_tab()
        self.create_provider_tab()
        self.create_cost_tab()
        self.create_alerts_tab()

        # Frame de controles
        self.controls_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        self.controls_frame.pack(fill="x", padx=16, pady=8)

        self.create_controls()

    def create_stats_cards(self):
        """Crear tarjetas de estadísticas rápidas"""
        # Frame contenedor para las tarjetas
        cards_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=16, pady=16)

        # Configurar grid
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Tarjeta de tokens totales
        self.total_tokens_card = self.create_stat_card(
            cards_frame, "Tokens Totales", "0", self.colors["primary"], 0
        )

        # Tarjeta de costo total
        self.total_cost_card = self.create_stat_card(
            cards_frame, "Costo Total", "$0.00", self.colors["secondary"], 1
        )

        # Tarjeta de sesiones
        self.sessions_card = self.create_stat_card(
            cards_frame, "Sesiones", "0", self.colors["warning"], 2
        )

        # Tarjeta de promedio por sesión
        self.avg_card = self.create_stat_card(
            cards_frame, "Promedio/Sesión", "0", self.colors["error"], 3
        )

    def create_stat_card(self, parent, title: str, value: str, color: str, column: int):
        """Crear una tarjeta de estadística"""
        card = ctk.CTkFrame(parent, corner_radius=8)
        card.grid(row=0, column=column, padx=8, pady=8, sticky="ew")

        # Título de la tarjeta
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        )
        title_label.pack(pady=(12, 4))

        # Valor de la tarjeta
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=color
        )
        value_label.pack(pady=(0, 12))

        return {"card": card, "title": title_label, "value": value_label}

    def create_overview_tab(self):
        """Crear tab de resumen general"""
        overview_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(overview_frame, text="📈 Resumen")

        # Frame para gráficos
        charts_frame = ctk.CTkFrame(overview_frame, corner_radius=8)
        charts_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # Crear figura de matplotlib
        self.overview_fig = Figure(figsize=(12, 8), facecolor='white')
        self.overview_canvas = FigureCanvasTkinter(self.overview_fig, charts_frame)
        self.overview_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        # Crear subplots
        self.daily_tokens_ax = self.overview_fig.add_subplot(2, 2, 1)
        self.daily_cost_ax = self.overview_fig.add_subplot(2, 2, 2)
        self.provider_pie_ax = self.overview_fig.add_subplot(2, 2, 3)
        self.efficiency_ax = self.overview_fig.add_subplot(2, 2, 4)

        self.overview_fig.tight_layout(pad=3.0)

    def create_provider_tab(self):
        """Crear tab de comparación por proveedor"""
        provider_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(provider_frame, text="🏢 Proveedores")

        # Frame para gráfico de proveedores
        provider_chart_frame = ctk.CTkFrame(provider_frame, corner_radius=8)
        provider_chart_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # Figura para comparación de proveedores
        self.provider_fig = Figure(figsize=(12, 6), facecolor='white')
        self.provider_canvas = FigureCanvasTkinter(self.provider_fig, provider_chart_frame)
        self.provider_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        # Crear subplots para proveedores
        self.provider_tokens_ax = self.provider_fig.add_subplot(1, 2, 1)
        self.provider_cost_ax = self.provider_fig.add_subplot(1, 2, 2)

        self.provider_fig.tight_layout(pad=3.0)

        # Frame para tabla de detalles
        self.create_provider_table(provider_frame)

    def create_cost_tab(self):
        """Crear tab de análisis de costos"""
        cost_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(cost_frame, text="💰 Costos")

        # Frame para análisis de costos
        cost_analysis_frame = ctk.CTkFrame(cost_frame, corner_radius=8)
        cost_analysis_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # Figura para análisis de costos
        self.cost_fig = Figure(figsize=(12, 8), facecolor='white')
        self.cost_canvas = FigureCanvasTkinter(self.cost_fig, cost_analysis_frame)
        self.cost_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        # Subplots para costos
        self.cost_trend_ax = self.cost_fig.add_subplot(2, 2, 1)
        self.cost_breakdown_ax = self.cost_fig.add_subplot(2, 2, 2)
        self.efficiency_comparison_ax = self.cost_fig.add_subplot(2, 2, 3)
        self.projection_ax = self.cost_fig.add_subplot(2, 2, 4)

        self.cost_fig.tight_layout(pad=3.0)

    def create_alerts_tab(self):
        """Crear tab de alertas y recomendaciones"""
        alerts_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(alerts_frame, text="⚠️ Alertas")

        # Frame para alertas
        alerts_container = ctk.CTkFrame(alerts_frame, corner_radius=8)
        alerts_container.pack(fill="both", expand=True, padx=16, pady=16)

        # Título de alertas
        alerts_title = ctk.CTkLabel(
            alerts_container,
            text="🚨 Alertas Activas",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        alerts_title.pack(pady=(16, 8))

        # Frame scrollable para alertas
        self.alerts_scroll = ctk.CTkScrollableFrame(alerts_container, height=200)
        self.alerts_scroll.pack(fill="both", expand=True, padx=16, pady=8)

        # Frame para recomendaciones
        recommendations_container = ctk.CTkFrame(alerts_frame, corner_radius=8)
        recommendations_container.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        # Título de recomendaciones
        rec_title = ctk.CTkLabel(
            recommendations_container,
            text="💡 Recomendaciones de Optimización",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        rec_title.pack(pady=(16, 8))

        # Frame scrollable para recomendaciones
        self.recommendations_scroll = ctk.CTkScrollableFrame(recommendations_container, height=200)
        self.recommendations_scroll.pack(fill="both", expand=True, padx=16, pady=8)

    def create_provider_table(self, parent):
        """Crear tabla de detalles por proveedor"""
        table_frame = ctk.CTkFrame(parent, corner_radius=8)
        table_frame.pack(fill="x", padx=16, pady=(8, 16))

        # Título de la tabla
        table_title = ctk.CTkLabel(
            table_frame,
            text="📋 Detalles por Proveedor",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        table_title.pack(pady=(12, 8))

        # Crear Treeview para la tabla
        columns = ("Proveedor", "Tokens", "Costo", "Sesiones", "Eficiencia")
        self.provider_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)

        # Configurar columnas
        for col in columns:
            self.provider_tree.heading(col, text=col)
            self.provider_tree.column(col, width=120, anchor="center")

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.provider_tree.yview)
        self.provider_tree.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.provider_tree.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)
        scrollbar.pack(side="right", fill="y", pady=12)

    def create_controls(self):
        """Crear controles del dashboard"""
        # Botón de exportar reporte
        self.export_btn = ctk.CTkButton(
            self.controls_frame,
            text="📄 Exportar Reporte",
            command=self.export_report,
            width=160
        )
        self.export_btn.pack(side="left", padx=(16, 8), pady=12)

        # Botón de limpiar datos
        self.clear_btn = ctk.CTkButton(
            self.controls_frame,
            text="🗑️ Limpiar Datos",
            command=self.clear_data,
            width=140,
            fg_color="gray"
        )
        self.clear_btn.pack(side="left", padx=8, pady=12)

        # Selector de período
        period_label = ctk.CTkLabel(self.controls_frame, text="Período:")
        period_label.pack(side="left", padx=(24, 8), pady=12)

        self.period_selector = ctk.CTkOptionMenu(
            self.controls_frame,
            values=["Últimas 24h", "Últimos 7 días", "Último mes", "Todo el tiempo"],
            command=self.on_period_changed
        )
        self.period_selector.pack(side="left", padx=8, pady=12)

        # Indicador de actualización en tiempo real
        self.status_label = ctk.CTkLabel(
            self.controls_frame,
            text="🟢 Actualización en tiempo real",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="right", padx=16, pady=12)

    def start_real_time_updates(self):
        """Iniciar actualizaciones en tiempo real"""
        if not self.is_running:
            self.is_running = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()

    def stop_real_time_updates(self):
        """Detener actualizaciones en tiempo real"""
        self.is_running = False

    def _update_loop(self):
        """Loop de actualización en tiempo real"""
        while self.is_running:
            try:
                self.after(0, self.update_all_charts)
                time.sleep(5)  # Actualizar cada 5 segundos
            except Exception as e:
                app_logger.error(f"Error en update loop: {e}")
                time.sleep(10)

    def update_all_charts(self):
        """Actualizar todos los gráficos"""
        try:
            self.update_stats_cards()
            self.update_overview_charts()
            self.update_provider_charts()
            self.update_cost_charts()
            self.update_alerts()
        except Exception as e:
            app_logger.error(f"Error actualizando charts: {e}")

    def update_stats_cards(self):
        """Actualizar tarjetas de estadísticas"""
        try:
            # Obtener datos actualizados
            total_tokens = self.token_agent.usage_data.get("total_tokens", 0)
            total_cost = self.token_agent.usage_data.get("total_cost", 0.0)
            sessions_count = len(self.token_agent.usage_data.get("sessions", []))

            avg_tokens = total_tokens / max(sessions_count, 1)

            # Actualizar valores
            self.total_tokens_card["value"].configure(text=f"{total_tokens:,}")
            self.total_cost_card["value"].configure(text=f"${total_cost:.2f}")
            self.sessions_card["value"].configure(text=str(sessions_count))
            self.avg_card["value"].configure(text=f"{avg_tokens:.0f}")

        except Exception as e:
            app_logger.error(f"Error actualizando stats cards: {e}")

    def update_overview_charts(self):
        """Actualizar gráficos del tab de resumen"""
        try:
            # Limpiar axes
            self.daily_tokens_ax.clear()
            self.daily_cost_ax.clear()
            self.provider_pie_ax.clear()
            self.efficiency_ax.clear()

            # Gráfico de tokens diarios
            daily_stats = self.token_agent.get_daily_stats(7)["daily_stats"]
            if daily_stats:
                dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in daily_stats]
                tokens = [d["tokens"] for d in daily_stats]

                self.daily_tokens_ax.plot(dates, tokens, marker='o', linewidth=2, color=self.colors["primary"])
                self.daily_tokens_ax.set_title("Tokens por Día", fontweight='bold')
                self.daily_tokens_ax.set_ylabel("Tokens")
                self.daily_tokens_ax.tick_params(axis='x', rotation=45)

            # Gráfico de costos diarios
            if daily_stats:
                costs = [d["cost"] for d in daily_stats]
                self.daily_cost_ax.plot(dates, costs, marker='s', linewidth=2, color=self.colors["secondary"])
                self.daily_cost_ax.set_title("Costo por Día", fontweight='bold')
                self.daily_cost_ax.set_ylabel("Costo (USD)")
                self.daily_cost_ax.tick_params(axis='x', rotation=45)

            # Gráfico circular de proveedores
            provider_stats = self.token_agent.usage_data.get("provider_stats", {})
            if provider_stats:
                providers = list(provider_stats.keys())
                tokens = [provider_stats[p]["tokens"] for p in providers]

                self.provider_pie_ax.pie(tokens, labels=providers, autopct='%1.1f%%', startangle=90)
                self.provider_pie_ax.set_title("Distribución por Proveedor", fontweight='bold')

            # Gráfico de eficiencia
            efficiency_data = self.token_agent.get_efficiency_analysis()["models"]
            if efficiency_data:
                models = [f"{m['provider']}\n{m['model']}" for m in efficiency_data[:5]]
                efficiency = [m["efficiency_score"] for m in efficiency_data[:5]]

                bars = self.efficiency_ax.bar(models, efficiency, color=self.colors["warning"], alpha=0.7)
                self.efficiency_ax.set_title("Eficiencia por Modelo", fontweight='bold')
                self.efficiency_ax.set_ylabel("Tokens/USD")
                self.efficiency_ax.tick_params(axis='x', rotation=45)

            self.overview_fig.tight_layout()
            self.overview_canvas.draw()

        except Exception as e:
            app_logger.error(f"Error actualizando overview charts: {e}")

    def update_provider_charts(self):
        """Actualizar gráficos del tab de proveedores"""
        try:
            # Limpiar axes
            self.provider_tokens_ax.clear()
            self.provider_cost_ax.clear()

            # Obtener datos de comparación
            comparison = self.token_agent.get_provider_comparison()["providers"]

            if comparison:
                providers = [p["provider"] for p in comparison]
                tokens = [p["tokens"] for p in comparison]
                costs = [p["cost"] for p in comparison]

                # Gráfico de tokens por proveedor
                bars1 = self.provider_tokens_ax.bar(providers, tokens, color=self.colors["primary"], alpha=0.7)
                self.provider_tokens_ax.set_title("Tokens por Proveedor", fontweight='bold')
                self.provider_tokens_ax.set_ylabel("Tokens")

                # Gráfico de costos por proveedor
                bars2 = self.provider_cost_ax.bar(providers, costs, color=self.colors["error"], alpha=0.7)
                self.provider_cost_ax.set_title("Costo por Proveedor", fontweight='bold')
                self.provider_cost_ax.set_ylabel("Costo (USD)")

                # Actualizar tabla
                self.update_provider_table(comparison)

            self.provider_fig.tight_layout()
            self.provider_canvas.draw()

        except Exception as e:
            app_logger.error(f"Error actualizando provider charts: {e}")

    def update_provider_table(self, comparison_data):
        """Actualizar tabla de proveedores"""
        try:
            # Limpiar tabla
            for item in self.provider_tree.get_children():
                self.provider_tree.delete(item)

            # Agregar datos
            for provider_data in comparison_data:
                efficiency = f"{provider_data['avg_cost_per_token']:.6f}"
                self.provider_tree.insert("", "end", values=(
                    provider_data["provider"],
                    f"{provider_data['tokens']:,}",
                    f"${provider_data['cost']:.2f}",
                    str(provider_data["sessions"]),
                    efficiency
                ))

        except Exception as e:
            app_logger.error(f"Error actualizando tabla de proveedores: {e}")

    def update_cost_charts(self):
        """Actualizar gráficos del tab de costos"""
        try:
            # Limpiar axes
            self.cost_trend_ax.clear()
            self.cost_breakdown_ax.clear()
            self.efficiency_comparison_ax.clear()
            self.projection_ax.clear()

            # Tendencia de costos
            daily_stats = self.token_agent.get_daily_stats(14)["daily_stats"]
            if daily_stats:
                dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in daily_stats]
                costs = [d["cost"] for d in daily_stats]

                self.cost_trend_ax.plot(dates, costs, marker='o', linewidth=2, color=self.colors["secondary"])
                self.cost_trend_ax.set_title("Tendencia de Costos (14 días)", fontweight='bold')
                self.cost_trend_ax.set_ylabel("Costo (USD)")
                self.cost_trend_ax.tick_params(axis='x', rotation=45)

            # Breakdown de costos por proveedor
            provider_stats = self.token_agent.usage_data.get("provider_stats", {})
            if provider_stats:
                providers = list(provider_stats.keys())
                costs = [provider_stats[p]["cost"] for p in providers]

                self.cost_breakdown_ax.pie(costs, labels=providers, autopct='%1.1f%%', startangle=90)
                self.cost_breakdown_ax.set_title("Distribución de Costos", fontweight='bold')

            # Comparación de eficiencia
            efficiency_data = self.token_agent.get_efficiency_analysis()["models"]
            if efficiency_data:
                models = [f"{m['provider']}" for m in efficiency_data[:5]]
                costs_per_session = [m["avg_cost_per_session"] for m in efficiency_data[:5]]

                bars = self.efficiency_comparison_ax.bar(models, costs_per_session, color=self.colors["warning"], alpha=0.7)
                self.efficiency_comparison_ax.set_title("Costo Promedio por Sesión", fontweight='bold')
                self.efficiency_comparison_ax.set_ylabel("Costo (USD)")

            # Proyección simple (últimos 7 días)
            if len(daily_stats) >= 7:
                recent_costs = [d["cost"] for d in daily_stats[-7:]]
                avg_daily_cost = sum(recent_costs) / len(recent_costs)

                # Proyección para próximos 7 días
                future_dates = [datetime.now() + timedelta(days=i) for i in range(1, 8)]
                projected_costs = [avg_daily_cost] * 7

                self.projection_ax.plot(future_dates, projected_costs, '--', marker='o',
                                      color=self.colors["error"], alpha=0.7, label="Proyección")
                self.projection_ax.set_title("Proyección de Costos (7 días)", fontweight='bold')
                self.projection_ax.set_ylabel("Costo (USD)")
                self.projection_ax.legend()
                self.projection_ax.tick_params(axis='x', rotation=45)

            self.cost_fig.tight_layout()
            self.cost_canvas.draw()

        except Exception as e:
            app_logger.error(f"Error actualizando cost charts: {e}")

    def update_alerts(self):
        """Actualizar alertas y recomendaciones"""
        try:
            # Limpiar alertas existentes
            for widget in self.alerts_scroll.winfo_children():
                widget.destroy()

            # Limpiar recomendaciones existentes
            for widget in self.recommendations_scroll.winfo_children():
                widget.destroy()

            # Obtener recomendaciones del token agent
            recommendations = self.token_agent.optimize_recommendations()

            # Mostrar alertas (simular algunas alertas basadas en uso)
            today = datetime.now().strftime("%Y-%m-%d")
            daily_data = self.token_agent.usage_data.get("daily_stats", {}).get(today, {})

            if daily_data.get("cost", 0) > 5.0:  # Si gasta más de $5 al día
                alert_frame = ctk.CTkFrame(self.alerts_scroll, fg_color=self.colors["error"])
                alert_frame.pack(fill="x", padx=8, pady=4)

                alert_label = ctk.CTkLabel(
                    alert_frame,
                    text=f"⚠️ Alto gasto diario: ${daily_data.get('cost', 0):.2f}",
                    text_color="white",
                    font=ctk.CTkFont(weight="bold")
                )
                alert_label.pack(pady=8)

            # Mostrar recomendaciones
            for rec in recommendations:
                rec_frame = ctk.CTkFrame(self.recommendations_scroll, corner_radius=8)
                rec_frame.pack(fill="x", padx=8, pady=4)

                # Título de la recomendación
                rec_title = ctk.CTkLabel(
                    rec_frame,
                    text=f"💡 {rec['title']}",
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                rec_title.pack(anchor="w", padx=12, pady=(8, 4))

                # Descripción
                rec_desc = ctk.CTkLabel(
                    rec_frame,
                    text=rec["description"],
                    font=ctk.CTkFont(size=12),
                    wraplength=400
                )
                rec_desc.pack(anchor="w", padx=12, pady=(0, 8))

        except Exception as e:
            app_logger.error(f"Error actualizando alertas: {e}")

    def on_period_changed(self, value):
        """Manejar cambio de período"""
        # TODO: Implementar filtrado por período
        app_logger.info(f"Período cambiado a: {value}")
        self.update_all_charts()

    def export_report(self):
        """Exportar reporte de tokens"""
        try:
            report = self.token_agent.generate_report()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reportes/token_report_{timestamp}.md"

            import os
            os.makedirs("reportes", exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)

            app_logger.info(f"Reporte exportado: {filename}")

            # Mostrar confirmación
            self.status_label.configure(text=f"✅ Reporte exportado: {filename}")
            self.after(3000, lambda: self.status_label.configure(text="🟢 Actualización en tiempo real"))

        except Exception as e:
            app_logger.error(f"Error exportando reporte: {e}")
            self.status_label.configure(text="❌ Error exportando reporte")

    def clear_data(self):
        """Limpiar datos de tokens"""
        try:
            # Reinicializar datos del token agent
            self.token_agent.usage_data = {
                "sessions": [],
                "daily_stats": {},
                "provider_stats": {},
                "model_stats": {},
                "total_tokens": 0,
                "total_cost": 0.0
            }
            self.token_agent.save_data()

            # Actualizar dashboard
            self.update_all_charts()

            app_logger.info("Datos de tokens limpiados")
            self.status_label.configure(text="✅ Datos limpiados")
            self.after(3000, lambda: self.status_label.configure(text="🟢 Actualización en tiempo real"))

        except Exception as e:
            app_logger.error(f"Error limpiando datos: {e}")
            self.status_label.configure(text="❌ Error limpiando datos")

    def destroy(self):
        """Limpiar recursos al cerrar"""
        self.stop_real_time_updates()
        super().destroy()