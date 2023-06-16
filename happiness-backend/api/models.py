import hashlib
import os
from datetime import datetime, timedelta
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
        "Group", secondary=group_users, back_populates="users")

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

    def serialize(self):
        """
        Serializes user object into readable JSON.
        Omits email password, and session information for security reasons
        """
        return {
            "id": self.id,
            "username": self.username,
            "profile picture": self.profile_picture,
            "settings": [setting.serialize() for setting in self.settings]
        }

    def verify_password(self, password):
        """
        Verifies the password of a user
        """
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
        Checks to see if another user shares a happiness group with the user
        :param user_to_check the user object to check if it is in the same group.
        """
        for group in self.groups:
            if user_to_check in group.users:
                return True
        return False


class Setting(db.Model):
    """
    Settings model. Has a many-to-one relationship with User.
    To store settings I chose to use the property bag method [1]
    """
    __tablename__ = "setting"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String, nullable=False)
    value = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, **kwargs):
        """
        Initializes a setting.
        Requires that kwargs contains key, value, user_id
        """
        self.key = kwargs.get("key")
        self.value = kwargs.get("value")
        self.user_id = kwargs.get("user_id")

    def serialize(self):
        """
        Serializes a user settings object for returning JSON
        """
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "user_id": self.user_id,
        }


class Group(db.Model):
    """
    Group model. Has a many-to-many relationship with User.
    """
    __tablename__ = "group"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    users = db.relationship(
        "User", secondary=group_users, back_populates="groups")

    def __init__(self, **kwargs):
        """
        Initializes a group.
        Requires that kwargs argument name
        """
        self.name = kwargs.get("name")

    def add_users(self, new_users):
        """
        Adds users to a group
        Requires a list of usernames to add
        Users to be added must exist and not already be in the group
        """
        for username in new_users:
            user = User.query.filter(User.username.ilike(username)).first()
            if user is not None and user not in self.users:
                self.users.append(user)

    def remove_users(self, users_to_remove):
        """
        Removes users to a group
        Requires a list of usernames to remove
        Users to be removed must exist and already be in the group
        """
        for username in users_to_remove:
            user = User.query.filter(User.username.ilike(username)).first()
            if user is not None and user in self.users:
                self.users.remove(user)


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

    def __init__(self, **kwargs):
        """
        Initializes a Happiness object.
        Requires non-null kwargs: happiness value, timestamp, and user ID.
        """
        self.user_id = kwargs.get("user_id")
        self.value = kwargs.get("value")
        self.comment = kwargs.get("comment")
        self.timestamp = kwargs.get("timestamp")


class Token(db.Model):
    """
   Model for the token table. Has a many-to-one relationship with users table.
   """
    __tablename__ = "token"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)

    def __init__(self, **kwargs):
        """
        Generates a new session token for a user
        """
        self.user_id = kwargs.get("user_id")
        self.session_token = hashlib.sha1(os.urandom(64)).hexdigest()
        self.session_expiration = datetime.utcnow() + timedelta(weeks=3)

    def verify(self):
        """
        Verifies a user's session token
        """
        return self.session_expiration > datetime.utcnow()

    def revoke(self):
        """
        Expires a user's session token
        """
        self.session_expiration = datetime.utcnow() - timedelta(seconds=1)
