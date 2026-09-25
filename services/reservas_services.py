# services/reservas_services.py
from datetime import datetime, timezone, timedelta
from db import execute

# Zona horaria del club: GMT-3
TZ_ARG = timezone(timedelta(hours=-3))


def parsear_fecha_iso(dt_value):
    """Asegura que el datetime devuelto por MySQL tenga el formato ISO con offset -03:00."""
    if not dt_value:
        return None
    if isinstance(dt_value, str):
        dt_value = datetime.fromisoformat(dt_value)
    if dt_value.tzinfo is None:
        dt_value = dt_value.replace(tzinfo=TZ_ARG)
    return dt_value.strftime("%Y-%m-%dT%H:%M:%S.%f-03:00")


def contar_reservas_db(filtros: dict = None) -> int:
    """Calcula el total de registros coincidentes para armar los links HATEOAS."""
    query = "SELECT COUNT(*) as total FROM reservas WHERE 1=1"
    params = []

    if filtros:
        if filtros.get("id_cancha") is not None:
            query += " AND id_cancha = %s"
            params.append(filtros["id_cancha"])
        if filtros.get("id_socio") is not None:
            query += " AND id_socio = %s"
            params.append(filtros["id_socio"])
        if filtros.get("estado"):
            query += " AND estado = %s"
            params.append(filtros["estado"])
        if filtros.get("fecha_desde"):
            query += " AND DATE(fecha_hora_inicio) >= %s"
            params.append(filtros["fecha_desde"])
        if filtros.get("fecha_hasta"):
            query += " AND DATE(fecha_hora_inicio) <= %s"
            params.append(filtros["fecha_hasta"])

    res = execute(query, tuple(params))
    return res[0]["total"] if res else 0


def obtener_reservas_db(filtros: dict = None, limit: int = 10, offset: int = 0) -> list:
    """Consulta las reservas aplicando filtros combinados con AND y paginación."""
    query = """
        SELECT id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, 
               estado, tarifa_historica AS precio_hora, total AS precio_total
        FROM reservas 
        WHERE 1=1
    """
    params = []

    if filtros:
        if filtros.get("id_cancha") is not None:
            query += " AND id_cancha = %s"
            params.append(filtros["id_cancha"])
        if filtros.get("id_socio") is not None:
            query += " AND id_socio = %s"
            params.append(filtros["id_socio"])
        if filtros.get("estado"):
            query += " AND estado = %s"
            params.append(filtros["estado"])
        if filtros.get("fecha_desde"):
            query += " AND DATE(fecha_hora_inicio) >= %s"
            params.append(filtros["fecha_desde"])
        if filtros.get("fecha_hasta"):
            query += " AND DATE(fecha_hora_inicio) <= %s"
            params.append(filtros["fecha_hasta"])

    query += " ORDER BY id ASC LIMIT %s OFFSET %s;"
    params.extend([limit, offset])

    filas = execute(query, tuple(params))
    if filas is None:
        return None

    # Formateo de fechas a ISO con timezone -03:00 para cumplir Swagger
    for r in filas:
        r["fecha_hora_inicio"] = parsear_fecha_iso(r["fecha_hora_inicio"])
        r["fecha_hora_fin"] = parsear_fecha_iso(r["fecha_hora_fin"])

    return filas


def obtener_reserva_por_id_db(reserva_id: int):
    """Obtiene el detalle completo de una reserva por su identificador."""
    query = """
        SELECT id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, 
               estado, tarifa_historica AS precio_hora, total AS precio_total
        FROM reservas 
        WHERE id = %s;
    """
    res = execute(query, (reserva_id,))
    if not res:
        return None

    reserva = res[0]
    reserva["fecha_hora_inicio"] = parsear_fecha_iso(
        reserva["fecha_hora_inicio"])
    reserva["fecha_hora_fin"] = parsear_fecha_iso(reserva["fecha_hora_fin"])
    return reserva


def actualizar_estado_reserva_db(reserva_id: int, nuevo_estado: str):
    """Actualiza en MySQL la columna 'estado' y confirma la transacción."""
    query = "UPDATE reservas SET estado = %s WHERE id = %s;"
    return execute(query, (nuevo_estado, reserva_id))


def crear_reserva_db(datos):
    """Placeholder para validar y guardar una reserva (Alumno 6)."""
    return True
