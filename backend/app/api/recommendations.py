from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user_id, get_document_retriever
from app.schemas.recommendation import (
    ActivityRecommendRequest,
    ActivityRecommendResponse,
    TrackRecommendRequest,
    TrackRecommendResponse,
)
from app.services.recommendation_service import recommend_activity, recommend_track
from app.services.retrieval_service import (
    LocalDocumentRetriever,
    SupabaseTextRetriever,
    SupabaseVectorRetriever,
)

router = APIRouter(prefix="/recommend", tags=["recommendations"])
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
RetrieverDep = Annotated[
    LocalDocumentRetriever | SupabaseTextRetriever | SupabaseVectorRetriever,
    Depends(get_document_retriever),
]


@router.post("/track")
def post_track_recommendation(
    request: TrackRecommendRequest,
    _: CurrentUserId,
    retriever: RetrieverDep,
) -> TrackRecommendResponse:
    return recommend_track(request, retriever=retriever)


@router.post("/activity")
def post_activity_recommendation(
    request: ActivityRecommendRequest,
    _: CurrentUserId,
    retriever: RetrieverDep,
) -> ActivityRecommendResponse:
    return recommend_activity(request, retriever=retriever)
