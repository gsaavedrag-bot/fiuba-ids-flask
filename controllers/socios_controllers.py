# controllers/socios_controllers.py
from flask import jsonify, request
from errors import ERRORS
from helpers import (
    es_email_valido,
    parsear_paginacion,
    parsear_booleano,
    build_hateoas_links
)
from services.socios_services import (
    obtener_todos_los_socios,
    contar_socios_db,
    obtener_socio_por_id_db,
    obtener_socio_por_email_db,
    guardar_nuevo_socio,
    actualizar_socio_db
)


def listar_socios_controller():
    try:
        limit, offset = parsear_paginacion(
            request.args.get("_limit"),
            request.args.get("_offset")
        )

        filtros = {}

        nombre = request.args.get("nombre")
        if nombre is not None:
            filtros["nombre"] = nombre

        activo = parsear_booleano(
            request.args.get("activo"),
            "activo"
        )
        if activo is not None:
            filtros["activo"] = activo

    except ValueError as error:
        return ERRORS["INVALID_FORMAT"](str(error))

    total = contar_socios_db(filtros)

    if total is None:
        return ERRORS["INTERNAL_SERVER_ERROR"](
            "Error al contar socios en la base de datos."
        )

    links = build_hateoas_links(
        request.base_url,
        limit,
        offset,
        total,
        request.args.to_dict()
    )

    socios = obtener_todos_los_socios(filtros, limit, offset)

    if socios is None:
        return ERRORS["INTERNAL_SERVER_ERROR"](
            "Error al consultar socios en la base de datos."
        )

    return jsonify({
        "socios": socios,
        "_links": links
    }), 200


def obtener_socio_controller(socio_id: int):
    socio = obtener_socio_por_id_db(socio_id)

    if socio is None:
        return ERRORS["NOT_FOUND"](
            f"No se encontró el socio con id {socio_id}."
        )

    return jsonify(socio), 200


def crear_socio_controller():
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre")
    email = data.get("email")

    if not nombre or not email:
        return ERRORS["MISSING_REQUIRED_FIELDS"]("nombre y email son obligatorios.")

    if not isinstance(nombre, str) or not nombre.strip():
        return ERRORS["INVALID_FORMAT"]("El nombre debe ser un texto no vacío.")

    if not isinstance(email, str) or not es_email_valido(email):
        return ERRORS["INVALID_FORMAT"]("El formato del correo electrónico no es válido.")

    nombre_limpio = nombre.strip()
    email_limpio = email.strip().lower()

    if obtener_socio_por_email_db(email_limpio):
        return ERRORS["CONFLICT"](f"Ya existe un socio registrado con el correo '{email_limpio}'.")

    nuevo_id = guardar_nuevo_socio(nombre_limpio, email_limpio)
    if not nuevo_id:
        return ERRORS["INTERNAL_SERVER_ERROR"]("No se pudo registrar el socio en la base de datos.")

    respuesta = {
        "id": nuevo_id,
        "nombre": nombre_limpio,
        "email": email_limpio,
        "activo": True
    }
    return jsonify(respuesta), 201


def actualizar_socio_controller(socio_id: int):
    """Actualiza parcialmente un socio (nombre, email, activo)."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return ERRORS["MISSING_REQUIRED_FIELDS"]("El cuerpo JSON no puede estar vacío.")

    socio_actual = obtener_socio_por_id_db(socio_id)
    if not socio_actual:
        return ERRORS["NOT_FOUND"](f"No se encontró el socio con id {socio_id}.")

    campos_a_actualizar = {}

    if "nombre" in data:
        nombre = data["nombre"]
        if not isinstance(nombre, str) or not nombre.strip():
            return ERRORS["INVALID_FORMAT"]("El campo 'nombre' debe ser un texto no vacío.")
        campos_a_actualizar["nombre"] = nombre.strip()

    if "email" in data:
        email = data["email"]
        if not isinstance(email, str) or not es_email_valido(email):
            return ERRORS["INVALID_FORMAT"]("El formato del correo electrónico no es válido.")

        email_limpio = email.strip().lower()
        if obtener_socio_por_email_db(email_limpio, excluir_id=socio_id):
            return ERRORS["CONFLICT"](f"El correo '{email_limpio}' ya pertenece a otro socio registrado.")
        campos_a_actualizar["email"] = email_limpio

    if "activo" in data:
        activo = data["activo"]
        if not isinstance(activo, bool):
            return ERRORS["INVALID_FORMAT"]("El campo 'activo' debe ser un booleano (true o false).")
        campos_a_actualizar["activo"] = activo

    if not campos_a_actualizar:
        return ERRORS["INVALID_FORMAT"]("No se enviaron campos válidos para actualizar ('nombre', 'email', 'activo').")

    filas_modificadas = actualizar_socio_db(socio_id, campos_a_actualizar)
    if filas_modificadas is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("Error al actualizar el socio en la base de datos.")

    return "", 204
