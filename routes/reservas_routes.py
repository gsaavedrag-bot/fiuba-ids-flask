# routes/reservas_routes.py
from flask import Blueprint
from controllers.reservas_controllers import (
    listar_reservas_controller,
    crear_reserva_controller,
    obtener_reserva_controller,
    actualizar_estado_controller
)

# Blueprint para agrupar los endpoints de reservas
reservas_bp = Blueprint('reservas_bp', __name__)


@reservas_bp.route('', methods=['GET'])
@reservas_bp.route('/', methods=['GET'])
def listar_reservas():
    return listar_reservas_controller()


# POST solicita la creación de una reserva
@reservas_bp.route('', methods=['POST'])
@reservas_bp.route('/', methods=['POST'])
def crear_reserva():
    return crear_reserva_controller()


# GET /reservas/{id} devuelve el detalle de una reserva específica
@reservas_bp.route('/<int:reserva_id>', methods=['GET'])
def obtener_reserva(reserva_id):
    return obtener_reserva_controller(reserva_id)


# PUT /reservas/{id}/estado cambia el estado respetando las transiciones
@reservas_bp.route('/<int:reserva_id>/estado', methods=['PUT'])
def actualizar_estado_reserva(reserva_id):
    return actualizar_estado_controller(reserva_id)
