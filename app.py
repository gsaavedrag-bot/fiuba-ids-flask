from flask import Flask
from routes.deportes_routes import deportes_bp
from routes.canchas_routes import canchas_bp
from routes.socios_routes import socios_bp
from routes.reservas_routes import reservas_bp

app = Flask(__name__)

# Prefijos definidos en swagger.yaml
app.register_blueprint(deportes_bp, url_prefix='/deportes')
app.register_blueprint(canchas_bp, url_prefix='/canchas')
app.register_blueprint(socios_bp, url_prefix='/socios')
app.register_blueprint(reservas_bp, url_prefix='/reservas')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
