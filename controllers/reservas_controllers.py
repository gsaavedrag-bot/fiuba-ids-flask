# controllers/reservas_controllers.py
from flask import jsonify, request
from services.reservas_services import obtener_reservas_db, crear_reserva_db


def listar_reservas_controller():
    reservas = obtener_reservas_db()
    return jsonify({"reservas": reservas}), 200


def crear_reserva_controller():
    data = request.get_json(silent=True) or {}

    if not data:
        return jsonify({"error": "No se recibieron datos"}), 400

    ok = crear_reserva_db(data)
    if not ok:
        return jsonify({"error": "No se pudo crear la reserva"}), 500

    return jsonify({"mensaje": "Reserva creada correctamente"}), 201
