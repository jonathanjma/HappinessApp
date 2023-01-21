from apifairy import APIFairy
from flask import Flask, redirect, url_for
from flask_marshmallow import Marshmallow

from config import Config

ma = Marshmallow()
apifairy = APIFairy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    ma.init_app(app)
    apifairy.init_app(app)

    from api.user import user
    app.register_blueprint(user, url_prefix='/api/user')
    from api.token import token
    app.register_blueprint(token, url_prefix='/api/token')
    from api.group import group
    app.register_blueprint(group, url_prefix='/api/group')
    from api.happiness import happiness
    app.register_blueprint(happiness, url_prefix='/api/happiness')
    from api.errors import errors
    app.register_blueprint(errors)

    @app.route('/')
    @app.route('/api')
    def index():
        return redirect(url_for('apifairy.docs'))

    return app
