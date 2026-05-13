from typing import Any, Literal

from pydantic import BaseModel, Field

CodingLevel = Literal["beginner", "intermediate", "advanced"]
Preference = Literal["lecture", "project", "study", "unknown"]
ActivityStyle = Literal["solo", "team", "mixed", "unknown"]


class TrackRecommendRequest(BaseModel):
    grade: int = Field(ge=1, le=4)
    interests: list[str] = Field(default_factory=list)
    goal: str = ""
    coding_level: CodingLevel = "beginner"
    preference: Preference = "unknown"


class ActivityRecommendRequest(BaseModel):
    interests: list[str] = Field(default_factory=list)
    activity_style: ActivityStyle = "unknown"
    weekly_hours: int = Field(default=3, ge=0, le=40)


class RecommendationItem(BaseModel):
    id: str
    title: str
    score: int
    reasons: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class RecommendationEvidence(BaseModel):
    internal_sources: list[dict[str, Any]] = Field(default_factory=list)


class TrackRecommendResponse(BaseModel):
    primary_recommendation: RecommendationItem
    recommendations: list[RecommendationItem]
    recommended_actions: list[str]
    evidence: RecommendationEvidence = Field(default_factory=RecommendationEvidence)


class ActivityRecommendResponse(BaseModel):
    activity_style: str
    recommendations: list[RecommendationItem]
    recommended_actions: list[str]
    evidence: RecommendationEvidence = Field(default_factory=RecommendationEvidence)
