# routes/canchas_routes.py
from flask import Blueprint
from controllers.canchas_controllers import (
    listar_canchas_controller,
    crear_cancha_controller,
    consultar_disponibles_controller,
    obtener_cancha_controller,
    actualizar_cancha_controller,
    eliminar_cancha_controller
)

canchas_bp = Blueprint('canchas_bp', __name__)

@canchas_bp.route('', methods=['GET'])
@canchas_bp.route('/', methods=['GET'])
def listar():
    return listar_canchas_controller()

@canchas_bp.route('', methods=['POST'])
@canchas_bp.route('/', methods=['POST'])
def crear():
    return crear_cancha_controller()

@canchas_bp.route('/disponibles', methods=['GET'])
@canchas_bp.route('/disponibles/', methods=['GET'])
def consultar_disponibles():
    return consultar_disponibles_controller()

@canchas_bp.route('/<int:cancha_id>', methods=['GET'])
def obtener_cancha(cancha_id):
    return obtener_cancha_controller(cancha_id)

@canchas_bp.route('/<int:cancha_id>', methods=['PATCH'])
def actualizar_cancha(cancha_id):
    return actualizar_cancha_controller(cancha_id)

@canchas_bp.route('/<int:cancha_id>', methods=['DELETE'])
def eliminar_cancha(cancha_id):
    return eliminar_cancha_controller(cancha_id)
