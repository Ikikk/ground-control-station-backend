from .engine_controller import drone_api as engine_controller_blueprint
from .page_controller import rest_api as page_controller_blueprint


def setup_blueprints(app) -> None:
    app.register_blueprint(engine_controller_blueprint, url_prefix="/api")
    app.register_blueprint(page_controller_blueprint, url_prefix="/")
    return app


__all__ = ['setup_blueprints']