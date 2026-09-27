# controllers/canchas_controllers.py
from datetime import datetime, timezone, timedelta
from flask import jsonify, request
from errors import ERRORS
from services.canchas_services import (
    obtener_canchas_db,
    crear_cancha_db,
    obtener_canchas_disponibles_db,
    contar_canchas_db
)

TZ_ARG = timezone(timedelta(hours=-3))


def _parsear_booleano(valor: str | None, nombre: str):
    if valor is None:
        return None
    if valor.lower() in ("true", "1"):
        return True
    if valor.lower() in ("false", "0"):
        return False
    raise ValueError(f"{nombre} debe ser true o false.")


def _construir_links(base_url: str, limit: int, offset: int, total: int, params: dict):
    clean_params = {k: v for k, v in params.items() if k not in ("_limit", "_offset")}

    def generar_url(page_offset: int):
        query_params = clean_params | {"_offset": page_offset, "_limit": limit}
        query = "&".join(f"{key}={value}" for key, value in query_params.items())
        return f"{base_url}?{query}"

    last_offset = max(0, ((total - 1) // limit) * limit) if total else 0
    links = {
        "_first": {"href": generar_url(0)},
        "_last": {"href": generar_url(last_offset)}
    }
    if offset > 0:
        links["_prev"] = {"href": generar_url(max(0, offset - limit))}
    if offset + limit < total:
        links["_next"] = {"href": generar_url(offset + limit)}
    return links


def listar_canchas_controller():
    try:
        limit = int(request.args.get("_limit", 10))
        offset = int(request.args.get("_offset", 0))
        if limit < 1 or limit > 100 or offset < 0:
            return ERRORS["INVALID_FORMAT"]("_limit debe estar entre 1 y 100 y _offset debe ser >= 0.")

        filtros: dict[str, int | str | bool] = {}
        id_deporte = request.args.get("id_deporte")
        if id_deporte is not None:
            filtros["id_deporte"] = int(id_deporte)
        nombre = request.args.get("nombre")
        if nombre is not None:
            filtros["nombre"] = nombre
        for campo in ("techada", "activa"):
            valor = _parsear_booleano(request.args.get(campo), campo)
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

    links = _construir_links(
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

    try:
        techada = data.get("techada", False)
        activa = data.get("activa", True)
        if not isinstance(techada, bool) or not isinstance(activa, bool):
            raise ValueError("techada y activa deben ser valores booleanos.")
    except ValueError as error:
        return ERRORS["INVALID_FORMAT"](str(error))

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
        # Validar horas en punto (ej. 18:00 o 18:00:00)
        h_ini = datetime.strptime(hora_inicio_str[:5], "%H:%M").time()
        h_fin = datetime.strptime(hora_fin_str[:5], "%H:%M").time()
        f = datetime.strptime(fecha_str, "%Y-%m-%d").date()

        if h_ini.minute != 0 or h_fin.minute != 0:
            return ERRORS["INVALID_FORMAT"]("Las reservas deben iniciar y finalizar en horas en punto.")

        inicio_dt = datetime(f.year, f.month, f.day,
                             h_ini.hour, 0, 0, tzinfo=TZ_ARG)
        fin_dt = datetime(f.year, f.month, f.day,
                          h_fin.hour, 0, 0, tzinfo=TZ_ARG)
    except ValueError:
        return ERRORS["INVALID_FORMAT"]("Formato inválido de fecha u hora (esperado YYYY-MM-DD y HH:00:00).")

    # Reglas de negocio: 08:00 a 23:00, duración entre 1 y 3 horas, horario futuro
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

    # Paginación y filtros opcionales
    try:
        limit = int(request.args.get("_limit", 10))
        offset = int(request.args.get("_offset", 0))
    except ValueError:
        return ERRORS["INVALID_FORMAT"]("_limit y _offset deben ser números enteros.")

    id_deporte = request.args.get("id_deporte", type=int)
    techada_raw = request.args.get("techada")
    techada = None
    if techada_raw is not None:
        techada = techada_raw.lower() in ("true", "1")

    inicio_sql = inicio_dt.strftime("%Y-%m-%d %H:%M:%S")
    fin_sql = fin_dt.strftime("%Y-%m-%d %H:%M:%S")

    canchas = obtener_canchas_disponibles_db(
        inicio_sql, fin_sql, id_deporte, techada, limit, offset)
    if canchas is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("Error al consultar la disponibilidad en la base de datos.")

    return jsonify({"canchas": canchas}), 200
