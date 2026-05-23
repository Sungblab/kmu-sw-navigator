from fastapi.testclient import TestClient
from postgrest.exceptions import APIError

from app.api.dependencies import get_current_user_id, get_profile_store
from app.main import app


class _SchemaMissingProfileStore:
    def get_profile(self, user_id: str):  # noqa: ANN001
        raise AssertionError("not used")

    def upsert_profile(self, user_id: str, request):  # noqa: ANN001
        raise APIError(
            {
                "message": "Could not find the table 'public.profiles' in the schema cache",
                "code": "PGRST205",
                "hint": None,
                "details": None,
            }
        )


def test_postgrest_schema_cache_error_returns_503() -> None:
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_profile_store] = lambda: _SchemaMissingProfileStore()
    client = TestClient(app)

    response = client.post(
        "/api/profile",
        json={"department": "software", "grade": 1, "curriculum_year": "2025"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 503
    assert response.json()["code"] == "supabase_schema_missing"
