from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
APP_TSX = REPO_ROOT / "frontend" / "src" / "App.tsx"


def _schedule_page_source() -> str:
    source = APP_TSX.read_text(encoding="utf-8")
    start = source.index("function SchedulePage(")
    end = source.index("function ScheduleMetric(")
    return source[start:end]


def test_schedule_page_does_not_offer_direct_ai_extraction_form() -> None:
    schedule_page = _schedule_page_source()

    assert "AI 일정 추출" not in schedule_page
    assert "일정 자연어 입력" not in schedule_page
    assert "onPreview" not in schedule_page
    assert "onSave" not in schedule_page
    assert "setDraft" not in schedule_page


def test_schedule_page_formats_assignment_dates_in_korean_timezone() -> None:
    source = APP_TSX.read_text(encoding="utf-8")
    schedule_page = _schedule_page_source()

    assert 'const KOREA_TIME_ZONE = "Asia/Seoul";' in source
    assert "formatAssignmentDate(assignment.due_at)" in schedule_page
    assert "getAssignmentDateKey(assignment.due_at)" in source
    assert "getCalendarDateKey(date)" in source
    assert "new Date(assignment.due_at).toLocaleDateString()" not in schedule_page
    assert "dueDate.toDateString()" not in schedule_page
    assert "date.toISOString().slice(0, 10)" not in schedule_page
