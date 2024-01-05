from datetime import datetime, timedelta

from apifairy import authenticate, response, body, other_responses, arguments
from flask import Blueprint
from sqlalchemy import select

from api.app import db
from api.authentication.auth import token_auth, token_current_user
from api.dao import happiness_dao
from api.models.models import Happiness, User
from api.models.schema import CreateReadsSchema, HappinessSchema, HappinessGetPaginatedSchema
from api.util.errors import failure_response

reads = Blueprint('reads', __name__)


@reads.post('/')
@authenticate(token_auth)
@body(CreateReadsSchema)
@response(CreateReadsSchema)
@other_responses({400: "No corresponding Happiness entry found"})
def create_read(req):
    """
    Create Read
    Creates a read and adds it to the Reads table.
    """
    user = token_current_user()
    happiness = happiness_dao.get_happiness_by_id(req.get("happiness_id"))
    if happiness is None:
        return {400: "No corresponding Happiness entry found"}
    user.read_happiness(happiness)
    db.session.commit()
    return ({
                "happiness_id": happiness.id
            }, 201)


@reads.delete('/')
@authenticate(token_auth)
@body(CreateReadsSchema)
@response(CreateReadsSchema)
@other_responses({400: "No corresponding Happiness entry found"})
def mark_unread(req):
    """
    Mark Unread
    Deletes the read record that corresponds to the provided Happiness ID from the Reads table.
    """
    user = token_current_user()
    happiness = happiness_dao.get_happiness_by_id(req.get("happiness_id"))
    if happiness is None:
        return failure_response("No corresponding read Happiness entry found", code=400)
    if not user.has_read_happiness(happiness):
        return failure_response("No corresponding read Happiness entry found", code=400)
    user.unread_happiness(happiness)
    db.session.commit()
    return ({
                "happiness_id": happiness.id
            }, 200)


@reads.get('/')
@arguments(HappinessGetPaginatedSchema)
@authenticate(token_auth)
@response(HappinessSchema(many=True))
def get_read_happiness(req):
    """
    Get Read Happiness
    Gets paginated list of all happiness entries that the user has read.
    Optionally takes "page" and "count" in request body, which default to 1 and 10 respectively.
    """
    page, per_page = req.get("page", 1), req.get("count", 10)
    user = token_current_user()
    return user.posts_read.order_by(Happiness.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)


@reads.get("/unread/")
@arguments(HappinessGetPaginatedSchema)
@authenticate(token_auth)
@response(HappinessSchema(many=True))
def get_unread_happiness(req):
    """
    Get Unread Happiness
    Gets paginated list of all happiness entries that the user has not read.
    Optionally takes "page" and "count" in request body, which default to 1 and 10 respectively.
    """
    page, per_page = req.get("page", 1), req.get("count", 10)
    current_user = token_current_user()
    # Also I am aware that has_mutual_group exists, but we can't use that as a SQLAlchemy query,
    # and we don't want to for loop through all happiness entries on the db.

    # use a set to avoid duplicates
    friend_users = set()

    # First get all groups the user is a part of
    groups = current_user.groups.all()

    # For each group, get all happiness entries for that group in the past week
    # Yes this is O(n^2), but even at full scale this should be at most 100 iterations
    for g in groups:
        for u in g.users:
            friend_users.add(u.id)

    # Find unread entries by selecting happiness with some criteria:
    return db.paginate(
        select=(select(Happiness).where(
            # Happiness falls in the last week
            Happiness.timestamp.between(str(datetime.utcnow() - timedelta(weeks=1)), str(datetime.utcnow())),
            # User shares a group with this user
            Happiness.user_id.in_(friend_users),
            # We want Happiness objects that where the user's id doesn't exist in its readers
            # https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#exists-forms-has-any
            ~Happiness.readers.any(User.id == current_user.id)
        ).order_by(Happiness.timestamp.desc())),
        per_page=per_page,
        page=page
    )
