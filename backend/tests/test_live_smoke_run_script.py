import subprocess
from urllib.error import URLError

from app.scripts.live_smoke_run import (
    SmokeCommand,
    SmokeCommandResult,
    build_smoke_commands,
    check_api_health,
    print_api_health_blocker,
    print_failure_guidance,
    print_result_summary,
    print_schema_blocker_next_actions,
    run_smoke_commands,
)


def test_build_smoke_commands_uses_api_base_and_keeps_google_optional() -> None:
    commands = build_smoke_commands(api_base="http://127.0.0.1:8001", include_google=False)

    names = [command.name for command in commands]
    assert "Google Calendar event smoke" not in names
    login = next(command for command in commands if command.name == "Supabase login/API smoke")
    assert login.args[-1] == "http://127.0.0.1:8001"
    assert login.failure_category == "auth"
    embedding = next(command for command in commands if command.name == "Embedding ingest")
    assert embedding.failure_category == "code"


def test_build_smoke_commands_can_include_google() -> None:
    commands = build_smoke_commands(api_base="http://api.test", include_google=True)

    assert commands[-1].name == "Google Calendar event smoke"


def test_run_smoke_commands_stops_on_required_failure(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(args: list[str], *, check: bool) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        return subprocess.CompletedProcess(args=args, returncode=1)

    monkeypatch.setattr(subprocess, "run", fake_run)

    results = run_smoke_commands(
        [
            SmokeCommand("first", ["-m", "first"]),
            SmokeCommand("second", ["-m", "second"]),
        ]
    )

    assert [result.name for result in results] == ["first"]
    assert len(calls) == 1


def test_print_result_summary_marks_failed_result(capsys) -> None:
    print_result_summary(
        [
            SmokeCommandResult(name="ok", returncode=0),
            SmokeCommandResult(name="bad", returncode=1),
        ]
    )

    output = capsys.readouterr().out
    assert "[passed] ok" in output
    assert "[failed:1] bad" in output


def test_print_failure_guidance_classifies_first_failed_command(capsys) -> None:
    print_failure_guidance(
        [
            SmokeCommandResult(
                name="Supabase login/API smoke",
                returncode=1,
                failure_category="auth",
                next_action="Check backend server and Supabase Auth credentials.",
            )
        ]
    )

    output = capsys.readouterr().out
    assert "Failure classification: auth" in output
    assert "Check backend server and Supabase Auth credentials." in output


def test_print_schema_blocker_next_actions_names_bundle_command(capsys) -> None:
    print_schema_blocker_next_actions()

    output = capsys.readouterr().out
    assert "Supabase schema is not ready" in output
    assert "pnpm supabase:sql-bundle -- --include-seed" in output
    assert "supabase/live-schema-bundle.sql" in output
    assert "pnpm live:smoke-run --api-base http://127.0.0.1:8001" in output


def test_check_api_health_calls_health_endpoint(monkeypatch) -> None:
    requested: list[str] = []

    class Response:
        status = 200

    def fake_urlopen(url: str, timeout: int) -> Response:
        requested.append(f"{url} timeout={timeout}")
        return Response()

    monkeypatch.setattr("app.scripts.live_smoke_run.request.urlopen", fake_urlopen)

    assert check_api_health("http://127.0.0.1:8001") is True
    assert requested == ["http://127.0.0.1:8001/health timeout=2"]


def test_check_api_health_returns_false_on_connection_error(monkeypatch) -> None:
    def fake_urlopen(url: str, timeout: int) -> object:
        raise URLError("connection refused")

    monkeypatch.setattr("app.scripts.live_smoke_run.request.urlopen", fake_urlopen)

    assert check_api_health("http://127.0.0.1:8001") is False


def test_print_api_health_blocker_names_backend_command(capsys) -> None:
    print_api_health_blocker("http://127.0.0.1:8001")

    output = capsys.readouterr().out
    assert "FastAPI server is not reachable" in output
    assert "uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8001" in output
