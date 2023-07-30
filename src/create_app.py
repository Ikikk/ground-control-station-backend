from flask import Flask
from src.api.controllers import setup_blueprints

def create_app(
    config
):

    app = Flask(__name__)
    app = setup_blueprints(app)

    return app