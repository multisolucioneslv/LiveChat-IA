# Funciones auxiliares y utilidades comunes
# Contiene funciones de uso general que pueden ser utilizadas
# en cualquier parte de la aplicación

import re
import hashlib
from datetime import datetime, timedelta


def validate_email(email):
    """
    Valida si un email tiene un formato correcto
    Args:
        email: String con el email a validar
    Returns:
        Boolean indicando si el email es válido
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_string(text):
    """
    Limpia y sanitiza un string removiendo caracteres especiales
    Args:
        text: String a sanitizar
    Returns:
        String sanitizado
    """
    if not text:
        return ""

    # Remover caracteres especiales peligrosos
    text = re.sub(r'[<>"\']', '', text)
    # Remover espacios extras
    text = ' '.join(text.split())
    return text.strip()


def generate_hash(text, algorithm='sha256'):
    """
    Genera un hash de un texto usando el algoritmo especificado
    Args:
        text: Texto a hashear
        algorithm: Algoritmo a usar (sha256, md5, sha1)
    Returns:
        String con el hash generado
    """
    if algorithm == 'md5':
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(text.encode()).hexdigest()
    else:  # sha256 por defecto
        return hashlib.sha256(text.encode()).hexdigest()


def format_datetime_spanish(dt):
    """
    Formatea una fecha en español
    Args:
        dt: Objeto datetime
    Returns:
        String con la fecha formateada en español
    """
    months = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }

    day = dt.day
    month = months[dt.month]
    year = dt.year
    hour = dt.strftime('%H:%M')

    return f"{day} de {month} de {year} a las {hour}"


def paginate_results(results, page=1, per_page=10):
    """
    Pagina una lista de resultados
    Args:
        results: Lista de resultados
        page: Número de página (inicia en 1)
        per_page: Resultados por página
    Returns:
        Diccionario con los resultados paginados y metadatos
    """
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page

    paginated_results = results[start:end]

    return {
        'data': paginated_results,
        'pagination': {
            'current_page': page,
            'per_page': per_page,
            'total_items': total,
            'total_pages': (total + per_page - 1) // per_page,
            'has_next': end < total,
            'has_prev': page > 1
        }
    }