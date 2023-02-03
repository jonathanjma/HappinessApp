import hashlib
import os
from datetime import datetime, timedelta

import bcrypt

from api.app import db

# Group Users association table
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
    profile_picture = db.Column(db.String, nullable=False)  # Will represent an AWS URL
    # If the user has not yet set a profile picture the field gets set to "default"
    settings = db.relationship("Setting", cascade="delete")

    # Session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

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
        Requires that kwargs argument name
        """
        self.name = kwargs.get("name")

    # TODO error if username not valid
    def add_users(self, new_users):
        """
        Adds users to a group
        Requires a list of usernames to add
        """
        for username in new_users:
            user = User.query.filter(User.username == username).first()
            if user not in self.users:
                self.users.append(user)

    def remove_users(self, users_to_remove):
        """
        Removes users to a group
        Requires a list of usernames to remove
        """
        for username in users_to_remove:
            user = User.query.filter(User.username == username).first()
            if user in self.users:
                self.users.remove(user)
