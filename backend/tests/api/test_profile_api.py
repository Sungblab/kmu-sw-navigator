from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user_id, get_profile_store
from app.main import app
from app.services.profile_service import InMemoryProfileStore


def test_get_profile_returns_missing_profile_state() -> None:
    store = InMemoryProfileStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_profile_store] = lambda: store
    client = TestClient(app)

    response = client.get("/api/profile")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {"exists": False}


def test_post_profile_stores_required_fields() -> None:
    store = InMemoryProfileStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_profile_store] = lambda: store
    client = TestClient(app)

    response = client.post(
        "/api/profile",
        json={"department": "software", "grade": 1, "curriculum_year": "2025"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["id"] == "user-1"
    assert response.json()["department"] == "software"
    assert response.json()["grade"] == 1
    assert response.json()["curriculum_year"] == "2025"


def test_patch_profile_updates_grade_and_curriculum_year() -> None:
    store = InMemoryProfileStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_profile_store] = lambda: store
    client = TestClient(app)
    client.post(
        "/api/profile",
        json={"department": "software", "grade": 1, "curriculum_year": "2025"},
    )

    response = client.patch(
        "/api/profile",
        json={"department": "software", "grade": 2, "curriculum_year": "2024"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["grade"] == 2
    assert response.json()["curriculum_year"] == "2024"
