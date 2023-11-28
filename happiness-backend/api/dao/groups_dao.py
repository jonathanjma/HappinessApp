from sqlalchemy import select

from api.app import db
from api.models.models import Group


def get_group_by_id(group_id: int) -> Group:
    """
    Returns a Group object by ID.
    """
    return db.session.execute(select(Group).where(Group.id == group_id)).scalar()
