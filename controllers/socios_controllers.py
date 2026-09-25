# controllers/socios_controllers.py
from flask import jsonify, request
from services.socios_services import obtener_todos_los_socios, guardar_nuevo_socio


def listar_socios_controller():
    """Devuelve en JSON la lista de socios activos."""
    socios = obtener_todos_los_socios()
    return jsonify({"socios": socios}), 200


def crear_socio_controller():
    """Valida los datos básicos de entrada y solicita crear un socio."""
    # silent=True evita una excepción si el cuerpo no contiene JSON válido.
    data = request.get_json(silent=True) or {}
    nombre = data.get('nombre')
    email = data.get('email')

    # Ambos campos son obligatorios para registrar un socio.
    if not nombre or not email:
        return jsonify({"error": "nombre y email son requeridos"}), 400

    # La capa de servicio realiza la inserción en MySQL.
    resultado = guardar_nuevo_socio(nombre, email)
    if resultado is False:
        return jsonify({"error": "No se pudo guardar el socio"}), 500

    return jsonify({"mensaje": "Socio creado correctamente"}), 201
