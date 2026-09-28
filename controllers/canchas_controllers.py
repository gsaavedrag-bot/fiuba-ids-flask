# controllers/canchas_controllers.py
from datetime import datetime
from typing import Any

from flask import jsonify, request
from errors import ERRORS
from helpers import (
    build_hateoas_links,
    parsear_booleano,
    parsear_entero_positivo,
    parsear_paginacion,
    validar_campos_permitidos,
    TZ_ARG
)
from services.canchas_services import (
    obtener_canchas_db,
    obtener_cancha_por_id_db,
    crear_cancha_db,
    actualizar_cancha_db,
    cancha_tiene_reservas_db,
    eliminar_cancha_db,
    obtener_canchas_disponibles_db,
    contar_canchas_disponibles_db,
    contar_canchas_db
)

PARAMS_LISTADO = {"id_deporte", "nombre", "techada", "activa", "_limit", "_offset"}
PARAMS_DISPONIBLES = {"fecha", "hora_inicio", "hora_fin", "id_deporte", "techada", "_limit", "_offset"}
CAMPOS_CREACION = {"nombre", "id_deporte", "precio_hora", "techada", "activa"}
CAMPOS_EDITABLES = {"nombre", "precio_hora", "techada", "activa"}
NOMBRE_MAX = 50 


def validar_campos_cancha(data: dict[str, Any]) -> str | None:
    """Valida el tipo de cada campo presente. Devuelve el mensaje de error o None."""
    if "nombre" in data:
        nombre = data["nombre"]
        if not isinstance(nombre, str) or not nombre.strip():
            return "nombre debe ser un texto no vacío."
        if len(nombre.strip()) > NOMBRE_MAX:
            return f"nombre no puede superar los {NOMBRE_MAX} caracteres."
    if "id_deporte" in data:
        id_deporte = data["id_deporte"]
        if isinstance(id_deporte, bool) or not isinstance(id_deporte, int) or id_deporte < 1:
            return "id_deporte debe ser un entero positivo."
    if "precio_hora" in data:
        precio_hora = data["precio_hora"]
        if isinstance(precio_hora, bool) or not isinstance(precio_hora, int) or precio_hora <= 0:
            return "precio_hora debe ser un entero mayor a cero."
    for campo in ("techada", "activa"):
        if campo in data and not isinstance(data[campo], bool):
            return f"{campo} debe ser un valor booleano."
    return None


def listar_canchas_controller():
    try:
        validar_campos_permitidos(request.args.keys(), PARAMS_LISTADO)
        limit, offset = parsear_paginacion(
            request.args.get("_limit"),
            request.args.get("_offset")
        )

        filtros: dict = {}
        id_deporte = parsear_entero_positivo(request.args.get("id_deporte"), "id_deporte")
        if id_deporte is not None:
            filtros["id_deporte"] = id_deporte
        nombre = request.args.get("nombre")
        if nombre is not None:
            filtros["nombre"] = nombre
        for campo in ("techada", "activa"):
            valor = parsear_booleano(request.args.get(campo), campo)
            if valor is not None:
                filtros[campo] = valor
    except ValueError as error:
        return ERRORS["INVALID_FORMAT"](str(error))

    total = contar_canchas_db(filtros)
    if total is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("Error al contar canchas en la base de datos.")
    canchas = obtener_canchas_db(filtros, limit, offset)
    if canchas is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("Error al consultar canchas en la base de datos.")
    if not canchas and total == 0:
        return "", 204

    links = build_hateoas_links(
        request.base_url, limit, offset, total, request.args.to_dict())
    return jsonify({"canchas": canchas, "_links": links}), 200


def obtener_cancha_controller(cancha_id):
    """Devuelve una cancha o 404."""
    try:
        validar_campos_permitidos(request.args, set())
    except ValueError as e:
        return ERRORS["INVALID_FORMAT"](str(e))

    cancha = obtener_cancha_por_id_db(cancha_id)
    if not cancha:
        return ERRORS["NOT_FOUND"](f"No se encontró la cancha con id {cancha_id}.")
    return jsonify(cancha), 200


def crear_cancha_controller():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return ERRORS["MISSING_REQUIRED_FIELDS"]("El cuerpo JSON es obligatorio.")

    try:
        validar_campos_permitidos(data.keys(), CAMPOS_CREACION)
    except ValueError as error:
        return ERRORS["INVALID_FORMAT"](str(error))

    requeridos = ("nombre", "id_deporte", "precio_hora")
    if any(campo not in data for campo in requeridos):
        return ERRORS["MISSING_REQUIRED_FIELDS"]("nombre, id_deporte y precio_hora son obligatorios.")

    mensaje_error = validar_campos_cancha(data)
    if mensaje_error:
        return ERRORS["INVALID_FORMAT"](mensaje_error)

    cancha_id, error = crear_cancha_db({
        "nombre": data["nombre"].strip(),
        "id_deporte": data["id_deporte"],
        "precio_hora": data["precio_hora"],
        "techada": data.get("techada", False),
        "activa": data.get("activa", True)
    })
    if error == "DEPORTE_NOT_FOUND":
        return ERRORS["NOT_FOUND"](f"No existe el deporte con id {data['id_deporte']}.")
    if error or not cancha_id:
        return ERRORS["INTERNAL_SERVER_ERROR"]("No se pudo crear la cancha en la base de datos.")

    cancha = obtener_cancha_por_id_db(cancha_id)
    if not cancha:
        return ERRORS["INTERNAL_SERVER_ERROR"]("La cancha se creó pero no pudo consultarse.")
    return jsonify(cancha), 201


def actualizar_cancha_controller(cancha_id: int):
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return ERRORS["MISSING_REQUIRED_FIELDS"]("El cuerpo JSON no puede estar vacío.")

    if "id_deporte" in data:
        return ERRORS["INVALID_FORMAT"]("El deporte de una cancha no puede modificarse.")
    try:
        validar_campos_permitidos(data.keys(), CAMPOS_EDITABLES)
    except ValueError as error:
        return ERRORS["INVALID_FORMAT"](str(error))

    mensaje_error = validar_campos_cancha(data)
    if mensaje_error:
        return ERRORS["INVALID_FORMAT"](mensaje_error)

    cancha_actual = obtener_cancha_por_id_db(cancha_id)
    if not cancha_actual:
        return ERRORS["NOT_FOUND"](f"No existe la cancha con id {cancha_id}.")

    cambios = dict(data)
    if "nombre" in cambios:
        cambios["nombre"] = cambios["nombre"].strip()
    if actualizar_cancha_db(cancha_id, cambios) is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("No se pudo actualizar la cancha.")

    return "", 204


def eliminar_cancha_controller(cancha_id: int):
    cancha_actual = obtener_cancha_por_id_db(cancha_id)
    if not cancha_actual:
        return ERRORS["NOT_FOUND"](f"No existe la cancha con id {cancha_id}.")

    tiene_reservas = cancha_tiene_reservas_db(cancha_id)
    if tiene_reservas is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("Error al verificar las reservas de la cancha.")
    if tiene_reservas:
        return ERRORS["CONFLICT"](
            "La cancha tiene reservas asociadas. Puede desactivarse mediante PATCH.")

    if eliminar_cancha_db(cancha_id) is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("No se pudo eliminar la cancha.")
    return "", 204


def consultar_disponibles_controller():
    try:
        validar_campos_permitidos(request.args.keys(), PARAMS_DISPONIBLES)
    except ValueError as error:
        return ERRORS["INVALID_FORMAT"](str(error))

    fecha_str = request.args.get("fecha")
    hora_inicio_str = request.args.get("hora_inicio")
    hora_fin_str = request.args.get("hora_fin")
    if not fecha_str or not hora_inicio_str or not hora_fin_str:
        return ERRORS["MISSING_REQUIRED_FIELDS"]("fecha, hora_inicio y hora_fin son obligatorios.")

    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        if len(hora_inicio_str) not in (5, 8) or len(hora_fin_str) not in (5, 8):
            raise ValueError
        formato_inicio = "%H:%M" if len(hora_inicio_str) == 5 else "%H:%M:%S"
        formato_fin = "%H:%M" if len(hora_fin_str) == 5 else "%H:%M:%S"
        hora_inicio = datetime.strptime(hora_inicio_str, formato_inicio).time()
        hora_fin = datetime.strptime(hora_fin_str, formato_fin).time()
    except ValueError:
        return ERRORS["INVALID_FORMAT"]("Formato inválido de fecha u hora (esperado YYYY-MM-DD y HH:00[:00]).")

    # Las reglas del intervalo son las de una reserva nueva; si no se cumplen es una solicitud inválida (400)
    if hora_inicio.minute != 0 or hora_inicio.second != 0 or hora_fin.minute != 0 or hora_fin.second != 0:
        return ERRORS["INVALID_FORMAT"]("Las reservas deben iniciar y finalizar en horas en punto.")

    inicio_dt = datetime.combine(fecha, hora_inicio, tzinfo=TZ_ARG)
    fin_dt = datetime.combine(fecha, hora_fin, tzinfo=TZ_ARG)
    ahora = datetime.now(TZ_ARG)
    if inicio_dt <= ahora:
        return ERRORS["INVALID_FORMAT"]("La fecha y hora de inicio deben ser posteriores al momento actual.")
    if inicio_dt >= fin_dt:
        return ERRORS["INVALID_FORMAT"]("La hora de inicio debe ser anterior a la hora de fin.")

    duracion_horas = (fin_dt - inicio_dt).total_seconds() / 3600
    if duracion_horas < 1 or duracion_horas > 3:
        return ERRORS["INVALID_FORMAT"]("La duración de la reserva debe ser de entre 1 y 3 horas completas.")
    if inicio_dt.hour < 8 or fin_dt.hour > 23 or (fin_dt.hour == 23 and fin_dt.minute > 0):
        return ERRORS["INVALID_FORMAT"]("El intervalo debe encontrarse dentro del horario del club (08:00 a 23:00).")

    try:
        limit, offset = parsear_paginacion(
            request.args.get("_limit"),
            request.args.get("_offset")
        )
        id_deporte = parsear_entero_positivo(request.args.get("id_deporte"), "id_deporte")
        techada = parsear_booleano(request.args.get("techada"), "techada")
    except ValueError as error:
        return ERRORS["INVALID_FORMAT"](str(error))

    inicio_sql = inicio_dt.strftime("%Y-%m-%d %H:%M:%S")
    fin_sql = fin_dt.strftime("%Y-%m-%d %H:%M:%S")
    total = contar_canchas_disponibles_db(inicio_sql, fin_sql, id_deporte, techada)
    if total is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("Error al contar las canchas disponibles en la base de datos.")
    canchas = obtener_canchas_disponibles_db(
        inicio_sql, fin_sql, id_deporte, techada, limit, offset
    )
    if canchas is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("Error al consultar la disponibilidad en la base de datos.")

    # Sin canchas libres se responde 200 con arreglo vacío, según el enunciado
    links = build_hateoas_links(
        request.base_url, limit, offset, total, request.args.to_dict())
    return jsonify({"canchas": canchas, "_links": links}), 200
