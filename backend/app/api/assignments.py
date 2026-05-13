from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_assignment_parser,
    get_assignment_store,
    get_current_user_id,
    get_google_oauth_http_client,
    get_google_oauth_token_store,
    get_llm_usage_log_store,
)
from app.core.config import get_settings
from app.schemas.assignment import (
    AssignmentCreateRequest,
    AssignmentListResponse,
    AssignmentParseRequest,
    AssignmentPreviewResponse,
    AssignmentResponse,
    AssignmentUpdateRequest,
)
from app.schemas.calendar import CalendarExportResponse
from app.schemas.llm_usage import LLMUsageLogCreateRequest
from app.services.assignment_service import AssignmentParser, preview_assignment_from_text
from app.services.calendar_service import export_assignment_to_calendar
from app.services.google_oauth_token_service import GoogleOAuthTokenStore
from app.services.store_protocols import AssignmentStore, LLMUsageLogStore

router = APIRouter(prefix="/assignments", tags=["assignments"])
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
AssignmentStoreDep = Annotated[AssignmentStore, Depends(get_assignment_store)]
AssignmentParserDep = Annotated[AssignmentParser | None, Depends(get_assignment_parser)]
GoogleOAuthTokenStoreDep = Annotated[
    GoogleOAuthTokenStore,
    Depends(get_google_oauth_token_store),
]
GoogleOAuthHttpClientDep = Annotated[httpx.Client, Depends(get_google_oauth_http_client)]
LLMUsageLogStoreDep = Annotated[LLMUsageLogStore, Depends(get_llm_usage_log_store)]


@router.post("/preview")
def preview_assignment(
    request: AssignmentParseRequest,
    user_id: CurrentUserId,
    parser: AssignmentParserDep,
    llm_usage_log_store: LLMUsageLogStoreDep,
) -> AssignmentPreviewResponse:
    preview = preview_assignment_from_text(
        request.text,
        reference_date=request.reference_date,
        parser=parser,
    )
    if parser is not None and preview.parser == "gemini":
        llm_usage_log_store.create_log(
            user_id,
            LLMUsageLogCreateRequest(
                feature="schedule_parser",
                input_text=request.text,
                output_text=preview.model_dump_json(),
                model=getattr(parser, "model", None),
                purpose="자연어 일정 문장에서 제목, 과목, 마감일 JSON 추출",
                metadata={"confidence": preview.confidence},
            ),
        )
    return preview


@router.post("")
def create_assignment(
    request: AssignmentCreateRequest,
    user_id: CurrentUserId,
    store: AssignmentStoreDep,
) -> AssignmentResponse:
    return store.create_assignment(user_id, request)


@router.get("")
def list_assignments(
    user_id: CurrentUserId,
    store: AssignmentStoreDep,
) -> AssignmentListResponse:
    return AssignmentListResponse(assignments=store.list_assignments(user_id))


@router.patch("/{assignment_id}")
def update_assignment(
    assignment_id: str,
    request: AssignmentUpdateRequest,
    user_id: CurrentUserId,
    store: AssignmentStoreDep,
) -> AssignmentResponse:
    try:
        return store.update_assignment(user_id, assignment_id, request)
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "일정을 찾을 수 없습니다.") from exc


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: str,
    user_id: CurrentUserId,
    store: AssignmentStoreDep,
) -> None:
    try:
        store.delete_assignment(user_id, assignment_id)
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "일정을 찾을 수 없습니다.") from exc


@router.post("/{assignment_id}/export-calendar")
def export_calendar(
    assignment_id: str,
    user_id: CurrentUserId,
    store: AssignmentStoreDep,
    token_store: GoogleOAuthTokenStoreDep,
    client: GoogleOAuthHttpClientDep,
) -> CalendarExportResponse:
    try:
        return export_assignment_to_calendar(
            user_id,
            assignment_id,
            store=store,
            token_store=token_store,
            settings=get_settings(),
            client=client,
        )
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "일정을 찾을 수 없습니다.") from exc
