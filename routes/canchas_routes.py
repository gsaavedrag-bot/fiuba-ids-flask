# routes/canchas_routes.py
from flask import Blueprint
# Importamos los controladores que atienden cada ruta
from controllers.canchas_controllers import (
    listar_canchas_controller,
    crear_cancha_controller
)

canchas_bp = Blueprint('canchas_bp', __name__)

# Mapeo de rutas a las funciones del controller
@canchas_bp.route('/', methods=['GET'])
def listar():
    return listar_canchas_controller()

@canchas_bp.route('/', methods=['POST'])
def crear():
    return crear_cancha_controller()