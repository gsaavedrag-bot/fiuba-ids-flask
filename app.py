from dotenv import load_dotenv
load_dotenv()
import os

from flask import Flask, jsonify
from routes.deportes_routes import deportes_bp
from routes.canchas_routes import canchas_bp
from routes.socios_routes import socios_bp
from routes.reservas_routes import reservas_bp

app = Flask(__name__)

app.register_blueprint(deportes_bp, url_prefix='/deportes')
app.register_blueprint(canchas_bp, url_prefix='/canchas')
app.register_blueprint(socios_bp, url_prefix='/socios')
app.register_blueprint(reservas_bp, url_prefix='/reservas')

@app.errorhandler(404)
def ruta_no_encontrada(e):
    return jsonify({"errors": [{
        "code": 404,
        "message": "La ruta solicitada no existe.",
        "level": "error",
        "description": "Verifique la URL y que los identificadores sean enteros positivos."
    }]}), 404


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT') or 5000)
    if os.getenv('ENV') == 'dev':
        app.run(debug=True, port=port)
    else:
        app.run(debug=False, host='0.0.0.0', port=port)