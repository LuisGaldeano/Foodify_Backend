import asyncio

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from application.database.database import Base, get_db
from get_application import get_application

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base.metadata.create_all(bind=engine)


def get_test_db_session():
    return TestingSessionLocal()


def override_get_db():
    try:
        db = get_test_db_session()
        yield db
    finally:
        db.close()


test_app = get_application(db_initialization=False)
test_app.dependency_overrides[get_db] = override_get_db

test_client = TestClient(
    test_app, backend_options={"loop_factory": asyncio.new_event_loop}
)
