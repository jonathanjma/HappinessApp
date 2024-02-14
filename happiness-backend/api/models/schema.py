from apifairy.fields import FileField
from marshmallow import post_dump

from api.app import ma
from api.authentication.auth import token_current_user
from api.models.models import User, Group, Happiness, Setting, Comment, Journal
from api.util.errors import failure_response


class EmptySchema(ma.Schema):
    pass


class SettingsSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Setting
        ordered = True

    id = ma.auto_field(dump_only=True, required=True)
    key = ma.Str(dump_only=True, required=True)
    enabled = ma.Bool(required=True)
    value = ma.Str()
    user_id = ma.auto_field(dump_only=True, required=True)


class SettingInfoSchema(ma.Schema):
    value = ma.Str()
    enabled = ma.Bool(required=True)
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
    session_token = ma.Str(required=True)


class UsernameSchema(ma.Schema):
    username = ma.Str(required=True)


class PasswordResetReqSchema(ma.Schema):
    # This is probably bad practice (I am still learning)
    email = ma.Email(required=True)


class PasswordResetSchema(ma.Schema):
    password = ma.Str(required=True)
    recovery_phrase = ma.Str()


class CreateUserSchema(ma.Schema):
    email = ma.Str(required=True)
    username = ma.Str(required=True)
    password = ma.Str(required=True)


class GroupSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Group
        ordered = True

    id = ma.auto_field(required=True)
    name = ma.auto_field(required=True)
    users = ma.Nested(SimpleUserSchema, many=True, required=True)
    invited_users = ma.Nested(SimpleUserSchema, many=True, required=True)


class UserGroupsSchema(ma.Schema):
    groups = ma.Nested(GroupSchema, many=True, required=True)
    group_invites = ma.Nested(GroupSchema, many=True, required=True)


class CreateGroupSchema(ma.Schema):
    name = ma.Str(required=True)


class EditGroupSchema(ma.Schema):
    name = ma.Str()
    invite_users = ma.List(ma.Str(), many=True)
    remove_users = ma.List(ma.Str(), many=True)


class CommentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Comment
        ordered = True

    id = ma.auto_field(dump_only=True)
    happiness_id = ma.auto_field(dump_only=True)
    author = ma.Nested(SimpleUserSchema, dump_only=True)
    text = ma.auto_field(required=True)
    timestamp = ma.Str(dump_only=True)


class CommentEditSchema(ma.Schema):
    data = ma.Str(required=True)


class HappinessSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Happiness
        ordered = True

    id = ma.auto_field(dump_only=True)
    author = ma.Nested(SimpleUserSchema, dump_only=True)
    value = ma.auto_field(required=True)
    comment = ma.auto_field()
    timestamp = ma.Date()


class DateIdGetSchema(ma.Schema):
    id = ma.Int()
    date = ma.Date()


class HappinessEditSchema(ma.Schema):
    value = ma.Float()
    comment = ma.Str()


class HappinessGetTimeSchema(ma.Schema):
    start = ma.Date(required=True)
    end = ma.Date()
    id = ma.Int()


class HappinessGetCountSchema(ma.Schema):
    page = ma.Int()
    count = ma.Int()
    id = ma.Int()


class HappinessGetPaginatedSchema(ma.Schema):
    page = ma.Int()
    count = ma.Int()


class GetByDateRangeSchema(ma.Schema):
    start = ma.Date(required=True)
    end = ma.Date()


class FileUploadSchema(ma.Schema):
    file = FileField()


class UserInfoSchema(ma.Schema):
    data_type = ma.Str(required=True)
    data = ma.Str(required=True)
    data2 = ma.Str()


class JournalSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Journal
        ordered = True

    id = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(dump_only=True)
    data = ma.auto_field(required=True)
    timestamp = ma.Date(required=True)

    @post_dump
    def decrypt_entry(self, data, **kwargs):
        try:
            if self.context.get('password_key'):
                decrypted = token_current_user().decrypt_data(self.context['password_key'], data['data'])
                data['data'] = decrypted.decode('utf-8')
        except Exception as e:
            print(e)
            return failure_response('Invalid password key.', 400)
        return data


DecryptedJournalSchema = JournalSchema(many=True)


class JournalGetSchema(ma.Schema):
    page = ma.Int()
    count = ma.Int()


class JournalEditSchema(ma.Schema):
    data = ma.Str(required=True)


class GetPasswordKeySchema(ma.Schema):
    password = ma.Str(required=True)


class PasswordKeyJWTSchema(ma.Schema):
    key_token = ma.Str(data_key='Password-Key', required=True)


class CreateReadsSchema(ma.Schema):
    happiness_id = ma.Int(required=True)


class ReadsSchema(ma.Schema):
    happiness_id = ma.Int(dump_only=True, required=True)
    user_id = ma.Int(dump_only=True, required=True)
    timestamp = ma.Str(dump_only=True, required=True)


class HappinessMultiFilterSchema(ma.Schema):
    user_id = ma.Int()
    page = ma.Int()
    count = ma.Int()
    low = ma.Float()
    high = ma.Float()
    start = ma.Date()
    end = ma.Date()
    text = ma.Str()


class NumberSchema(ma.Schema):
    number = ma.Int(required=True)


class CountSchema(ma.Schema):
    entries = ma.Int(required=True)
    groups = ma.Int(required=True)


class AmountSchema(ma.Schema):
    user_id = ma.Int()


class UserDeleteSchema(ma.Schema):
    password = ma.Str(required=True)
