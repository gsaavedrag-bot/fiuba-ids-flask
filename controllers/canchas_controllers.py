# controllers/canchas_controllers.py
from datetime import datetime
from flask import jsonify, request
from errors import ERRORS
from helpers import build_hateoas_links, parsear_booleano, parsear_paginacion, TZ_ARG
from services.canchas_services import (
    obtener_canchas_db,
    crear_cancha_db,
    obtener_canchas_disponibles_db,
    contar_canchas_db
)

def listar_canchas_controller():
    try:
        limit, offset = parsear_paginacion(
            request.args.get("_limit"),
            request.args.get("_offset")
        )

        filtros: dict = {}
        id_deporte = request.args.get("id_deporte")
        if id_deporte is not None:
            filtros["id_deporte"] = int(id_deporte)
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


def crear_cancha_controller():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return ERRORS["MISSING_REQUIRED_FIELDS"]("El cuerpo JSON es obligatorio.")

    requeridos = ("nombre", "id_deporte", "precio_hora")
    if any(campo not in data for campo in requeridos):
        return ERRORS["MISSING_REQUIRED_FIELDS"]("nombre, id_deporte y precio_hora son obligatorios.")

    nombre = data["nombre"]
    id_deporte = data["id_deporte"]
    precio_hora = data["precio_hora"]
    if not isinstance(nombre, str) or not nombre.strip():
        return ERRORS["INVALID_FORMAT"]("nombre debe ser un texto no vacío.")
    if isinstance(id_deporte, bool) or not isinstance(id_deporte, int):
        return ERRORS["INVALID_FORMAT"]("id_deporte debe ser un entero.")
    if isinstance(precio_hora, bool) or not isinstance(precio_hora, int) or precio_hora <= 0:
        return ERRORS["INVALID_FORMAT"]("precio_hora debe ser un entero mayor a cero.")

    techada = data.get("techada", False)
    activa = data.get("activa", True)
    if not isinstance(techada, bool) or not isinstance(activa, bool):
        return ERRORS["INVALID_FORMAT"]("techada y activa deben ser valores booleanos.")

    cancha_id, error = crear_cancha_db({
        "nombre": nombre.strip(),
        "id_deporte": id_deporte,
        "precio_hora": precio_hora,
        "techada": techada,
        "activa": activa
    })
    if error == "DEPORTE_NOT_FOUND":
        return ERRORS["NOT_FOUND"](f"No existe el deporte con id {id_deporte}.")
    if error or not cancha_id:
        return ERRORS["INTERNAL_SERVER_ERROR"]("No se pudo crear la cancha en la base de datos.")
    return jsonify({"id": cancha_id, "mensaje": "Cancha creada correctamente."}), 201


def consultar_disponibles_controller():
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

    if hora_inicio.minute != 0 or hora_inicio.second != 0 or hora_fin.minute != 0 or hora_fin.second != 0:
        return ERRORS["INVALID_FORMAT"]("Las reservas deben iniciar y finalizar en horas en punto.")

    inicio_dt = datetime.combine(fecha, hora_inicio, tzinfo=TZ_ARG)
    fin_dt = datetime.combine(fecha, hora_fin, tzinfo=TZ_ARG)
    ahora = datetime.now(TZ_ARG)
    if inicio_dt <= ahora:
        return ERRORS["CONFLICT"]("La fecha y hora de inicio deben ser posteriores al momento actual.")
    if inicio_dt >= fin_dt:
        return ERRORS["INVALID_FORMAT"]("La hora de inicio debe ser anterior a la hora de fin.")

    duracion_horas = (fin_dt - inicio_dt).total_seconds() / 3600
    if duracion_horas < 1 or duracion_horas > 3:
        return ERRORS["CONFLICT"]("La duración de la reserva debe ser de entre 1 y 3 horas completas.")
    if inicio_dt.hour < 8 or fin_dt.hour > 23 or (fin_dt.hour == 23 and fin_dt.minute > 0):
        return ERRORS["CONFLICT"]("El intervalo debe encontrarse dentro del horario del club (08:00 a 23:00).")

    try:
        limit, offset = parsear_paginacion(
            request.args.get("_limit"),
            request.args.get("_offset")
        )
        id_deporte_raw = request.args.get("id_deporte")
        id_deporte = int(id_deporte_raw) if id_deporte_raw is not None else None
        techada = parsear_booleano(request.args.get("techada"), "techada")
    except ValueError as error:
        return ERRORS["INVALID_FORMAT"](str(error))

    inicio_sql = inicio_dt.strftime("%Y-%m-%d %H:%M:%S")
    fin_sql = fin_dt.strftime("%Y-%m-%d %H:%M:%S")
    canchas = obtener_canchas_disponibles_db(
        inicio_sql, fin_sql, id_deporte, techada, limit, offset
    )
    if canchas is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("Error al consultar la disponibilidad en la base de datos.")
    return jsonify({"canchas": canchas}), 200