from marshmallow import post_dump

from api.app import ma
from api.models import User, Group, Happiness, Setting


class SettingsSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Setting
        ordered = True

    id = ma.auto_field(dump_only=True, required=True)
    key = ma.Str(dump_only=True, required=True)
    value = ma.Bool(required=True)
    user_id = ma.auto_field(dump_only=True, required=True)


class SettingInfoSchema(ma.Schema):
    value = ma.Bool(required=True)
    key = ma.Str(required=True)


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        ordered = True

    id = ma.auto_field(required=True, dump_only=True)
    username = ma.auto_field(required=True)
    email = ma.Email(required=True)
    password = ma.auto_field(required=True, load_only=True)
    created = ma.auto_field(required=True)
    profile_picture = ma.auto_field()
    settings = ma.Nested(SettingsSchema, many=True, required=True)

class SimpleUserSchema(ma.Schema):
    class Meta:
        ordered = True

    id = ma.Int(required=True)
    username = ma.Str(required=True)
    profile_picture = ma.Str(required=True)

class TokenSchema(ma.Schema):
    session_token = ma.Str()


class UsernameSchema(ma.Schema):
    username = ma.Str()


class UserEmailSchema(ma.Schema):
    email = ma.Email()  # This is probably bad practice (I am still learning)


class CreateUserSchema(ma.Schema):
    email = ma.Str(required=True)
    username = ma.Str(required=True)
    password = ma.Str(required=True)


class GetUserByIdSchema(ma.Schema):
    id = ma.Integer()


class GroupSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Group
        ordered = True

    id = ma.auto_field(required=True)
    name = ma.auto_field(required=True)
    users = ma.Nested(SimpleUserSchema, many=True, required=True)


class CreateGroupSchema(ma.Schema):
    name = ma.Str(required=True)


class EditGroupSchema(ma.Schema):
    new_name = ma.Str()
    add_users = ma.List(ma.Str(), many=True)
    remove_users = ma.List(ma.Str(), many=True)


class HappinessSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Happiness
        ordered = True

    id = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(dump_only=True)
    value = ma.auto_field(required=True)
    comment = ma.auto_field()
    timestamp = ma.Str(required=True)

    @post_dump
    def fix_time(self, data, **kwargs):
        if data.get('timestamp'):
            data['timestamp'] = data['timestamp'].split()[0]
        return data


class HappinessEditSchema(ma.Schema):
    value = ma.Float()
    comment = ma.Str()


class HappinessGetTime(ma.Schema):
    start = ma.Str()
    end = ma.Str()
    id = ma.Int()


class HappinessGetCount(ma.Schema):
    page = ma.Int()
    count = ma.Int()
    id = ma.Int()
