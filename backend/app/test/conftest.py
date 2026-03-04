import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.db.database import Base
from app.db.dependencies import get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """
    Dependency override for getting a database session for tests.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the override to the app for all tests
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    """
    Pytest fixture to provide a test client. It handles database setup
    and teardown for each test function to ensure isolation.
    """
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def authenticated_client(client: TestClient):
    """
    Pytest fixture to provide a client that is already authenticated as an agent.
    """
    user_data = {"email": "test@example.com", "password": "testpassword", "name": "Test User"}
    client.post("/api/v1/auth/register", json=user_data)

    # Manually verify the user in the test DB to allow login
    db = TestingSessionLocal()
    from app.db.models import SupportAgent
    user = db.query(SupportAgent).filter(SupportAgent.email == user_data["email"]).first()
    if user:
        user.is_verified = True
        db.commit()
    db.close()

    client.post("/api/v1/auth/login", json={"email": user_data["email"], "password": user_data["password"]})
    return client