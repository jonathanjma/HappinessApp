from api.models import Community


def get_community_by_id(community_id):
    """
    Returns a Community object by ID.
    """
    return Community.query.filter_by(id=community_id).first()