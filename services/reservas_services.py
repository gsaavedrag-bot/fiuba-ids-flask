# reservas/reservas_services.py
from datetime import datetime
from typing import Any
from db import execute
from helpers import parsear_fecha_iso

FiltrosReserva = dict[str, int | str]


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


def crear_reserva_db(datos: dict[str, Any]) -> tuple[dict | None, str | None]:
    id_socio = datos.get("id_socio")
    id_cancha = datos.get("id_cancha")
    inicio_iso = datos.get("fecha_hora_inicio")
    fin_iso = datos.get("fecha_hora_fin")
    if not isinstance(inicio_iso, str) or not isinstance(fin_iso, str):
        return None, "INVALID_DATE"

    # 1. Validar existencia y estado del socio
    query_socio = "SELECT id_socio, estado FROM socios WHERE id_socio = %s;"
    socio_res = execute(query_socio, (id_socio,))
    if not socio_res:
        return None, "SOCIO_NOT_FOUND"
    if not socio_res[0]["estado"]:
        return None, "SOCIO_INACTIVE"

    # 2. Validar existencia y estado de la cancha
    query_cancha = "SELECT id_cancha, precio_hora, activa FROM canchas WHERE id_cancha = %s;"
    cancha_res = execute(query_cancha, (id_cancha,))
    if not cancha_res:
        return None, "CANCHA_NOT_FOUND"
    cancha = cancha_res[0]
    if not cancha["activa"]:
        return None, "CANCHA_INACTIVE"

    # 3. Validar solapamiento de cancha (reservas confirmadas)
    query_cancha_solapada = """
        SELECT COUNT(*) AS total FROM reservas
        WHERE id_cancha = %s AND estado = 'confirmada'
          AND fecha_hora_inicio < %s AND fecha_hora_fin > %s;
    """
    res_solapada = execute(query_cancha_solapada,
                           (id_cancha, fin_iso, inicio_iso))
    if res_solapada and res_solapada[0]["total"] > 0:
        return None, "OVERLAP_CANCHA"

    # 4. Validar solapamiento de socio (reservas confirmadas)
    query_socio_solapado = """
        SELECT COUNT(*) AS total FROM reservas
        WHERE id_socio = %s AND estado = 'confirmada'
          AND fecha_hora_inicio < %s AND fecha_hora_fin > %s;
    """
    res_socio = execute(query_socio_solapado, (id_socio, fin_iso, inicio_iso))
    if res_socio and res_socio[0]["total"] > 0:
        return None, "OVERLAP_SOCIO"

    # 5. Cálculo de importe y congelamiento de tarifa
    dt_inicio = datetime.fromisoformat(inicio_iso)
    dt_fin = datetime.fromisoformat(fin_iso)
    duracion_horas = int((dt_fin - dt_inicio).total_seconds() // 3600)
    precio_hora = cancha["precio_hora"]
    total = duracion_horas * precio_hora

    # 6. Inserción
    query_insert = """
        INSERT INTO reservas (id_cancha, id_socio, fecha_hora_inicio, fecha_hora_fin, estado, tarifa_historica, total)
        VALUES (%s, %s, %s, %s, 'confirmada', %s, %s);
    """
    nuevo_id = execute(query_insert, (id_cancha, id_socio,
                       inicio_iso, fin_iso, precio_hora, total))
    if not nuevo_id:
        return None, "DB_ERROR"

    reserva_creada = {
        "id": nuevo_id,
        "id_socio": id_socio,
        "id_cancha": id_cancha,
        "fecha_hora_inicio": parsear_fecha_iso(inicio_iso),
        "fecha_hora_fin": parsear_fecha_iso(fin_iso),
        "estado": "confirmada",
        "precio_hora": precio_hora,
        "precio_total": total
    }
    return reserva_creada, None
