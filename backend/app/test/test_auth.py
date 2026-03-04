from fastapi.testclient import TestClient
from .conftest import TestingSessionLocal
from app.db.models import SupportAgent

def test_register_agent_success(client: TestClient):
    """
    Tests successful agent registration.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "testagent@example.com", "password": "password123", "name": "Test Agent"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testagent@example.com"
    assert "id" in data
    assert data["is_verified"] is False

def test_register_agent_conflict(client: TestClient):
    """
    Tests that registering with a duplicate email returns a 409 Conflict.
    """
    user_data = {"email": "conflict@example.com", "password": "password123", "name": "Conflict Agent"}
    client.post("/api/v1/auth/register", json=user_data)
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 409
    assert response.json() == {"detail": "User exists"}

def test_login_success(client: TestClient):
    """
    Tests successful login for a verified agent.
    """
    email = "login@example.com"
    password = "loginpassword"
    client.post("/api/v1/auth/register", json={"email": email, "password": password, "name": "Login User"})
    
    # Manually verify the user in the test DB
    db = TestingSessionLocal()
    user = db.query(SupportAgent).filter(SupportAgent.email == email).first()
    user.is_verified = True
    db.commit()
    db.close()

    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

def test_login_unverified_user(client: TestClient):
    """
    Tests that an unverified agent cannot log in.
    """
    email = "unverified@example.com"
    password = "unverifiedpassword"
    client.post("/api/v1/auth/register", json={"email": email, "password": password, "name": "Unverified User"})

    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 400
    assert response.json() == {"detail": "User not verified"}

def test_login_wrong_password(client: TestClient):
    """
    Tests that login fails with an incorrect password.
    """
    email = "wrongpass@example.com"
    password = "correctpassword"
    client.post("/api/v1/auth/register", json={"email": email, "password": password, "name": "Wrong Pass User"})
    
    db = TestingSessionLocal()
    user = db.query(SupportAgent).filter(SupportAgent.email == email).first()
    user.is_verified = True
    db.commit()
    db.close()

    response = client.post("/api/v1/auth/login", json={"email": email, "password": "wrongpassword"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect credentials"}