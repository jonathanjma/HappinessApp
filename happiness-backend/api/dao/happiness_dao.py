from datetime import timedelta

from api.models.models import Happiness
from sqlalchemy import select
from api.app import db
from api.util.errors import failure_response


def get_happiness_by_id(id):
    """
    Returns a Happiness object by ID.
    :param id: ID of the Happiness object being searched for.
    :return: A Happiness object with the same ID as the one provided.
    """
    return Happiness.query.filter_by(id=id).first()


def get_happiness_by_date(user_id, date):
    """
    Returns a Happiness object, given a User ID and a date.
    :param user_id: ID of the User whose Happiness object is being searched for.
    :param date: Date object representing the day the happiness value was recorded.
    :return: A Happiness object of the given User ID corresponding to the given date.
    """
    return Happiness.query.filter_by(user_id=user_id, timestamp=date).first()


def get_user_happiness(user_id):
    """
    Returns a list of all Happiness objects corresponding to the given User ID.
    """
    return Happiness.query.filter_by(user_id=user_id).all()


def get_happiness_by_timestamp(user_id, start, end):
    """
    Returns a list of all Happiness objects corresponding to a given User ID between 2 timestamps.
    """
    return Happiness.query.filter(
        Happiness.user_id == user_id,
        Happiness.timestamp.between(start, end)).order_by(Happiness.timestamp.asc()).all()


def get_happiness_by_count(user_id, page, n):
    """
    Returns a list of n Happiness objects given a User ID (sorted from newest to oldest).
    Page variable can be changed to show the next n objects for pagination.
    """
    return Happiness.query.filter_by(user_id=user_id).order_by(Happiness.timestamp.desc()) \
        .paginate(page=page, per_page=n, error_out=False)


def get_happiness_by_group_timestamp(user_ids, start, end):
    """
    Returns a list of all Happiness objects (sorted from oldest to newest) between 2 timestamps
    given a list of User IDs.
    """
    return Happiness.query.filter(
        Happiness.user_id.in_(user_ids),
        Happiness.timestamp.between(start, end)).order_by(Happiness.timestamp.asc()).all()


def get_happiness_by_group_count(user_ids, page, n):
    """
    Returns a list of n Happiness objects (sorted from newest to oldest) given a list of User IDs.
    Page variable can be changed to show the next n objects for pagination.
    """
    return Happiness.query.filter(Happiness.user_id.in_(user_ids)).order_by(
        Happiness.timestamp.desc()) \
        .paginate(page=page, per_page=n, error_out=False)


def get_happiness_by_filter(user_id, page, per_page, start, end, low, high, query):
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
    #         # start.year > end.year or start.year == end.year and (start.month > end.month or (start.month == end.month and
    #         #                                                                                 start.day > end.day)):
            return failure_response("Start is an earlier date than end.", 400)
    acc = 0
    obj = select(Happiness)
    obj = obj.where(Happiness.user_id == user_id)
    if start is not None and end is not None:
        obj = obj.where(Happiness.timestamp.between(start, end + timedelta(days=1)))
        acc = acc + 1
    if low is not None and high is not None:
        obj = obj.where(Happiness.value >= low, Happiness.value <= high)
        acc = acc + 1
    if query is not None:
        obj = obj.where(Happiness.comment.like(f"%{query}%"))
        acc = acc + 1
    obj = obj.order_by(Happiness.timestamp.asc())
    if acc == 0:
        return []
    return db.paginate(
        select=obj,
        per_page=per_page,
        page=page
    )



