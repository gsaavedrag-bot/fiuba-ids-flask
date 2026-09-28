# controllers/socios_controllers.py
from flask import jsonify, request
from services.socios_services import (
    actualizar_socio,
    guardar_nuevo_socio,
    obtener_socio_por_id,
    obtener_todos_los_socios,
)

# GET /socios/ lista los socios.
def listar_socios_controller():
    """Devuelve en JSON la lista de socios activos."""
    socios = obtener_todos_los_socios()
    return jsonify({"socios": socios}), 200

# GET /socios/{id} devuelve el detalle de un socio específico.
def obtener_socio_controller(socio_id):
    """Devuelve los detalles de un socio específico por ID."""
    if socio_id <= 0:
        return jsonify({"error": "El id debe ser positivo"}), 400

    socio, error = obtener_socio_por_id(socio_id)
    if error == "NOT_FOUND":
        return jsonify({"error": "No existe el socio solicitado"}), 404
    elif error:
        return jsonify({"error": "No se pudo consultar el socio"}), 500

    return jsonify(socio), 200


def crear_socio_controller():
    """Valida los datos básicos de entrada y solicita crear un socio."""
    # silent=True evita una excepción si el cuerpo no contiene JSON válido.
    data = request.get_json(silent=True)
    if type(data) is not dict:
        return jsonify({"error": "Los datos enviados no son validos"}), 400
    elif set(data) - {"nombre", "email"}:
        return jsonify({"error": "Solo se permiten nombre y email"}), 400
    
    nombre = data.get('nombre')
    email = data.get('email')

    # Ambos campos son obligatorios para registrar un socio.
    if not nombre or not email:
        return jsonify({"error": "nombre y email son requeridos"}), 400

    if type(nombre) is not str or not nombre.strip():
        return jsonify({"error": "nombre debe ser texto y no estar vacio"}), 400
    nombre = nombre.strip() 

    if type(email) is not str:
        return jsonify({"error": "email debe ser texto"}), 400
    email = email.strip()
    email = email.lower()
    partes_email = email.split("@")
    if (
        len(partes_email) != 2
        or not partes_email[0]
        or "." not in partes_email[1]
        or " " in email
    ):
        return jsonify({"error": "email no tiene un formato valido"}), 400

    # La capa de servicio realiza la inserción en MySQL.
    resultado = guardar_nuevo_socio(nombre, email)
    socio_id = resultado[0]
    error = resultado[1]
    if error == "EMAIL_EXISTS":
        return jsonify({"error": "Ya existe un socio con ese email"}), 409
    elif error or socio_id is None:
        return jsonify({"error": "No se pudo guardar el socio"}), 500

    return jsonify({"mensaje": "Socio creado correctamente"}), 201

# PATCH /socios/{id} actualiza parcialmente un socio.
def actualizar_socio_controller(socio_id):
    """Actualiza parcialmente un socio."""
    if socio_id <= 0:
        return jsonify({"error": "El id debe ser positivo"}), 400
    
    data = request.get_json(silent=True)
    if type(data) is not dict:
        return jsonify({"error": "Los datos enviados no son validos"}), 400
    elif not data:
        return jsonify({"error": "Se requiere al menos un campo para actualizar"}), 400
    elif set(data) - {"nombre", "email", "activo"}:
        return jsonify({"error": "Solo se permiten nombre, email y activo"}), 400
    
    cambios = {} # Diccionario para almacenar los cambios validados
    for campo, valor in data.items():
        if campo == "nombre": # Validación de nombre
            if type(valor) is not str or not valor.strip():
                return jsonify({"error": "nombre debe ser texto y no estar vacio"}), 400
            cambios[campo] = valor.strip()

        elif campo == "email": # Validación de formato de email
            if type(valor) is not str or not valor.strip():
                return jsonify({"error": "email debe ser texto y no estar vacio"}), 400
            email = valor.strip().lower()
            partes_email = email.split("@")
            if (
                len(partes_email) != 2
                or not partes_email[0]
                or "." not in partes_email[1]
                or " " in email
            ):
                return jsonify({"error": "email no tiene un formato valido"}), 400
            cambios[campo] = email
            
        else:
            if type(valor) is not bool:
                return jsonify({"error": "activo debe ser true o false"}), 400
            cambios[campo] = valor

    socio, error = obtener_socio_por_id(socio_id) # Verifica que el socio exista antes de actualizar.
    if error == "NOT_FOUND":
        return jsonify({"error": "No existe el socio solicitado"}), 404
    elif error:
        return jsonify({"error": "No se pudo consultar el socio"}), 500

    error = actualizar_socio(socio_id, cambios)
    if error == "EMAIL_EXISTS":
        return jsonify({"error": "Ya existe un socio con ese email"}), 409
    elif error:
        return jsonify({"error": "No se pudo actualizar el socio"}), 500

    socio.update(cambios) # Actualiza el diccionario con los cambios realizados
    return jsonify(socio), 200
