from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from core.logging import logger
from core.settings.connection import SQLALCHEMY_DATABASE_URL

Base = declarative_base()


def init_db():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Initializing database")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")


def get_db():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_local()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
