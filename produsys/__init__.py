import os
from flask import Flask, redirect, url_for, g
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from produsys import auth, dashboard, projects, tasks, statistics
from produsys.db import repo


def create_app(config=None, config_mapping=None):
    app = Flask(__name__, instance_relative_config=True)
    Bootstrap(app)

    if config is None:
        config = os.environ.get('FLASK_CONFIG')
        if config is None:
            config = 'DevConfig'

    config_path = 'config.' + config
    try:
        app.config.from_object(config_path)
    except ImportError:
        print('Unknown config, running with DevConfig')
        config_path = 'produsys.config.DevConfig'
    finally:
        app.config.from_object(config_path)

    with app.app_context():
        repo.init_app(app)
    migrate = Migrate(app, repo.db)

    @app.route('/')
    def index():
        if g.user is None:
            return redirect(url_for('auth.login'))
        return redirect(url_for('dashboard.index'))

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(tasks.bp)
    app.register_blueprint(statistics.bp)

    return app
