# routes/socios_routes.py
from flask import Blueprint
from controllers.socios_controllers import listar_socios_controller, crear_socio_controller

socios_bp = Blueprint('socios_bp', __name__)

@socios_bp.route('/', methods=['GET'])
def listar_socios():
    return listar_socios_controller()

@socios_bp.route('/', methods=['POST'])
def crear_socio():
    return crear_socio_controller()
