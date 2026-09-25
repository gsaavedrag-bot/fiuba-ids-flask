# routes/socios_routes.py
from flask import Blueprint
from controllers.socios_controllers import listar_socios_controller, crear_socio_controller

# Blueprint para agrupar los endpoints de socios.
socios_bp = Blueprint('socios_bp', __name__)

# GET /socios/ lista los socios.
@socios_bp.route('/', methods=['GET'])
def listar_socios():
    return listar_socios_controller()

# POST /socios/ registra un socio a partir del cuerpo de la solicitud.
@socios_bp.route('/', methods=['POST'])
def crear_socio():
    return crear_socio_controller()
