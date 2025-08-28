from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_engine = None
SessionLocal = None

def init_engine():
    global _engine, SessionLocal
    from flask import current_app
    _engine = create_engine(current_app.config["DATABASE_URL"], future=True, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
    return _engine
