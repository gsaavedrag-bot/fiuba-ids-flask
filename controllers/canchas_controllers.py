# controllers/canchas_controllers.py
from datetime import datetime, timezone, timedelta
from flask import jsonify, request
from errors import ERRORS
from services.canchas_services import (
    obtener_canchas_db,
    crear_cancha_db,
    obtener_canchas_disponibles_db,
    contar_canchas_disponibles_db
)

TZ_ARG = timezone(timedelta(hours=-3))


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
