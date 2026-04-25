from fastapi.testclient import TestClient


def test_health_check_returns_200(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200


def test_health_check_body(client: TestClient) -> None:
    data = client.get("/").json()
    assert data["status"] == "ok"
    assert "app" in data
    assert "version" in data
