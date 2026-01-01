import redis
import rq
from apifairy import APIFairy
from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

import api.util.email_methods as email_methods
from config import Config
from jobs import scheduler

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
apifairy = APIFairy()
cors = CORS()


# noinspection PyUnresolvedReferences
def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    app.redis = redis.from_url(app.config['REDISCLOUD_URL'])
    app.job_queue = rq.Queue('happiness-backend-jobs', connection=app.redis)
    # Do not remove!
    from api import models

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    apifairy.init_app(app)
    email_methods.init_app(app)
    cors.init_app(app)
    scheduler.init_app(app)

    from api.routes.user import user
    app.register_blueprint(user, url_prefix='/api/user')
    from api.routes.token import token
    app.register_blueprint(token, url_prefix='/api/token')
    from api.routes.group import group
    app.register_blueprint(group, url_prefix='/api/group')
    from api.routes.happiness import happiness
    app.register_blueprint(happiness, url_prefix='/api/happiness')
    from api.routes.journal import journal
    app.register_blueprint(journal, url_prefix='/api/journal')
    from api.routes.reads import reads
    app.register_blueprint(reads, url_prefix='/api/reads')
    from api.routes.mcp_oauth import mcp_oauth
    app.register_blueprint(mcp_oauth, url_prefix='/api/mcp/oauth')
    from api.routes.discord_link import discord_link
    app.register_blueprint(discord_link, url_prefix='/api/discord/link')
    from api.util.errors import errors
    app.register_blueprint(errors)

    # Register well-known OAuth endpoints at root level
    from api.routes.mcp_oauth import oauth_authorization_server, oauth_protected_resource
    app.add_url_rule('/.well-known/oauth-authorization-server',
                     'oauth_authorization_server',
                     oauth_authorization_server,
                     methods=['GET'])
    app.add_url_rule('/.well-known/oauth-protected-resource',
                     'oauth_protected_resource',
                     oauth_protected_resource,
                     methods=['GET'])

    @app.route('/')
    @app.route('/api')
    def api_docs():
        return redirect(url_for('apifairy.docs'))

    return app
