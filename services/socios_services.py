# services/socios_services.py
from db import execute

# 1. Para leer datos (SELECT):
def obtener_todos_los_socios():
    query = "SELECT id, nombre, email, activo FROM socios WHERE activo = %s;"
    socios = execute(query, (True,))  # Devuelve una lista de dicts: [{'id': 1, 'nombre': 'Juan'}, ...]
    return socios

# 2. Para escribir datos (INSERT / UPDATE):
def guardar_nuevo_socio(nombre, email):
    query = "INSERT INTO socios (nombre, email, activo) VALUES (%s, %s, TRUE);"
    resultado = execute(query, (nombre, email))
    return resultado