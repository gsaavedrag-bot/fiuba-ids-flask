from flask import Blueprint
from controllers.deportes_controllers import listar_deportes_controller

# Blueprint que agrupa los endpoints relacionados con deportes.
deportes_bp = Blueprint('deportes_bp', __name__)

# La ruta completa incluye el prefijo /deportes registrado en app.py.
@deportes_bp.route('/', methods=['GET'])
def listar_deportes():
    return listar_deportes_controller()