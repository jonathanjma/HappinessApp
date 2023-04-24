import os

from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')

    # API documentation
    APIFAIRY_TITLE = 'Happiness App API'
    APIFAIRY_VERSION = '1.0'
    APIFAIRY_UI = os.environ.get('DOCS_UI', 'elements')

    # Security measures
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SERVER_NAME = "happiness-qfvoiwgqdq-ue.a.run.app"

    # Email sending
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = "465"
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = "noreply.happiness.app"
    MAIL_PASSWORD = os.environ.get("SECRET_APP_PASSWORD")

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'
