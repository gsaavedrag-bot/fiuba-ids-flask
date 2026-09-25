# controllers/canchas_controllers.py
from flask import jsonify, request
# La capa de servicio separa las operaciones de datos de la respuesta HTTP.
from services.canchas_services import obtener_canchas_db, crear_cancha_db

def listar_canchas_controller():
    """Prepara la respuesta para el listado de canchas."""
    canchas = obtener_canchas_db()
    # El servicio todavía es un placeholder; este estado lo hace explícito.
    return jsonify({"canchas": canchas, "status": "pendiente de implementacion"}), 200

def crear_cancha_controller():
    """Recibe los datos JSON y delega la creación al servicio."""
    datos = request.get_json()
    crear_cancha_db(datos)
    # La persistencia y la validación todavía no están implementadas.
    return jsonify({"mensaje": "Endpoint listo para implementar"}), 201