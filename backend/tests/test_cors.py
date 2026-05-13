from fastapi.testclient import TestClient

from app.main import app


def test_local_vite_fallback_port_is_allowed_for_api_preflight() -> None:
    client = TestClient(app)

    response = client.options(
        "/api/profile",
        headers={
            "Origin": "http://127.0.0.1:5174",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5174"
