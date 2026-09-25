from flask import jsonify
from services.deportes_services import listar_deportes_db

def listar_deportes_controller():
    """Obtiene los deportes y construye la respuesta HTTP en formato JSON."""
    deportes = listar_deportes_db()
    if not deportes:
        # 204 indica que la consulta no encontró elementos para devolver.
        return "", 204
    return jsonify({"deportes": deportes}), 200