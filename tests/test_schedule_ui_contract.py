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
