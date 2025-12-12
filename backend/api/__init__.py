from .routes.health import health_bp

def create_api_blueprints(app):
    app.register_blueprint(health_bp, url_prefix="/api")

