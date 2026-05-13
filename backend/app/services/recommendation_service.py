from __future__ import annotations

from typing import Protocol

from app.schemas.recommendation import (
    ActivityRecommendRequest,
    ActivityRecommendResponse,
    RecommendationEvidence,
    RecommendationItem,
    TrackRecommendRequest,
    TrackRecommendResponse,
)
from app.services.retrieval_service import RetrievalResult

TRACK_RULES = [
    {
        "id": "ai-backend-rag",
        "title": "AI 서비스 백엔드/RAG 프로젝트 트랙",
        "keywords": ["AI", "인공지능", "백엔드", "backend", "RAG", "데이터"],
        "base_score": 2,
        "actions": [
            "RAG 기반 상담 API를 작은 프로젝트로 구현하기",
            "데이터베이스와 API 인증 흐름 정리하기",
        ],
    },
    {
        "id": "foundation-web",
        "title": "전공 기초 + 작은 웹 프로젝트 트랙",
        "keywords": ["웹", "web", "기초", "프론트", "frontend"],
        "base_score": 2,
        "actions": ["Python 문법과 자료구조 복습하기", "React/FastAPI 미니 기능 하나 완성하기"],
    },
    {
        "id": "startup-mvp",
        "title": "문제 정의 + MVP 검증 트랙",
        "keywords": ["창업", "스타트업", "mvp", "공모전", "서비스"],
        "base_score": 1,
        "actions": ["사용자 문제를 한 문장으로 정의하기", "1주 안에 검증 가능한 MVP 범위로 줄이기"],
    },
]

ACTIVITY_RULES = [
    {
        "id": "project-study",
        "title": "개발 프로젝트 스터디",
        "keywords": ["개발", "코딩", "백엔드", "ai", "앱", "웹"],
        "base_score": 3,
        "actions": ["주 1회 프로젝트 스터디 참여", "GitHub에 진행 기록 남기기"],
    },
    {
        "id": "sports-community",
        "title": "운동/친목 활동",
        "keywords": ["운동", "스포츠", "친목", "체력"],
        "base_score": 2,
        "actions": ["학기 초 동아리 모집 기간 확인", "부담 없는 정기 활동부터 참여"],
    },
    {
        "id": "algorithm-club",
        "title": "알고리즘/코딩테스트 스터디",
        "keywords": ["알고리즘", "코테", "취업", "문제풀이"],
        "base_score": 2,
        "actions": ["백준/프로그래머스 주간 목표 설정", "자료구조 과목과 병행"],
    },
]


class RecommendationRetriever(Protocol):
    def search(self, query: str, *, limit: int = 5) -> list[RetrievalResult]:
        ...


def recommend_track(
    request: TrackRecommendRequest,
    *,
    retriever: RecommendationRetriever | None = None,
) -> TrackRecommendResponse:
    normalized = _normalize_terms([*request.interests, request.goal, request.preference])
    items = []
    for rule in TRACK_RULES:
        score = rule["base_score"]
        reasons: list[str] = []

        # 학년, 관심사, 경험 수준을 분리해 더하는 방식이라 발표에서 조건문 근거를 설명하기 쉽다.
        keyword_hits = _matching_keywords(normalized, rule["keywords"])
        if keyword_hits:
            score += len(keyword_hits) * 2
            reasons.append(f"입력 관심사와 연결됨: {', '.join(keyword_hits)}")
        if request.grade >= 3 and rule["id"] == "ai-backend-rag":
            score += 2
            reasons.append("3학년 이상은 포트폴리오형 프로젝트 경험이 중요함")
        if request.coding_level == "beginner" and rule["id"] == "foundation-web":
            score += 4
            reasons.append("초급 단계에서는 전공 기초와 작은 웹 구현이 우선")
        if "창업" in normalized and rule["id"] == "startup-mvp":
            score += 4
            reasons.append("창업 목표가 있어 문제 정의와 MVP 검증이 필요함")
        if request.preference == "project" and rule["id"] in {"ai-backend-rag", "startup-mvp"}:
            score += 1
            reasons.append("프로젝트형 학습 선호와 맞음")

        items.append(
            RecommendationItem(
                id=rule["id"],
                title=rule["title"],
                score=score,
                reasons=reasons or ["현재 입력 기준으로 탐색 후보에 포함"],
                next_steps=rule["actions"],
            )
        )

    ranked = sorted(items, key=lambda item: item.score, reverse=True)
    actions = _unique_actions(ranked)
    return TrackRecommendResponse(
        primary_recommendation=ranked[0],
        recommendations=ranked,
        recommended_actions=actions,
        evidence=_build_evidence(
            _track_evidence_query(request, ranked[0]),
            retriever,
        ),
    )


def recommend_activity(
    request: ActivityRecommendRequest,
    *,
    retriever: RecommendationRetriever | None = None,
) -> ActivityRecommendResponse:
    normalized = _normalize_terms(request.interests)
    items = []
    for rule in ACTIVITY_RULES:
        score = rule["base_score"]
        reasons: list[str] = []
        keyword_hits = _matching_keywords(normalized, rule["keywords"])
        if keyword_hits:
            score += len(keyword_hits) * 3
            reasons.append(f"관심사와 연결됨: {', '.join(keyword_hits)}")
        if request.activity_style == "team":
            score += 1
            reasons.append("팀 활동 선호와 맞음")
        if request.weekly_hours <= 2 and rule["id"] == "sports-community":
            score += 1
            reasons.append("시간 부담이 낮은 활동부터 시작하기 좋음")

        items.append(
            RecommendationItem(
                id=rule["id"],
                title=rule["title"],
                score=score,
                reasons=reasons or ["현재 입력 기준으로 탐색 후보에 포함"],
                next_steps=rule["actions"],
            )
        )

    ranked = sorted(items, key=lambda item: item.score, reverse=True)
    return ActivityRecommendResponse(
        activity_style=_activity_style_label(request.activity_style),
        recommendations=ranked,
        recommended_actions=_unique_actions(ranked),
        evidence=_build_evidence(
            _activity_evidence_query(request, ranked[0]),
            retriever,
        ),
    )


def _normalize_terms(values: list[str]) -> set[str]:
    terms: set[str] = set()
    for value in values:
        lowered = value.casefold()
        terms.add(lowered)
        for token in lowered.replace("/", " ").replace(",", " ").split():
            terms.add(token)
    return terms


def _matching_keywords(terms: set[str], keywords: list[str]) -> list[str]:
    return [keyword for keyword in keywords if keyword.casefold() in terms]


def _unique_actions(items: list[RecommendationItem]) -> list[str]:
    actions: list[str] = []
    for item in items:
        for action in item.next_steps:
            if action not in actions:
                actions.append(action)
    return actions[:4]


def _activity_style_label(style: str) -> str:
    return {
        "solo": "개인 활동 선호",
        "team": "팀 활동 선호",
        "mixed": "혼합 활동 선호",
        "unknown": "활동 성향 미정",
    }.get(style, "활동 성향 미정")


def _build_evidence(
    query: str,
    retriever: RecommendationRetriever | None,
) -> RecommendationEvidence:
    if retriever is None:
        return RecommendationEvidence()

    # 추천 점수는 규칙 기반으로 유지하고, 선택된 추천어로 내부 문서를 다시 찾아 설명 근거를 붙인다.
    results = retriever.search(query, limit=3)
    return RecommendationEvidence(
        internal_sources=[result.to_evidence() for result in results],
    )


def _track_evidence_query(
    request: TrackRecommendRequest,
    primary: RecommendationItem,
) -> str:
    return " ".join(
        [
            primary.title,
            *request.interests,
            request.goal,
            request.coding_level,
            request.preference,
        ]
    )


def _activity_evidence_query(
    request: ActivityRecommendRequest,
    primary: RecommendationItem,
) -> str:
    return " ".join(
        [
            primary.title,
            *request.interests,
            request.activity_style,
            str(request.weekly_hours),
        ]
    )
