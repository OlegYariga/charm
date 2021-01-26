import click
from flask import Flask
from flask_bootstrap import Bootstrap

from .auth import login_manager, add_user
from .endpoints import api
from .models import db, Event
from .views import frontend


def format_event(value):
    return Event(value)


def format_datetime(value):
    if value is None:
        return ""

    try:
        return value.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return ""


def create_app(config):
    app = Flask(__name__)

    app.config.from_object(__name__)
    app.config.from_object("keyserv.config.{}".format(config))
    app.jinja_env.filters["event"] = format_event
    app.jinja_env.filters["datetime"] = format_datetime

    Bootstrap(app)
    api.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(frontend)

    @app.cli.command("initdb")
    def initdb_command():
        db.create_all()
        print("database initialized")

    @app.cli.command("create-user")
    @click.argument("username")
    @click.argument("password")
    def create_user_command(username: str, password: str):
        add_user(username, password.encode())

    return app

