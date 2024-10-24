from datetime import timedelta
from http.client import HTTPException
from flask import Flask
from app.db import db
import os
from app.utils.request import generate_response
from app.routes import auth_route
from marshmallow import ValidationError
from flask_jwt_extended import JWTManager


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(auth_route, url_prefix='/auth')
    app.config['SECRET_KEY'] = 'your_strong_secret_key'
    app.config["JWT_SECRET_KEY"] = 'your_jwt_secret_key'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=2)


    return app

app = create_app()

jwt = JWTManager(app)

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return generate_response(message=e.messages, status=400, error="Validation Error")

@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return generate_response(status=code)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
