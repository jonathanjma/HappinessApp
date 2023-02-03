import hashlib
import os
from datetime import datetime, timedelta

import bcrypt

from api.app import db


class User(db.Model):
    """
    User model. Has a one-to-many relationship with setting table.
    """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # User information
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password_digest = db.Column(db.String, nullable=False)
    # Will represent an AWS URL
    profile_picture = db.Column(db.String, nullable=False)
    # If the user has not yet set a profile picture the field gets set to "default"
    settings = db.relationship("Setting", cascade="delete")

    # Session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, **kwargs):
        """
        Initializes a User object.
        Requires non-null kwargs: unique email, password, and unique username.
        """
        self.email = kwargs.get("email")
        # Convert raw password into encrypted string that can still be decrypted, but we cannot decrypt it.
        self.password_digest = bcrypt.hashpw(kwargs.get(
            "password").encode("utf8"), bcrypt.gensalt(rounds=13))
        self.username = kwargs.get("username")
        self.profile_picture = kwargs.get("profile_picture", "default")
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
        self.update_token = self._urlsafe_base_64()  # don't need anymore?
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


class Happiness(db.Model):
    """
    Happiness model. Has a many-to-one relationship with users table.
    """
    __tablename__ = "happiness"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    value = db.Column(db.Integer)
    comment = db.Column(db.String(700))
    timestamp = db.Column(db.DateTime, unique=True)

    def __init__(self, **kwargs):
        """
        Initializes a Happiness object.
        Requires non-null kwargs: happiness value, timestamp, and user ID.
        """
        self.user_id = kwargs.get("user_id")
        self.value = kwargs.get("value")
        self.comment = kwargs.get("comment")
        self.timestamp = kwargs.get("timestamp")
        # self.timestamp = kwargs.get("timestamp")

    def serialize(self):
        return {
            "user id": self.user_id,
            "happiness value": self.value,
            "comment": self.comment,
            "timestamp": self.timestamp.strftime("%Y-%m-%d")
        }
