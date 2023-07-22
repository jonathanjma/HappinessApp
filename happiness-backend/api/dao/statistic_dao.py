from api.models import Statistic


def get_statistic_by_id(id):
    """
    Returns a Statistic object by ID.
    :param id: ID of the Statistic object being searched for.
    :return: A Statistic object with the same ID as the one provided.
    """
    return Statistic.query.filter_by(id=id).first()


def get_statistic_by_date(community_id, date):
    """
    Returns a Statistic object, given a Community ID and a date.
    :param community_id: ID of the Community whose Statistic object is being searched for.
    :param date: Date object representing the date the Statistic was recorded.
    :return: A Statistic object of the given Community ID corresponding to the given date.
    """
    return Statistic.query.filter_by(community_id=community_id, timestamp=date).first()


def get_statistic_by_timestamp(community_id, start, end):
    """
    Returns a list of all Statistic objects corresponding to a given Community ID between 2 timestamps.
    """
    return Statistic.query.filter(Statistic.community_id == community_id,
                                  Statistic.timestamp.between(start, end)).order_by(Statistic.timestamp.asc()).all()


def get_statistic_by_count(community_id, page, n):
    """
    Returns a list of n Statistic objects given a Community ID, in reverse chronological order.
    Page variable can be changed to show the next n objects for pagination.
    """
    return Statistic.query.filter_by(community_id=community_id).order_by(Statistic.timestamp.desc()) \
        .paginate(page=page, per_page=n, error_out=False)
