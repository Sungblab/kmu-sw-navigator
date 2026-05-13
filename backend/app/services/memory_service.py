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
