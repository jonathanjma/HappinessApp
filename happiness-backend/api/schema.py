from api.app import ma
from api.models import User, Group


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = ma.auto_field(dump_only=True)
    username = ma.auto_field(required=True)
    profile_picture = ma.auto_field(dump_only=True)


class GroupSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Group
        ordered = True

    id = ma.auto_field(required=True)
    name = ma.auto_field(required=True)
    users = ma.Nested(UserSchema, many=True, required=True)


class CreateGroupSchema(ma.Schema):
    name = ma.Str(required=True)


class EditGroupSchema(ma.Schema):
    new_name = ma.Str()
    add_users = ma.Nested(UserSchema, many=True)
    remove_users = ma.Nested(UserSchema, many=True)
