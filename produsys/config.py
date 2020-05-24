import os


class Config(object):
    """Base configuration."""
    DATABASE = 'SQLAlchemy'
    DB_MIGRATION = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost/produsys'


class ProdConfig(Config):
    ENV = 'production'
    DEBUG = False
    USE_RELOADER = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    ENV = 'development'
    DEBUG = True
    USE_RELOADER = True
    SECRET_KEY = 'dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
