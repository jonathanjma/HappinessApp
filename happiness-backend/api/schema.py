from marshmallow import post_dump

from api.app import ma
from api.models import User, Group, Happiness


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


class HappinessSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Happiness

    id = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(dump_only=True)
    value = ma.auto_field(required=True)
    comment = ma.auto_field()
    timestamp = ma.Str(required=True)

    @post_dump
    def fix_time(self, data, **kwargs):
        if data.get('timestamp'): data['timestamp'] = data['timestamp'].split()[0]
        return data


class HappinessPutSchema(ma.Schema):
    value = ma.Int()
    comment = ma.Str()


class HappinessGetTime(ma.Schema):
    start = ma.Str()
    end = ma.Str()


class HappinessGetCount(ma.Schema):
    page = ma.Int()
    count = ma.Int()
