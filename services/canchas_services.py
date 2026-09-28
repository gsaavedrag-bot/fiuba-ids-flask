# services/canchas_services.py
from typing import Any

from db import execute


def _construir_filtros(filtros: dict):
    condiciones: list[str] = []
    params: list[Any] = []
    for campo, columna in (
        ("id_deporte", "id_deporte"),
        ("nombre", "nombre"),
        ("techada", "techada"),
        ("activa", "activa")
    ):
        if campo not in filtros:
            continue
        if campo == "nombre":
            condiciones.append(f"{columna} LIKE %s")
            params.append(f"%{filtros[campo]}%")
        else:
            condiciones.append(f"{columna} = %s")
            params.append(filtros[campo])
    where = f" WHERE {' AND '.join(condiciones)}" if condiciones else ""
    return where, tuple(params)


def contar_canchas_db(filtros: dict | None = None) -> int | None:
    where, params = _construir_filtros(filtros or {})
    resultado = execute(f"SELECT COUNT(*) AS total FROM canchas{where};", params)
    return resultado[0]["total"] if resultado else None


def obtener_canchas_db(
    filtros: dict | None = None,
    limit: int = 10,
    offset: int = 0
) -> list[dict] | None:
    where, params = _construir_filtros(filtros or {})
    query = f"""
        SELECT id_cancha AS id, nombre, id_deporte, precio_hora, techada, activa
        FROM canchas{where}
        ORDER BY id_cancha ASC
        LIMIT %s OFFSET %s;
    """
    parametros = list(params)
    parametros.extend([limit, offset])
    return execute(query, tuple(parametros))


def crear_cancha_db(datos: dict) -> tuple[int | None, str | None]:
    deportes = execute(
        "SELECT id_deporte FROM deportes WHERE id_deporte = %s;",
        (datos["id_deporte"],)
    )
    if deportes is None:
        return None, "DB_ERROR"
    if not deportes:
        return None, "DEPORTE_NOT_FOUND"

    query = """
        INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa, precio_reserva)
        VALUES (%s, %s, %s, %s, %s, %s);
    """

    cancha_id = execute(query, (
        datos["nombre"],
        datos["id_deporte"],
        datos["precio_hora"],
        datos["techada"],
        datos["activa"],
        datos["precio_hora"]
    ))
    return (cancha_id, None) if cancha_id else (None, "DB_ERROR")


def contar_canchas_disponibles_db(inicio: str, fin: str, id_deporte: int | None = None, techada: bool | None = None) -> int:
    query = """
        SELECT COUNT(*) AS total
        FROM canchas c
        WHERE c.activa = TRUE
          AND c.id_cancha NOT IN (
              SELECT r.id_cancha
              FROM reservas r
              WHERE r.estado = 'confirmada'
                AND r.fecha_hora_inicio < %s
                AND r.fecha_hora_fin > %s
          )
    """
    params: list[Any] = [fin, inicio]
    if id_deporte is not None:
        query += " AND c.id_deporte = %s"
        params.append(id_deporte)
    if techada is not None:
        query += " AND c.techada = %s"
        params.append(techada)

    res = execute(query, tuple(params))
    return res[0]["total"] if res else 0


def obtener_canchas_disponibles_db(
    inicio: str,
    fin: str,
    id_deporte: int | None = None,
    techada: bool | None = None,
    limit: int = 10,
    offset: int = 0
) -> list[dict] | None:
    query = """
        SELECT c.id_cancha AS id, c.nombre, c.id_deporte, c.precio_hora, c.techada, c.activa
        FROM canchas c
        WHERE c.activa = TRUE
          AND c.id_cancha NOT IN (
              SELECT r.id_cancha
              FROM reservas r
              WHERE r.estado = 'confirmada'
                AND r.fecha_hora_inicio < %s
                AND r.fecha_hora_fin > %s
          )
    """
    params: list[Any] = [fin, inicio]
    if id_deporte is not None:
        query += " AND c.id_deporte = %s"
        params.append(id_deporte)
    if techada is not None:
        query += " AND c.techada = %s"
        params.append(techada)

    query += " ORDER BY c.id_cancha LIMIT %s OFFSET %s;"
    params.extend([limit, offset])

    return execute(query, tuple(params))

def obtener_cancha_por_id_db(cancha_id: int) -> dict[str, Any] | None:
    query = """
        SELECT id_cancha AS id, nombre, id_deporte, precio_hora, techada, activa
        FROM canchas
        WHERE id_cancha = %s;
    """
    resultado = execute(query, (cancha_id,))
    if not isinstance(resultado, list) or not resultado:
        return None
    return resultado[0]


def actualizar_cancha_db(cancha_id: int, campos: dict[str, Any]) -> int | None:
    set_clauses = []
    params = []

    if "nombre" in campos:
        set_clauses.append("nombre = %s")
        params.append(campos["nombre"])

    if "precio_hora" in campos:
        set_clauses.append("precio_hora = %s")
        params.append(campos["precio_hora"])
        set_clauses.append("precio_reserva = %s")
        params.append(campos["precio_hora"])

    if "techada" in campos:
        set_clauses.append("techada = %s")
        params.append(campos["techada"])

    if "activa" in campos:
        set_clauses.append("activa = %s")
        params.append(campos["activa"])

    if not set_clauses:
        return 0

    query = f"UPDATE canchas SET {', '.join(set_clauses)} WHERE id_cancha = %s;"
    params.append(cancha_id)

    return execute(query, tuple(params))


def contar_reservas_por_cancha_db(cancha_id: int) -> int | None:
    query = "SELECT COUNT(*) AS total FROM reservas WHERE id_cancha = %s;"
    resultado = execute(query, (cancha_id,))
    if not isinstance(resultado, list) or not resultado:
        return 0
    return int(resultado[0]["total"])


def eliminar_cancha_db(cancha_id: int) -> int | None:
    query = "DELETE FROM canchas WHERE id_cancha = %s;"
    return execute(query, (cancha_id,))