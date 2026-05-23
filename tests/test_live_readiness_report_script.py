from __future__ import annotations

from scripts.live_readiness_report import build_readiness_report, parse_args


def test_build_readiness_report_marks_schema_blocker() -> None:
    lines, exit_code = build_readiness_report(
        env_missing_core=False,
        bundle_errors=[],
        schema_ready=False,
        missing_schema_items=["table: profiles", "function: match_document_chunks"],
        api_ready=False,
        include_seed=True,
        api_base="http://127.0.0.1:8001",
    )
    report = "\n".join(lines)

    assert exit_code == 1
    assert "Supabase schema: blocker" in report
    assert "table: profiles" in report
    assert "API health: skipped" in report
    assert "pnpm supabase:sql-bundle -- --include-seed" in report
    assert "pnpm live:smoke-run --api-base http://127.0.0.1:8001" in report


def test_build_readiness_report_marks_env_blocker_before_schema() -> None:
    lines, exit_code = build_readiness_report(
        env_missing_core=True,
        bundle_errors=[],
        schema_ready=None,
        missing_schema_items=[],
        api_ready=None,
        include_seed=False,
        api_base="http://127.0.0.1:8001",
    )
    report = "\n".join(lines)

    assert exit_code == 2
    assert "Core env: blocker" in report
    assert "Supabase schema: skipped" in report


def test_build_readiness_report_marks_bundle_validation_errors() -> None:
    lines, exit_code = build_readiness_report(
        env_missing_core=False,
        bundle_errors=["secret marker must not be present: GEMINI_API_KEY"],
        schema_ready=True,
        missing_schema_items=[],
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
        api_ready=True,
        include_seed=True,
        api_base="http://127.0.0.1:8001",
    )
    report = "\n".join(lines)

    assert exit_code == 0
    assert "Core env: ready" in report
    assert "SQL bundle: ready" in report
    assert "Supabase schema: ready" in report
    assert "API health: ready" in report


def test_build_readiness_report_marks_api_health_blocker_after_schema_ready() -> None:
    lines, exit_code = build_readiness_report(
        env_missing_core=False,
        bundle_errors=[],
        schema_ready=True,
        missing_schema_items=[],
        api_ready=False,
        include_seed=True,
        api_base="http://127.0.0.1:8001",
    )
    report = "\n".join(lines)

    assert exit_code == 1
    assert "Supabase schema: ready" in report
    assert "API health: blocker" in report
    assert "uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8001" in report
    assert "pnpm live:smoke-run --api-base http://127.0.0.1:8001" in report


def test_parse_args_accepts_pnpm_separator() -> None:
    args = parse_args(["--", "--include-seed", "--api-base", "http://api.test"])

    assert args.include_seed is True
    assert args.api_base == "http://api.test"


def test_parse_args_accepts_pnpm_separator_after_script_defaults() -> None:
    args = parse_args(["--repo-root", "..", "--", "--include-seed"])

    assert args.repo_root == ".."
    assert args.include_seed is True
