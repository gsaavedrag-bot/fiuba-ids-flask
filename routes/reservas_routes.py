# routes/reservas_routes.py
from flask import Blueprint
from controllers.reservas_controllers import listar_reservas_controller, crear_reserva_controller

reservas_bp = Blueprint('reservas_bp', __name__)

@reservas_bp.route('/', methods=['GET'])
def listar_reservas():
    return listar_reservas_controller()

@reservas_bp.route('/', methods=['POST'])
def crear_reserva():
    return crear_reserva_controller()
