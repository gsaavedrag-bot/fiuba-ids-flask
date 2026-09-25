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

# Zona horaria oficial del club (GMT-3)
TZ_ARG = timezone(timedelta(hours=-3))


def _construir_hateoas(base_url: str, limit: int, offset: int, total: int, query_params: dict):
    """Genera los enlaces _first, _prev, _next y _last respetando HATEOAS."""
    clean_params = {k: v for k, v in query_params.items() if k not in [
        "_limit", "_offset"]}

    def generar_url(o, l):
        p = clean_params.copy()
        p["_offset"] = o
        p["_limit"] = l
        qs = "&".join(f"{k}={v}" for k, v in p.items())
        return f"{base_url}?{qs}" if qs else f"{base_url}?_offset={o}&_limit={l}"

    last_offset = max(0, ((total - 1) // limit) * limit) if total > 0 else 0
    prev_offset = max(0, offset - limit) if offset > 0 else None
    next_offset = offset + limit if (offset + limit) < total else None

    links = {
        "_first": {"href": generar_url(0, limit)},
        "_last": {"href": generar_url(last_offset, limit)}
    }
    if prev_offset is not None and offset > 0:
        links["_prev"] = {"href": generar_url(prev_offset, limit)}
    if next_offset is not None:
        links["_next"] = {"href": generar_url(next_offset, limit)}

    return links


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

    links = _construir_hateoas(
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
    """Válida que llegue un cuerpo JSON y delega la creación (Módulo)."""
    data = request.get_json(silent=True) or {}

    if not data:
        return ERRORS["MISSING_REQUIRED_FIELDS"]("No se recibieron datos en la solicitud.")

    ok = crear_reserva_db(data)
    if not ok:
        return ERRORS["INTERNAL_SERVER_ERROR"]("No se pudo crear la reserva.")

    return jsonify({"mensaje": "Reserva creada correctamente"}), 201
