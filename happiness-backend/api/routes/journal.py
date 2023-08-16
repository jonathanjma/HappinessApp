from apifairy import authenticate, body, response, other_responses, arguments
from flask import Blueprint

from api.app import db
from api.authentication.auth import token_auth
from api.dao import journal_dao
from api.models.models import Journal
from api.models.schema import JournalSchema, JournalGetSchema, DecryptedJournalSchema, PasswordKeySchema, \
    JournalEditSchema, JournalGetBySchema
from api.util.errors import failure_response

journal = Blueprint('journal', __name__)


@journal.post('/')
@authenticate(token_auth)
@body(JournalSchema)
@arguments(PasswordKeySchema, location='headers')
@response(JournalSchema, 201)
@other_responses({400: "Invalid password key."})
def create_entry(req, headers):
    """
    Create Journal Entry
    Creates a new private journal entry, which is stored using end-to-end encryption. \n
    Requires: the user's `password_key` for data encryption (provided by server during API token creation)
    """
    try:
        user = token_auth.current_user()
        data = user.encrypt_data(headers.get('password_key'), req.get('data'))
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
@arguments(PasswordKeySchema, location='headers')
@response(DecryptedJournalSchema)
@other_responses({400: "Invalid password key."})
def get_entries(args, headers):
    """
    Get Journal Entries
    Gets a specified number of journal entries in reverse order.
    Paginated based on page number and journal entries per page. Defaults to page=1 and count=10. \n
    Requires: the user's `password_key` for data decryption (provided by server during API token creation)
    """
    user = token_auth.current_user()
    page, count = args.get("page", 1), args.get("count", 10)
    # add password key to schema context so entries can be decrypted
    DecryptedJournalSchema.context['password_key'] = headers.get('password_key')
    return journal_dao.get_entries_by_count(user.id, page, count)


@journal.put('/')
@authenticate(token_auth)
@arguments(JournalGetBySchema)
@arguments(PasswordKeySchema, location='headers')
@body(JournalEditSchema)
@response(JournalSchema)
@other_responses({404: "Entry Not Found.", 400: "Invalid password key."})
def edit_entry(args, headers, req):
    """
    Edit Journal Entry by ID
    Modifies the journal entry corresponding to the provided ID with the given text. \n
    Requires: the user's `password_key` for data encryption (provided by server during API token creation)
    """
    entry = journal_dao.get_journal_by_id(args.get('id'))
    if not entry:
        return failure_response("Entry Not Found.", 404)
    try:
        entry.data = token_auth.current_user().encrypt_data(headers.get('password_key'), req.get('data'))
        db.session.commit()
        return entry
    except Exception as e:
        print(e)
        return failure_response('Invalid password key.', 400)


@journal.delete('/')
@authenticate(token_auth)
@arguments(JournalGetBySchema)
@other_responses({404: "Entry Not Found."})
def delete_entry(args):
    """
    Delete Journal Entry by ID
    Deletes the journal entry corresponding to a specific ID.
    """
    entry = journal_dao.get_journal_by_id(args.get('id'))
    if not entry:
        return failure_response("Entry Not Found.", 404)
    db.session.delete(entry)
    db.session.commit()
    return "", 204