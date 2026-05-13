from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user_id, get_document_retriever
from app.main import app
from app.services.retrieval_service import RetrievalResult


class FakeRetriever:
    def search(self, query: str, *, limit: int = 5) -> list[RetrievalResult]:
        return [
            RetrievalResult(
                source_type="wiki_page",
                title="동아리 안내",
                source="data/wiki/club.md",
                category="club",
                heading_path="개발 동아리",
                content="개발 동아리와 프로젝트 스터디를 탐색한다.",
                score=2.0,
                metadata={"slug": "club"},
            )
        ][:limit]


def test_recommend_track_api_returns_ranked_recommendations() -> None:
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_document_retriever] = lambda: FakeRetriever()
    client = TestClient(app)

    response = client.post(
        "/api/recommend/track",
        json={
            "grade": 3,
            "interests": ["AI", "백엔드"],
            "goal": "AI 서비스 개발",
            "coding_level": "intermediate",
            "preference": "project",
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["primary_recommendation"]["id"] == "ai-backend-rag"
    assert response.json()["evidence"]["internal_sources"][0]["title"] == "동아리 안내"


def test_recommend_activity_api_returns_activity_mix() -> None:
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_document_retriever] = lambda: FakeRetriever()
    client = TestClient(app)

    response = client.post(
        "/api/recommend/activity",
        json={
            "interests": ["개발", "운동"],
            "activity_style": "team",
            "weekly_hours": 4,
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["recommendations"]][:2] == [
        "project-study",
        "sports-community",
    ]
