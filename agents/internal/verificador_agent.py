# Agente Verificador Interno
# Guarda reglas críticas y realiza análisis del sistema

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from utils.logger import app_logger


class AgenteVerificador:
    """
    Agente interno para verificación, análisis y mejoras del sistema
    Mantiene reglas críticas y directrices de desarrollo
    """

    def __init__(self):
        self.config_file = "agents/internal/reglas_criticas.json"
        self.analysis_dir = "analysis/"
        self.rules = self.load_rules()
        self.ensure_directories()

        # Registrar regla crítica inicial
        self.add_critical_rule(
            "SEGURIDAD_GITHUB",
            "NUNCA subir a GitHub archivos que contengan credenciales reales (.env, passwords, API keys)",
            "CRÍTICO",
            "Se subió .env con credenciales a GitHub - IMPERDONABLE"
        )

    def ensure_directories(self):
        """Crear directorios necesarios"""
        os.makedirs(self.analysis_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

    def load_rules(self) -> Dict[str, Any]:
        """Cargar reglas críticas desde archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"rules": {}, "created": datetime.now().isoformat()}
        except Exception as e:
            app_logger.error(f"Error cargando reglas: {e}")
            return {"rules": {}, "created": datetime.now().isoformat()}

    def save_rules(self):
        """Guardar reglas críticas"""
        try:
            self.rules["updated"] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, indent=2, ensure_ascii=False)
        except Exception as e:
            app_logger.error(f"Error guardando reglas: {e}")

    def add_critical_rule(self, rule_id: str, description: str, severity: str, context: str = ""):
        """Agregar regla crítica"""
        if "rules" not in self.rules:
            self.rules["rules"] = {}

        self.rules["rules"][rule_id] = {
            "description": description,
            "severity": severity,
            "context": context,
            "created": datetime.now().isoformat(),
            "violations": []
        }
        self.save_rules()
        app_logger.warning(f"Regla crítica agregada: {rule_id} - {description}")

    def record_violation(self, rule_id: str, details: str):
        """Registrar violación de regla"""
        if rule_id in self.rules.get("rules", {}):
            violation = {
                "timestamp": datetime.now().isoformat(),
                "details": details
            }
            self.rules["rules"][rule_id]["violations"].append(violation)
            self.save_rules()
            app_logger.error(f"VIOLACIÓN DE REGLA {rule_id}: {details}")

    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analizar estructura completa del proyecto"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "structure": {},
            "vulnerabilities": [],
            "improvements": [],
            "metrics": {}
        }

        # Análisis de estructura de archivos
        analysis["structure"] = self._analyze_file_structure()

        # Análisis de vulnerabilidades
        analysis["vulnerabilities"] = self._scan_vulnerabilities()

        # Métricas del código
        analysis["metrics"] = self._calculate_code_metrics()

        # Sugerencias de mejora
        analysis["improvements"] = self._suggest_improvements(analysis)

        # Guardar análisis
        self._save_analysis(analysis)

        return analysis

    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analizar estructura de archivos del proyecto"""
        structure = {
            "total_files": 0,
            "by_type": {},
            "by_directory": {},
            "large_files": [],
            "security_files": []
        }

        for root, dirs, files in os.walk("."):
            # Ignorar directorios de Git y cache
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.') and file not in ['.gitignore', '.env.example']:
                    continue

                filepath = os.path.join(root, file)
                structure["total_files"] += 1

                # Por tipo
                ext = os.path.splitext(file)[1] or 'no_extension'
                structure["by_type"][ext] = structure["by_type"].get(ext, 0) + 1

                # Por directorio
                dir_name = os.path.dirname(filepath) or 'root'
                structure["by_directory"][dir_name] = structure["by_directory"].get(dir_name, 0) + 1

                # Archivos grandes (>50KB)
                try:
                    size = os.path.getsize(filepath)
                    if size > 50000:
                        structure["large_files"].append({
                            "file": filepath,
                            "size": size
                        })
                except:
                    pass

                # Archivos de seguridad
                if any(keyword in file.lower() for keyword in ['password', 'secret', 'key', 'token', 'credential']):
                    structure["security_files"].append(filepath)

        return structure

    def _scan_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Escanear vulnerabilidades de seguridad"""
        vulnerabilities = []

        # 1. Verificar archivos sensibles
        sensitive_patterns = ['.env', 'password', 'secret', 'private_key']
        for pattern in sensitive_patterns:
            for root, dirs, files in os.walk("."):
                for file in files:
                    if pattern in file.lower():
                        vulnerabilities.append({
                            "type": "SENSITIVE_FILE",
                            "severity": "HIGH",
                            "file": os.path.join(root, file),
                            "description": f"Archivo sensible detectado: {file}"
                        })

        # 2. Verificar credenciales en código
        python_files = []
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))

        for py_file in python_files[:10]:  # Limitar para no usar muchos tokens
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Buscar patrones peligrosos
                danger_patterns = [
                    'password = "',
                    'api_key = "',
                    'secret = "',
                    'token = "'
                ]

                for pattern in danger_patterns:
                    if pattern in content.lower():
                        vulnerabilities.append({
                            "type": "HARDCODED_CREDENTIAL",
                            "severity": "CRITICAL",
                            "file": py_file,
                            "description": f"Posible credencial hardcodeada: {pattern}"
                        })
            except:
                pass

        # 3. Verificar importaciones peligrosas
        dangerous_imports = ['eval', 'exec', 'os.system', 'subprocess.call']
        for py_file in python_files[:10]:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for danger in dangerous_imports:
                        if danger in content:
                            vulnerabilities.append({
                                "type": "DANGEROUS_FUNCTION",
                                "severity": "MEDIUM",
                                "file": py_file,
                                "description": f"Función peligrosa detectada: {danger}"
                            })
            except:
                pass

        return vulnerabilities

    def _calculate_code_metrics(self) -> Dict[str, Any]:
        """Calcular métricas del código"""
        metrics = {
            "total_lines": 0,
            "python_files": 0,
            "comment_lines": 0,
            "empty_lines": 0,
            "complexity": "low"
        }

        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            metrics["python_files"] += 1
                            metrics["total_lines"] += len(lines)

                            for line in lines:
                                stripped = line.strip()
                                if not stripped:
                                    metrics["empty_lines"] += 1
                                elif stripped.startswith('#'):
                                    metrics["comment_lines"] += 1
                    except:
                        pass

        # Calcular complejidad aproximada
        if metrics["total_lines"] > 5000:
            metrics["complexity"] = "high"
        elif metrics["total_lines"] > 2000:
            metrics["complexity"] = "medium"

        return metrics

    def _suggest_improvements(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sugerir mejoras basadas en el análisis"""
        improvements = []

        # Mejoras de seguridad
        if analysis["vulnerabilities"]:
            improvements.append({
                "category": "SECURITY",
                "priority": "HIGH",
                "description": "Corregir vulnerabilidades de seguridad detectadas",
                "count": len(analysis["vulnerabilities"])
            })

        # Mejoras de estructura
        if analysis["structure"]["total_files"] > 100:
            improvements.append({
                "category": "STRUCTURE",
                "priority": "MEDIUM",
                "description": "Considerar refactorización - proyecto grande",
                "files": analysis["structure"]["total_files"]
            })

        # Mejoras de documentación
        improvements.append({
            "category": "DOCUMENTATION",
            "priority": "MEDIUM",
            "description": "Agregar documentación de API y componentes"
        })

        # Mejoras de rendimiento
        if analysis["structure"]["large_files"]:
            improvements.append({
                "category": "PERFORMANCE",
                "priority": "LOW",
                "description": "Optimizar archivos grandes",
                "large_files": len(analysis["structure"]["large_files"])
            })

        return improvements

    def _save_analysis(self, analysis: Dict[str, Any]):
        """Guardar análisis en archivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.analysis_dir}analysis_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            app_logger.info(f"Análisis guardado en: {filename}")
        except Exception as e:
            app_logger.error(f"Error guardando análisis: {e}")

    def get_critical_rules(self) -> List[Dict[str, Any]]:
        """Obtener todas las reglas críticas"""
        return list(self.rules.get("rules", {}).values())

    def check_rule_compliance(self) -> Dict[str, Any]:
        """Verificar cumplimiento de reglas"""
        compliance = {
            "total_rules": len(self.rules.get("rules", {})),
            "violations": 0,
            "critical_issues": []
        }

        for rule_id, rule in self.rules.get("rules", {}).items():
            if rule.get("violations"):
                compliance["violations"] += len(rule["violations"])
                if rule.get("severity") == "CRÍTICO":
                    compliance["critical_issues"].append({
                        "rule": rule_id,
                        "description": rule.get("description"),
                        "violations": len(rule["violations"])
                    })

        return compliance