# controllers/socios_controllers.py
import re
from flask import jsonify, request
from errors import ERRORS
from services.socios_services import (
    obtener_todos_los_socios,
    obtener_socio_por_id_db,
    obtener_socio_por_email_db,
    guardar_nuevo_socio,
    actualizar_socio_db
)

EMAIL_REGEX = re.compile(r"^[\w.-]+@[\w.-]+\.\w+$")


def listar_socios_controller():
    """Devuelve en JSON la lista de socios activos."""
    socios = obtener_todos_los_socios()
    if socios is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("Error al consultar socios en la base de datos.")
    return jsonify({"socios": socios}), 200


def crear_socio_controller():
    """Válida los campos requeridos, formato y unicidad de email antes de dar de alta."""
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre")
    email = data.get("email")

    if not nombre or not email:
        return ERRORS["MISSING_REQUIRED_FIELDS"]("nombre y email son obligatorios.")

    if not isinstance(nombre, str) or not nombre.strip():
        return ERRORS["INVALID_FORMAT"]("El nombre debe ser un texto no vacío.")

    if not isinstance(email, str) or not EMAIL_REGEX.match(email.strip()):
        return ERRORS["INVALID_FORMAT"]("El formato del correo electrónico no es válido.")

    nombre_limpio = nombre.strip()
    email_limpio = email.strip().lower()

    # Comprobación de duplicados (409 Conflict)
    socio_existente = obtener_socio_por_email_db(email_limpio)
    if socio_existente:
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

    # 1. Verificar existencia del socio (404 Not Found)
    socio_actual = obtener_socio_por_id_db(socio_id)
    if not socio_actual:
        return ERRORS["NOT_FOUND"](f"No se encontró el socio con id {socio_id}.")

    campos_a_actualizar = {}

    # 2. Validación de nombre (si viene)
    if "nombre" in data:
        nombre = data["nombre"]
        if not isinstance(nombre, str) or not nombre.strip():
            return ERRORS["INVALID_FORMAT"]("El campo 'nombre' debe ser un texto no vacío.")
        campos_a_actualizar["nombre"] = nombre.strip()

    # 3. Validación de email (si viene)
    if "email" in data:
        email = data["email"]
        if not isinstance(email, str) or not EMAIL_REGEX.match(email.strip()):
            return ERRORS["INVALID_FORMAT"]("El formato del correo electrónico no es válido.")

        email_limpio = email.strip().lower()
        # Verificar que ningún otro socio tenga ese email (409 Conflict)
        if obtener_socio_por_email_db(email_limpio, excluir_id=socio_id):
            return ERRORS["CONFLICT"](f"El correo '{email_limpio}' ya pertenece a otro socio registrado.")
        campos_a_actualizar["email"] = email_limpio

    # 4. Validación de activo (si viene)
    if "activo" in data:
        activo = data["activo"]
        if not isinstance(activo, bool):
            return ERRORS["INVALID_FORMAT"]("El campo 'activo' debe ser un booleano (true o false).")
        campos_a_actualizar["activo"] = activo

    if not campos_a_actualizar:
        return ERRORS["INVALID_FORMAT"]("No se enviaron campos válidos para actualizar ('nombre', 'email', 'activo').")

    # 5. Ejecutar la actualización en MySQL
    filas_modificadas = actualizar_socio_db(socio_id, campos_a_actualizar)
    if filas_modificadas is None:
        return ERRORS["INTERNAL_SERVER_ERROR"]("Error al actualizar el socio en la base de datos.")

    # El contrato swagger.yaml exige 204 No Content para PATCH /socios/{id}
    return "", 204
