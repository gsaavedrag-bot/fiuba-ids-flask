from flask import Flask
from routes.canchas_routes import canchas_bp
# from routes.socios_routes import socios_bp
# from routes.reservas_routes import reservas_bp

app = Flask(__name__)

# Registro del Blueprint
app.register_blueprint(canchas_bp, url_prefix='/canchas')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
