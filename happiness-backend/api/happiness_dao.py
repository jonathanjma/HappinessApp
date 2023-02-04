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


def get_happiness_by_range(user_id, start, end):
    return Happiness.query.filter(
        Happiness.user_id == user_id,
        Happiness.timestamp.between(start, end)).all()


def get_user_happiness(user_id):
    """
    :return: a list of all Happiness objects corresponding to the given User ID.
    """
    return Happiness.query.filter(Happiness.user_id == user_id).all()


def get_happiness_by_count(user_id, start, page, n):
    """
    Returns a list of n Happiness objects (sorted from newest to oldest) given a starting value.
    Page variable can be changed to show the next n objects for pagination.
    """
    return Happiness.query.filter(Happiness.user_id == user_id, Happiness.timestamp <= start).order_by(Happiness.timestamp.desc()).paginate(page=page, per_page=n, error_out=False)
