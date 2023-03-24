from api import create_app
from api.app import db
from api.models import User, Setting, Happiness

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Setting': Setting, 'Happiness': Happiness}