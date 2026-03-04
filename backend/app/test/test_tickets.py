from fastapi.testclient import TestClient
from unittest.mock import patch

def test_create_ticket_success(client: TestClient):
    """
    Tests successful creation of a ticket via the public customer endpoint.
    Mocks the external AI analysis call.
    """
    with patch("app.services.customer.analyze_ticket") as mock_analyze:
        mock_analyze.return_value = {"category": "technical_bug", "priority": "High"}
        
        response = client.post(
            "/api/v1/customer/ticket",
            json={"title": "Test Ticket", "description": "This is a test description."},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Ticket"
        assert data["category"] == "technical_bug"
        assert data["priority"] == "high"  # Service layer converts to lowercase
        assert data["status"] == "open"
        mock_analyze.assert_called_once_with("Test Ticket", "This is a test description.")

def test_get_tickets_unauthenticated(client: TestClient):
    """
    Tests that an unauthenticated user cannot access the get_tickets endpoint.
    """
    response = client.get("/api/v1/ticket/ticket")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_get_tickets_authenticated_empty(authenticated_client: TestClient):
    """
    Tests that an authenticated agent can get an empty list of tickets.
    """
    response = authenticated_client.get("/api/v1/ticket/ticket")
    assert response.status_code == 200
    assert response.json() == []

def test_get_tickets_with_data_and_pagination(authenticated_client: TestClient):
    """
    Tests pagination for the get_tickets endpoint.
    """
    with patch("app.services.customer.analyze_ticket") as mock_analyze:
        mock_analyze.return_value = {"category": "other", "priority": "low"}
        for i in range(15):
            authenticated_client.post("/api/v1/customer/ticket", json={"title": f"Ticket {i}", "description": "desc"})

    # Get first page
    response = authenticated_client.get("/api/v1/ticket/ticket?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    assert data[0]["title"] == "Ticket 0"

    # Get second page
    response = authenticated_client.get("/api/v1/ticket/ticket?skip=10&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[0]["title"] == "Ticket 10"

def test_get_tickets_with_filters(authenticated_client: TestClient):
    """
    Tests filtering for the get_tickets endpoint.
    """
    with patch("app.services.customer.analyze_ticket") as mock_analyze:
        mock_analyze.return_value = {"category": "billing", "priority": "high"}
        authenticated_client.post("/api/v1/customer/ticket", json={"title": "Billing Ticket", "description": "desc"})
        
        mock_analyze.return_value = {"category": "technical_bug", "priority": "low"}
        authenticated_client.post("/api/v1/customer/ticket", json={"title": "Bug Ticket", "description": "desc"})

    response = authenticated_client.get("/api/v1/ticket/ticket?category=billing&priority=high")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Billing Ticket"

def test_modify_ticket_status(authenticated_client: TestClient):
    """
    Tests successfully modifying a ticket's status.
    """
    with patch("app.services.customer.analyze_ticket") as mock_analyze:
        mock_analyze.return_value = {"category": "other", "priority": "low"}
        create_response = authenticated_client.post("/api/v1/customer/ticket", json={"title": "Modifiable", "description": "desc"})
    ticket_id = create_response.json()["id"]

    patch_response = authenticated_client.patch(f"/api/v1/ticket/ticket/{ticket_id}", json={"status": "in_progress"})
    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == "in_progress"

def test_modify_ticket_not_found(authenticated_client: TestClient):
    """
    Tests that modifying a non-existent ticket returns a 404.
    """
    response = authenticated_client.patch("/api/v1/ticket/ticket/nonexistentid", json={"status": "resolved"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket not found"}

def test_modify_resolved_ticket_fails(authenticated_client: TestClient):
    """
    Tests that a ticket with 'resolved' status cannot be modified again.
    """
    with patch("app.services.customer.analyze_ticket") as mock_analyze:
        mock_analyze.return_value = {"category": "other", "priority": "low"}
        create_response = authenticated_client.post("/api/v1/customer/ticket", json={"title": "Resolved Ticket", "description": "desc"})
    ticket_id = create_response.json()["id"]
    
    authenticated_client.patch(f"/api/v1/ticket/ticket/{ticket_id}", json={"status": "resolved"})
    response = authenticated_client.patch(f"/api/v1/ticket/ticket/{ticket_id}", json={"status": "in_progress"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Ticket is already resolved"}