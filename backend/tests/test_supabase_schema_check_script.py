from app.scripts.supabase_schema_check import (
    REQUIRED_FUNCTION_ARGS,
    REQUIRED_TABLES,
    check_supabase_schema,
    format_schema_report,
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
