# services/canchas_services.py
from typing import Any

from db import execute

COLUMNAS_CANCHA = "c.id_cancha AS id, c.nombre, c.id_deporte, c.precio_hora, c.techada, c.activa"
CAMPOS_EDITABLES = ("nombre", "precio_hora", "techada", "activa")


def _formatear_cancha(cancha: dict) -> dict:
    """MySQL guarda BOOLEAN como TINYINT: se convierten 0/1 a false/true."""
    cancha["techada"] = bool(cancha["techada"])
    cancha["activa"] = bool(cancha["activa"])
    return cancha


def _formatear_canchas(filas: list[dict] | None) -> list[dict] | None:
    if not isinstance(filas, list):
        return None
    return [_formatear_cancha(cancha) for cancha in filas]


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
        SELECT {COLUMNAS_CANCHA}
        FROM canchas c{where}
        ORDER BY c.id_cancha ASC
        LIMIT %s OFFSET %s;
    """
    parametros = list(params)
    parametros.extend([limit, offset])
    return _formatear_canchas(execute(query, tuple(parametros)))


def obtener_cancha_por_id_db(cancha_id: int) -> dict | None:
    resultado = execute(
        f"SELECT {COLUMNAS_CANCHA} FROM canchas c WHERE c.id_cancha = %s;",
        (cancha_id,)
    )
    if not resultado:
        return None
    return _formatear_cancha(resultado[0])


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


def actualizar_cancha_db(cancha_id: int, cambios: dict) -> int | None:
    """Actualiza solo los campos editables presentes en 'cambios'. None si falla."""
    asignaciones: list[str] = []
    params: list[Any] = []
    for campo in CAMPOS_EDITABLES:
        if campo in cambios:
            asignaciones.append(f"{campo} = %s")
            params.append(cambios[campo])

    if not asignaciones:
        return 0

    params.append(cancha_id)
    query = f"UPDATE canchas SET {', '.join(asignaciones)} WHERE id_cancha = %s;"
    resultado = execute(query, tuple(params))
    return resultado if isinstance(resultado, int) else None


def cancha_tiene_reservas_db(cancha_id: int) -> bool | None:
    """Indica si la cancha tiene alguna reserva, sin importar su estado. None si falla."""
    resultado = execute(
        "SELECT 1 FROM reservas WHERE id_cancha = %s LIMIT 1;",
        (cancha_id,)
    )
    if resultado is None:
        return None
    return len(resultado) > 0


def eliminar_cancha_db(cancha_id: int) -> int | None:
    """Elimina la cancha. Devuelve las filas borradas o None si falla."""
    resultado = execute("DELETE FROM canchas WHERE id_cancha = %s;", (cancha_id,))
    return resultado if isinstance(resultado, int) else None


def _construir_filtros_disponibles(
    inicio: str,
    fin: str,
    id_deporte: int | None,
    techada: bool | None
):
    """Canchas activas sin reservas confirmadas que se superpongan con [inicio, fin)."""
    where = """
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
        where += " AND c.id_deporte = %s"
        params.append(id_deporte)
    if techada is not None:
        where += " AND c.techada = %s"
        params.append(techada)
    return where, params


def contar_canchas_disponibles_db(
    inicio: str,
    fin: str,
    id_deporte: int | None = None,
    techada: bool | None = None
) -> int | None:
    where, params = _construir_filtros_disponibles(inicio, fin, id_deporte, techada)
    res = execute(f"SELECT COUNT(*) AS total FROM canchas c {where};", tuple(params))
    return res[0]["total"] if res else None


def obtener_canchas_disponibles_db(
    inicio: str,
    fin: str,
    id_deporte: int | None = None,
    techada: bool | None = None,
    limit: int = 10,
    offset: int = 0
) -> list[dict] | None:
    where, params = _construir_filtros_disponibles(inicio, fin, id_deporte, techada)
    query = f"""
        SELECT {COLUMNAS_CANCHA}
        FROM canchas c {where}
        ORDER BY c.id_cancha
        LIMIT %s OFFSET %s;
    """
    params.extend([limit, offset])
    return _formatear_canchas(execute(query, tuple(params)))
