import re
from dataclasses import dataclass
from typing import Any, Literal
from uuid import uuid4

from app.schemas.memory import MemoryEventResponse, MemoryResponse
from app.services.store_protocols import MemoryStore

MemoryDecision = Literal["auto_save", "requires_confirmation", "reject"]


@dataclass(frozen=True)
class MemoryPolicy:
    sensitivity: Literal["low", "medium", "high"]
    decision: MemoryDecision
    reason: str


class InMemoryMemoryStore:
    def __init__(self) -> None:
        self._memories: dict[str, tuple[str, MemoryResponse]] = {}
        self._events: dict[str, list[MemoryEventResponse]] = {}

    def save_memory(self, user_id: str, memory: MemoryResponse) -> MemoryResponse:
        self._memories[memory.id] = (user_id, memory)
        return memory

    def get_memory(self, user_id: str, memory_id: str) -> MemoryResponse:
        owner_id, memory = self._memories[memory_id]
        if owner_id != user_id:
            raise KeyError(memory_id)
        return memory

    def add_event(self, user_id: str, event: MemoryEventResponse) -> MemoryEventResponse:
        self._events.setdefault(user_id, []).append(event)
        return event

    def list_active_memories(self, user_id: str) -> list[MemoryResponse]:
        return [
            memory
            for owner_id, memory in self._memories.values()
            if owner_id == user_id and memory.status == "active"
        ]

    def list_events(self, user_id: str) -> list[MemoryEventResponse]:
        return list(self._events.get(user_id, []))


def classify_memory_sensitivity(text: str) -> MemoryPolicy:
    normalized = text.casefold()
    high_keywords = ["비밀번호", "password", "주민등록", "계좌", "카드번호"]
    medium_keywords = ["학점", "성적", "불안", "우울", "취업이 걱정", "걱정돼"]

    # 비밀값과 강한 개인정보는 LLM 판단 전에 Python 규칙으로 먼저 차단한다.
    if any(keyword in normalized for keyword in high_keywords):
        return MemoryPolicy("high", "reject", "민감한 비밀값 또는 개인정보는 저장하지 않습니다.")

    # 학점/정서/취업 불안은 도움이 되는 개인화 정보일 수 있어 사용자 확인 뒤 저장한다.
    if any(keyword in normalized for keyword in medium_keywords):
        return MemoryPolicy(
            "medium",
            "requires_confirmation",
            "민감할 수 있어 사용자 확인이 필요합니다.",
        )

    return MemoryPolicy("low", "auto_save", "일반 관심사로 자동 저장할 수 있습니다.")


def create_memory_candidate(
    *,
    store: MemoryStore,
    user_id: str,
    natural_text: str,
    category: str,
    key: str,
    value_json: dict[str, Any],
    confidence: float = 0.7,
) -> MemoryResponse:
    policy = classify_memory_sensitivity(natural_text)
    # 민감도 정책의 결정값을 저장 상태로 분리해 UI가 확인/거절 흐름을 명확히 보여준다.
    status = {
        "auto_save": "active",
        "requires_confirmation": "candidate",
        "reject": "rejected",
    }[policy.decision]

    memory = MemoryResponse(
        id=str(uuid4()),
        category=category,
        key=key,
        value_json=value_json,
        natural_text=natural_text,
        confidence=confidence,
        sensitivity=policy.sensitivity,
        status=status,
        embedding_status="pending",
    )
    store.save_memory(user_id, memory)

    # 모든 저장 판단을 event로 남겨 LLM이 만든 메모리를 사람이 검토했다는 증거를 유지한다.
    if policy.decision == "auto_save":
        _add_memory_event(store, user_id, memory, "created", policy.reason)
    elif policy.decision == "requires_confirmation":
        _add_memory_event(store, user_id, memory, "candidate_created", policy.reason)
    else:
        _add_memory_event(store, user_id, memory, "rejected", policy.reason)

    return memory


def create_learning_context_memory_from_chat(
    *,
    store: MemoryStore,
    user_id: str,
    message: str,
) -> list[MemoryResponse]:
    value_json = extract_learning_context(message)
    if not _has_learning_context(value_json):
        return []

    parts = []
    if value_json["track_interests"]:
        parts.append(f"관심 트랙: {', '.join(value_json['track_interests'])}")
    if value_json["activity_interests"]:
        parts.append(f"관심 활동: {', '.join(value_json['activity_interests'])}")
    if value_json["goal"]:
        parts.append(f"목표: {value_json['goal']}")
    if value_json["coding_level"] != "unknown":
        parts.append(f"코딩 경험: {value_json['coding_level']}")
    if value_json["preference"] != "unknown":
        parts.append(f"학습 선호: {value_json['preference']}")
    if value_json["activity_style"] != "unknown":
        parts.append(f"활동 방식: {value_json['activity_style']}")
    if value_json["weekly_hours"]:
        parts.append(f"주간 가능 시간: {value_json['weekly_hours']}시간")

    return [
        create_memory_candidate(
            store=store,
            user_id=user_id,
            natural_text=f"대화에서 파악한 학습/진로 정보: {'; '.join(parts)}",
            category="conversation",
            key="learning_context",
            value_json=value_json,
            confidence=0.72,
        )
    ]


def extract_learning_context(message: str) -> dict[str, Any]:
    normalized = message.casefold()
    # 추천에 바로 쓰이는 낮은 민감도의 학습 선호만 규칙으로 추출한다.
    return {
        "track_interests": _match_keyword_labels(
            normalized,
            [
                ("AI", ["ai", "인공지능", "머신러닝", "llm"]),
                ("백엔드", ["백엔드", "backend", "api", "서버"]),
                ("프론트엔드", ["프론트", "frontend", "react", "웹"]),
                ("데이터", ["데이터", "분석", "db", "database"]),
                ("창업", ["창업", "스타트업", "mvp"]),
            ],
        ),
        "activity_interests": _match_keyword_labels(
            normalized,
            [
                ("개발", ["개발", "코딩", "프로젝트", "앱", "웹"]),
                ("알고리즘", ["알고리즘", "코테", "문제풀이"]),
                ("동아리", ["동아리", "스터디", "팀 활동"]),
            ],
        ),
        "goal": _extract_goal(message),
        "coding_level": _extract_coding_level(normalized),
        "preference": _extract_learning_preference(normalized),
        "activity_style": _extract_activity_style(normalized),
        "weekly_hours": _extract_weekly_hours(message),
    }


def confirm_memory(
    store: MemoryStore,
    user_id: str,
    memory_id: str,
) -> MemoryResponse:
    memory = store.get_memory(user_id, memory_id)
    updated = memory.model_copy(update={"status": "active"})
    store.save_memory(user_id, updated)
    _add_memory_event(store, user_id, updated, "confirmed", "사용자가 메모리 저장을 확인했습니다.")
    return updated


def _has_learning_context(value_json: dict[str, Any]) -> bool:
    return bool(
        value_json["track_interests"]
        or value_json["activity_interests"]
        or value_json["goal"]
        or value_json["coding_level"] != "unknown"
        or value_json["preference"] != "unknown"
        or value_json["activity_style"] != "unknown"
        or value_json["weekly_hours"]
    )


def _match_keyword_labels(
    text: str,
    rules: list[tuple[str, list[str]]],
) -> list[str]:
    return [label for label, keywords in rules if any(keyword in text for keyword in keywords)]


def _extract_goal(message: str) -> str:
    match = re.search(r"목표(?:는|가)?\s*([^.!?\n。]+)", message)
    if not match:
        return ""
    return match.group(1).strip(" 이야입니다해요")


def _extract_coding_level(text: str) -> str:
    if any(keyword in text for keyword in ["초급", "처음", "기초", "입문"]):
        return "beginner"
    if any(keyword in text for keyword in ["중급", "어느정도", "어느 정도"]):
        return "intermediate"
    if any(keyword in text for keyword in ["고급", "상급", "실무"]):
        return "advanced"
    return "unknown"


def _extract_learning_preference(text: str) -> str:
    if "프로젝트" in text or "개발" in text:
        return "project"
    if "강의" in text or "수업" in text:
        return "lecture"
    if "스터디" in text:
        return "study"
    return "unknown"


def _extract_activity_style(text: str) -> str:
    if "혼자" in text or "개인" in text:
        return "solo"
    if "팀" in text or "동아리" in text:
        return "team"
    if "둘 다" in text or "혼합" in text:
        return "mixed"
    return "unknown"


def _extract_weekly_hours(message: str) -> int:
    match = re.search(r"주\s*(\d{1,2})\s*시간", message)
    if not match:
        return 0
    return min(max(int(match.group(1)), 0), 40)


def reject_memory(
    store: MemoryStore,
    user_id: str,
    memory_id: str,
) -> MemoryResponse:
    memory = store.get_memory(user_id, memory_id)
    updated = memory.model_copy(update={"status": "rejected"})
    store.save_memory(user_id, updated)
    _add_memory_event(store, user_id, updated, "rejected", "사용자가 메모리 저장을 거절했습니다.")
    return updated


def archive_memory(
    store: MemoryStore,
    user_id: str,
    memory_id: str,
) -> MemoryResponse:
    memory = store.get_memory(user_id, memory_id)
    updated = memory.model_copy(update={"status": "archived"})
    store.save_memory(user_id, updated)
    _add_memory_event(store, user_id, updated, "archived", "사용자가 메모리를 보관 처리했습니다.")
    return updated


def update_memory(
    *,
    store: MemoryStore,
    user_id: str,
    memory_id: str,
    natural_text: str | None = None,
    value_json: dict[str, Any] | None = None,
) -> MemoryResponse:
    memory = store.get_memory(user_id, memory_id)
    updated = memory.model_copy(
        update={
            "natural_text": natural_text if natural_text is not None else memory.natural_text,
            "value_json": value_json if value_json is not None else memory.value_json,
        }
    )
    store.save_memory(user_id, updated)
    _add_memory_event(store, user_id, updated, "updated", "사용자가 메모리 내용을 수정했습니다.")
    return updated


def _add_memory_event(
    store: MemoryStore,
    user_id: str,
    memory: MemoryResponse,
    event_type: str,
    reason: str,
) -> MemoryEventResponse:
    return store.add_event(
        user_id,
        MemoryEventResponse(
            id=str(uuid4()),
            memory_id=memory.id,
            event_type=event_type,
            reason=reason,
            snapshot=memory.model_dump(),
        ),
    )
