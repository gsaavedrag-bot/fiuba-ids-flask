from flask import jsonify
from services.deportes_services import listar_deportes_db

def listar_deportes_controller():
    deportes = listar_deportes_db()
    if not deportes:
        return "", 204
    return jsonify({"deportes": deportes}), 200