from datetime import timedelta, datetime

from api.authentication.auth import token_current_user
from api.util.errors import failure_response
from sqlalchemy import select

from api.app import db
from api.models.models import Happiness, Comment


def get_happiness_by_id(happiness_id: int) -> Happiness:
    """
    Returns a Happiness object by ID.
    """
    return db.session.execute(select(Happiness).where(Happiness.id == happiness_id)).scalar()


def get_happiness_by_date(user_id: int, date: datetime):
    """
    Returns a Happiness object, given a User ID and a Datetime object.
    :param user_id: ID of the User whose Happiness object is being searched for.
    :param date: Date object representing the day the happiness value was recorded.
    :return: A Happiness object of the given User ID corresponding to the given date.
    """
    db_date = datetime.strftime(date, "%Y-%m-%d 00:00:00.000000")
    return db.session.execute(
        select(Happiness).where(Happiness.user_id == user_id, Happiness.timestamp == db_date)
    ).scalar()

def get_happiness_by_id_or_date(args: dict) -> Happiness:
    id, date = args.get("id"), args.get("date")
    if id is not None:
        return get_happiness_by_id(id)
    elif date is not None:
        return get_happiness_by_date(token_current_user().id, date)
    else:
        return failure_response('Insufficient Information', 400)


def get_user_happiness(user_id: int):
    """
    Returns a list of all Happiness objects corresponding to the given User ID.
    """
    return db.session.execute(select(Happiness).where(Happiness.user_id == user_id)).all()


def get_happiness_by_timestamp(user_id, start, end):
    """
    Returns a list of all Happiness objects corresponding to a given User ID between 2 Datetime objects.
    """
    return Happiness.query.filter(
        Happiness.user_id == user_id, Happiness.timestamp.between(start, end + timedelta(days=1))
    ).order_by(Happiness.timestamp.asc()).all()


def get_happiness_by_count(user_id, page, n):
    """
    Returns a list of n Happiness objects given a User ID (sorted from newest to oldest).
    Page variable can be changed to show the next n objects for pagination.
    """
    return Happiness.query.filter_by(user_id=user_id).order_by(Happiness.timestamp.desc()) \
        .paginate(page=page, per_page=n, error_out=False)


def get_happiness_by_group_timestamp(user_ids, start, end):
    """
    Returns a list of all Happiness objects (sorted from oldest to newest) between 2 Datetime objects
    given a list of User IDs.
    """
    return Happiness.query.filter(
        Happiness.user_id.in_(user_ids), Happiness.timestamp.between(start, end + timedelta(days=1))
    ).order_by(Happiness.timestamp.asc()).all()


def get_happiness_by_group_count(user_ids, page, n):
    """
    Returns a list of n Happiness objects (sorted from newest to oldest) given a list of User IDs.
    Page variable can be changed to show the next n objects for pagination.
    """
    return Happiness.query.filter(Happiness.user_id.in_(user_ids)).order_by(
        Happiness.timestamp.desc()) \
        .paginate(page=page, per_page=n, error_out=False)


def get_happiness_by_filter(user_id: int, page: int, per_page: int, start: datetime, end: datetime,
                            low: int, high: int, text: str):
    """
    Filters according to the provided arguments. Checks to see what filters to apply. Will not apply the filters if they
    have the value [None]. For example, if start = end = None, then the happiness will NONE be filtered by timestamp.
    Also, if low > high, or start is a later date than end, will raise an exception.
    """
    if low is not None and high is not None:
        if low > high:
            return failure_response("Low is greater than high.",400)
    if start is not None and end is not None:
        if start > end:
            return failure_response("Start is an earlier date than end.", 400)

    acc = 0
    query = select(Happiness).where(Happiness.user_id == user_id)
    if start is not None and end is not None:
        query = query.where(Happiness.timestamp.between(start, end + timedelta(days=1)))
        acc = acc + 1
    if low is not None and high is not None:
        query = query.where(Happiness.value >= low, Happiness.value <= high)
        acc = acc + 1
    if text is not None:
        query = query.where(Happiness.comment.like(f"%{text}%"))
        acc = acc + 1
    query = query.order_by(Happiness.timestamp.asc())

    if acc == 0: return []

    return db.paginate(
        select=query,
        per_page=per_page,
        page=page
    )

def get_paginated_happiness_by_query(user_id, query, page, n):
    return Happiness.query.filter_by(user_id=user_id) \
        .filter(Happiness.comment.like(f"%{query}%")).paginate(page=page, per_page=n, error_out=False)

def get_comment_by_id(id: int) -> Comment:
    return db.session.execute(select(Comment).where(Comment.id == id)).scalar()
