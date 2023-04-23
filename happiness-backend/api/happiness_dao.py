from api.models import Happiness


def get_happiness_by_id(id):
    """
    Returns a Happiness object by ID.
    :param id: ID of the Happiness object being searched for.
    :return: A Happiness object with the same ID as the one provided.
    """
    return Happiness.query.filter(Happiness.id == id).first()


def get_happiness_by_date(user_id, date):
    """
    Returns a Happiness object, given a User ID and a date.
    :param user_id: ID of the User whose Happiness object is being searched for.
    :param date: Date object representing the day the happiness value was recorded.
    :return: A Happiness object of the given User ID corresponding to the given date.
    """
    return Happiness.query.filter(Happiness.user_id == user_id, Happiness.timestamp == date).first()

def get_user_happiness(user_id):
    """
    Returns a list of all Happiness objects corresponding to the given User ID.
    """
    return Happiness.query.filter(Happiness.user_id == user_id).all()


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
    return Happiness.query.filter(Happiness.user_id == user_id).order_by(Happiness.timestamp.desc()) \
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
