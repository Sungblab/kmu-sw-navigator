from app.services.memory_service import (
    InMemoryMemoryStore,
    classify_memory_sensitivity,
    confirm_memory,
    create_memory_candidate,
    reject_memory,
)


def test_classify_low_sensitivity_interest_allows_auto_save() -> None:
    policy = classify_memory_sensitivity("AI랑 백엔드 관심 있어")

    assert policy.sensitivity == "low"
    assert policy.decision == "auto_save"


def test_classify_medium_sensitivity_grade_concern_requires_confirmation() -> None:
    policy = classify_memory_sensitivity("학점이 낮아서 취업이 걱정돼")

    assert policy.sensitivity == "medium"
    assert policy.decision == "requires_confirmation"


def test_classify_high_sensitivity_password_rejects_storing() -> None:
    policy = classify_memory_sensitivity("내 비밀번호는 test1234야")

    assert policy.sensitivity == "high"
    assert policy.decision == "reject"


def test_auto_saved_memory_creates_created_event() -> None:
    store = InMemoryMemoryStore()

    memory = create_memory_candidate(
        store=store,
        user_id="user-1",
        natural_text="AI랑 백엔드 관심 있어",
        category="interest",
        key="topic",
        value_json={"topics": ["AI", "백엔드"]},
    )

    assert memory.status == "active"
    assert memory.sensitivity == "low"
    assert [event.event_type for event in store.list_events("user-1")] == ["created"]


def test_confirmed_memory_creates_confirmed_event() -> None:
    store = InMemoryMemoryStore()
    memory = create_memory_candidate(
        store=store,
        user_id="user-1",
        natural_text="학점이 낮아서 취업이 걱정돼",
        category="concern",
        key="career",
        value_json={"topic": "취업 걱정"},
    )

    confirmed = confirm_memory(store, "user-1", memory.id)

    assert memory.status == "candidate"
    assert confirmed.status == "active"
    assert [event.event_type for event in store.list_events("user-1")] == [
        "candidate_created",
        "confirmed",
    ]


def test_rejected_memory_creates_rejected_event_and_no_active_memory() -> None:
    store = InMemoryMemoryStore()
    memory = create_memory_candidate(
        store=store,
        user_id="user-1",
        natural_text="학점이 낮아서 취업이 걱정돼",
        category="concern",
        key="career",
        value_json={"topic": "취업 걱정"},
    )

    rejected = reject_memory(store, "user-1", memory.id)

    assert rejected.status == "rejected"
    assert store.list_active_memories("user-1") == []
    assert [event.event_type for event in store.list_events("user-1")] == [
        "candidate_created",
        "rejected",
    ]
