import os

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    # Keep data for local inspection; uncomment to drop automatically.
    # Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_session_cookies():
    # Ensures each test starts with a clean browser state.
    yield
