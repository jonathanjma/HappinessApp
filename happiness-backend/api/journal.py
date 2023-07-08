from apifairy import authenticate, body, response, other_responses, arguments
from flask import Blueprint

from api.app import db
from api.auth import token_auth
from api.dao import journal_dao
from api.errors import failure_response
from api.models import Journal
from api.schema import JournalSchema, JournalGetSchema

journal = Blueprint('journal', __name__)

@journal.post('/')
@authenticate(token_auth)
@body(JournalSchema)
@response(JournalSchema)
@other_responses({400: "Invalid password key."})
def create_entry(req):
    try:
        user = token_auth.current_user()
        data = user.encrypt_data(req.get('password_key'), req.get('data'))
        entry = Journal(user_id=user.id, encrypted_data=data)
        db.session.add(entry)
        db.session.commit()
        return entry
    except Exception as e:
        print(e)
        return failure_response('Invalid password key.', 400)

@journal.get('/')
@authenticate(token_auth)
@arguments(JournalGetSchema)
@response(JournalSchema(many=True))
@other_responses({400: "Invalid password key."})
def get_entries(req):
    try:
        user = token_auth.current_user()
        page, count = req.get("page", 1), req.get("count", 10)
        encrypted_entries = journal_dao.get_entries_by_count(user.id, page, count)

        def decrypt_data(obj):
            obj.data = user.decrypt_data(req.get('password_key'), obj.data)
            return obj

        return list(map(decrypt_data, encrypted_entries))
    except Exception as e:
        print(e)
        return failure_response('Invalid password key.', 400)