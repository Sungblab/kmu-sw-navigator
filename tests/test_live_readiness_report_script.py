from __future__ import annotations

from scripts.live_readiness_report import build_readiness_report, check_api_contract, parse_args


def test_build_readiness_report_marks_schema_blocker() -> None:
    lines, exit_code = build_readiness_report(
        env_missing_core=False,
        bundle_errors=[],
        schema_ready=False,
        missing_schema_items=["table: profiles", "function: match_document_chunks"],
        api_contract="ready",
        api_ready=False,
        include_seed=True,
        api_base="http://127.0.0.1:8001",
    )
    report = "\n".join(lines)

    assert exit_code == 1
    assert "Supabase schema: blocker" in report
    assert "table: profiles" in report
    assert "API contract: ready" in report
    assert "API health: skipped" in report
    assert "pnpm supabase:sql-copy" in report
    assert "schema+seed SQL" in report
    assert "pnpm live:smoke-run --api-base http://127.0.0.1:8001" in report


def test_build_readiness_report_marks_env_blocker_before_schema() -> None:
    lines, exit_code = build_readiness_report(
        env_missing_core=True,
        bundle_errors=[],
        schema_ready=None,
        missing_schema_items=[],
        api_contract="skipped",
        api_ready=None,
        include_seed=False,
        api_base="http://127.0.0.1:8001",
    )
    report = "\n".join(lines)

    assert exit_code == 2
    assert "Core env: blocker" in report
    assert "Supabase schema: skipped" in report
    assert "API contract: skipped" in report


def test_build_readiness_report_marks_bundle_validation_errors() -> None:
    lines, exit_code = build_readiness_report(
        env_missing_core=False,
        bundle_errors=["secret marker must not be present: GEMINI_API_KEY"],
        schema_ready=True,
        missing_schema_items=[],
        api_contract="ready",
        api_ready=True,
        include_seed=True,
        api_base="http://127.0.0.1:8001",
    )
    report = "\n".join(lines)

    assert exit_code == 2
    assert "SQL bundle: blocker" in report
    assert "secret marker must not be present: GEMINI_API_KEY" in report


def test_build_readiness_report_can_be_ready() -> None:
    lines, exit_code = build_readiness_report(
        env_missing_core=False,
        bundle_errors=[],
        schema_ready=True,
        missing_schema_items=[],
        api_contract="ready",
        api_ready=True,
        include_seed=True,
        api_base="http://127.0.0.1:8001",
    )
    report = "\n".join(lines)

    assert exit_code == 0
    assert "Core env: ready" in report
    assert "SQL bundle: ready" in report
    assert "Supabase schema: ready" in report
    assert "API contract: ready" in report
    assert "API health: ready" in report


def test_build_readiness_report_marks_api_health_blocker_after_schema_ready() -> None:
    lines, exit_code = build_readiness_report(
        env_missing_core=False,
        bundle_errors=[],
        schema_ready=True,
        missing_schema_items=[],
        api_contract="ready",
        api_ready=False,
        include_seed=True,
        api_base="http://127.0.0.1:8001",
    )
    report = "\n".join(lines)

    assert exit_code == 1
    assert "Supabase schema: ready" in report
    assert "API contract: ready" in report
    assert "API health: blocker" in report
    assert "uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8001" in report
    assert "pnpm live:smoke-run --api-base http://127.0.0.1:8001" in report


def test_build_readiness_report_marks_stale_api_contract_before_schema_ready() -> None:
    lines, exit_code = build_readiness_report(
        env_missing_core=False,
        bundle_errors=[],
        schema_ready=False,
        missing_schema_items=["table: profiles"],
        api_contract="stale",
        api_ready=None,
        include_seed=True,
        api_base="http://127.0.0.1:8000",
    )
    report = "\n".join(lines)

    assert exit_code == 1
    assert "Supabase schema: blocker" in report
    assert "API contract: blocker" in report
    assert "/api/runtime/public-status" in report
    assert "Restart FastAPI with the current repo code" in report


def test_check_api_contract_detects_current_backend(monkeypatch) -> None:
    class Response:
        status = 200

    monkeypatch.setattr(
        "scripts.live_readiness_report.request.urlopen",
        lambda url, timeout: Response(),
    )

    assert check_api_contract("http://api.test") == "ready"


def test_check_api_contract_detects_unreachable_backend(monkeypatch) -> None:
    def fake_urlopen(url: str, timeout: int) -> object:
        raise OSError("connection refused")

    monkeypatch.setattr("scripts.live_readiness_report.request.urlopen", fake_urlopen)

    assert check_api_contract("http://api.test") == "unreachable"


def test_check_api_contract_detects_stale_backend(monkeypatch) -> None:
    class Response:
        status = 404

    monkeypatch.setattr(
        "scripts.live_readiness_report.request.urlopen",
        lambda url, timeout: Response(),
    )

    assert check_api_contract("http://api.test") == "stale"


def test_parse_args_accepts_pnpm_separator() -> None:
    args = parse_args(["--", "--include-seed", "--api-base", "http://api.test"])

    assert args.include_seed is True
    assert args.api_base == "http://api.test"


def test_parse_args_accepts_pnpm_separator_after_script_defaults() -> None:
    args = parse_args(["--repo-root", "..", "--", "--include-seed"])

    assert args.repo_root == ".."
    assert args.include_seed is True
