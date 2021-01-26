import secrets

import argon2
from flask_login import LoginManager, UserMixin

from keyserv.models import db

login_manager = LoginManager()
login_manager.session_protection = "strong"


def add_user(username: str, password: bytes, level=500):
    passwd = argon2.hash_password(password, secrets.token_bytes(None))
    user = Users(username, passwd, level)
    db.session.add(user)
    db.session.commit()


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    passwd = db.Column(db.LargeBinary(), nullable=False)
    level = db.Column(db.Integer())

    def __init__(self, username=None, passwd=None, level=0):
        self.username = username
        self.passwd = passwd
        self.level = level

    def get_id(self):
        return self.id

    def check_password(self, passwd):
        try:
            return argon2.verify_password(self.passwd, bytes(passwd, "UTF-8"))
        except argon2.exceptions.VerifyMismatchError:
            return False


@login_manager.user_loader
def user_loader(user_id) -> Users:
    return Users.query.get(user_id)

