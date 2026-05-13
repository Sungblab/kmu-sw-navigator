from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Protocol
from uuid import uuid4

from google import genai
from google.genai import types

from app.schemas.assignment import (
    AssignmentCreateRequest,
    AssignmentPreviewResponse,
    AssignmentResponse,
    AssignmentUpdateRequest,
)

WEEKDAY_INDEX = {
    "월요일": 0,
    "화요일": 1,
    "수요일": 2,
    "목요일": 3,
    "금요일": 4,
    "토요일": 5,
    "일요일": 6,
}


@dataclass(frozen=True)
class ParsedAssignment:
    title: str
    due_at: datetime
    course: str | None = None
    memo: str | None = None
    confidence: float = 0.8


class AssignmentParser(Protocol):
    def parse_assignment(self, text: str, *, reference_date: date) -> ParsedAssignment:
        ...


class GeminiAssignmentParser:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def parse_assignment(self, text: str, *, reference_date: date) -> ParsedAssignment:
        response = self.client.models.generate_content(
            model=self.model,
            contents=_build_assignment_parse_prompt(text, reference_date),
            config=types.GenerateContentConfig(
                system_instruction=ASSIGNMENT_PARSE_SYSTEM_INSTRUCTION,
                temperature=0.1,
                max_output_tokens=256,
                response_mime_type="application/json",
            ),
        )
        payload = json.loads(response.text or "{}")
        return _parsed_assignment_from_payload(payload, original_text=text)


class InMemoryAssignmentStore:
    def __init__(self) -> None:
        self.assignments: dict[str, list[AssignmentResponse]] = {}

    def create_assignment(
        self,
        user_id: str,
        request: AssignmentCreateRequest,
        *,
        today: date | None = None,
    ) -> AssignmentResponse:
        assignment = build_assignment_response(
            id=str(uuid4()),
            title=request.title,
            due_at=request.due_at,
            course=request.course,
            memo=request.memo,
            today=today,
        )
        self.assignments.setdefault(user_id, []).append(assignment)
        return assignment

    def list_assignments(
        self,
        user_id: str,
        *,
        today: date | None = None,
    ) -> list[AssignmentResponse]:
        items = self.assignments.get(user_id, [])
        return [
            build_assignment_response(
                id=item.id,
                title=item.title,
                due_at=item.due_at,
                course=item.course,
                memo=item.memo,
                status=item.status,
                calendar_event_id=item.calendar_event_id,
                calendar_synced_at=item.calendar_synced_at,
                today=today,
            )
            for item in sorted(items, key=lambda assignment: assignment.due_at)
            if item.status == "todo"
        ]

    def update_assignment(
        self,
        user_id: str,
        assignment_id: str,
        request: AssignmentUpdateRequest,
    ) -> AssignmentResponse:
        items = self.assignments.get(user_id, [])
        for index, item in enumerate(items):
            if item.id == assignment_id:
                updated = item.model_copy(
                    update={"status": request.status or item.status},
                )
                items[index] = updated
                return build_assignment_response(
                    id=updated.id,
                    title=updated.title,
                    due_at=updated.due_at,
                    course=updated.course,
                    memo=updated.memo,
                    status=updated.status,
                    calendar_event_id=updated.calendar_event_id,
                    calendar_synced_at=updated.calendar_synced_at,
                )
        raise KeyError(assignment_id)

    def get_assignment(self, user_id: str, assignment_id: str) -> AssignmentResponse:
        for item in self.assignments.get(user_id, []):
            if item.id == assignment_id:
                return item
        raise KeyError(assignment_id)

    def mark_calendar_exported(
        self,
        user_id: str,
        assignment_id: str,
        *,
        calendar_event_id: str,
        synced_at: datetime,
    ) -> AssignmentResponse:
        items = self.assignments.get(user_id, [])
        for index, item in enumerate(items):
            if item.id == assignment_id:
                updated = item.model_copy(
                    update={
                        "calendar_event_id": calendar_event_id,
                        "calendar_synced_at": synced_at,
                    },
                )
                items[index] = updated
                return updated
        raise KeyError(assignment_id)

    def delete_assignment(self, user_id: str, assignment_id: str) -> None:
        items = self.assignments.get(user_id, [])
        before_count = len(items)
        self.assignments[user_id] = [item for item in items if item.id != assignment_id]
        if len(self.assignments[user_id]) == before_count:
            raise KeyError(assignment_id)


def preview_assignment_from_text(
    text: str,
    *,
    reference_date: date | None = None,
    parser: AssignmentParser | None = None,
) -> AssignmentPreviewResponse:
    today = reference_date or date.today()
    if parser is not None:
        parsed = _try_parse_with_parser(text, parser=parser, reference_date=today)
        if parsed is not None:
            d_day = calculate_d_day(parsed.due_at, today=today)
            return AssignmentPreviewResponse(
                title=parsed.title,
                course=parsed.course,
                due_at=parsed.due_at,
                memo=parsed.memo or text,
                d_day=d_day,
                d_day_label=format_d_day(d_day),
                confidence=parsed.confidence,
                missing_fields=[],
                parser="gemini",
            )

    due_date = _extract_due_date(text, today)
    title = _extract_title(text)
    course = _extract_course(text)
    missing_fields: list[str] = []

    if due_date is None:
        due_date = today
        missing_fields.append("due_at")
    if not title:
        title = "새 일정"
        missing_fields.append("title")

    due_at = datetime.combine(due_date, time(hour=23, minute=59))
    d_day = calculate_d_day(due_at, today=today)
    confidence = 0.85 if not missing_fields else 0.45
    return AssignmentPreviewResponse(
        title=title,
        course=course,
        due_at=due_at,
        memo=text,
        d_day=d_day,
        d_day_label=format_d_day(d_day),
        confidence=confidence,
        missing_fields=missing_fields,
        parser="python_rules",
    )


def build_assignment_response(
    *,
    id: str,
    title: str,
    due_at: datetime,
    course: str | None = None,
    memo: str | None = None,
    status: str = "todo",
    calendar_event_id: str | None = None,
    calendar_synced_at: datetime | None = None,
    today: date | None = None,
) -> AssignmentResponse:
    d_day = calculate_d_day(due_at, today=today)
    return AssignmentResponse(
        id=id,
        title=title,
        course=course,
        due_at=due_at,
        memo=memo,
        status=status,
        calendar_event_id=calendar_event_id,
        calendar_synced_at=calendar_synced_at,
        d_day=d_day,
        d_day_label=format_d_day(d_day),
    )


def calculate_d_day(due_at: datetime, *, today: date | None = None) -> int:
    base = today or date.today()
    return (due_at.date() - base).days


def format_d_day(d_day: int) -> str:
    if d_day == 0:
        return "D-Day"
    if d_day > 0:
        return f"D-{d_day}"
    return f"D+{abs(d_day)}"


def _extract_due_date(text: str, today: date) -> date | None:
    normalized = text.strip()
    if "오늘" in normalized:
        return today
    if "내일" in normalized:
        return today + timedelta(days=1)
    if "다음주" in normalized:
        for weekday, index in WEEKDAY_INDEX.items():
            if weekday in normalized:
                start_next_week = today + timedelta(days=(7 - today.weekday()))
                return start_next_week + timedelta(days=index)
        return today + timedelta(days=7)

    date_match = re.search(r"(20\d{2})[-./년 ]+(\d{1,2})[-./월 ]+(\d{1,2})", normalized)
    if date_match:
        year, month, day = (int(part) for part in date_match.groups())
        return date(year, month, day)

    month_day_match = re.search(r"(\d{1,2})월\s*(\d{1,2})일", normalized)
    if month_day_match:
        month, day = (int(part) for part in month_day_match.groups())
        year = today.year + (1 if month < today.month else 0)
        return date(year, month, day)
    return None


def _extract_title(text: str) -> str:
    cleaned = re.sub(r"(오늘|내일|다음주\s*[월화수목금토일]요일|까지|마감|제출)", " ", text)
    cleaned = re.sub(r"20\d{2}[-./년 ]+\d{1,2}[-./월 ]+\d{1,2}", " ", cleaned)
    cleaned = re.sub(r"\d{1,2}월\s*\d{1,2}일", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned[:80]


def _extract_course(text: str) -> str | None:
    match = re.search(r"([가-힣A-Za-z0-9 ]{2,20})(?:\s*과제|\s*시험|\s*프로젝트)", text)
    if not match:
        return None
    return match.group(1).strip()


ASSIGNMENT_PARSE_SYSTEM_INSTRUCTION = (
    "너는 한국어 과제/시험 일정 문장을 JSON으로 구조화하는 파서다. "
    "없는 정보는 null로 두고, 설명 문장 없이 JSON만 반환한다."
)


def _build_assignment_parse_prompt(text: str, reference_date: date) -> str:
    return f"""기준 날짜: {reference_date.isoformat()}
입력 문장: {text}

아래 JSON 형태로만 답한다.
{{
  "title": "일정 제목",
  "course": "과목명 또는 null",
  "due_at": "YYYY-MM-DDTHH:MM:SS",
  "confidence": 0.0
}}
"""


def _try_parse_with_parser(
    text: str,
    *,
    parser: AssignmentParser,
    reference_date: date,
) -> ParsedAssignment | None:
    try:
        parsed = parser.parse_assignment(text, reference_date=reference_date)
    except Exception:
        return None
    if not parsed.title.strip():
        return None
    return parsed


def _parsed_assignment_from_payload(
    payload: dict[str, object],
    *,
    original_text: str,
) -> ParsedAssignment:
    due_at_value = payload.get("due_at")
    if not isinstance(due_at_value, str):
        raise ValueError("Gemini assignment parser did not return due_at")

    return ParsedAssignment(
        title=str(payload.get("title") or "새 일정")[:80],
        course=_optional_string(payload.get("course")),
        due_at=datetime.fromisoformat(due_at_value),
        memo=original_text,
        confidence=_bounded_confidence(payload.get("confidence")),
    )


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _bounded_confidence(value: object) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.7
    return min(max(confidence, 0.0), 1.0)
