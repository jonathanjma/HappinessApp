import hashlib
import os
from datetime import datetime, timedelta

from sqlalchemy import delete
from werkzeug.security import generate_password_hash, check_password_hash

from api.app import db

# Group Users association table
group_users = db.Table(
    "group_users",
    db.Model.metadata,
    db.Column("group_id", db.Integer, db.ForeignKey(
        "group.id", ondelete='cascade')),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"))
)

# Group Invites association table
group_invites = db.Table(
    "group_invites",
    db.Model.metadata,
    db.Column("group_id", db.Integer, db.ForeignKey(
        "group.id", ondelete='cascade')),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"))
)


class User(db.Model):
    """
    User model. Has a one-to-many relationship with Setting.
    """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # User information
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime)
    profile_picture = db.Column(db.String, nullable=False)
    settings = db.relationship("Setting", cascade="delete")

    groups = db.relationship(
        "Group", secondary=group_users, back_populates="users", lazy='dynamic')
    invites = db.relationship(
        "Group", secondary=group_invites, back_populates="invited_users")

    def __init__(self, **kwargs):
        """
        Initializes a User object.
        Requires non-null kwargs: unique email, password, and unique username.
        """
        self.email = kwargs.get("email")

        # Convert raw password into encrypted string that can still be decrypted, but we cannot decrypt it.
        self.password = generate_password_hash(kwargs.get("password"))
        self.username = kwargs.get("username")
        self.profile_picture = kwargs.get("profile_picture", self.avatar_url())
        self.created = datetime.today()

    def avatar_url(self):
        digest = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon'

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def create_token(self):
        """
        Generates a new session token for a user
        """
        return Token(user_id=self.id)

    def has_mutual_group(self, user_to_check):
        """
        Checks to see if the current users shares a happiness group user_to_check (a user object)
        """
        # checks if intersection of user's groups and user_to_check's groups is non-empty
        if user_to_check is None:
            return False
        return self.groups.intersect(user_to_check.groups).count() > 0


class Setting(db.Model):
    """
    Settings model. Has a many-to-one relationship with User.
    To store settings I chose to use the property bag method.
    """
    __tablename__ = "setting"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False)
    value = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, **kwargs):
        """
        Initializes a setting.
        Requires that kwargs contains key, enabled val, user_id
        """
        self.key = kwargs.get("key")
        self.enabled = kwargs.get("enabled")
        self.value = kwargs.get("value")
        self.user_id = kwargs.get("user_id")


class Group(db.Model):
    """
    Group model. Has a many-to-many relationship with User.
    """
    __tablename__ = "group"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    users = db.relationship(
        "User", secondary=group_users, back_populates="groups")
    invited_users = db.relationship(
        "User", secondary=group_invites, back_populates="invites")

    def __init__(self, **kwargs):
        """
        Creates a happiness group.
        Required kwargs: name
        """
        self.name = kwargs.get("name")

    def invite_users(self, users_to_invite):
        """
        Invites a list of usernames to join a group
        Requires: Users to be invited must exist and not already be in the group
        """
        for username in users_to_invite:
            user = User.query.filter(User.username.ilike(username)).first()
            if user is not None and user not in self.users and user not in self.invited_users:
                self.invited_users.append(user)

    def add_user(self, user_to_add):
        """
        Adds a user object to a group
        Requires: User must already have been invited to the group
        """
        if user_to_add in self.invited_users:
            self.invited_users.remove(user_to_add)
            self.users.append(user_to_add)

    def remove_users(self, users_to_remove):
        """
        Removes a list of usernames from a group
        Requires: Users to be removed must exist and already be in or invited to the group
        """
        for username in users_to_remove:
            user = User.query.filter(User.username.ilike(username)).first()
            if user is not None:
                if user in self.users:
                    self.users.remove(user)
                elif user in self.invited_users:
                    self.invited_users.remove(user)


class Happiness(db.Model):
    """
    Happiness model. Has a many-to-one relationship with users table.
    """
    __tablename__ = "happiness"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    value = db.Column(db.Float)
    comment = db.Column(db.String)
    timestamp = db.Column(db.DateTime)

    discussion_comments = db.relationship(
        "Comment", cascade='delete', lazy='dynamic')

    def __init__(self, **kwargs):
        """
        Initializes a Happiness object.
        Requires non-null kwargs: happiness value, timestamp, and user ID.
        """
        self.user_id = kwargs.get("user_id")
        self.value = kwargs.get("value")
        self.comment = kwargs.get("comment")
        self.timestamp = kwargs.get("timestamp")


class Comment(db.Model):
    """
    Comment model. Has a many-to-one relationship with happiness table.
    """
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    happiness_id = db.Column(db.Integer, db.ForeignKey("happiness.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    text = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    author = db.relationship("User")

    def __init__(self, **kwargs):
        """
        Initializes a Happiness Discussion Comment object.
        Requires non-null kwargs: happiness ID, user ID, and comment text.
        """
        self.happiness_id = kwargs.get("happiness_id")
        self.user_id = kwargs.get("user_id")
        self.text = kwargs.get("text")
        self.timestamp = datetime.utcnow()


class Token(db.Model):
    """
    Token model. Has a many-to-one relationship with users table.
    """
    __tablename__ = "token"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)

    def __init__(self, **kwargs):
        """Generates a new session token for a user."""
        self.user_id = kwargs.get("user_id")
        self.session_token = hashlib.sha1(os.urandom(64)).hexdigest()
        self.session_expiration = datetime.utcnow() + timedelta(weeks=3)

    def verify(self):
        """Verifies a user's session token."""
        return self.session_expiration > datetime.utcnow()

    def revoke(self):
        """Expires a user's session token."""
        self.session_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        db.session.execute(delete(Token).where(
            Token.session_expiration < yesterday))
