from apifairy import fields
from marshmallow import post_dump

from api.app import ma
from api.models import User, Group, Happiness, Setting


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = ma.auto_field(dump_only=True)
    username = ma.auto_field(required=True)
    email = ma.auto_field(required=True)
    password_digest = ma.auto_field(load_only=True)
    profile_picture = ma.auto_field()
    settings = ma.auto_field()


class CreateUserSchema(ma.Schema):
    email = ma.Str(required=True)
    username = ma.Str(required=True)
    password = ma.Str(required=True, load_only=True)


class GetUserByIdSchema(ma.Schema):
    id = ma.Integer()


class SettingInfoSchema(ma.Schema):
    value = ma.Bool(required=True)
    key = ma.Str(required=True)


class SettingsSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Setting

    id = ma.auto_field(dump_only=True)
    key = ma.Str(dump_only=True, required=True)
    value = ma.Bool(required=True)
    user_id = ma.auto_field(dump_only=True)


class SettingListSchema(ma.Schema):
    settingsList = ma.List(ma.Nested(SettingsSchema, only=('key', 'value')))


class AddUserSettingSchema(ma.Schema):
    key = ma.Str(required=True)
    value = ma.Bool(required=True)


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
    # Add users and remove users only uses an array of usernames, not full user objects.
    # We represent these as a list of mappings: [{"username": "u1"}, {"username": "u2"}]
    add_users = ma.List(ma.Mapping())
    remove_users = ma.List(ma.Mapping())


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
        if data.get('timestamp'):
            data['timestamp'] = data['timestamp'].split()[0]
        return data


class HappinessPutSchema(ma.Schema):
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
