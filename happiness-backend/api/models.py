import base64
import hashlib
import os
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import current_app
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

# Community Users association table
community_users = db.Table(
    "community_users",
    db.Model.metadata,
    db.Column("community_id", db.Integer, db.ForeignKey(
        "community.id", ondelete='cascade')),
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
    encrypted_key = db.Column(db.String)
    encrypted_key_recovery = db.Column(db.String)

    settings = db.relationship("Setting", cascade="delete")
    groups = db.relationship("Group", secondary=group_users, back_populates="users", lazy='dynamic')

    communities = db.relationship(
        "Community", secondary=community_users, back_populates="users", lazy='dynamic')

    def __init__(self, **kwargs):
        """
        Initializes a User object.
        Requires non-null kwargs: unique email, password, and unique username.
        """
        self.email = kwargs.get("email")

        # Convert raw password into encrypted string that can still be decrypted, but we cannot decrypt it.
        raw_pwd = kwargs.get("password")
        self.password = generate_password_hash(raw_pwd)
        self.username = kwargs.get("username")
        self.profile_picture = kwargs.get("profile_picture", self.avatar_url())
        self.created = datetime.today()
        self.e2e_init(raw_pwd)

    # generate user key for encrypting/decrypting data
    # derive password key for encrypting/decrypting user key from user password
    # store encrypted user key in db
    # https://security.stackexchange.com/questions/157422/store-encrypted-user-data-in-database
    def e2e_init(self, password):
        user_key = base64.urlsafe_b64encode(os.urandom(32))
        password_key = self.derive_pwd_key(password)
        self.encrypted_key = Fernet(password_key).encrypt(user_key)

    # derive password key from user password
    def derive_pwd_key(self, password):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=bytes(current_app.config["ENCRYPT_SALT"], 'utf-8'),
            iterations=200000,
        )
        return base64.urlsafe_b64encode(kdf.derive(bytes(password, 'utf-8')))

    # decrypt user key using password key
    def decrypt_user_key(self, pwd_key):
        return Fernet(bytes(pwd_key, 'utf-8')).decrypt(self.encrypted_key)

    # decrypt user key with password key, then encrypt data with user key
    def encrypt_data(self, pwd_key, data):
        user_key = self.decrypt_user_key(pwd_key)
        return Fernet(user_key).encrypt(bytes(data, 'utf-8'))

    # decrypt user key with password key, then decrypt data with user key
    def decrypt_data(self, pwd_key, data):
        user_key = self.decrypt_user_key(pwd_key)
        return Fernet(user_key).decrypt(data)

    def avatar_url(self):
        digest = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon'

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    # change user password + update encrypted key
    # (decrypt user key with old password key, then encrypt with new password key, update db)
    def change_password(self, new_pwd, pwd_key):
        user_key = self.decrypt_user_key(pwd_key)
        new_pwd_key = self.derive_pwd_key(new_pwd)
        self.encrypted_key = Fernet(new_pwd_key).encrypt(user_key)
        self.password = generate_password_hash(new_pwd)

    # add recovery phrase to prevent data loss if password is forgotten
    # (stores a copy of the user key encrypted with a recovery phrase)
    def add_key_recovery(self, recovery_phrase, pwd_key):
        user_key = self.decrypt_user_key(pwd_key)
        recovery_key = self.derive_pwd_key(recovery_phrase.lower())
        self.encrypted_key_recovery = Fernet(recovery_key).encrypt(user_key)

    # reset password
    # *** !!! Will cause encrypted data to be lost if recovery not set up
    # or old password key not provided !!! ***
    def reset_password(self, new_pwd, recovery_phrase=None, pwd_key=None):
        self.password = generate_password_hash(new_pwd)
        if self.encrypted_key_recovery and recovery_phrase:
            # decrypts user key with recovery phrase, allowing user key to be encrypted with new password
            recovery_key = self.derive_pwd_key(recovery_phrase.lower())
            user_key = Fernet(recovery_key).decrypt(self.encrypted_key_recovery)
            new_pwd_key = self.derive_pwd_key(new_pwd)
            self.encrypted_key = Fernet(new_pwd_key).encrypt(user_key)
        elif pwd_key:
            # decrypt data with old password key (useful if old key is still stored in client)
            self.change_password(new_pwd, pwd_key)
        else:
            # creates new user key, rendering previously created encrypted data useless
            self.e2e_init(new_pwd)
            db.session.execute(delete(Journal).where(Journal.user_id == self.id)) # delete entries

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

    users = db.relationship("User", secondary=group_users, back_populates="groups")

    def __init__(self, **kwargs):
        """
        Creates a happiness group.
        Required kwargs: name
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
        Removes a list of usernames from a group
        Requires: Users to be removed must exist and already be in or invited to the group
        """
        for username in users_to_remove:
            user = User.query.filter(User.username.ilike(username)).first()
            if user is not None and user in self.users:
                self.users.remove(user)


class Community(db.Model):
    """
    Community model. Has a many-to-one relationship with users table.
    """
    __tablename__ = "community"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    users = db.relationship(
        "User", secondary=community_users, back_populates="communities")

    def __init__(self, **kwargs):
        """
        Creates a happiness community.
        Required kwargs: name
        """
        self.name = kwargs.get("name")

    def add_users(self, new_users):
        """
        Adds users to a community
        Requires: List of usernames to add; Users to be added must exist and not already be in the community
        """
        for username in new_users:
            user = User.query.filter(User.username.ilike(username)).first()
            if user is not None and user not in self.users:
                self.users.append(user)

    def remove_users(self, users_to_remove):
        """
        Removes a list of usernames from a community
        Requires: Users to be removed must exist and already be in the community
        """
        for username in users_to_remove:
            user = User.query.filter(User.username.ilike(username)).first()
            if user is not None and user in self.users:
                self.users.remove(user)


class Statistic(db.Model):
    """
    Statistic model. Has a many-to-one-relationship with Community table.
    """
    __tablename__ = "statistic"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    community_id = db.Column(db.Integer, db.ForeignKey("community.id"))
    mean = db.Column(db.Float)
    median = db.Column(db.Float)
    stdev = db.Column(db.Float)
    minval = db.Column(db.Float)
    maxval = db.Column(db.Float)
    firstquar = db.Column(db.Float)
    thirdquar = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        """
        Initializes a Statistc object.
        Requires non-null kwargs: mean, median, standard deviation, minimum
        value, maxmimum value, Q1, Q3, timestamp, and community ID.
        """
        self.community_id = kwargs.get("community_id")
        self.mean = kwargs.get("mean")
        self.median = kwargs.get("median")
        self.stdev = kwargs.get("stdev")
        self.minval = kwargs.get("minval")
        self.maxval = kwargs.get("maxval")
        self.firstquar = kwargs.get("firstquar")
        self.thirdquar = kwargs.get("thirdquar")
        self.timestamp = kwargs.get("timestamp")


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

class Journal(db.Model):
    """
    Journal model. Has a many-to-one relationship with user table.
    """
    __tablename__ = "journal"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    data = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, **kwargs):
        """
        Initializes a Private Journal Entry object.
        Requires non-null kwargs: user ID and encrypted entry text.
        """
        self.user_id = kwargs.get("user_id")
        self.data = kwargs.get("encrypted_data")
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
