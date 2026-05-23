import httpx

from app.scripts.create_smoke_user import create_supabase_auth_user, generate_password


def test_generate_password_has_basic_complexity() -> None:
    password = generate_password()

    assert len(password) == 24
    assert any(char.islower() for char in password)
    assert any(char.isupper() for char in password)
    assert any(char.isdigit() for char in password)


def test_create_supabase_auth_user_uses_admin_endpoint_without_printing_password() -> None:
    seen_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_request
        seen_request = request
        return httpx.Response(200, json={"id": "11111111-1111-4111-8111-111111111111"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        user_id = create_supabase_auth_user(
            client,
            supabase_url="https://project.supabase.co",
            service_role_key="service-role",
            email="student@example.com",
            password="secret-password",
        )

    assert user_id == "11111111-1111-4111-8111-111111111111"
    assert seen_request is not None
    assert seen_request.url.path == "/auth/v1/admin/users"
    assert seen_request.headers["apikey"] == "service-role"
    assert seen_request.headers["Authorization"] == "Bearer service-role"
    assert seen_request.read()
