from flask_migrate import Migrate


def init_app(app, db):
    Migrate(app, db)
