from flask import Blueprint
from controllers.deportes_controllers import listar_deportes_controller

deportes_bp = Blueprint('deportes_bp', __name__)

@deportes_bp.route('/', methods=['GET'])
def listar_deportes():
    return listar_deportes_controller()