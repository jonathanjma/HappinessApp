from marshmallow import post_dump, pre_dump

from api.app import ma
from api.auth import token_auth
from api.dao.users_dao import get_user_by_id
from api.models import User, Group, Happiness, Setting, Comment, clone_model


class EmptySchema(ma.Schema):
    pass

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
    session_token = ma.Str(required=True)


class UsernameSchema(ma.Schema):
    username = ma.Str(required=True)


class PasswordResetReqSchema(ma.Schema):
    email = ma.Email(required=True)  # This is probably bad practice (I am still learning)

class PasswordResetSchema(ma.Schema):
    password = ma.Str(required=True)

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

class HappinessSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Happiness
        ordered = True

    id = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(dump_only=True)
    value = ma.auto_field(required=True)
    comment = ma.auto_field()
    timestamp = ma.Str(required=True)
    discussion_comments = ma.Nested(CommentSchema, many=True, dump_only=True)

    @pre_dump
    def filter_comments(self, happiness_obj, **kwargs):
        # only show comments if the commenter shares a group with the current user
        cloned = Happiness(**clone_model(happiness_obj))
        filtered = []
        for comment in happiness_obj.discussion_comments:
            if token_auth.current_user().has_mutual_group(get_user_by_id(comment.user_id)):
                filtered.append(comment)
        cloned.discussion_comments = filtered
        return cloned

    @post_dump
    def fix_time(self, data, **kwargs):
        if data.get('timestamp'):
            data['timestamp'] = data['timestamp'].split()[0]
        return data

class HappinessEditSchema(ma.Schema):
    value = ma.Float()
    comment = ma.Str()


class HappinessGetTime(ma.Schema):
    start = ma.Str(required=True)
    end = ma.Str()
    id = ma.Int()


class HappinessGetCount(ma.Schema):
    page = ma.Int()
    count = ma.Int()
    id = ma.Int()
