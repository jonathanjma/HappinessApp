from datetime import datetime, timedelta

from api.authentication.auth import token_current_user
from api.util.errors import failure_response
from sqlalchemy import select

from api.app import db
from api.models.models import Happiness, Comment, User


def get_happiness_by_id(happiness_id: int) -> Happiness:
    """
    Returns a Happiness object by ID.
    """
    return db.session.execute(select(Happiness).where(Happiness.id == happiness_id)).scalar()


def get_happiness_by_date(user_id: int, date: datetime) -> Happiness:
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


def get_all_happiness(user_id: int) -> list[Happiness]:
    """
    Returns a list of all Happiness objects corresponding to the given User ID.
    """
    return list(db.session.execute(select(Happiness).where(Happiness.user_id == user_id)).scalars())


def get_happiness_by_date_range(user_ids: list[int], start: datetime, end: datetime) -> list[Happiness]:
    """
    Returns all Happiness objects (sorted from oldest to newest) between 2 Datetime objects (inclusive)
    given a list of User IDs.
    """
    db_start = datetime.strftime(start, "%Y-%m-%d 00:00:00.000000")
    db_end = datetime.strftime(end, "%Y-%m-%d 00:00:00.000000")
    return list(db.session.execute(select(Happiness).where(
        Happiness.user_id.in_(user_ids), Happiness.timestamp.between(db_start, db_end)
    ).order_by(Happiness.timestamp.asc())).scalars())


def get_happiness_by_count(user_ids: list[int], page: int, n: int) -> list[Happiness]:
    """
    Returns a paginated list of Happiness objects (sorted from newest to oldest) given a list of User IDs.
    Page variable can be changed to show the next n objects for pagination.
    """
    return list(db.paginate(
        select=(
            select(Happiness).where(Happiness.user_id.in_(user_ids))
            .order_by(Happiness.timestamp.desc(), Happiness.user_id.asc())
        ),
        per_page=n,
        page=page,
        error_out=False
    ))


def get_happiness_by_unread(user_id: int, user_ids: list[int], per_page: int, page: int) -> list[Happiness]:
    """
    Returns a paginated list of Happiness objects (sorted from newest to oldest) from all the users
    in the user_ids list in the last week for which the given user has not read.
    """
    return list(db.paginate(
        select=(select(Happiness).where(
            # Happiness falls in the last week
            Happiness.timestamp.between(str(datetime.utcnow() - timedelta(weeks=1)), str(datetime.utcnow())),
            # User shares a group with this user
            Happiness.user_id.in_(user_ids),
            # We want Happiness objects that where the user's id doesn't exist in its readers
            # https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#exists-forms-has-any
            ~Happiness.readers.any(User.id == user_id)
        ).order_by(Happiness.timestamp.desc(), Happiness.user_id.asc())),
        per_page=per_page,
        page=page,
        error_out=False
    ))


def get_happiness_by_filter(user_id: int, page: int, per_page: int, start: datetime, end: datetime,
                            low: int, high: int, text: str) -> list[Happiness]:
    """
    Filters according to the provided arguments. Checks to see what filters to apply. Will not apply the filters if they
    have the value [None]. For example, if start = end = None, then the happiness will NONE be filtered by timestamp.
    Also, if low > high, or start is a later date than end, will raise an exception.
    """
    if low is not None and high is not None:
        if low > high:
            return failure_response("Low is greater than high.", 400)
    if start is not None and end is not None:
        if start > end:
            return failure_response("Start is an earlier date than end.", 400)

    acc = 0
    query = select(Happiness).where(Happiness.user_id == user_id)
    if start is not None and end is not None:
        db_start = datetime.strftime(start, "%Y-%m-%d 00:00:00.000000")
        db_end = datetime.strftime(end, "%Y-%m-%d 00:00:00.000000")
        query = query.where(Happiness.timestamp.between(db_start, db_end))
        acc = acc + 1
    if low is not None and high is not None:
        query = query.where(Happiness.value >= low, Happiness.value <= high)
        acc = acc + 1
    if text is not None:
        query = query.where(Happiness.comment.like(f"%{text}%"))
        acc = acc + 1
    query = query.order_by(Happiness.timestamp.asc())

    if acc == 0: return []

    return list(db.paginate(
        select=query,
        per_page=per_page,
        page=page
    ))


def get_comment_by_id(comment_id: int) -> Comment:
    return db.session.execute(select(Comment).where(Comment.id == comment_id)).scalar()
