from api.models import Group


def get_group_by_id(group_id):
    """
    Returns a Group object by ID.
    """
    return Group.query.filter(Group.id == group_id).first()
