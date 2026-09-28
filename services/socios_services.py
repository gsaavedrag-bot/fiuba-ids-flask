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
    query = "SELECT id_socio FROM socios WHERE email = %s;"
    existente = execute(query, (email,))

    if existente:
        return (None, "EMAIL_EXISTS")  # Ya existe un socio con ese email.
    elif existente is None:
        return (None, "DB_ERROR")  # Error de base de datos al verificar existencia.
    
    # Los marcadores %s se completan con los parámetros de forma segura.
    query = "INSERT INTO socios (nombre, email, estado) VALUES (%s, %s, TRUE);"

    resultado = execute(query, (nombre, email))
    if resultado is None:
        return (None, "DB_ERROR")
    return (resultado, None) 


def obtener_socio_por_id(socio_id):
    """Busca un socio por su identificador."""
    query = """
        SELECT id_socio AS id, nombre, email, estado AS activo
        FROM socios
        WHERE id_socio = %s;
    """
    resultado = execute(query, (socio_id,))
    if resultado is None:
        return None, "DB_ERROR"
    elif not resultado:
        return None, "NOT_FOUND"
    return resultado[0], None


def actualizar_socio(socio_id, cambios):
    """Actualiza solo los campos editables del socio."""
    if "email" in cambios:
        query = "SELECT id_socio FROM socios WHERE email = %s AND id_socio <> %s;"
        existente = execute(query, (cambios["email"], socio_id))
        if existente is None:
            return "DB_ERROR"
        elif existente:
            return "EMAIL_EXISTS"

    columnas = {"nombre": "nombre", "email": "email", "activo": "estado"}
    asignaciones = [f"{columnas[campo]} = %s" for campo in cambios]
    valores = [cambios[campo] for campo in cambios]
    valores.append(socio_id)
    query = f"UPDATE socios SET {', '.join(asignaciones)} WHERE id_socio = %s;"
    resultado = execute(query, tuple(valores))
    if resultado is None:
        return "DB_ERROR"
    return None