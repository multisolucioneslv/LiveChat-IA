# Modern Theme System
# Sistema de temas moderno basado en investigación de mercado
# Inspirado en NextChat, Lobe Chat y Material Design 3

import customtkinter as ctk
from typing import Dict, Any, List
import json
import os

class ModernTheme:
    """
    Sistema de temas moderno para LiveChat-IA
    Basado en las mejores prácticas de UI encontradas en la investigación
    """

    def __init__(self):
        self.themes = self.load_themes()
        self.current_theme = "nextchat_inspired"

    def load_themes(self) -> Dict[str, Any]:
        """Cargar todos los temas disponibles"""
        return {
            "nextchat_inspired": {
                "name": "NextChat Inspired",
                "description": "Inspirado en NextChat (85.9k stars)",
                "colors": {
                    # Colores principales (basado en NextChat)
                    "primary": "#1976d2",
                    "primary_hover": "#1565c0",
                    "secondary": "#9c27b0",
                    "accent": "#ff6b35",

                    # Fondos
                    "background": "#ffffff",
                    "surface": "#f8f9fa",
                    "surface_variant": "#e3f2fd",
                    "card": "#ffffff",

                    # Textos
                    "text_primary": "#212121",
                    "text_secondary": "#757575",
                    "text_disabled": "#bdbdbd",
                    "text_on_primary": "#ffffff",

                    # Estados
                    "success": "#4caf50",
                    "warning": "#ff9800",
                    "error": "#f44336",
                    "info": "#2196f3",

                    # Bordes y divisores
                    "border": "#e0e0e0",
                    "divider": "#eeeeee",
                    "outline": "#9e9e9e",

                    # Sidebar (específico de NextChat)
                    "sidebar_bg": "#f5f5f5",
                    "sidebar_active": "#e3f2fd",
                    "sidebar_hover": "#f0f0f0",

                    # Chat
                    "user_message": "#1976d2",
                    "bot_message": "#ffffff",
                    "message_border": "#e0e0e0",

                    # Botones
                    "button_primary": "#1976d2",
                    "button_secondary": "#f5f5f5",
                    "button_danger": "#f44336"
                },
                "shadows": {
                    "sm": "0 1px 2px rgba(0,0,0,0.1)",
                    "md": "0 4px 6px rgba(0,0,0,0.1)",
                    "lg": "0 10px 15px rgba(0,0,0,0.1)",
                    "xl": "0 20px 25px rgba(0,0,0,0.15)"
                },
                "typography": {
                    "font_family": "Segoe UI, system-ui, -apple-system, sans-serif",
                    "font_family_mono": "Consolas, 'Courier New', monospace",
                    "sizes": {
                        "xs": 10,
                        "sm": 12,
                        "md": 14,
                        "lg": 16,
                        "xl": 18,
                        "xxl": 24,
                        "title": 32
                    },
                    "weights": {
                        "light": 300,
                        "normal": 400,
                        "medium": 500,
                        "semibold": 600,
                        "bold": 700
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
                        "none": 0,
                        "sm": 4,
                        "md": 8,
                        "lg": 12,
                        "xl": 16,
                        "full": 9999
                    },
                    "width": {
                        "thin": 1,
                        "medium": 2,
                        "thick": 4
                    }
                }
            },

            "lobe_chat_inspired": {
                "name": "Lobe Chat Inspired",
                "description": "Inspirado en Lobe Chat (65.8k stars)",
                "colors": {
                    # Colores principales (basado en Lobe Chat)
                    "primary": "#6366f1",
                    "primary_hover": "#5b5cf6",
                    "secondary": "#06b6d4",
                    "accent": "#f59e0b",

                    # Fondos
                    "background": "#fafbfc",
                    "surface": "#ffffff",
                    "surface_variant": "#f1f5f9",
                    "card": "#ffffff",

                    # Textos
                    "text_primary": "#0f172a",
                    "text_secondary": "#64748b",
                    "text_disabled": "#cbd5e1",
                    "text_on_primary": "#ffffff",

                    # Estados
                    "success": "#10b981",
                    "warning": "#f59e0b",
                    "error": "#ef4444",
                    "info": "#3b82f6",

                    # Bordes y divisores
                    "border": "#e2e8f0",
                    "divider": "#f1f5f9",
                    "outline": "#94a3b8",

                    # Sidebar
                    "sidebar_bg": "#f8fafc",
                    "sidebar_active": "#ede9fe",
                    "sidebar_hover": "#f1f5f9",

                    # Chat
                    "user_message": "#6366f1",
                    "bot_message": "#ffffff",
                    "message_border": "#e2e8f0",

                    # Botones
                    "button_primary": "#6366f1",
                    "button_secondary": "#f1f5f9",
                    "button_danger": "#ef4444"
                },
                "shadows": {
                    "sm": "0 1px 2px rgba(0,0,0,0.05)",
                    "md": "0 4px 6px rgba(0,0,0,0.07)",
                    "lg": "0 10px 15px rgba(0,0,0,0.1)",
                    "xl": "0 20px 25px rgba(0,0,0,0.1)"
                },
                "typography": {
                    "font_family": "Inter, system-ui, sans-serif",
                    "font_family_mono": "'Fira Code', Consolas, monospace",
                    "sizes": {
                        "xs": 11,
                        "sm": 13,
                        "md": 14,
                        "lg": 16,
                        "xl": 18,
                        "xxl": 24,
                        "title": 28
                    },
                    "weights": {
                        "light": 300,
                        "normal": 400,
                        "medium": 500,
                        "semibold": 600,
                        "bold": 700
                    }
                },
                "spacing": {
                    "xs": 4,
                    "sm": 8,
                    "md": 16,
                    "lg": 20,
                    "xl": 32,
                    "xxl": 48
                },
                "borders": {
                    "radius": {
                        "none": 0,
                        "sm": 6,
                        "md": 8,
                        "lg": 12,
                        "xl": 16,
                        "full": 9999
                    },
                    "width": {
                        "thin": 1,
                        "medium": 2,
                        "thick": 3
                    }
                }
            },

            "libre_chat_inspired": {
                "name": "LibreChat Inspired",
                "description": "Inspirado en LibreChat (30.2k stars)",
                "colors": {
                    # Colores principales (basado en LibreChat)
                    "primary": "#2563eb",
                    "primary_hover": "#1d4ed8",
                    "secondary": "#059669",
                    "accent": "#dc2626",

                    # Fondos
                    "background": "#ffffff",
                    "surface": "#f9fafb",
                    "surface_variant": "#f3f4f6",
                    "card": "#ffffff",

                    # Textos
                    "text_primary": "#111827",
                    "text_secondary": "#6b7280",
                    "text_disabled": "#d1d5db",
                    "text_on_primary": "#ffffff",

                    # Estados
                    "success": "#059669",
                    "warning": "#d97706",
                    "error": "#dc2626",
                    "info": "#2563eb",

                    # Bordes y divisores
                    "border": "#d1d5db",
                    "divider": "#f3f4f6",
                    "outline": "#9ca3af",

                    # Sidebar
                    "sidebar_bg": "#f9fafb",
                    "sidebar_active": "#dbeafe",
                    "sidebar_hover": "#f3f4f6",

                    # Chat
                    "user_message": "#2563eb",
                    "bot_message": "#ffffff",
                    "message_border": "#d1d5db",

                    # Botones
                    "button_primary": "#2563eb",
                    "button_secondary": "#f3f4f6",
                    "button_danger": "#dc2626"
                },
                "shadows": {
                    "sm": "0 1px 3px rgba(0,0,0,0.1)",
                    "md": "0 4px 6px rgba(0,0,0,0.1)",
                    "lg": "0 10px 15px rgba(0,0,0,0.1)",
                    "xl": "0 20px 25px rgba(0,0,0,0.1)"
                },
                "typography": {
                    "font_family": "system-ui, -apple-system, sans-serif",
                    "font_family_mono": "ui-monospace, monospace",
                    "sizes": {
                        "xs": 12,
                        "sm": 14,
                        "md": 16,
                        "lg": 18,
                        "xl": 20,
                        "xxl": 24,
                        "title": 30
                    },
                    "weights": {
                        "light": 300,
                        "normal": 400,
                        "medium": 500,
                        "semibold": 600,
                        "bold": 700
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
                        "none": 0,
                        "sm": 4,
                        "md": 6,
                        "lg": 8,
                        "xl": 12,
                        "full": 9999
                    },
                    "width": {
                        "thin": 1,
                        "medium": 2,
                        "thick": 4
                    }
                }
            },

            "livechat_ai_dark": {
                "name": "LiveChat-IA Dark",
                "description": "Tema oscuro moderno para LiveChat-IA",
                "colors": {
                    # Colores principales
                    "primary": "#3b82f6",
                    "primary_hover": "#2563eb",
                    "secondary": "#8b5cf6",
                    "accent": "#f59e0b",

                    # Fondos oscuros
                    "background": "#0f172a",
                    "surface": "#1e293b",
                    "surface_variant": "#334155",
                    "card": "#1e293b",

                    # Textos para tema oscuro
                    "text_primary": "#f8fafc",
                    "text_secondary": "#cbd5e1",
                    "text_disabled": "#64748b",
                    "text_on_primary": "#ffffff",

                    # Estados
                    "success": "#10b981",
                    "warning": "#f59e0b",
                    "error": "#ef4444",
                    "info": "#3b82f6",

                    # Bordes y divisores
                    "border": "#475569",
                    "divider": "#334155",
                    "outline": "#64748b",

                    # Sidebar
                    "sidebar_bg": "#1e293b",
                    "sidebar_active": "#3730a3",
                    "sidebar_hover": "#334155",

                    # Chat
                    "user_message": "#3b82f6",
                    "bot_message": "#1e293b",
                    "message_border": "#475569",

                    # Botones
                    "button_primary": "#3b82f6",
                    "button_secondary": "#334155",
                    "button_danger": "#ef4444"
                },
                "shadows": {
                    "sm": "0 1px 2px rgba(0,0,0,0.3)",
                    "md": "0 4px 6px rgba(0,0,0,0.3)",
                    "lg": "0 10px 15px rgba(0,0,0,0.3)",
                    "xl": "0 20px 25px rgba(0,0,0,0.4)"
                },
                "typography": {
                    "font_family": "Segoe UI, system-ui, sans-serif",
                    "font_family_mono": "Consolas, 'Courier New', monospace",
                    "sizes": {
                        "xs": 11,
                        "sm": 13,
                        "md": 14,
                        "lg": 16,
                        "xl": 18,
                        "xxl": 24,
                        "title": 28
                    },
                    "weights": {
                        "light": 300,
                        "normal": 400,
                        "medium": 500,
                        "semibold": 600,
                        "bold": 700
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
                        "none": 0,
                        "sm": 6,
                        "md": 8,
                        "lg": 12,
                        "xl": 16,
                        "full": 9999
                    },
                    "width": {
                        "thin": 1,
                        "medium": 2,
                        "thick": 3
                    }
                }
            }
        }

    def get_theme(self, theme_name: str = None) -> Dict[str, Any]:
        """Obtener tema específico o el actual"""
        if theme_name is None:
            theme_name = self.current_theme

        return self.themes.get(theme_name, self.themes[self.current_theme])

    def set_theme(self, theme_name: str):
        """Establecer tema actual"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False

    def get_available_themes(self) -> List[Dict[str, str]]:
        """Obtener lista de temas disponibles"""
        return [
            {
                "id": theme_id,
                "name": theme_data["name"],
                "description": theme_data["description"]
            }
            for theme_id, theme_data in self.themes.items()
        ]

    def apply_theme_to_customtkinter(self, theme_name: str = None):
        """Aplicar tema a CustomTkinter"""
        theme = self.get_theme(theme_name)
        colors = theme["colors"]

        # Configurar CustomTkinter con los colores del tema
        ctk.set_appearance_mode("light" if "white" in colors["background"] else "dark")

        # Crear un tema personalizado para CustomTkinter
        # Nota: CustomTkinter tiene limitaciones en personalización de colores
        # Esta es una implementación básica

        return theme

    def get_color(self, color_name: str, theme_name: str = None) -> str:
        """Obtener color específico del tema"""
        theme = self.get_theme(theme_name)
        return theme["colors"].get(color_name, "#000000")

    def get_font(self, size: str = "md", weight: str = "normal", mono: bool = False, theme_name: str = None) -> ctk.CTkFont:
        """Obtener fuente configurada según el tema"""
        theme = self.get_theme(theme_name)
        typography = theme["typography"]

        font_family = typography["font_family_mono"] if mono else typography["font_family"]
        font_size = typography["sizes"].get(size, 14)
        font_weight = typography["weights"].get(weight, 400)

        # Convertir peso a string para CustomTkinter
        weight_map = {
            300: "light",
            400: "normal",
            500: "normal",
            600: "bold",
            700: "bold"
        }

        ctk_weight = weight_map.get(font_weight, "normal")

        return ctk.CTkFont(family=font_family, size=font_size, weight=ctk_weight)

    def get_spacing(self, size: str = "md", theme_name: str = None) -> int:
        """Obtener spacing según el tema"""
        theme = self.get_theme(theme_name)
        return theme["spacing"].get(size, 16)

    def get_border_radius(self, size: str = "md", theme_name: str = None) -> int:
        """Obtener border radius según el tema"""
        theme = self.get_theme(theme_name)
        return theme["borders"]["radius"].get(size, 8)

    def save_theme_preference(self, theme_name: str):
        """Guardar preferencia de tema"""
        try:
            config_dir = "components/ui/themes/"
            os.makedirs(config_dir, exist_ok=True)

            config_file = os.path.join(config_dir, "theme_preference.json")

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({"current_theme": theme_name}, f, indent=2)

        except Exception as e:
            print(f"Error saving theme preference: {e}")

    def load_theme_preference(self) -> str:
        """Cargar preferencia de tema guardada"""
        try:
            config_file = "components/ui/themes/theme_preference.json"

            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("current_theme", self.current_theme)

        except Exception as e:
            print(f"Error loading theme preference: {e}")

        return self.current_theme

    def generate_css_variables(self, theme_name: str = None) -> str:
        """Generar variables CSS del tema (para futuro uso web)"""
        theme = self.get_theme(theme_name)
        colors = theme["colors"]

        css_vars = [":root {"]

        for color_name, color_value in colors.items():
            css_var_name = f"--{color_name.replace('_', '-')}"
            css_vars.append(f"  {css_var_name}: {color_value};")

        css_vars.append("}")

        return "\n".join(css_vars)

# Instancia global del sistema de temas
theme_system = ModernTheme()

def get_current_theme() -> Dict[str, Any]:
    """Función de conveniencia para obtener el tema actual"""
    return theme_system.get_theme()

def get_theme_color(color_name: str) -> str:
    """Función de conveniencia para obtener un color del tema actual"""
    return theme_system.get_color(color_name)

def get_theme_font(size: str = "md", weight: str = "normal", mono: bool = False) -> ctk.CTkFont:
    """Función de conveniencia para obtener una fuente del tema actual"""
    return theme_system.get_font(size, weight, mono)