# services/socios_services.py
from typing import Any
from db import execute

def obtener_todos_los_socios(filtros=None, limit=10, offset=0):
    """Obtiene socios aplicando filtros y paginación."""
    condiciones = []
    parametros = []

    if filtros:
        if "nombre" in filtros:
            condiciones.append("nombre LIKE %s")
            parametros.append(f"%{filtros['nombre']}%")

        if "activo" in filtros:
            condiciones.append("estado = %s")
            parametros.append(filtros["activo"])

    query = """
        SELECT id_socio AS id, nombre, email, estado AS activo
        FROM socios
    """

    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)

    query += " ORDER BY id_socio LIMIT %s OFFSET %s;"
    parametros.extend([limit, offset])

    return execute(query, tuple(parametros))

def contar_socios_db(filtros=None):
    condiciones = []
    parametros = []

    if filtros:
        if "nombre" in filtros:
            condiciones.append("nombre LIKE %s")
            parametros.append(f"%{filtros['nombre']}%")

        if "activo" in filtros:
            condiciones.append("estado = %s")
            parametros.append(filtros["activo"])

    query = "SELECT COUNT(*) AS total FROM socios"

    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)

    resultado = execute(query, tuple(parametros))

    if not resultado:
        return None

    return resultado[0]["total"]

def obtener_socio_por_id_db(socio_id: int) -> dict[str, Any] | None:
    """Busca un socio por su clave primaria id_socio."""
    query = "SELECT id_socio AS id, nombre, email, estado AS activo FROM socios WHERE id_socio = %s;"
    filas = execute(query, (socio_id,))
    if not isinstance(filas, list) or not filas:
        return None
    return filas[0]

def obtener_socio_por_email_db(email: str, excluir_id: int | None = None) -> dict[str, Any] | None:
    """
    Verifica si un email ya está registrado (incluso inactivo).
    Si se pasa excluir_id, omite al propio socio durante el PATCH.
    """
    query = "SELECT id_socio AS id, nombre, email, estado AS activo FROM socios WHERE email = %s"
    params: list[str | int] = [email]
    if excluir_id is not None:
        query += " AND id_socio != %s"
        params.append(excluir_id)

    filas = execute(query, tuple(params))
    if not isinstance(filas, list) or not filas:
        return None
    return filas[0]

def guardar_nuevo_socio(nombre: str, email: str) -> int | None:
    """Inserta un socio nuevo con estado habilitado (TRUE)."""
    query = "INSERT INTO socios (nombre, email, estado) VALUES (%s, %s, TRUE);"
    resultado = execute(query, (nombre, email))
    return resultado if isinstance(resultado, int) else None

def actualizar_socio_db(socio_id: int, campos: dict[str, Any]) -> int | None:
    """Construye dinámicamente el UPDATE según los campos recibidos."""
    set_clauses = []
    params = []

    if "nombre" in campos:
        set_clauses.append("nombre = %s")
        params.append(campos["nombre"])

    if "email" in campos:
        set_clauses.append("email = %s")
        params.append(campos["email"])

    if "activo" in campos:
        # En la tabla de la DB la columna se llama estado
        set_clauses.append("estado = %s")
        params.append(campos["activo"])

    if not set_clauses:
        return 0

    query = f"UPDATE socios SET {', '.join(set_clauses)} WHERE id_socio = %s;"
    params.append(socio_id)

    return execute(query, tuple(params))
