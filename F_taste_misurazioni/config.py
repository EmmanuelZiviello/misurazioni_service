from datetime import timedelta
from F_taste_nutrizionista.utils.credentials import secret_key
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    TESTING = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URI','postgresql://postgres:Bcsoftqwerty@localhost:5432/f-taste')
    DB_URI_PATIENT = os.environ.get('DB_URI_PATIENT', 'postgresql://patient:patient@localhost:5432/f-taste')
    DB_URI_ADMIN = os.environ.get('DB_URI_ADMIN', 'postgresql://f_taste_admin:admin@localhost:5432/f-taste')
    DB_URI_DIETITIAN = os.environ.get('DB_URI_DIETITIAN', 'postgresql://dietitian:dietitian@localhost:5432/f-taste')
    RAISE_EXCEPTIONS = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = secret_key
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    ERROR_INCLUDE_MESSAGE  = True
    RESTX_VALIDATE = True
    RATELIMIT_ENABLED = False
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)

config = {
    'dev': DevelopmentConfig
}