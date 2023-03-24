from apifairy import APIFairy
from flask import Flask, redirect, url_for
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import api.email_methods as email_methods

from config import Config

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
apifairy = APIFairy()
cors = CORS()

# noinspection PyUnresolvedReferences


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    # Do not remove!
    from api import models

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    apifairy.init_app(app)
    email_methods.init_app(app)
    cors.init_app(app)

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
