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
