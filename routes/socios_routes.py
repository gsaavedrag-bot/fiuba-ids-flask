# routes/socios_routes.py
from flask import Blueprint
from controllers.socios_controllers import (
    actualizar_socio_controller,
    crear_socio_controller,
    obtener_socio_controller,
    listar_socios_controller,
)

# Blueprint para agrupar los endpoints de socios.
socios_bp = Blueprint('socios_bp', __name__)

# GET /socios/ lista los socios.
@socios_bp.route('/', methods=['GET'])
def listar_socios():
    return listar_socios_controller()
# GET /socios/{id} devuelve el detalle de un socio específico.
@socios_bp.route('/<int:socio_id>', methods=['GET'])
def obtener_socio(socio_id):
    return obtener_socio_controller(socio_id)

# POST /socios/ solicita la creación de un socio.
@socios_bp.route('/', methods=['POST'])
def crear_socio():
    return crear_socio_controller()

# PATCH /socios/{id} actualiza los datos de un socio.
@socios_bp.route('/<int:socio_id>', methods=['PATCH'])
def actualizar_socio(socio_id):
    return actualizar_socio_controller(socio_id)
