# adjust the Config class below, then rename this file to config.py


class DefaultConfig(object):
    # a decent way to generate a secret key is by running: python -c "import os; print(repr(os.urandom(24)))"
    # then pasting the output here.
    SECRET_KEY = "3f5f72e6-0064-4372-a957-bf405b3b5bf9"

    DEBUG = False
    TESTING = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(DefaultConfig):

    SQLALCHEMY_DATABASE_URI = "postgres://localhost/keyserver"


class DevelopmentConfig(ProductionConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
