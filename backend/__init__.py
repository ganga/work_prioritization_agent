from flask import Flask
from .api import create_api_blueprints

def create_app():
    app = Flask(__name__)
    create_api_blueprints(app)
    return app

