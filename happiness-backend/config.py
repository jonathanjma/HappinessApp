import os

from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

    # API documentation
    APIFAIRY_TITLE = 'Happiness App API'
    APIFAIRY_VERSION = '1.0'
    APIFAIRY_UI = os.environ.get('DOCS_UI', 'elements')

    # Security measures
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ENCRYPT_SALT = os.environ.get("ENCRYPT_SALT")

    # Email sending
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = "465"
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = "noreply.happiness.app"
    MAIL_PASSWORD = os.environ.get("SECRET_APP_PASSWORD")

    # AWS Profile Picture Storage
    AWS_ACCESS = os.environ.get("AWS_ACCESS")
    AWS_SECRET = os.environ.get("AWS_SECRET")
    AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
    AWS_REGION = os.environ.get("AWS_REGION")

    # Happiness export
    UPLOAD_FOLDER = "./export/"

    # Scheduled jobs
    REDISCLOUD_URL = os.environ.get("REDISCLOUD_URL")

    # Discord webhooks
    AST_WEBHOOK_URL = os.environ.get("AST_WEBHOOK_URL")
    BOIS_WEBHOOK_URL = os.environ.get("BOIS_WEBHOOK_URL")

    WRAPPED_DATA_URL = os.environ.get("WRAPPED_DATA_URL")
    WRAPPED_YEAR = 2025

    # MCP OAuth
    OAUTH_BASE_URL = os.environ.get("OAUTH_BASE_URL", "http://localhost:5001")
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

    # Discord bot linking (bot -> backend shared secret)
    # If unset, /api/discord/link/start and /api/discord/link/poll will not enforce auth (dev-only).
    DISCORD_BOT_LINK_SECRET = os.environ.get("DISCORD_BOT_LINK_SECRET")


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'

    SECRET_KEY = Config.SECRET_KEY
    ENCRYPT_SALT = Config.ENCRYPT_SALT
    REDISCLOUD_URL = Config.REDISCLOUD_URL
