import hashlib
import os
import jwt
from datetime import datetime, timedelta

import bcrypt

from api.app import db

group_users = db.Table(
    "group_users",
    db.Model.metadata,
    db.Column("group_id", db.Integer, db.ForeignKey("group.id", ondelete='cascade')),
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
    password_digest = db.Column(db.String, nullable=False)
    profile_picture = db.Column(db.String, nullable=False)
    # Will represent an AWS URL
    # If the user has not yet set a profile picture the field gets set to "default"

    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    # Whether the user has confirmed their email

    settings = db.relationship("Setting", cascade="delete")

    # Session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)

    groups = db.relationship("Group", secondary=group_users, back_populates="users")

    def __init__(self, **kwargs):
        """
        Initializes a User object.
        Requires non-null kwargs: unique email, password, and unique username.
        """
        self.email = kwargs.get("email")
        # Convert raw password into encrypted string that can still be decrypted, but we cannot decrypt it.
        self.password_digest = bcrypt.hashpw(kwargs.get("password").encode("utf8"),
                                             bcrypt.gensalt(rounds=13))
        self.username = kwargs.get("username")
        self.profile_picture = kwargs.get("profile_picture", "default")
        self.confirmed = kwargs.get("confirmed", False)
        self.get_token()

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
        return bcrypt.checkpw(password.encode("utf8"), self.password_digest)

    def _urlsafe_base_64(self):
        """
        Randomly generates hashed tokens (used for session/update tokens)
        """
        return hashlib.sha1(os.urandom(64)).hexdigest()

    def get_token(self):
        """
        Generates a new session token for a user
        """
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.utcnow() + timedelta(weeks=1)
        return self.session_token

    def revoke_token(self):
        """
        Expires the session token of a user
        """
        self.session_expiration = datetime.utcnow() - timedelta(seconds=1)

    def verify_session_token(self):
        """
        Verifies the session token of a user
        """
        return self.session_expiration > datetime.utcnow()

    def get_reset_password_token(self, expires_in=10):
        """
        Generates a password reset token with PyJWT.
        :param expires_in: How long it takes for the token to expire, in minutes.
        :return: an encoded
        """
        return jwt.encode(
            {'reset_password': self.id, 'exp': datetime.utcnow() + timedelta(minutes=expires_in)},
            os.environ.get("SECRET_KEY"), algorithm='HS256'
        )

    def set_password(self, password):
        self.password_digest = bcrypt.hashpw(password.encode("utf8"),
                                             bcrypt.gensalt(rounds=13))

    @staticmethod
    def verify_reset_password(token):
        try:
            id = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


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
    users = db.relationship("User", secondary=group_users, back_populates="groups")

    def __init__(self, **kwargs):
        """
        Initializes a group.
        Requires that kwargs contains name
        """
        self.name = kwargs.get("name")

    def add_users(self, new_users):
        for user_dict in new_users:
            user = User.query.filter(User.username == user_dict['username']).first()
            if user not in self.users:
                self.users.append(user)

    def remove_users(self, users_to_remove):
        for user_dict in users_to_remove:
            user = User.query.filter(User.username == user_dict['username']).first()
            if user in self.users:
                self.users.remove(user)
