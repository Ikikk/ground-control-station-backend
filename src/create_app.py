from flask import Flask
from flask_cors import CORS
from src.api.controllers import setup_blueprints

def create_app(config):

    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app = setup_blueprints(app)
    CORS(app, origins="http://localhost:3000", allow_headers=["Content-Type"])

    return app