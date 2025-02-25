import os
from flask import current_app
from flask_jwt_extended import get_jwt
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from F_taste_misurazioni.utils.jwt_functions import get_role
from F_taste_misurazioni.utils.config_loader import ConfigLoader


Base = declarative_base()

# Configuration for different roles
DB_CONFIG = {}

def get_db_config():
    global DB_CONFIG
    return DB_CONFIG

# Engine cache to avoid recreating engines
engine_cache = {}

session_factory_cache = {}

def get_engine(role):
    if role not in engine_cache:
        engine_url = get_db_config().get(role)
        if not engine_url:
            raise ValueError("Invalid role or no database configuration for role.")
        engine_cache[role] = create_engine(engine_url)
    return engine_cache[role]

def get_session_factory(role):
    if role not in session_factory_cache:
        engine = get_engine(role)
        session_factory_cache[role] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return session_factory_cache[role]

def get_session(role):
    return scoped_session(get_session_factory(role))

def set_DB_CONFIG():
    global DB_CONFIG
    config = ConfigLoader.load_config_from_class()
    DB_CONFIG = {
        'admin': config.DB_URI_ADMIN,
        'patient': config.DB_URI_PATIENT,
        'dietitian':config.DB_URI_DIETITIAN
    }

def create_db():
    set_DB_CONFIG()
    engine = get_engine('dietitian')
    Base.metadata.create_all(engine)

def drop_db():
    engine = get_engine('dietitian')
    Base.metadata.drop_all(engine)