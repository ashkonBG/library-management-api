from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config.db_settings import db_settings


def create_db_session() -> Session:
    connect_args = {"check_same_thread": False} if "sqlite" in db_settings.url else {}

    engine = create_engine(db_settings.url, connect_args=connect_args)

    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return session()
