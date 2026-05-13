from datetime import date, datetime

from app.schemas.assignment import AssignmentCreateRequest, AssignmentUpdateRequest
from app.services.assignment_service import (
    InMemoryAssignmentStore,
    ParsedAssignment,
    calculate_d_day,
    format_d_day,
    preview_assignment_from_text,
)


class FakeAssignmentParser:
    def parse_assignment(self, text: str, *, reference_date: date) -> ParsedAssignment:
        assert text == "내일 AI 보고서 제출"
        assert reference_date == date(2026, 5, 14)
        return ParsedAssignment(
            title="AI 보고서",
            course="인공지능",
            due_at=datetime(2026, 5, 15, 18, 0),
            confidence=0.92,
        )


class BrokenAssignmentParser:
    def parse_assignment(self, text: str, *, reference_date: date) -> ParsedAssignment:
        raise RuntimeError("parser unavailable")


def test_preview_assignment_uses_structured_parser_when_available() -> None:
    preview = preview_assignment_from_text(
        "내일 AI 보고서 제출",
        reference_date=date(2026, 5, 14),
        parser=FakeAssignmentParser(),
    )

    assert preview.title == "AI 보고서"
    assert preview.course == "인공지능"
    assert preview.due_at == datetime(2026, 5, 15, 18, 0)
    assert preview.d_day_label == "D-1"
    assert preview.confidence == 0.92
    assert preview.parser == "gemini"


def test_preview_assignment_falls_back_to_python_rules_when_parser_fails() -> None:
    preview = preview_assignment_from_text(
        "자료구조 과제 내일까지",
        reference_date=date(2026, 5, 14),
        parser=BrokenAssignmentParser(),
    )

    assert preview.course == "자료구조"
    assert preview.due_at.date() == date(2026, 5, 15)
    assert preview.parser == "python_rules"


def test_preview_assignment_extracts_next_weekday_and_d_day() -> None:
    preview = preview_assignment_from_text(
        "자료구조 과제 다음주 금요일까지 제출",
        reference_date=date(2026, 5, 14),
    )

    assert preview.course == "자료구조"
    assert preview.due_at.date() == date(2026, 5, 22)
    assert preview.d_day == 8
    assert preview.d_day_label == "D-8"
    assert preview.missing_fields == []


def test_preview_assignment_marks_missing_due_date() -> None:
    preview = preview_assignment_from_text(
        "캡스톤 프로젝트 정리",
        reference_date=date(2026, 5, 14),
    )

    assert "due_at" in preview.missing_fields
    assert preview.confidence < 0.5


def test_d_day_formatting() -> None:
    assert calculate_d_day(datetime(2026, 5, 14, 23, 59), today=date(2026, 5, 14)) == 0
    assert format_d_day(0) == "D-Day"
    assert format_d_day(3) == "D-3"
    assert format_d_day(-2) == "D+2"


def test_assignment_store_lists_todo_by_due_date() -> None:
    store = InMemoryAssignmentStore()
    later = store.create_assignment(
        "user-1",
        AssignmentCreateRequest(
            title="나중 과제",
            due_at=datetime(2026, 5, 20, 23, 59),
        ),
        today=date(2026, 5, 14),
    )
    earlier = store.create_assignment(
        "user-1",
        AssignmentCreateRequest(
            title="먼저 과제",
            due_at=datetime(2026, 5, 16, 23, 59),
        ),
        today=date(2026, 5, 14),
    )

    assert [item.id for item in store.list_assignments("user-1", today=date(2026, 5, 14))] == [
        earlier.id,
        later.id,
    ]


def test_assignment_store_updates_and_deletes_assignment() -> None:
    store = InMemoryAssignmentStore()
    assignment = store.create_assignment(
        "user-1",
        AssignmentCreateRequest(
            title="자료구조 과제",
            due_at=datetime(2026, 5, 20, 23, 59),
        ),
    )

    updated = store.update_assignment(
        "user-1",
        assignment.id,
        request=AssignmentUpdateRequest(status="done"),
    )
    store.delete_assignment("user-1", assignment.id)

    assert updated.status == "done"
    assert store.list_assignments("user-1") == []
