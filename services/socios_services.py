# services/socios_services.py
from db import execute

def obtener_todos_los_socios():
    """Obtiene socios activos y adapta los nombres de columnas para la API."""
    # En la tabla las columnas se llaman id_socio y estado.
    # Los alias id y activo mantienen el formato esperado por la respuesta.
    query = "SELECT id_socio AS id, nombre, email, estado AS activo FROM socios WHERE estado = %s;"
    socios = execute(query, (True,))  # Devuelve una lista de dicts: [{'id': 1, 'nombre': 'Juan'}, ...]
    return socios

def guardar_nuevo_socio(nombre, email):
    """Inserta un socio nuevo, inicialmente habilitado."""
    # Los marcadores %s se completan con los parámetros de forma segura.
    query = "INSERT INTO socios (nombre, email, estado) VALUES (%s, %s, TRUE);"
    resultado = execute(query, (nombre, email))
    return resultado