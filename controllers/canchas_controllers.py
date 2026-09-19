# controllers/canchas_controllers.py
from flask import jsonify, request
# Importamos las funciones correspondientes de services
from services.canchas_services import obtener_canchas_db, crear_cancha_db

def listar_canchas_controller():
    canchas = obtener_canchas_db()
    return jsonify({"canchas": canchas, "status": "pendiente de implementacion"}), 200

def crear_cancha_controller():
    datos = request.get_json()
    crear_cancha_db(datos)
    return jsonify({"mensaje": "Endpoint listo para implementar"}), 201