# UI Design Agent
# Agente especializado para mejoras de interfaz de usuario

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import tkinter as tk
import customtkinter as ctk
from utils.logger import app_logger

class UIDesignAgent:
    """
    Agente especializado para análisis y mejoras de UI/UX
    Basado en investigación de mercado y mejores prácticas
    """

    def __init__(self):
        self.design_config = self.load_design_config()
        self.market_insights = self.load_market_insights()
        self.ui_components = {}
        self.ensure_directories()

    def ensure_directories(self):
        """Crear directorios necesarios"""
        os.makedirs("analysis/ui_design/", exist_ok=True)
        os.makedirs("components/ui/themes/", exist_ok=True)

    def load_design_config(self) -> Dict[str, Any]:
        """Cargar configuración de diseño"""
        config_file = "components/ui/design_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            app_logger.error(f"Error cargando configuración de diseño: {e}")

        # Configuración por defecto basada en investigación de mercado
        return {
            "themes": {
                "modern_dark": {
                    "name": "Modern Dark",
                    "primary_color": "#2b2b2b",
                    "secondary_color": "#3c3c3c",
                    "accent_color": "#007acc",
                    "text_color": "#ffffff",
                    "text_secondary": "#b0b0b0",
                    "success_color": "#4caf50",
                    "warning_color": "#ff9800",
                    "error_color": "#f44336",
                    "background": "#1a1a1a",
                    "surface": "#2b2b2b",
                    "border": "#404040"
                },
                "light_modern": {
                    "name": "Light Modern",
                    "primary_color": "#ffffff",
                    "secondary_color": "#f5f5f5",
                    "accent_color": "#2196f3",
                    "text_color": "#212121",
                    "text_secondary": "#757575",
                    "success_color": "#4caf50",
                    "warning_color": "#ff9800",
                    "error_color": "#f44336",
                    "background": "#fafafa",
                    "surface": "#ffffff",
                    "border": "#e0e0e0"
                },
                "claude_inspired": {
                    "name": "Claude Inspired",
                    "primary_color": "#2d3748",
                    "secondary_color": "#4a5568",
                    "accent_color": "#ff6b35",
                    "text_color": "#1a202c",
                    "text_secondary": "#718096",
                    "success_color": "#38a169",
                    "warning_color": "#d69e2e",
                    "error_color": "#e53e3e",
                    "background": "#f7fafc",
                    "surface": "#ffffff",
                    "border": "#e2e8f0"
                }
            },
            "layout": {
                "sidebar_width": 280,
                "header_height": 60,
                "footer_height": 40,
                "padding": 16,
                "border_radius": 8,
                "font_family": "Segoe UI",
                "font_sizes": {
                    "small": 11,
                    "normal": 13,
                    "large": 16,
                    "title": 20
                }
            },
            "animations": {
                "enabled": True,
                "duration": 200,
                "easing": "ease-in-out"
            },
            "features": {
                "model_comparison": True,
                "token_visualization": True,
                "conversation_export": True,
                "custom_prompts": True,
                "dark_mode_toggle": True
            }
        }

    def load_market_insights(self) -> Dict[str, Any]:
        """Cargar insights de investigación de mercado"""
        return {
            "top_features": [
                {
                    "feature": "Multi-model comparison",
                    "importance": 95,
                    "description": "Comparar respuestas de múltiples modelos lado a lado",
                    "examples": ["NextChat Beam", "Big-AGI", "OpenAI Playground"]
                },
                {
                    "feature": "Real-time token tracking",
                    "importance": 90,
                    "description": "Visualización en tiempo real del consumo de tokens",
                    "examples": ["LibreChat", "LangChain UI"]
                },
                {
                    "feature": "Conversation templates",
                    "importance": 85,
                    "description": "Plantillas predefinidas para casos de uso comunes",
                    "examples": ["Poe", "Character AI"]
                },
                {
                    "feature": "Export/Import conversations",
                    "importance": 80,
                    "description": "Capacidad de exportar conversaciones en múltiples formatos",
                    "examples": ["NextChat", "Lobe Chat"]
                },
                {
                    "feature": "Custom system prompts",
                    "importance": 85,
                    "description": "Personalización de prompts del sistema por conversación",
                    "examples": ["Claude", "GPT-4"]
                }
            ],
            "ui_patterns": [
                {
                    "pattern": "Sidebar navigation",
                    "adoption": 95,
                    "description": "Navegación lateral para conversaciones y configuración"
                },
                {
                    "pattern": "Floating action button",
                    "adoption": 70,
                    "description": "Botón flotante para nueva conversación"
                },
                {
                    "pattern": "Message bubbles",
                    "adoption": 100,
                    "description": "Burbujas diferenciadas para usuario y AI"
                },
                {
                    "pattern": "Typing indicators",
                    "adoption": 85,
                    "description": "Indicador visual cuando el AI está generando respuesta"
                }
            ],
            "performance_insights": [
                "Interfaces con menos de 200ms de respuesta visual tienen 40% más engagement",
                "Dark mode es preferido por 70% de usuarios técnicos",
                "Layouts responsivos aumentan retención en 25%",
                "Shortcuts de teclado mejoran productividad en 35%"
            ]
        }

    def analyze_current_ui(self) -> Dict[str, Any]:
        """Analizar la UI actual del proyecto"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "components_found": [],
            "issues": [],
            "opportunities": [],
            "score": 0
        }

        # Buscar componentes UI existentes
        ui_files = []
        for root, dirs, files in os.walk("components/ui"):
            for file in files:
                if file.endswith('.py'):
                    ui_files.append(os.path.join(root, file))

        analysis["components_found"] = ui_files

        # Analizar cada componente
        for file_path in ui_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Detectar problemas comunes
                issues = self.detect_ui_issues(content, file_path)
                analysis["issues"].extend(issues)

                # Detectar oportunidades de mejora
                opportunities = self.detect_opportunities(content, file_path)
                analysis["opportunities"].extend(opportunities)

            except Exception as e:
                app_logger.error(f"Error analizando {file_path}: {e}")

        # Calcular puntuación
        analysis["score"] = self.calculate_ui_score(analysis)

        return analysis

    def detect_ui_issues(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Detectar problemas en el código UI"""
        issues = []

        # Verificar hardcoded colors
        if '"#' in content or "'#" in content:
            issues.append({
                "type": "HARDCODED_COLORS",
                "severity": "MEDIUM",
                "file": file_path,
                "description": "Colores hardcodeados - usar tema configurable",
                "line": content.count('\n') + 1
            })

        # Verificar hardcoded fonts
        if 'font=' in content and 'Arial' in content:
            issues.append({
                "type": "HARDCODED_FONT",
                "severity": "LOW",
                "file": file_path,
                "description": "Fuente hardcodeada - usar configuración de tema"
            })

        # Verificar responsividad
        if 'width=' in content and 'height=' in content:
            if not any(word in content for word in ['grid', 'pack', 'place']):
                issues.append({
                    "type": "FIXED_DIMENSIONS",
                    "severity": "MEDIUM",
                    "file": file_path,
                    "description": "Dimensiones fijas - considerar layout responsivo"
                })

        # Verificar accesibilidad
        if 'Button' in content and 'relief=' not in content:
            issues.append({
                "type": "ACCESSIBILITY",
                "severity": "LOW",
                "file": file_path,
                "description": "Falta configuración de accesibilidad en botones"
            })

        return issues

    def detect_opportunities(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Detectar oportunidades de mejora"""
        opportunities = []

        # Oportunidad para animaciones
        if 'Button' in content and 'hover' not in content:
            opportunities.append({
                "type": "ANIMATION_OPPORTUNITY",
                "priority": "MEDIUM",
                "file": file_path,
                "description": "Agregar efectos hover para mejor UX",
                "feature": "Micro-interactions"
            })

        # Oportunidad para theming
        if not any(word in content for word in ['theme', 'color_scheme']):
            opportunities.append({
                "type": "THEMING_OPPORTUNITY",
                "priority": "HIGH",
                "file": file_path,
                "description": "Implementar sistema de temas",
                "feature": "Dynamic theming"
            })

        # Oportunidad para componentes reutilizables
        if content.count('Button(') > 3:
            opportunities.append({
                "type": "COMPONENT_REUSE",
                "priority": "MEDIUM",
                "file": file_path,
                "description": "Crear componente reutilizable para botones",
                "feature": "Component library"
            })

        return opportunities

    def calculate_ui_score(self, analysis: Dict[str, Any]) -> int:
        """Calcular puntuación de UI"""
        base_score = 100

        # Penalizar por issues
        for issue in analysis["issues"]:
            if issue["severity"] == "HIGH":
                base_score -= 15
            elif issue["severity"] == "MEDIUM":
                base_score -= 8
            elif issue["severity"] == "LOW":
                base_score -= 3

        # Bonificar por componentes encontrados
        component_bonus = min(len(analysis["components_found"]) * 5, 20)
        base_score += component_bonus

        return max(0, min(100, base_score))

    def create_modern_theme(self, theme_name: str = "modern_professional") -> Dict[str, Any]:
        """Crear tema moderno basado en mejores prácticas"""
        return {
            "name": theme_name,
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "colors": {
                # Colores principales basados en Material Design 3
                "primary": "#1976d2",
                "primary_variant": "#1565c0",
                "secondary": "#388e3c",
                "secondary_variant": "#2e7d32",
                "background": "#fafafa",
                "surface": "#ffffff",
                "error": "#d32f2f",
                "warning": "#f57c00",
                "info": "#1976d2",
                "success": "#388e3c",

                # Colores de texto
                "on_primary": "#ffffff",
                "on_secondary": "#ffffff",
                "on_background": "#212121",
                "on_surface": "#212121",
                "on_error": "#ffffff",

                # Colores de estado
                "hover": "#f5f5f5",
                "active": "#e0e0e0",
                "disabled": "#9e9e9e",
                "border": "#e0e0e0",
                "divider": "#eeeeee"
            },
            "typography": {
                "font_family": "Segoe UI, system-ui, sans-serif",
                "font_family_mono": "Consolas, Monaco, monospace",
                "font_sizes": {
                    "xs": 10,
                    "sm": 12,
                    "md": 14,
                    "lg": 16,
                    "xl": 18,
                    "xxl": 24,
                    "title": 32
                },
                "font_weights": {
                    "light": 300,
                    "normal": 400,
                    "medium": 500,
                    "bold": 700
                },
                "line_heights": {
                    "tight": 1.2,
                    "normal": 1.5,
                    "relaxed": 1.8
                }
            },
            "spacing": {
                "xs": 4,
                "sm": 8,
                "md": 16,
                "lg": 24,
                "xl": 32,
                "xxl": 48
            },
            "borders": {
                "radius": {
                    "sm": 4,
                    "md": 8,
                    "lg": 12,
                    "full": 9999
                },
                "width": {
                    "thin": 1,
                    "medium": 2,
                    "thick": 4
                }
            },
            "shadows": {
                "sm": "0 1px 3px rgba(0,0,0,0.12)",
                "md": "0 4px 6px rgba(0,0,0,0.16)",
                "lg": "0 10px 15px rgba(0,0,0,0.2)",
                "xl": "0 20px 25px rgba(0,0,0,0.25)"
            }
        }

    def generate_component_improvements(self) -> List[Dict[str, Any]]:
        """Generar mejoras específicas para componentes"""
        improvements = []

        # Mejoras basadas en investigación de mercado
        market_features = self.market_insights["top_features"]

        for feature in market_features:
            if feature["importance"] >= 85:
                improvements.append({
                    "component": f"{feature['feature'].replace(' ', '_').lower()}_component",
                    "priority": "HIGH",
                    "description": feature["description"],
                    "implementation": self.get_implementation_guide(feature["feature"]),
                    "examples": feature["examples"]
                })

        # Mejoras específicas de UI
        ui_improvements = [
            {
                "component": "message_bubble_component",
                "priority": "HIGH",
                "description": "Mejorar burbujas de mensaje con animaciones y mejor tipografía",
                "implementation": {
                    "features": [
                        "Animación de aparición",
                        "Indicador de tipo de mensaje",
                        "Mejor contraste de colores",
                        "Soporte para markdown",
                        "Copy button hover"
                    ]
                }
            },
            {
                "component": "sidebar_navigation",
                "priority": "MEDIUM",
                "description": "Sidebar colapsible con navegación mejorada",
                "implementation": {
                    "features": [
                        "Animación de colapso/expansión",
                        "Búsqueda de conversaciones",
                        "Filtros por fecha",
                        "Indicadores de estado",
                        "Shortcuts de teclado"
                    ]
                }
            },
            {
                "component": "token_dashboard",
                "priority": "HIGH",
                "description": "Dashboard visual para tracking de tokens",
                "implementation": {
                    "features": [
                        "Gráficos en tiempo real",
                        "Alertas de consumo",
                        "Comparación por modelo",
                        "Proyecciones de costo",
                        "Exportación de reportes"
                    ]
                }
            }
        ]

        improvements.extend(ui_improvements)
        return improvements

    def get_implementation_guide(self, feature_name: str) -> Dict[str, Any]:
        """Obtener guía de implementación para una característica"""
        guides = {
            "Multi-model comparison": {
                "components": ["BeamInterface", "ModelComparison", "ResponseGrid"],
                "complexity": "HIGH",
                "estimated_hours": 16,
                "dependencies": ["threading", "asyncio"],
                "steps": [
                    "Crear interfaz de comparación lado a lado",
                    "Implementar sistema de solicitudes paralelas",
                    "Agregar votación/ranking de respuestas",
                    "Incluir métricas de tiempo y tokens"
                ]
            },
            "Real-time token tracking": {
                "components": ["TokenDashboard", "UsageChart", "AlertSystem"],
                "complexity": "MEDIUM",
                "estimated_hours": 8,
                "dependencies": ["matplotlib", "tkinter"],
                "steps": [
                    "Crear dashboard con gráficos",
                    "Implementar tracking en tiempo real",
                    "Agregar sistema de alertas",
                    "Incluir proyecciones de costo"
                ]
            },
            "Conversation templates": {
                "components": ["TemplateManager", "PromptLibrary", "CategoryFilter"],
                "complexity": "MEDIUM",
                "estimated_hours": 6,
                "dependencies": ["json", "templates"],
                "steps": [
                    "Crear sistema de plantillas",
                    "Implementar categorización",
                    "Agregar editor de plantillas",
                    "Incluir compartir/importar"
                ]
            }
        }

        return guides.get(feature_name, {
            "components": ["CustomComponent"],
            "complexity": "MEDIUM",
            "estimated_hours": 4,
            "dependencies": [],
            "steps": ["Implementar componente básico"]
        })

    def create_component_blueprint(self, component_name: str, feature_type: str) -> str:
        """Crear blueprint de código para nuevo componente"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        blueprint = f'''# {component_name.title()}
# Componente UI moderno basado en mejores prácticas
# Generado: {timestamp}

import customtkinter as ctk
import tkinter as tk
from typing import Dict, Any, Optional, Callable
from utils.logger import app_logger

class {component_name.title().replace('_', '')}:
    """
    {component_name.replace('_', ' ').title()} component
    Implementa {feature_type} con diseño moderno y accesible
    """

    def __init__(self, parent, theme: Dict[str, Any] = None, **kwargs):
        self.parent = parent
        self.theme = theme or self._get_default_theme()
        self.callbacks = {{}}

        # Configuración del componente
        self.config = {{
            "width": kwargs.get("width", 300),
            "height": kwargs.get("height", 200),
            "padding": self.theme.get("spacing", {{}}).get("md", 16),
            "border_radius": self.theme.get("borders", {{}}).get("radius", {{}}).get("md", 8)
        }}

        self._create_widgets()
        self._setup_layout()
        self._bind_events()

    def _get_default_theme(self) -> Dict[str, Any]:
        """Tema por defecto si no se proporciona uno"""
        return {{
            "colors": {{
                "primary": "#1976d2",
                "background": "#ffffff",
                "text": "#212121",
                "border": "#e0e0e0"
            }},
            "spacing": {{"md": 16}},
            "borders": {{"radius": {{"md": 8}}}}
        }}

    def _create_widgets(self):
        """Crear widgets del componente"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(
            self.parent,
            width=self.config["width"],
            height=self.config["height"],
            corner_radius=self.config["border_radius"],
            fg_color=self.theme["colors"]["background"]
        )

        # Agregar widgets específicos aquí
        # TODO: Implementar widgets específicos del componente

    def _setup_layout(self):
        """Configurar layout del componente"""
        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=self.config["padding"],
            pady=self.config["padding"]
        )

    def _bind_events(self):
        """Configurar eventos del componente"""
        # TODO: Implementar eventos específicos
        pass

    def on_event(self, event_name: str, callback: Callable):
        """Registrar callback para evento"""
        if event_name not in self.callbacks:
            self.callbacks[event_name] = []
        self.callbacks[event_name].append(callback)

    def trigger_event(self, event_name: str, data: Any = None):
        """Disparar evento"""
        if event_name in self.callbacks:
            for callback in self.callbacks[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    app_logger.error(f"Error en callback {{event_name}}: {{e}}")

    def update_theme(self, theme: Dict[str, Any]):
        """Actualizar tema del componente"""
        self.theme = theme
        # TODO: Actualizar apariencia visual

    def get_data(self) -> Dict[str, Any]:
        """Obtener datos del componente"""
        return {{}}

    def set_data(self, data: Dict[str, Any]):
        """Establecer datos del componente"""
        pass

    def refresh(self):
        """Refrescar componente"""
        pass

    def destroy(self):
        """Limpiar recursos del componente"""
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
'''

        return blueprint

    def save_theme(self, theme: Dict[str, Any], filename: str):
        """Guardar tema en archivo"""
        theme_path = f"components/ui/themes/{filename}.json"
        try:
            with open(theme_path, 'w', encoding='utf-8') as f:
                json.dump(theme, f, indent=2, ensure_ascii=False)
            app_logger.info(f"Tema guardado en: {theme_path}")
        except Exception as e:
            app_logger.error(f"Error guardando tema: {e}")

    def generate_ui_roadmap(self) -> Dict[str, Any]:
        """Generar roadmap de mejoras UI"""
        analysis = self.analyze_current_ui()
        improvements = self.generate_component_improvements()

        roadmap = {
            "timestamp": datetime.now().isoformat(),
            "current_score": analysis["score"],
            "target_score": 90,
            "phases": [
                {
                    "phase": 1,
                    "name": "Fundación",
                    "duration_weeks": 2,
                    "items": [
                        "Implementar sistema de temas",
                        "Crear componentes base reutilizables",
                        "Corregir issues críticos de UI"
                    ]
                },
                {
                    "phase": 2,
                    "name": "Características Core",
                    "duration_weeks": 3,
                    "items": [
                        "Dashboard de tokens con gráficos",
                        "Sistema de comparación de modelos",
                        "Navegación mejorada con sidebar"
                    ]
                },
                {
                    "phase": 3,
                    "name": "Experiencia Avanzada",
                    "duration_weeks": 2,
                    "items": [
                        "Animaciones y micro-interacciones",
                        "Personalización avanzada",
                        "Exportación y plantillas"
                    ]
                }
            ],
            "estimated_total_hours": sum(imp.get("implementation", {}).get("estimated_hours", 4) for imp in improvements),
            "priority_improvements": sorted(improvements, key=lambda x: x["priority"] == "HIGH", reverse=True)[:5]
        }

        return roadmap

    def save_analysis_report(self, analysis: Dict[str, Any]):
        """Guardar reporte de análisis UI"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis/ui_design/ui_analysis_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            app_logger.info(f"Análisis UI guardado en: {filename}")
        except Exception as e:
            app_logger.error(f"Error guardando análisis UI: {e}")