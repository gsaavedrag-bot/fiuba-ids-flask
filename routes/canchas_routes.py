# routes/canchas_routes.py
from flask import Blueprint
# Importamos los controladores que atienden cada ruta
from controllers.canchas_controllers import (
    listar_canchas_controller,
    crear_cancha_controller
)

# Blueprint para agrupar los endpoints de canchas.
canchas_bp = Blueprint('canchas_bp', __name__)

# GET lista las canchas y POST recibe los datos de una nueva cancha.
@canchas_bp.route('/', methods=['GET'])
def listar():
    return listar_canchas_controller()

@canchas_bp.route('/', methods=['POST'])
def crear():
    return crear_cancha_controller()