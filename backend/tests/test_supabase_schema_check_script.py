from app.scripts.supabase_schema_check import (
    REQUIRED_FUNCTION_ARGS,
    REQUIRED_TABLES,
    check_supabase_schema,
    check_supabase_schema_with_retries,
    format_schema_report,
    parse_args,
)


class _Execute:
    def __init__(self, *, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    def execute(self) -> None:
        if self.should_fail:
            raise RuntimeError("missing relation")


class _TableQuery:
    def __init__(self, *, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    def select(self, _: str) -> "_TableQuery":
        return self

    def limit(self, _: int) -> _Execute:
        return _Execute(should_fail=self.should_fail)


class _FakeClient:
    def __init__(self, missing: set[str]) -> None:
        self.missing = missing

    def table(self, name: str) -> _TableQuery:
        return _TableQuery(should_fail=name in self.missing)

    def rpc(self, name: str, _: dict[str, object]) -> _Execute:
        return _Execute(should_fail=name in self.missing)


def test_check_supabase_schema_reports_tables_and_functions() -> None:
    items = check_supabase_schema(_FakeClient({"profiles", "match_document_chunks"}))

    missing = {(item.kind, item.name) for item in items if not item.ready}
    assert missing == {("table", "profiles"), ("function", "match_document_chunks")}
    assert len(items) == len(REQUIRED_TABLES) + len(REQUIRED_FUNCTION_ARGS)


def test_format_schema_report_names_required_action() -> None:
    report = "\n".join(format_schema_report(check_supabase_schema(_FakeClient({"profiles"}))))

    assert "[missing] table: profiles" in report
    assert "apply supabase/schema.sql" in report


def test_check_supabase_schema_with_retries_stops_after_ready(monkeypatch) -> None:
    attempts = 0

    def fake_check(client: object):
        nonlocal attempts
        attempts += 1
        return check_supabase_schema(_FakeClient({"profiles"} if attempts == 1 else set()))

    monkeypatch.setattr("app.scripts.supabase_schema_check.check_supabase_schema", fake_check)
    monkeypatch.setattr("app.scripts.supabase_schema_check.time.sleep", lambda _seconds: None)

    items = check_supabase_schema_with_retries(object(), retries=3, delay_seconds=0.01)

    assert attempts == 2
    assert all(item.ready for item in items)


def test_check_supabase_schema_with_retries_returns_last_failure(monkeypatch) -> None:
    attempts = 0

    def fake_check(client: object):
        nonlocal attempts
        attempts += 1
        return check_supabase_schema(_FakeClient({"profiles"}))

    monkeypatch.setattr("app.scripts.supabase_schema_check.check_supabase_schema", fake_check)
    monkeypatch.setattr("app.scripts.supabase_schema_check.time.sleep", lambda _seconds: None)

    items = check_supabase_schema_with_retries(object(), retries=2, delay_seconds=0.01)

    assert attempts == 2
    assert ("table", "profiles") in {(item.kind, item.name) for item in items if not item.ready}


def test_parse_args_accepts_pnpm_separator() -> None:
    args = parse_args(["--", "--retries", "1", "--retry-delay", "0.01"])

    assert args.retries == 1
    assert args.retry_delay == 0.01
