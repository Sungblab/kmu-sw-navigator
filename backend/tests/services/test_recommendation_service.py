from app.schemas.recommendation import ActivityRecommendRequest, TrackRecommendRequest
from app.services.recommendation_service import recommend_activity, recommend_track
from app.services.retrieval_service import RetrievalResult


class FakeRetriever:
    def search(self, query: str, *, limit: int = 5) -> list[RetrievalResult]:
        assert "AI" in query or "개발" in query
        return [
            RetrievalResult(
                source_type="wiki_page",
                title="트랙 안내",
                source="data/wiki/track.md",
                category="track",
                heading_path="AI 트랙",
                content="AI와 백엔드 프로젝트는 RAG 서비스로 연결할 수 있다.",
                score=2.5,
                metadata={"slug": "track"},
            )
        ][:limit]


def test_recommend_track_prioritizes_ai_backend_for_upper_grade() -> None:
    response = recommend_track(
        TrackRecommendRequest(
            grade=3,
            interests=["AI", "백엔드"],
            goal="AI 서비스 개발",
            coding_level="intermediate",
            preference="project",
        ),
        retriever=FakeRetriever(),
    )

    assert response.primary_recommendation.id == "ai-backend-rag"
    assert response.primary_recommendation.score >= 7
    assert "AI" in response.primary_recommendation.reasons[0]
    assert "RAG" in response.recommended_actions[0]
    assert response.evidence.internal_sources[0]["title"] == "트랙 안내"


def test_recommend_track_guides_beginner_to_foundation() -> None:
    response = recommend_track(
        TrackRecommendRequest(
            grade=1,
            interests=["웹"],
            goal="전공 적응",
            coding_level="beginner",
            preference="lecture",
        )
    )

    assert response.primary_recommendation.id == "foundation-web"
    assert any("Python" in action for action in response.recommended_actions)


def test_recommend_activity_combines_development_and_sports_interests() -> None:
    response = recommend_activity(
        ActivityRecommendRequest(
            interests=["개발", "운동"],
            activity_style="team",
            weekly_hours=4,
        ),
        retriever=FakeRetriever(),
    )

    ids = [item.id for item in response.recommendations]
    assert "project-study" in ids
    assert "sports-community" in ids
    assert response.activity_style == "팀 활동 선호"
    assert response.evidence.internal_sources[0]["category"] == "track"
