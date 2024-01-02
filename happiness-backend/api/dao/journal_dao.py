from datetime import datetime

from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import select

from api.app import db
from api.authentication.auth import token_current_user
from api.models.models import Journal
from api.util.errors import failure_response


def get_journal_by_id(entry_id: int) -> Journal:
    """
    Returns a Journal entry object by ID.
    """
    return db.session.execute(select(Journal).where(Journal.id == entry_id)).scalar()


def get_journal_by_date(user_id: int, date: datetime) -> Journal:
    """
    Returns a Journal entry corresponding to the Datetime object
    """
    db_date = datetime.strftime(date, "%Y-%m-%d 00:00:00.000000")
    return db.session.execute(
        select(Journal).where(Journal.user_id == user_id, Journal.timestamp == db_date)
    ).scalar()


def get_journal_by_date_range(user_id: int, start: datetime, end: datetime) -> list[Journal]:
    """
    Returns journal entries between start date and end date, inclusive
    """
    db_start = datetime.strftime(start, "%Y-%m-%d 00:00:00.000000")
    db_end = datetime.strftime(end, "%Y-%m-%d 00:00:00.000000")

    return list(
        db.session.execute(
            select(Journal).where(
                Journal.user_id == user_id,
                Journal.timestamp.between(db_start, db_end)
            )).scalars())


def get_entry_by_id_or_date(args: dict) -> Journal:
    id, date = args.get("id"), args.get("date")
    if id is not None:
        return get_journal_by_id(id)
    elif date is not None:
        return get_journal_by_date(token_current_user().id, date)
    else:
        return failure_response('Insufficient Information', 400)


def get_entries_by_count(user_id: int, page: int, per_page: int) -> Pagination:
    """
    Returns a list of per_page Journal entry objects given a User ID (sorted from newest to oldest).
    Page variable can be changed to show the next per_page objects for pagination.
    """
    return db.paginate(
        select=(
            select(Journal).where(Journal.user_id == user_id).order_by(Journal.timestamp.desc())),
        per_page=per_page,
        page=page
    )
