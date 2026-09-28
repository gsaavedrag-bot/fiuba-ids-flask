# services/socios_services.py
from typing import Any
from db import execute


def _construir_filtros_socios(filtros: dict):
    condiciones = []
    params: list[Any] = []

    if "nombre" in filtros:
        condiciones.append("nombre LIKE %s")
        params.append(f"%{filtros['nombre']}%")

    if "activo" in filtros:
        condiciones.append("estado = %s")
        params.append(filtros["activo"])

    where = f" WHERE {' AND '.join(condiciones)}" if condiciones else ""
    return where, tuple(params)


def contar_socios_db(filtros: dict | None = None) -> int | None:
    where, params = _construir_filtros_socios(filtros or {})
    resultado = execute(f"SELECT COUNT(*) AS total FROM socios{where};", params)
    return resultado[0]["total"] if resultado else None


def obtener_socios_db(
    filtros: dict | None = None,
    limit: int = 10,
    offset: int = 0
) -> list[dict] | None:
    where, params = _construir_filtros_socios(filtros or {})
    query = f"""
        SELECT id_socio AS id, nombre, email, estado AS activo
        FROM socios{where}
        ORDER BY id_socio ASC
        LIMIT %s OFFSET %s;
    """
    parametros = list(params)
    parametros.extend([limit, offset])
    return execute(query, tuple(parametros))


def obtener_socio_por_id_db(socio_id: int) -> dict[str, Any] | None:
    query = "SELECT id_socio AS id, nombre, email, estado AS activo FROM socios WHERE id_socio = %s;"
    filas = execute(query, (socio_id,))
    if not isinstance(filas, list) or not filas:
        return None
    return filas[0]


def obtener_socio_por_email_db(email: str, excluir_id: int | None = None) -> dict[str, Any] | None:
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
    query = "INSERT INTO socios (nombre, email, estado) VALUES (%s, %s, TRUE);"
    resultado = execute(query, (nombre, email))
    return resultado if isinstance(resultado, int) else None


def actualizar_socio_db(socio_id: int, campos: dict[str, Any]) -> int | None:
    set_clauses = []
    params = []

    if "nombre" in campos:
        set_clauses.append("nombre = %s")
        params.append(campos["nombre"])

    if "email" in campos:
        set_clauses.append("email = %s")
        params.append(campos["email"])

    if "activo" in campos:
        set_clauses.append("estado = %s")
        params.append(campos["activo"])

    if not set_clauses:
        return 0

    query = f"UPDATE socios SET {', '.join(set_clauses)} WHERE id_socio = %s;"
    params.append(socio_id)

    return execute(query, tuple(params))