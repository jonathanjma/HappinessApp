from datetime import datetime

from api.models.models import Journal


def get_journal_by_id(entry_id):
    """
    Returns a Journal entry object by ID.
    """
    return Journal.query.filter_by(id=entry_id).first()


def get_journal_by_date(date):
    """
    Returns a Journal entry corresponding to the Datetime object
    """
    date = datetime.strftime(date, "%Y-%m-%d 00:00:00.000000")
    return Journal.query.filter_by(timestamp=date).first()


def get_entries_by_count(user_id, page, n):
    """
    Returns a list of n Journal entry objects given a User ID (sorted from newest to oldest).
    Page variable can be changed to show the next n objects for pagination.
    """
    return Journal.query.filter_by(user_id=user_id).order_by(Journal.timestamp.desc()) \
        .paginate(page=page, per_page=n, error_out=False)
