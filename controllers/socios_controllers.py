# controllers/socios_controllers.py
from flask import jsonify, request
from services.socios_services import obtener_todos_los_socios, guardar_nuevo_socio


def listar_socios_controller():
    socios = obtener_todos_los_socios()
    return jsonify({"socios": socios}), 200


def crear_socio_controller():
    data = request.get_json(silent=True) or {}
    nombre = data.get('nombre')
    email = data.get('email')

    if not nombre or not email:
        return jsonify({"error": "nombre y email son requeridos"}), 400

    resultado = guardar_nuevo_socio(nombre, email)
    if resultado is False:
        return jsonify({"error": "No se pudo guardar el socio"}), 500

    return jsonify({"mensaje": "Socio creado correctamente"}), 201
