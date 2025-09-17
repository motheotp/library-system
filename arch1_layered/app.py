from flask import Flask
from config import Config
from models import db
from routes import api_blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(api_blueprint)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)