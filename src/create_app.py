from flask import Flask
from src.api.controllers import setup_blueprints

def create_app(config):

    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app = setup_blueprints(app)


    return app