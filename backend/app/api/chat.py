import json
from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse
from starlette.status import HTTP_204_NO_CONTENT

from app.api.dependencies import (
    get_answer_generator,
    get_chat_store,
    get_current_user_id,
    get_document_retriever,
    get_grounding_answer_generator,
    get_llm_usage_log_store,
    get_memory_store,
)
from app.core.config import get_settings
from app.schemas.chat import ChatMessagesResponse, ChatRequest, ChatResponse, ChatSessionsResponse
from app.schemas.llm_usage import LLMUsageLogCreateRequest
from app.services.answer_generation_service import (
    AnswerGenerator,
    GeminiAnswerGenerator,
    GroundingAnswerGenerator,
    StreamedAnswerChunk,
    _looks_incomplete_answer,
)
from app.services.chat_contract_service import build_chat_response, detect_intent
from app.services.memory_service import create_learning_context_memory_from_chat
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
    return _build_and_store_chat_response(
        request=request,
        user_id=user_id,
        store=store,
        chat_store=chat_store,
        llm_usage_log_store=llm_usage_log_store,
        retriever=retriever,
        answer_generator=answer_generator,
        grounding_answer_generator=grounding_answer_generator,
    )


@router.post("/stream")
def stream_chat(
    request: ChatRequest,
    user_id: CurrentUserId,
    store: MemoryStoreDep,
    chat_store: ChatStoreDep,
    llm_usage_log_store: LLMUsageLogStoreDep,
    retriever: RetrieverDep,
    answer_generator: AnswerGeneratorDep,
    grounding_answer_generator: GroundingAnswerGeneratorDep,
) -> StreamingResponse:
    def events() -> Iterator[str]:
        yield _sse("status", {"message": "근거와 개인 정보를 확인하고 있습니다."})
        try:
            response = _build_and_store_streaming_chat_response(
                request=request,
                user_id=user_id,
                store=store,
                chat_store=chat_store,
                llm_usage_log_store=llm_usage_log_store,
                retriever=retriever,
                answer_generator=answer_generator,
                grounding_answer_generator=grounding_answer_generator,
            )
            yield from response
        except Exception as exc:
            yield _sse("error", {"message": str(exc)})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _build_and_store_streaming_chat_response(
    *,
    request: ChatRequest,
    user_id: str,
    store: MemoryStore,
    chat_store: ChatStore,
    llm_usage_log_store: LLMUsageLogStore,
    retriever: LocalDocumentRetriever | SupabaseTextRetriever | SupabaseVectorRetriever,
    answer_generator: AnswerGenerator | None,
    grounding_answer_generator: GroundingAnswerGenerator | None,
) -> Iterator[str]:
    intent = detect_intent(request.message, mode=request.mode)
    if grounding_answer_generator is not None and intent in {
        "career_advisor",
        "startup_project_mentor",
    }:
        response = _build_and_store_chat_response(
            request=request,
            user_id=user_id,
            store=store,
            chat_store=chat_store,
            llm_usage_log_store=llm_usage_log_store,
            retriever=retriever,
            answer_generator=_chat_answer_generator_for_request(request, answer_generator),
            grounding_answer_generator=grounding_answer_generator,
        )
        yield _sse("session", {"session_id": response.session_id})
        for chunk in _chunk_text(response.answer):
            yield _sse("text", {"delta": chunk})
        yield _sse("done", response.model_dump(mode="json"))
        return

    memories = store.list_active_memories(user_id)
    retrieval_results = retriever.search(request.message)
    streaming_generator = _chat_answer_generator_for_request(request, answer_generator)
    if streaming_generator is None or not hasattr(streaming_generator, "stream_answer"):
        response = _build_and_store_chat_response(
            request=request,
            user_id=user_id,
            store=store,
            chat_store=chat_store,
            llm_usage_log_store=llm_usage_log_store,
            retriever=retriever,
            answer_generator=streaming_generator,
            grounding_answer_generator=grounding_answer_generator,
        )
        yield _sse("session", {"session_id": response.session_id})
        for chunk in _chunk_text(response.answer):
            yield _sse("text", {"delta": chunk})
        yield _sse("done", response.model_dump(mode="json"))
        return

    model = getattr(streaming_generator, "model", None)
    chunks: list[str] = []
    terminal_response: object | None = None
    for chunk in streaming_generator.stream_answer(
        request,
        intent=intent,
        memories=memories,
        retrieval_results=retrieval_results,
    ):
        chunk_text = chunk.text if isinstance(chunk, StreamedAnswerChunk) else chunk
        if isinstance(chunk, StreamedAnswerChunk):
            terminal_response = chunk.response
        chunks.append(chunk_text)
        if chunk_text:
            yield _sse("text", {"delta": chunk_text})
    answer = "".join(chunks).strip()
    if not answer:
        raise RuntimeError("Gemini returned an empty answer")
    if _looks_incomplete_answer(answer, terminal_response):
        retry_answer = streaming_generator.generate_answer(
            request,
            intent=intent,
            memories=memories,
            retrieval_results=retrieval_results,
        ).strip()
        if retry_answer and not _looks_incomplete_answer(retry_answer):
            answer = retry_answer
    response = build_chat_response(
        request,
        memories,
        retrieval_results,
        answer_generator=None,
        grounding_answer_generator=None,
    )
    response.answer = answer
    response.model = model
    response.memory_updates = create_learning_context_memory_from_chat(
        store=store,
        user_id=user_id,
        message=request.message,
    )
    response = chat_store.save_exchange(user_id, request, response)
    llm_usage_log_store.create_log(
        user_id,
        LLMUsageLogCreateRequest(
            feature="rag_chat",
            input_text=request.message,
            output_text=response.answer,
            model=model,
            purpose="검색 근거와 사용자 메모리를 바탕으로 채팅 답변 생성",
            metadata={
                "intent": response.intent,
                "mode": request.mode,
                "model_tier": request.model_tier,
                "attachment_count": len(request.attachments),
            },
        ),
    )
    yield _sse("session", {"session_id": response.session_id})
    yield _sse("done", response.model_dump(mode="json"))


def _build_and_store_chat_response(
    *,
    request: ChatRequest,
    user_id: str,
    store: MemoryStore,
    chat_store: ChatStore,
    llm_usage_log_store: LLMUsageLogStore,
    retriever: LocalDocumentRetriever | SupabaseTextRetriever | SupabaseVectorRetriever,
    answer_generator: AnswerGenerator | None,
    grounding_answer_generator: GroundingAnswerGenerator | None,
) -> ChatResponse:
    memories = store.list_active_memories(user_id)
    retrieval_results = retriever.search(request.message)
    answer_generator = _chat_answer_generator_for_request(request, answer_generator)
    response = build_chat_response(
        request,
        memories,
        retrieval_results,
        answer_generator,
        grounding_answer_generator,
    )
    response.memory_updates = create_learning_context_memory_from_chat(
        store=store,
        user_id=user_id,
        message=request.message,
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
                metadata={
                    "intent": response.intent,
                    "mode": request.mode,
                    "model_tier": request.model_tier,
                    "attachment_count": len(request.attachments),
                },
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


def _sse(event: str, data: dict | ChatResponse) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _chunk_text(text: str, *, size: int = 12) -> Iterator[str]:
    for index in range(0, len(text), size):
        yield text[index : index + size]


def _chat_answer_generator_for_request(
    request: ChatRequest,
    fallback: AnswerGenerator | None,
) -> AnswerGenerator | None:
    settings = get_settings()
    if fallback is None or not settings.gemini_api_key:
        return fallback
    if request.model_tier == "fast":
        return GeminiAnswerGenerator(
            api_key=settings.gemini_api_key,
            model=settings.gemini_schedule_model,
        )
    return fallback or GeminiAnswerGenerator(
        api_key=settings.gemini_api_key,
        model=settings.gemini_main_model,
    )


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


@router.delete("/sessions/{session_id}", status_code=HTTP_204_NO_CONTENT)
def delete_chat_session(
    session_id: str,
    user_id: CurrentUserId,
    chat_store: ChatStoreDep,
) -> None:
    chat_store.delete_session(user_id, session_id)
