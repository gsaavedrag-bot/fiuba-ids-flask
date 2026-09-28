# routes/socios_routes.py
from flask import Blueprint
from controllers.socios_controllers import (
    listar_socios_controller,
    crear_socio_controller,
    obtener_socio_controller,
    actualizar_socio_controller
)

socios_bp = Blueprint('socios_bp', __name__)

@socios_bp.route('', methods=['GET'])
@socios_bp.route('/', methods=['GET'])
def listar_socios():
    return listar_socios_controller()

@socios_bp.route('/<int:socio_id>', methods=['GET'])
def obtener_socio(socio_id):
    return obtener_socio_controller(socio_id)

@socios_bp.route('', methods=['POST'])
@socios_bp.route('/', methods=['POST'])
def crear_socio():
    return crear_socio_controller()

@socios_bp.route('/<int:socio_id>', methods=['PATCH'])
def actualizar_socio(socio_id):
    return actualizar_socio_controller(socio_id)
