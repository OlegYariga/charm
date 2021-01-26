import secrets
import string
from datetime import datetime
from hmac import compare_digest

from flask import current_app, request
from flask_login import current_user
from sqlalchemy import exists

from keyserv.models import AuditLog, Event, Key, db

class Memo:
    """Memo that identifies a key action."""

    def __init__(self, ip, machine, user, hardware_id=None):
        self.ip = ip
        self.machine = machine
        self.user = user
        self.hwid = hardware_id

    def __str__(self):
        return f"IP: {self.ip}, Machine: {self.machine}, User: {self.user}"

    def __repr__(self):
        return f"<Origin({self.ip}, {self.machine}, {self.user})>"


class ExhuastedActivations(Exception):
    """Raised when an activation attempt is made but the remaining activations
    is already at 0."""
    pass


class KeyNotFound(Exception):
    """Raised when an action is attempted on a non-existent key."""
    pass


class Origin:
    """Origin that identifies a key action."""

    def __init__(self, ip, machine, user, hardware_id=None):
        self.ip = ip
        self.machine = machine
        self.user = user
        self.hwid = hardware_id

    def __str__(self):
        return f"IP: {self.ip}, Machine: {self.machine}, User: {self.user}"

    def __repr__(self):
        return f"<Origin({self.ip}, {self.machine}, {self.user})>"


def rand_token(length: int = 25,
               chars: str = string.ascii_uppercase + string.digits) -> str:
    """
    Generate a random token. Does not check for duplicates yet.

    A length of 25 should give us 8.082812775E38 keys.

    length: - length of token to generate
    chars: - characters used in seeding of token
    """
    return "".join(secrets.choice(chars) for i in range(length))


def token_exists_unsafe(token: str, hwid: str = "") -> bool:
    """Check if `token` exists in the token database. Does NOT perform constant
    time comparison. Should not be used in APIs """
    return db.session.query(exists().where(Key.token == token)
                                    .where(Key.hwid == hwid)).scalar()


def token_matches_hwid(token: str, hwid: str) -> bool:
    """Check if the supplied hwid matches the hwid on a key"""
    k = Key.query(token=token)

    return bool(_compare(hwid, k.hwid))


def generate_token_unsafe() -> str:
    """
    Generate a new token.

    Does not perform constant time comparison when checking if the generated
    token is a duplicate.
    """
    key = rand_token()
    while token_exists_unsafe(key):
        key = rand_token()
    return key


def cut_key_unsafe(activations: int, app_id: int,
                   active: bool = True, memo: str = "") -> str:
    """
    Cuts a new key and returns the activation token.

    Cuts a new key with # `activations` allowed activations. -1 is considered
    unlimited activations.
    """
    token = generate_token_unsafe()
    key = Key(token, activations, app_id, active, memo)
    key.cutdate = datetime.utcnow()

    db.session.add(key)
    db.session.commit()

    current_app.logger.info(
        f"cut new key {key} with {activations} activation(s), memo: {memo}")
    AuditLog.from_key(key,
                      f"new key cut by {current_user.username} "
                      f"({request.remote_addr})",
                      Event.KeyCreated)

    return token


