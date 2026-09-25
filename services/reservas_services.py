from datetime import datetime, timezone, timedelta
from typing import Any

from db import execute

TZ_ARG = timezone(timedelta(hours=-3))

FiltrosReserva = dict[str, int | str]


def parsear_fecha_iso(dt_value: datetime | str | None) -> str | None:
    """Formatea una fecha de MySQL como ISO con zona horaria GMT-3."""
    if dt_value is None:
        return None
    if isinstance(dt_value, str):
        dt_value = datetime.fromisoformat(dt_value)
    if dt_value.tzinfo is None:
        dt_value = dt_value.replace(tzinfo=TZ_ARG)
    return dt_value.strftime("%Y-%m-%dT%H:%M:%S.%f-03:00")


def _construir_condiciones(
    filtros: FiltrosReserva | None,
) -> tuple[list[str], list[int | str]]:
    """Construye condiciones parametrizadas compartidas por las consultas."""
    condiciones = []
    parametros: list[int | str] = []

    if not filtros:
        return condiciones, parametros

    filtros_sql = (
        ("id_cancha", "id_cancha = %s"),
        ("id_socio", "id_socio = %s"),
        ("estado", "estado = %s"),
        ("fecha_desde", "DATE(fecha_hora_inicio) >= %s"),
        ("fecha_hasta", "DATE(fecha_hora_inicio) <= %s"),
    )
    for clave, condicion_sql in filtros_sql:
        valor = filtros.get(clave)
        if valor is not None:
            condiciones.append(condicion_sql)
            parametros.append(valor)

    return condiciones, parametros


def contar_reservas_db(filtros: FiltrosReserva | None = None) -> int | None:
    """Cuenta las reservas que coinciden con los filtros."""
    condiciones, parametros = _construir_condiciones(filtros)
    query = "SELECT COUNT(*) AS total FROM reservas"
    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)

    resultado = execute(query, tuple(parametros))
    if not isinstance(resultado, list):
        return None
    if not resultado:
        return 0
    return int(resultado[0]["total"])


def obtener_reservas_db(
    filtros: FiltrosReserva | None = None,
    limit: int = 10,
    offset: int = 0,
) -> list[dict[str, Any]] | None:
    """Consulta las reservas con filtros y paginación."""
    condiciones, parametros = _construir_condiciones(filtros)
    query = """
        SELECT id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin,
               estado, tarifa_historica AS precio_hora, total AS precio_total
        FROM reservas
    """
    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)

    query += " ORDER BY id ASC LIMIT %s OFFSET %s;"
    parametros.extend([limit, offset])

    filas = execute(query, tuple(parametros))
    if not isinstance(filas, list):
        return None

    for reserva in filas:
        reserva["fecha_hora_inicio"] = parsear_fecha_iso(
            reserva["fecha_hora_inicio"])
        reserva["fecha_hora_fin"] = parsear_fecha_iso(
            reserva["fecha_hora_fin"])

    return filas


def obtener_reserva_por_id_db(reserva_id: int) -> dict[str, Any] | None:
    """Obtiene una reserva por su identificador."""
    query = """
        SELECT id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin,
               estado, tarifa_historica AS precio_hora, total AS precio_total
        FROM reservas
        WHERE id = %s;
    """
    resultado = execute(query, (reserva_id,))
    if not isinstance(resultado, list) or not resultado:
        return None

    reserva = resultado[0]
    reserva["fecha_hora_inicio"] = parsear_fecha_iso(
        reserva["fecha_hora_inicio"])
    reserva["fecha_hora_fin"] = parsear_fecha_iso(
        reserva["fecha_hora_fin"])
    return reserva


def actualizar_estado_reserva_db(
    reserva_id: int,
    nuevo_estado: str,
) -> int | None:
    """Actualiza el estado de una reserva."""
    query = "UPDATE reservas SET estado = %s WHERE id = %s;"
    resultado = execute(query, (nuevo_estado, reserva_id))
    return resultado if isinstance(resultado, int) else None


def crear_reserva_db(_datos: dict[str, Any]) -> bool:
    """Indica que la creación aún no está implementada."""
    return False
