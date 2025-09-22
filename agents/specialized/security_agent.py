# Security Agent
# Agente especializado para análisis y mejoras de seguridad

import os
import re
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from utils.logger import app_logger

class SecurityAgent:
    """
    Agente especializado para análisis de seguridad
    Detecta vulnerabilidades, patrones peligrosos y mejora la seguridad del código
    """

    def __init__(self):
        self.security_rules = self.load_security_rules()
        self.scan_results = []
        self.report_dir = "analysis/security/"
        self.ensure_directories()

    def ensure_directories(self):
        """Crear directorios necesarios"""
        os.makedirs(self.report_dir, exist_ok=True)

    def load_security_rules(self) -> Dict[str, Any]:
        """Cargar reglas de seguridad predefinidas"""
        return {
            "critical_patterns": [
                {
                    "name": "HARDCODED_PASSWORD",
                    "pattern": r'password\s*=\s*["\'][^"\']+["\']',
                    "severity": "CRITICAL",
                    "description": "Contraseña hardcodeada detectada"
                },
                {
                    "name": "HARDCODED_API_KEY",
                    "pattern": r'(api_key|apikey|secret_key)\s*=\s*["\'][^"\']+["\']',
                    "severity": "CRITICAL",
                    "description": "API Key hardcodeada detectada"
                },
                {
                    "name": "SQL_INJECTION_RISK",
                    "pattern": r'execute\s*\(\s*["\'].*%.*["\']',
                    "severity": "HIGH",
                    "description": "Posible vulnerabilidad de inyección SQL"
                },
                {
                    "name": "COMMAND_INJECTION",
                    "pattern": r'os\.system\s*\([^)]*\+|subprocess\.call\s*\([^)]*\+',
                    "severity": "HIGH",
                    "description": "Posible inyección de comandos"
                },
                {
                    "name": "EVAL_USAGE",
                    "pattern": r'\beval\s*\(',
                    "severity": "HIGH",
                    "description": "Uso de eval() - riesgo de ejecución de código"
                },
                {
                    "name": "EXEC_USAGE",
                    "pattern": r'\bexec\s*\(',
                    "severity": "HIGH",
                    "description": "Uso de exec() - riesgo de ejecución de código"
                }
            ],
            "medium_patterns": [
                {
                    "name": "HTTP_NO_SSL",
                    "pattern": r'http://[^/\s]+',
                    "severity": "MEDIUM",
                    "description": "URL HTTP sin cifrado detectada"
                },
                {
                    "name": "WEAK_HASH",
                    "pattern": r'hashlib\.(md5|sha1)\(',
                    "severity": "MEDIUM",
                    "description": "Algoritmo de hash débil (MD5/SHA1)"
                },
                {
                    "name": "DEBUG_MODE",
                    "pattern": r'debug\s*=\s*True',
                    "severity": "MEDIUM",
                    "description": "Modo debug habilitado en producción"
                },
                {
                    "name": "TEMP_FILE_INSECURE",
                    "pattern": r'open\s*\(\s*["\']\/tmp\/',
                    "severity": "MEDIUM",
                    "description": "Uso inseguro de archivos temporales"
                }
            ],
            "low_patterns": [
                {
                    "name": "TODO_SECURITY",
                    "pattern": r'(TODO|FIXME|HACK).*security|security.*(TODO|FIXME|HACK)',
                    "severity": "LOW",
                    "description": "TODO relacionado con seguridad"
                },
                {
                    "name": "PRINT_SENSITIVE",
                    "pattern": r'print\s*\([^)]*(?:password|token|key|secret)',
                    "severity": "LOW",
                    "description": "Posible impresión de datos sensibles"
                }
            ]
        }

    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Escanear un archivo específico"""
        vulnerabilities = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

            # Escanear todos los patrones
            all_patterns = (
                self.security_rules["critical_patterns"] +
                self.security_rules["medium_patterns"] +
                self.security_rules["low_patterns"]
            )

            for rule in all_patterns:
                matches = re.finditer(rule["pattern"], content, re.IGNORECASE | re.MULTILINE)

                for match in matches:
                    # Encontrar número de línea
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""

                    vulnerabilities.append({
                        "file": file_path,
                        "line": line_num,
                        "rule": rule["name"],
                        "severity": rule["severity"],
                        "description": rule["description"],
                        "match": match.group(0),
                        "line_content": line_content,
                        "position": {
                            "start": match.start(),
                            "end": match.end()
                        }
                    })

        except Exception as e:
            app_logger.error(f"Error escaneando archivo {file_path}: {e}")

        return vulnerabilities

    def scan_directory(self, directory: str = ".", exclude_dirs: List[str] = None) -> List[Dict[str, Any]]:
        """Escanear directorio completo"""
        if exclude_dirs is None:
            exclude_dirs = ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'logs', 'testing']

        all_vulnerabilities = []

        for root, dirs, files in os.walk(directory):
            # Filtrar directorios excluidos
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                # Solo escanear archivos de código
                if file.endswith(('.py', '.js', '.ts', '.php', '.java', '.cpp', '.c', '.rb', '.go')):
                    file_path = os.path.join(root, file)
                    file_vulnerabilities = self.scan_file(file_path)
                    all_vulnerabilities.extend(file_vulnerabilities)

        return all_vulnerabilities

    def analyze_dependencies(self) -> List[Dict[str, Any]]:
        """Analizar dependencias en busca de vulnerabilidades conocidas"""
        issues = []

        # Verificar requirements.txt
        if os.path.exists("requirements.txt"):
            try:
                with open("requirements.txt", 'r') as f:
                    requirements = f.read()

                # Patrones de dependencias potencialmente inseguras
                risky_packages = [
                    "pickle",  # Serialización insegura
                    "yaml",    # YAML parsing puede ser peligroso
                    "eval",    # Evaluación dinámica
                ]

                for package in risky_packages:
                    if package in requirements:
                        issues.append({
                            "type": "DEPENDENCY_RISK",
                            "severity": "MEDIUM",
                            "package": package,
                            "description": f"Dependencia {package} puede tener riesgos de seguridad",
                            "file": "requirements.txt"
                        })

            except Exception as e:
                app_logger.error(f"Error analizando requirements.txt: {e}")

        return issues

    def check_file_permissions(self) -> List[Dict[str, Any]]:
        """Verificar permisos de archivos sensibles"""
        issues = []
        sensitive_files = ['.env', 'config.py', 'settings.py', 'secrets.json']

        for file_pattern in sensitive_files:
            for root, dirs, files in os.walk("."):
                for file in files:
                    if file_pattern in file:
                        file_path = os.path.join(root, file)
                        try:
                            # En Windows, los permisos son más complejos
                            # Verificar si el archivo existe y es accesible
                            if os.path.exists(file_path):
                                stat_info = os.stat(file_path)
                                issues.append({
                                    "type": "FILE_PERMISSION",
                                    "severity": "LOW",
                                    "file": file_path,
                                    "description": f"Archivo sensible detectado: {file}",
                                    "size": stat_info.st_size
                                })
                        except Exception as e:
                            app_logger.error(f"Error verificando permisos de {file_path}: {e}")

        return issues

    def validate_crypto_usage(self) -> List[Dict[str, Any]]:
        """Validar uso de criptografía"""
        issues = []

        # Buscar archivos que usen criptografía
        crypto_files = []
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if any(word in content for word in ['bcrypt', 'hashlib', 'crypto', 'fernet', 'rsa']):
                                crypto_files.append(file_path)
                    except:
                        pass

        # Analizar uso de criptografía
        for file_path in crypto_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Verificar buenas prácticas
                if 'bcrypt' in content and 'hash' in content:
                    issues.append({
                        "type": "CRYPTO_GOOD",
                        "severity": "INFO",
                        "file": file_path,
                        "description": "Uso correcto de bcrypt para hash de contraseñas"
                    })

                if re.search(r'random\.random\(\)', content):
                    issues.append({
                        "type": "WEAK_RANDOM",
                        "severity": "MEDIUM",
                        "file": file_path,
                        "description": "Uso de random.random() para criptografía - usar secrets.randbelow()"
                    })

            except Exception as e:
                app_logger.error(f"Error analizando criptografía en {file_path}: {e}")

        return issues

    def generate_security_score(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generar puntuación de seguridad"""
        score = 100
        severity_weights = {
            "CRITICAL": 25,
            "HIGH": 15,
            "MEDIUM": 8,
            "LOW": 3
        }

        deductions = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "LOW")
            if severity in deductions:
                deductions[severity] += 1
                score -= severity_weights.get(severity, 1)

        score = max(0, score)

        return {
            "score": score,
            "rating": self.get_security_rating(score),
            "deductions": deductions,
            "total_issues": len(vulnerabilities)
        }

    def get_security_rating(self, score: int) -> str:
        """Obtener rating de seguridad basado en puntuación"""
        if score >= 90:
            return "EXCELENTE"
        elif score >= 75:
            return "BUENO"
        elif score >= 60:
            return "REGULAR"
        elif score >= 40:
            return "MALO"
        else:
            return "CRÍTICO"

    def generate_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generar recomendaciones de seguridad"""
        recommendations = []

        # Agrupar por tipo de vulnerabilidad
        vuln_types = {}
        for vuln in vulnerabilities:
            rule = vuln["rule"]
            if rule not in vuln_types:
                vuln_types[rule] = []
            vuln_types[rule].append(vuln)

        # Generar recomendaciones específicas
        for rule, vulns in vuln_types.items():
            if rule == "HARDCODED_PASSWORD":
                recommendations.append({
                    "type": "CRITICAL_FIX",
                    "title": "Contraseñas hardcodeadas",
                    "description": "Mover todas las contraseñas a variables de entorno (.env)",
                    "files": [v["file"] for v in vulns],
                    "count": len(vulns)
                })

            elif rule == "HARDCODED_API_KEY":
                recommendations.append({
                    "type": "CRITICAL_FIX",
                    "title": "API Keys hardcodeadas",
                    "description": "Usar variables de entorno para todas las API keys",
                    "files": [v["file"] for v in vulns],
                    "count": len(vulns)
                })

            elif rule == "SQL_INJECTION_RISK":
                recommendations.append({
                    "type": "HIGH_FIX",
                    "title": "Riesgo de inyección SQL",
                    "description": "Usar parámetros preparados en todas las consultas SQL",
                    "files": [v["file"] for v in vulns],
                    "count": len(vulns)
                })

            elif rule == "EVAL_USAGE":
                recommendations.append({
                    "type": "HIGH_FIX",
                    "title": "Uso de eval()",
                    "description": "Reemplazar eval() con alternativas seguras como ast.literal_eval()",
                    "files": [v["file"] for v in vulns],
                    "count": len(vulns)
                })

        # Recomendaciones generales
        critical_count = len([v for v in vulnerabilities if v["severity"] == "CRITICAL"])
        if critical_count > 0:
            recommendations.append({
                "type": "URGENT",
                "title": "Acción inmediata requerida",
                "description": f"Se encontraron {critical_count} vulnerabilidades críticas que requieren atención inmediata",
                "priority": 1
            })

        return recommendations

    def run_full_scan(self) -> Dict[str, Any]:
        """Ejecutar escaneo completo de seguridad"""
        app_logger.info("Iniciando escaneo completo de seguridad...")

        # Escanear código
        code_vulnerabilities = self.scan_directory()

        # Analizar dependencias
        dependency_issues = self.analyze_dependencies()

        # Verificar permisos
        permission_issues = self.check_file_permissions()

        # Validar criptografía
        crypto_issues = self.validate_crypto_usage()

        # Combinar todos los resultados
        all_vulnerabilities = code_vulnerabilities + dependency_issues + permission_issues + crypto_issues

        # Generar puntuación y recomendaciones
        security_score = self.generate_security_score(code_vulnerabilities)
        recommendations = self.generate_recommendations(code_vulnerabilities)

        results = {
            "timestamp": datetime.now().isoformat(),
            "security_score": security_score,
            "vulnerabilities": {
                "code": code_vulnerabilities,
                "dependencies": dependency_issues,
                "permissions": permission_issues,
                "crypto": crypto_issues
            },
            "recommendations": recommendations,
            "summary": {
                "total_issues": len(all_vulnerabilities),
                "critical": len([v for v in all_vulnerabilities if v.get("severity") == "CRITICAL"]),
                "high": len([v for v in all_vulnerabilities if v.get("severity") == "HIGH"]),
                "medium": len([v for v in all_vulnerabilities if v.get("severity") == "MEDIUM"]),
                "low": len([v for v in all_vulnerabilities if v.get("severity") == "LOW"])
            }
        }

        # Guardar resultados
        self.save_scan_results(results)

        app_logger.info(f"Escaneo completado. Puntuación: {security_score['score']}/100 ({security_score['rating']})")

        return results

    def save_scan_results(self, results: Dict[str, Any]):
        """Guardar resultados del escaneo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.report_dir}security_scan_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            app_logger.info(f"Resultados de seguridad guardados en: {filename}")

            # También generar reporte en texto
            self.generate_text_report(results, f"{self.report_dir}security_report_{timestamp}.md")

        except Exception as e:
            app_logger.error(f"Error guardando resultados de seguridad: {e}")

    def generate_text_report(self, results: Dict[str, Any], filename: str):
        """Generar reporte en formato texto/markdown"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# REPORTE DE SEGURIDAD\n\n")
                f.write(f"**Fecha:** {results['timestamp']}\n")
                f.write(f"**Puntuación:** {results['security_score']['score']}/100 ({results['security_score']['rating']})\n\n")

                # Resumen
                summary = results['summary']
                f.write("## RESUMEN\n\n")
                f.write(f"- **Total de issues:** {summary['total_issues']}\n")
                f.write(f"- **Críticos:** {summary['critical']}\n")
                f.write(f"- **Altos:** {summary['high']}\n")
                f.write(f"- **Medios:** {summary['medium']}\n")
                f.write(f"- **Bajos:** {summary['low']}\n\n")

                # Vulnerabilidades críticas
                critical_vulns = [v for v in results['vulnerabilities']['code'] if v['severity'] == 'CRITICAL']
                if critical_vulns:
                    f.write("## VULNERABILIDADES CRÍTICAS\n\n")
                    for vuln in critical_vulns:
                        f.write(f"### {vuln['rule']}\n")
                        f.write(f"- **Archivo:** {vuln['file']}:{vuln['line']}\n")
                        f.write(f"- **Descripción:** {vuln['description']}\n")
                        f.write(f"- **Código:** `{vuln['line_content']}`\n\n")

                # Recomendaciones
                if results['recommendations']:
                    f.write("## RECOMENDACIONES\n\n")
                    for rec in results['recommendations']:
                        f.write(f"### {rec['title']}\n")
                        f.write(f"{rec['description']}\n")
                        if 'files' in rec:
                            f.write(f"**Archivos afectados:** {len(rec['files'])}\n")
                        f.write("\n")

            app_logger.info(f"Reporte de texto generado: {filename}")

        except Exception as e:
            app_logger.error(f"Error generando reporte de texto: {e}")