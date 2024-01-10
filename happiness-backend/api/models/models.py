from __future__ import annotations

import base64
import hashlib
import os
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import current_app
from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import delete, Integer, String, DateTime, ForeignKey, Column, Boolean, Float, \
    LargeBinary, select
from sqlalchemy.orm import mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from api.app import db
from api.util.jwt_methods import generate_jwt

BaseModel: DefaultMeta = db.Model

# Group Users association table
group_users = db.Table(
    "group_users",
    BaseModel.metadata,
    Column("group_id", Integer, ForeignKey("group.id", ondelete='cascade')),
    Column("user_id", Integer, ForeignKey("user.id"))
)

# Group Invites association table
group_invites = db.Table(
    "group_invites",
    BaseModel.metadata,
    Column("group_id", Integer, ForeignKey("group.id", ondelete='cascade')),
    Column("user_id", Integer, ForeignKey("user.id"))
)

# Reads association table
readers_happiness = db.Table(
    "readers_happiness",
    BaseModel.metadata,
    Column("happiness_id", Integer, ForeignKey("happiness.id")),
    Column("reader_id", Integer, ForeignKey("user.id")),
    Column("timestamp", DateTime, default=datetime.utcnow())
)


class User(BaseModel):
    """
    User model. Has a one-to-many relationship with Setting.
    """
    __tablename__ = "user"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)

    # User information
    email = mapped_column(String, nullable=False, unique=True)
    username = mapped_column(String, nullable=False, unique=True)
    password = mapped_column(String, nullable=False)
    created = mapped_column(DateTime)
    profile_picture = mapped_column(String, nullable=False)
    encrypted_key = mapped_column(LargeBinary)
    encrypted_key_recovery = mapped_column(LargeBinary)

    settings = relationship("Setting", cascade="delete")
    groups = relationship("Group", secondary=group_users, back_populates="users", lazy='dynamic')
    invites = relationship("Group", secondary=group_invites, back_populates="invited_users")
    posts_read = relationship("Happiness", secondary=readers_happiness, back_populates="readers",
                              lazy="dynamic")

    def __init__(self, **kwargs):
        """
        Initializes a User object.
        Requires non-null kwargs: unique email, password, and unique username.
        """
        self.email = kwargs.get("email")

        # Convert raw password into encrypted string that can still be decrypted, but we cannot decrypt it.
        raw_password = kwargs.get("password")
        self.password = generate_password_hash(raw_password)
        self.username = kwargs.get("username")
        self.profile_picture = kwargs.get("profile_picture", self.avatar_url())
        self.created = datetime.today()
        self.e2e_init(raw_password)

    def e2e_init(self, password: str):
        """Generate user key for encrypting/decrypting data"""
        # also derive password key for encrypting/decrypting user key from user password
        # https://security.stackexchange.com/questions/157422/store-encrypted-user-data-in-database
        user_key = base64.urlsafe_b64encode(os.urandom(32))
        password_key = self.derive_password_key(password)
        self.encrypted_key = Fernet(password_key).encrypt(user_key)

    def derive_password_key(self, password: str) -> bytes:
        """Derive password key from user password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=bytes(current_app.config["ENCRYPT_SALT"], 'utf-8'),
            iterations=200000,
        )
        return base64.urlsafe_b64encode(kdf.derive(bytes(password, 'utf-8')))

    def generate_password_key_token(self, password: str, expiration=60) -> str:
        return generate_jwt(
            {'Password-Key': self.derive_password_key(password).decode('utf-8')}, expiration)

    def decrypt_user_key(self, password_key: str) -> bytes:
        """Decrypt user key using password key"""
        return Fernet(bytes(password_key, 'utf-8')).decrypt(self.encrypted_key)

    def encrypt_data(self, password_key: str, data: str) -> bytes:
        """Decrypt user key with password key, then encrypt data with user key"""
        user_key = self.decrypt_user_key(password_key)
        return Fernet(user_key).encrypt(bytes(data, 'utf-8'))

    def decrypt_data(self, password_key: str, data: str) -> bytes:
        """Decrypt user key with password key, then decrypt data with user key"""
        user_key = self.decrypt_user_key(password_key)
        return Fernet(user_key).decrypt(data)

    def avatar_url(self):
        digest = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon'

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def change_password(self, old_password: str, new_password: str):
        """Changes a user's password and updates its encrypted key"""
        # Decrypts user key with the user's old password,
        # then encrypts the user key with new password's key
        user_key = self.decrypt_user_key(self.derive_password_key(old_password).decode())
        self.encrypted_key = Fernet(self.derive_password_key(new_password)).encrypt(user_key)
        self.password = generate_password_hash(new_password)

    def add_key_recovery(self, password: str, recovery_phrase: str):
        """Add recovery phrase to prevent loss of encrypted data if user forgets their password"""
        # stores a copy of the user key encrypted with a recovery phrase
        user_key = self.decrypt_user_key(self.derive_password_key(password).decode())
        recovery_key = self.derive_password_key(recovery_phrase.lower())
        self.encrypted_key_recovery = Fernet(recovery_key).encrypt(user_key)

    def generate_password_reset_token(self, expiration=10) -> str:
        return generate_jwt({'reset_email': self.email}, expiration)

    def reset_password(self, new_password: str, recovery_phrase: str = None):
        """
        Resets a user's password
        *** !!! Will cause encrypted data to be lost if recovery phrase not provided !!! ***
        """
        self.password = generate_password_hash(new_password)
        if self.encrypted_key_recovery and recovery_phrase:
            # decrypts user key with recovery phrase, allowing user key to be encrypted with new password
            recovery_key = self.derive_password_key(recovery_phrase.lower())
            user_key = Fernet(recovery_key).decrypt(self.encrypted_key_recovery)
            self.encrypted_key = Fernet(self.derive_password_key(new_password)).encrypt(user_key)
        else:
            # creates new user key, rendering previously created encrypted data useless
            self.e2e_init(new_password)
            db.session.execute(delete(Journal).where(Journal.user_id == self.id))  # delete entries

    def create_token(self) -> tuple[Token, str]:
        """Generates a new session token for a user"""
        return Token().hashed(self.id)

    def has_mutual_group(self, user_to_check: User) -> bool:
        """
        Checks to see if the current users shares a happiness group user_to_check (a user object)
        """
        # checks if intersection of user's groups and user_to_check's groups is non-empty
        if user_to_check is None:
            return False
        return self.groups.intersect(user_to_check.groups).count() > 0

    def has_read_happiness(self, happiness):
        """Returns true if the user has read that happiness entry, false otherwise"""
        return self.posts_read.filter_by(id=happiness.id).count() > 0

    def read_happiness(self, happiness):
        """Adds a read entry for the user"""
        if not self.has_read_happiness(happiness):
            self.posts_read.append(happiness)

    def unread_happiness(self, happiness):
        """Removes a read entry for the user"""
        if self.has_read_happiness(happiness):
            self.posts_read.remove(happiness)


class Setting(BaseModel):
    """
    Settings model. Has a many-to-one relationship with User.
    To store settings I chose to use the property bag method.
    """
    __tablename__ = "setting"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    key = mapped_column(String, nullable=False)
    enabled = mapped_column(Boolean, nullable=False)
    value = mapped_column(String)
    user_id = mapped_column(Integer, ForeignKey("user.id"))

    def __init__(self, **kwargs):
        """
        Initializes a setting.
        Requires that kwargs contains key, enabled val, user_id
        """
        self.key = kwargs.get("key")
        self.enabled = kwargs.get("enabled")
        self.value = kwargs.get("value")
        self.user_id = kwargs.get("user_id")


class Group(BaseModel):
    """
    Group model. Has a many-to-many relationship with User.
    """
    __tablename__ = "group"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False)

    users = relationship("User", secondary=group_users, back_populates="groups")
    invited_users = relationship("User", secondary=group_invites, back_populates="invites")

    def __init__(self, **kwargs):
        """
        Creates a happiness group.
        Required kwargs: name
        """
        self.name = kwargs.get("name")

    def invite_users(self, users_to_invite: list[str]):
        """
        Invites a list of usernames to join a group
        Requires: Users to be invited must exist and not already be in the group
        """
        for username in users_to_invite:
            user = db.session.execute(select(User).where(User.username.ilike(username))).scalar()
            if user is not None and user not in self.users and user not in self.invited_users:
                self.invited_users.append(user)

    def add_users(self, users_to_add: list[User]):
        """
        Adds a list of user objects to a group
        Requires: Users must already have been invited to the group
        """
        for user in users_to_add:
            if user in self.invited_users:
                self.invited_users.remove(user)
                self.users.append(user)

    def remove_users(self, users_to_remove: list[str]):
        """
        Removes a list of usernames from a group
        Requires: Users to be removed must exist and already be in or invited to the group
        """
        for username in users_to_remove:
            user = db.session.execute(select(User).where(User.username.ilike(username))).scalar()
            if user is not None:
                if user in self.users:
                    self.users.remove(user)
                elif user in self.invited_users:
                    self.invited_users.remove(user)


class Happiness(BaseModel):
    """
    Happiness model. Has a many-to-one relationship with users table.
    """
    __tablename__ = "happiness"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, ForeignKey("user.id"))
    value = mapped_column(Float)
    comment = mapped_column(String)
    timestamp = mapped_column(DateTime)

    author = relationship("User")
    discussion_comments = relationship("Comment", cascade='delete', lazy='dynamic')
    readers = relationship("User", secondary=readers_happiness, back_populates="posts_read",
                           lazy="dynamic")

    def __init__(self, **kwargs):
        """
        Initializes a Happiness object.
        Requires non-null kwargs: happiness value, timestamp, and user ID.
        """
        self.user_id = kwargs.get("user_id")
        self.value = kwargs.get("value")
        self.comment = kwargs.get("comment")
        self.timestamp = kwargs.get("timestamp")


class Comment(BaseModel):
    """
    Comment model. Has a many-to-one relationship with happiness table.
    """
    __tablename__ = "comment"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    happiness_id = mapped_column(ForeignKey("happiness.id"))
    user_id = mapped_column(ForeignKey("user.id"))
    text = mapped_column(String, nullable=False)
    timestamp = mapped_column(DateTime, nullable=False)

    author = relationship("User")

    def __init__(self, **kwargs):
        """
        Initializes a Happiness Discussion Comment object.
        Requires non-null kwargs: happiness ID, user ID, and comment text.
        """
        self.happiness_id = kwargs.get("happiness_id")
        self.user_id = kwargs.get("user_id")
        self.text = kwargs.get("text")
        self.timestamp = datetime.utcnow()


class Journal(BaseModel):
    """
    Journal model. Has a many-to-one relationship with user table.
    """
    __tablename__ = "journal"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, ForeignKey("user.id"))
    data = mapped_column(LargeBinary, nullable=False)
    timestamp = mapped_column(DateTime, nullable=False)

    def __init__(self, **kwargs):
        """
        Initializes a Private Journal Entry object.
        Requires non-null kwargs: user ID, date of entry, and encrypted entry text.
        """
        self.user_id = kwargs.get("user_id")
        self.data = kwargs.get("encrypted_data")
        self.timestamp = kwargs.get("timestamp")


class Token(BaseModel):
    """
    Token model. Has a many-to-one relationship with users table.
    """
    __tablename__ = "token"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, ForeignKey("user.id"))
    session_token = mapped_column(String, nullable=False, unique=True) # stored using hashing
    session_expiration = mapped_column(DateTime, nullable=False)

    @staticmethod
    def hashed(user_id: int) -> tuple[Token, str]:
        """
        Create a hashed session token for a user.
        Returns the associated token object and the unhashed token.
        """
        token = hashlib.sha1(os.urandom(64)).hexdigest()
        hashed_token = hashlib.sha256(token.encode()).hexdigest()
        return Token(user_id=user_id, hashed_token=hashed_token), token

    def __init__(self, **kwargs):
        """
        Generates a new session token for a user.
        Requires non-null kwargs: user ID and hashed session token.
        """
        self.user_id = kwargs.get("user_id")
        self.session_token = kwargs.get("hashed_token")
        self.session_expiration = datetime.utcnow() + timedelta(weeks=3)

    def verify(self) -> bool:
        """Verifies a user's session token."""
        return self.session_expiration > datetime.utcnow()

    def revoke(self):
        """Expires a user's session token."""
        self.session_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        db.session.execute(delete(Token).where(Token.session_expiration < yesterday))
