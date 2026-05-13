from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_answer_generator,
    get_chat_store,
    get_current_user_id,
    get_document_retriever,
    get_grounding_answer_generator,
    get_llm_usage_log_store,
    get_memory_store,
)
from app.schemas.chat import ChatMessagesResponse, ChatRequest, ChatResponse, ChatSessionsResponse
from app.schemas.llm_usage import LLMUsageLogCreateRequest
from app.services.answer_generation_service import AnswerGenerator, GroundingAnswerGenerator
from app.services.chat_contract_service import build_chat_response
from app.services.retrieval_service import (
    LocalDocumentRetriever,
    SupabaseTextRetriever,
    SupabaseVectorRetriever,
)
from app.services.store_protocols import ChatStore, LLMUsageLogStore, MemoryStore

router = APIRouter(prefix="/chat", tags=["chat"])
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
MemoryStoreDep = Annotated[MemoryStore, Depends(get_memory_store)]
ChatStoreDep = Annotated[ChatStore, Depends(get_chat_store)]
LLMUsageLogStoreDep = Annotated[LLMUsageLogStore, Depends(get_llm_usage_log_store)]
RetrieverDep = Annotated[
    LocalDocumentRetriever | SupabaseTextRetriever | SupabaseVectorRetriever,
    # SupabaseVectorRetriever is selected when both Supabase and Gemini env are configured.
    # The response evidence shape remains the same as text/local retrieval.
    Depends(get_document_retriever),
]
AnswerGeneratorDep = Annotated[AnswerGenerator | None, Depends(get_answer_generator)]
GroundingAnswerGeneratorDep = Annotated[
    GroundingAnswerGenerator | None,
    Depends(get_grounding_answer_generator),
]


@router.post("")
def post_chat(
    request: ChatRequest,
    user_id: CurrentUserId,
    store: MemoryStoreDep,
    chat_store: ChatStoreDep,
    llm_usage_log_store: LLMUsageLogStoreDep,
    retriever: RetrieverDep,
    answer_generator: AnswerGeneratorDep,
    grounding_answer_generator: GroundingAnswerGeneratorDep,
) -> ChatResponse:
    memories = store.list_active_memories(user_id)
    retrieval_results = retriever.search(request.message)
    response = build_chat_response(
        request,
        memories,
        retrieval_results,
        answer_generator,
        grounding_answer_generator,
    )
    if answer_generator is not None:
        llm_usage_log_store.create_log(
            user_id,
            LLMUsageLogCreateRequest(
                feature="rag_chat",
                input_text=request.message,
                output_text=response.answer,
                model=getattr(answer_generator, "model", None),
                purpose="검색 근거와 사용자 메모리를 바탕으로 채팅 답변 생성",
                metadata={"intent": response.intent},
            ),
        )
    if grounding_answer_generator is not None and response.evidence.web_sources:
        llm_usage_log_store.create_log(
            user_id,
            LLMUsageLogCreateRequest(
                feature="google_grounding",
                input_text=request.message,
                output_text=response.answer,
                model=getattr(grounding_answer_generator, "model", None),
                purpose="최신 웹 근거를 사용한 진로/프로젝트 답변 보강",
                metadata={
                    "intent": response.intent,
                    "web_source_count": len(response.evidence.web_sources),
                },
            ),
        )
    return chat_store.save_exchange(user_id, request, response)


@router.get("/sessions")
def list_chat_sessions(
    user_id: CurrentUserId,
    chat_store: ChatStoreDep,
) -> ChatSessionsResponse:
    return ChatSessionsResponse(sessions=chat_store.list_sessions(user_id))


@router.get("/sessions/{session_id}/messages")
def list_chat_messages(
    session_id: str,
    user_id: CurrentUserId,
    chat_store: ChatStoreDep,
) -> ChatMessagesResponse:
    return ChatMessagesResponse(messages=chat_store.list_messages(user_id, session_id))
