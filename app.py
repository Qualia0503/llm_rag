import os, time
from flask import Flask, redirect, url_for
from extensions import ext_template_filter, ext_database, ext_migrate, \
    ext_redis, ext_celery, ext_milvus, ext_logger
from commands import register_commands
from config import *
from apps.dataset.models import Dataset, Document, Segment
from apps.chat.models import Conversation

def create_app() -> Flask:
    app = Flask(__name__)
    
    app.config.from_pyfile('config.py')
    app.secret_key = SECRET_KEY

    os.environ['TZ'] = TIMEZONE
    # 仅在非Windows系统下生效
    if not os.name == 'nt':
        time.tzset()

    initialize_extensions(app)
    register_commands(app)
    register_blueprints(app)

    @app.route('/', endpoint='index')
    def index():
        # return 'index'
        return redirect(url_for('auth.login'))

    return app


def initialize_extensions(app):
    ext_template_filter.init_app(app)
    ext_database.init_app(app)
    ext_migrate.init_app(app, ext_database.db)
    ext_redis.init_app(app)
    ext_celery.init_app(app)
    ext_milvus.init_app(app)
    ext_logger.init_app(app)


def register_blueprints(app):
    # Chat模块
    from apps.chat import bp as chat_bp
    app.register_blueprint(chat_bp)
    
    # Auth模块
    from apps.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    # dataset模块
    from apps.dataset import bp as dataset_bp
    app.register_blueprint(dataset_bp)

app = create_app()
celery = app.extensions["celery"]


if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0')

