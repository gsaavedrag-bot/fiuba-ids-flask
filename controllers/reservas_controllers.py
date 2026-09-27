# controllers/reservas_controllers.py
from datetime import datetime, timezone, timedelta
from flask import jsonify, request
from errors import ERRORS
from services.reservas_services import (
    obtener_reservas_db,
    contar_reservas_db,
    crear_reserva_db,
    obtener_reserva_por_id_db,
    actualizar_estado_reserva_db
)
from helpers import build_hateoas_links

# Zona horaria oficial del club (GMT-3)
TZ_ARG = timezone(timedelta(hours=-3))


def listar_reservas_controller():
    """Devuelve en JSON las reservas paginadas con filtros."""
    # 1. Validación de paginación
    try:
        limit = int(request.args.get("_limit", 10))
        offset = int(request.args.get("_offset", 0))
        if limit < 1 or limit > 100 or offset < 0:
            return ERRORS["INVALID_FORMAT"]("Parámetros _limit (1-100) u _offset (>=0) inválidos.")
    except ValueError:
        return ERRORS["INVALID_FORMAT"]("_limit y _offset deben ser enteros.")

    # 2. Parseo de filtros de consulta
    filtros: dict[str, int | str] = {}
    try:
        id_cancha = request.args.get("id_cancha")
        if id_cancha is not None:
            filtros["id_cancha"] = int(id_cancha)
        id_socio = request.args.get("id_socio")
        if id_socio is not None:
            filtros["id_socio"] = int(id_socio)
    except ValueError:
        return ERRORS["INVALID_FORMAT"]("id_cancha e id_socio deben ser enteros.")

    estado = request.args.get("estado")
    if estado:
        if estado not in ["confirmada", "cancelada", "finalizada"]:
            return ERRORS["INVALID_FORMAT"](f"Estado desconocido: {estado}")
        filtros["estado"] = estado

    fecha_desde = request.args.get("fecha_desde")
    if fecha_desde is not None:
        filtros["fecha_desde"] = fecha_desde
    fecha_hasta = request.args.get("fecha_hasta")
    if fecha_hasta is not None:
        filtros["fecha_hasta"] = fecha_hasta

    total = contar_reservas_db(filtros)
    if total is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("Error al contar reservas en la base de datos.")

    reservas = obtener_reservas_db(filtros=filtros, limit=limit, offset=offset)

    if reservas is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("Error al consultar reservas en la base de datos.")

    if not reservas and total == 0:
        return "", 204

    links = build_hateoas_links(
        request.base_url, limit, offset, total, request.args.to_dict())
    return jsonify({"reservas": reservas, "_links": links}), 200


def obtener_reserva_controller(reserva_id):
    """Devuelve el detalle de una reserva o 404 Not Found."""
    reserva = obtener_reserva_por_id_db(reserva_id)
    if not reserva:
        return ERRORS["NOT_FOUND"](f"No se encontró la reserva con id {reserva_id}.")
    return jsonify(reserva), 200


def actualizar_estado_controller(reserva_id):
    """Cambia el estado de la reserva validando las transiciones permitidas (Issue #12)."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "estado" not in data:
        return ERRORS["MISSING_REQUIRED_FIELDS"]("El campo 'estado' es obligatorio.")

    nuevo_estado = data.get("estado")
    estados_validos = ["confirmada", "cancelada", "finalizada"]
    if not isinstance(nuevo_estado, str) or nuevo_estado not in estados_validos:
        return ERRORS["INVALID_FORMAT"](f"Estado no reconocido: '{nuevo_estado}'.")

    reserva = obtener_reserva_por_id_db(reserva_id)
    if not reserva:
        return ERRORS["NOT_FOUND"](f"No se encontró la reserva con id {reserva_id}.")

    estado_actual = reserva["estado"]

    # Regla: Repetir el estado actual devuelve éxito sin modificar
    if nuevo_estado == estado_actual:
        return jsonify(reserva), 200

    # Validaciones temporales de transición
    ahora = datetime.now(TZ_ARG)
    inicio_raw = reserva.get("fecha_hora_inicio")
    fin_raw = reserva.get("fecha_hora_fin")
    if not isinstance(inicio_raw, str) or not isinstance(fin_raw, str):
        return ERRORS["INTERNAL_SERVER_ERROR"]("Las fechas de la reserva no tienen un formato válido.")
    try:
        inicio = datetime.fromisoformat(inicio_raw)
        fin = datetime.fromisoformat(fin_raw)
    except ValueError:
        return ERRORS["INTERNAL_SERVER_ERROR"]("Las fechas de la reserva no tienen un formato válido.")

    if estado_actual == "confirmada":
        if nuevo_estado == "cancelada":
            if ahora >= inicio:
                return ERRORS["CONFLICT"]("No se puede cancelar una reserva cuyo horario de inicio ya comenzó o pasó.")
        elif nuevo_estado == "finalizada":
            if ahora < fin:
                return ERRORS["CONFLICT"]("No se puede finalizar una reserva antes de que concluya su horario.")
        else:
            return ERRORS["CONFLICT"](f"Transición no permitida de '{estado_actual}' a '{nuevo_estado}'.")
    else:
        # Ni 'cancelada' ni 'finalizada' admiten nuevas transiciones
        return ERRORS["CONFLICT"](f"No se permite modificar una reserva en estado '{estado_actual}'.")

    filas_afectadas = actualizar_estado_reserva_db(reserva_id, nuevo_estado)
    if filas_afectadas is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("No se pudo actualizar el estado de la reserva.")

    reserva["estado"] = nuevo_estado
    return jsonify(reserva), 200


def crear_reserva_controller():
    data = request.get_json(silent=True) or {}
    requeridos = ["id_socio", "id_cancha",
                  "fecha_hora_inicio", "fecha_hora_fin"]

    if not all(k in data for k in requeridos):
        return ERRORS["MISSING_REQUIRED_FIELDS"]("Faltan campos obligatorios (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin).")

    inicio_str = data["fecha_hora_inicio"]
    fin_str = data["fecha_hora_fin"]
    try:
        if not isinstance(inicio_str, str) or not isinstance(fin_str, str):
            raise ValueError
        inicio = datetime.fromisoformat(inicio_str)
        fin = datetime.fromisoformat(fin_str)
    except (TypeError, ValueError):
        return ERRORS["INVALID_FORMAT"]("Formato de fecha inválido. Se espera ISO 8601 con zona horaria.")

    ahora = datetime.now(TZ_ARG)
    if inicio <= ahora:
        return ERRORS["CONFLICT"]("La reserva debe comenzar en el futuro.")

    if inicio >= fin:
        return ERRORS["INVALID_FORMAT"]("fecha_hora_inicio debe ser menor a fecha_hora_fin.")

    if inicio.minute != 0 or fin.minute != 0:
        return ERRORS["INVALID_FORMAT"]("Las reservas deben iniciar y finalizar en horas en punto.")

    duracion_horas = (fin - inicio).total_seconds() / 3600
    if duracion_horas < 1 or duracion_horas > 3:
        return ERRORS["CONFLICT"]("La duración debe ser de entre 1 y 3 horas completas.")

    if inicio.hour < 8 or fin.hour > 23 or (fin.hour == 23 and fin.minute > 0):
        return ERRORS["CONFLICT"]("El horario solicitado debe encontrarse entre las 08:00 y las 23:00.")

    reserva, error = crear_reserva_db(data)

    if error == "SOCIO_NOT_FOUND":
        return ERRORS["NOT_FOUND"](f"No existe el socio con id {data['id_socio']}.")
    if error == "SOCIO_INACTIVE":
        return ERRORS["CONFLICT"]("El socio se encuentra inactivo.")
    if error == "CANCHA_NOT_FOUND":
        return ERRORS["NOT_FOUND"](f"No existe la cancha con id {data['id_cancha']}.")
    if error == "CANCHA_INACTIVE":
        return ERRORS["CONFLICT"]("La cancha se encuentra inactiva.")
    if error == "OVERLAP_CANCHA":
        return ERRORS["CONFLICT"]("La cancha ya tiene una reserva confirmada en ese intervalo.")
    if error == "OVERLAP_SOCIO":
        return ERRORS["CONFLICT"]("El socio ya tiene una reserva confirmada en ese intervalo.")
    if error == "DB_ERROR" or not reserva:
        return ERRORS["INTERNAL_SERVER_ERROR"]("No se pudo registrar la reserva en la base de datos.")

    return jsonify(reserva), 201
