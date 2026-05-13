from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user_id, get_memory_store
from app.main import app
from app.services.memory_service import InMemoryMemoryStore, create_memory_candidate


def test_get_memories_returns_active_memories_only() -> None:
    store = InMemoryMemoryStore()
    create_memory_candidate(
        store=store,
        user_id="user-1",
        natural_text="AI랑 백엔드 관심 있어",
        category="interest",
        key="topic",
        value_json={"topics": ["AI", "백엔드"]},
    )
    create_memory_candidate(
        store=store,
        user_id="user-1",
        natural_text="학점이 낮아서 취업이 걱정돼",
        category="concern",
        key="career",
        value_json={"topic": "취업"},
    )
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: store
    client = TestClient(app)

    response = client.get("/api/memories")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert len(response.json()["memories"]) == 1
    assert response.json()["memories"][0]["status"] == "active"


def test_patch_memory_updates_natural_text_and_value_json() -> None:
    store = InMemoryMemoryStore()
    memory = create_memory_candidate(
        store=store,
        user_id="user-1",
        natural_text="AI랑 백엔드 관심 있어",
        category="interest",
        key="topic",
        value_json={"topics": ["AI"]},
    )
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: store
    client = TestClient(app)

    response = client.patch(
        f"/api/memories/{memory.id}",
        json={
            "natural_text": "AI랑 백엔드, 데이터 관심 있어",
            "value_json": {"topics": ["AI", "백엔드", "데이터"]},
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["natural_text"] == "AI랑 백엔드, 데이터 관심 있어"
    assert response.json()["value_json"]["topics"] == ["AI", "백엔드", "데이터"]


def test_delete_memory_archives_memory() -> None:
    store = InMemoryMemoryStore()
    memory = create_memory_candidate(
        store=store,
        user_id="user-1",
        natural_text="AI랑 백엔드 관심 있어",
        category="interest",
        key="topic",
        value_json={"topics": ["AI"]},
    )
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_memory_store] = lambda: store
    client = TestClient(app)

    response = client.delete(f"/api/memories/{memory.id}")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["status"] == "archived"
    assert store.list_active_memories("user-1") == []
