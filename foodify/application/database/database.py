from core.logging import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session
from sqlalchemy.orm import sessionmaker
from core.settings.setting import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base = declarative_base()

session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)


def init_db():
    logger.info('Initializing database')
    Base.metadata.create_all(bind=engine)
    logger.info('Database initialized')
