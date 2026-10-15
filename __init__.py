from flask import Flask

from app.config import Config
from app.routes import routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(routes)
    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
