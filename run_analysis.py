# Script para ejecutar análisis completo del proyecto
# Utiliza el AgenteVerificador para generar reporte detallado

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.internal.verificador_agent import AgenteVerificador
import json

def main():
    print("Iniciando analisis completo del proyecto LiveChat-IA...")

    # Crear instancia del verificador
    verificador = AgenteVerificador()

    # Ejecutar análisis completo
    print("Analizando estructura del proyecto...")
    analysis = verificador.analyze_project_structure()

    # Mostrar resumen
    print("\n" + "="*60)
    print("RESUMEN DEL ANALISIS")
    print("="*60)

    print(f"Total de archivos: {analysis['structure']['total_files']}")
    print(f"Archivos Python: {analysis['metrics']['python_files']}")
    print(f"Lineas de codigo: {analysis['metrics']['total_lines']}")
    print(f"Vulnerabilidades: {len(analysis['vulnerabilities'])}")
    print(f"Mejoras sugeridas: {len(analysis['improvements'])}")

    print("\nARCHIVOS POR TIPO:")
    for ext, count in analysis['structure']['by_type'].items():
        print(f"  {ext}: {count}")

    print("\nVULNERABILIDADES CRITICAS:")
    critical_vulns = [v for v in analysis['vulnerabilities'] if v['severity'] in ['CRITICAL', 'HIGH']]
    for vuln in critical_vulns[:5]:
        print(f"  - {vuln['type']}: {vuln['description']}")

    print("\nMEJORAS PRIORITARIAS:")
    high_priority = [i for i in analysis['improvements'] if i['priority'] == 'HIGH']
    for improvement in high_priority:
        print(f"  - {improvement['category']}: {improvement['description']}")

    # Verificar cumplimiento de reglas
    print("\nCUMPLIMIENTO DE REGLAS CRITICAS:")
    compliance = verificador.check_rule_compliance()
    print(f"  Total reglas: {compliance['total_rules']}")
    print(f"  Violaciones: {compliance['violations']}")

    if compliance['critical_issues']:
        print("  ISSUES CRITICOS:")
        for issue in compliance['critical_issues']:
            print(f"    - {issue['rule']}: {issue['violations']} violaciones")

    print("\nAnalisis completado. Reporte guardado en analysis/")
    return analysis

if __name__ == "__main__":
    analysis_result = main()