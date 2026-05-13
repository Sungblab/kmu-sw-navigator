from functools import lru_cache
from pathlib import Path
from typing import Annotated

import httpx
from fastapi import Header, HTTPException, status

from app.api.auth import user_id_from_supabase_token
from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client
from app.services.answer_generation_service import (
    AnswerGenerator,
    GeminiAnswerGenerator,
    GeminiGroundingAnswerGenerator,
    GroundingAnswerGenerator,
)
from app.services.assignment_service import (
    AssignmentParser,
    GeminiAssignmentParser,
    InMemoryAssignmentStore,
)
from app.services.chat_store import InMemoryChatStore
from app.services.embedding_service import GeminiEmbeddingService
from app.services.google_oauth_token_service import (
    GoogleOAuthTokenStore,
    InMemoryGoogleOAuthTokenStore,
)
from app.services.llm_usage_log_service import InMemoryLLMUsageLogStore
from app.services.memory_service import InMemoryMemoryStore
from app.services.profile_service import InMemoryProfileStore
from app.services.retrieval_service import (
    LocalDocumentRetriever,
    SupabaseTextRetriever,
    SupabaseVectorRetriever,
)
from app.services.store_protocols import (
    AssignmentStore,
    ChatStore,
    LLMUsageLogStore,
    MemoryStore,
    ProfileStore,
)
from app.services.supabase_stores import (
    SupabaseAssignmentStore,
    SupabaseChatStore,
    SupabaseGoogleOAuthTokenStore,
    SupabaseLLMUsageLogStore,
    SupabaseMemoryStore,
    SupabaseProfileStore,
)

profile_store = InMemoryProfileStore()
memory_store = InMemoryMemoryStore()
chat_store = InMemoryChatStore()
assignment_store = InMemoryAssignmentStore()
google_oauth_token_store = InMemoryGoogleOAuthTokenStore()
llm_usage_log_store = InMemoryLLMUsageLogStore()
gemini_assignment_parser: GeminiAssignmentParser | None = None
supabase_profile_store: SupabaseProfileStore | None = None
supabase_memory_store: SupabaseMemoryStore | None = None
supabase_chat_store: SupabaseChatStore | None = None
supabase_assignment_store: SupabaseAssignmentStore | None = None
supabase_google_oauth_token_store: SupabaseGoogleOAuthTokenStore | None = None
supabase_llm_usage_log_store: SupabaseLLMUsageLogStore | None = None
supabase_document_retriever: SupabaseTextRetriever | SupabaseVectorRetriever | None = None
gemini_answer_generator: GeminiAnswerGenerator | None = None
gemini_grounding_answer_generator: GeminiGroundingAnswerGenerator | None = None


def get_current_user_id(
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> str:
    settings = get_settings()
    if settings.supabase_jwt_secret:
        return user_id_from_supabase_token(authorization, settings.supabase_jwt_secret)

    # Supabase JWT secret이 없는 로컬 테스트에서는 명시적 dev header만 허용한다.
    # 이 경로는 제출용 단위 테스트와 오프라인 발표 실행을 위한 fallback이다.
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증된 사용자만 사용할 수 있습니다.",
        )
    return x_user_id


def get_profile_store() -> ProfileStore:
    global supabase_profile_store
    # Supabase 키가 없는 로컬/발표 환경에서도 API 테스트가 돌아가도록 in-memory fallback을 유지한다.
    if get_settings().has_supabase_backend:
        if supabase_profile_store is None:
            supabase_profile_store = SupabaseProfileStore(get_supabase_client())
        return supabase_profile_store
    return profile_store


def get_memory_store() -> MemoryStore:
    global supabase_memory_store
    # 실제 배포에서는 Supabase adapter가 영속 저장을 맡는다.
    # 키가 없으면 deterministic 테스트용 저장소를 쓴다.
    if get_settings().has_supabase_backend:
        if supabase_memory_store is None:
            supabase_memory_store = SupabaseMemoryStore(get_supabase_client())
        return supabase_memory_store
    return memory_store


def get_chat_store() -> ChatStore:
    global supabase_chat_store
    if get_settings().has_supabase_backend:
        if supabase_chat_store is None:
            supabase_chat_store = SupabaseChatStore(get_supabase_client())
        return supabase_chat_store
    return chat_store


def get_assignment_store() -> AssignmentStore:
    global supabase_assignment_store
    if get_settings().has_supabase_backend:
        if supabase_assignment_store is None:
            supabase_assignment_store = SupabaseAssignmentStore(get_supabase_client())
        return supabase_assignment_store
    return assignment_store


def get_google_oauth_token_store() -> GoogleOAuthTokenStore:
    global supabase_google_oauth_token_store
    if get_settings().has_supabase_backend:
        if supabase_google_oauth_token_store is None:
            supabase_google_oauth_token_store = SupabaseGoogleOAuthTokenStore(
                get_supabase_client()
            )
        return supabase_google_oauth_token_store
    return google_oauth_token_store


def get_llm_usage_log_store() -> LLMUsageLogStore:
    global supabase_llm_usage_log_store
    if get_settings().has_supabase_backend:
        if supabase_llm_usage_log_store is None:
            supabase_llm_usage_log_store = SupabaseLLMUsageLogStore(get_supabase_client())
        return supabase_llm_usage_log_store
    return llm_usage_log_store


def get_google_oauth_http_client() -> httpx.Client:
    return httpx.Client(timeout=10)


@lru_cache
def get_local_document_retriever() -> LocalDocumentRetriever:
    # DB/RPC 연결 전에도 같은 Markdown 자료로 RAG 근거 선택을 검증한다.
    backend_dir = Path(__file__).resolve().parents[2]
    repo_root = backend_dir.parent
    return LocalDocumentRetriever.from_markdown_dirs(
        raw_dir=repo_root / "data" / "raw",
        wiki_dir=repo_root / "data" / "wiki",
    )


def get_document_retriever() -> (
    LocalDocumentRetriever | SupabaseTextRetriever | SupabaseVectorRetriever
):
    global supabase_document_retriever
    settings = get_settings()
    if settings.has_supabase_backend:
        if supabase_document_retriever is None:
            if settings.gemini_api_key:
                supabase_document_retriever = SupabaseVectorRetriever(
                    get_supabase_client(),
                    GeminiEmbeddingService(
                        api_key=settings.gemini_api_key,
                        model=settings.gemini_embedding_model,
                        output_dimensionality=settings.gemini_embedding_dim,
                    ),
                )
            else:
                supabase_document_retriever = SupabaseTextRetriever(get_supabase_client())
        return supabase_document_retriever
    return get_local_document_retriever()


def get_answer_generator() -> AnswerGenerator | None:
    global gemini_answer_generator
    settings = get_settings()
    if not settings.gemini_api_key:
        return None
    if gemini_answer_generator is None:
        gemini_answer_generator = GeminiAnswerGenerator(
            api_key=settings.gemini_api_key,
            model=settings.gemini_main_model,
        )
    return gemini_answer_generator


def get_grounding_answer_generator() -> GroundingAnswerGenerator | None:
    global gemini_grounding_answer_generator
    settings = get_settings()
    if not settings.gemini_api_key:
        return None
    if gemini_grounding_answer_generator is None:
        gemini_grounding_answer_generator = GeminiGroundingAnswerGenerator(
            api_key=settings.gemini_api_key,
            model=settings.gemini_main_model,
        )
    return gemini_grounding_answer_generator


def get_assignment_parser() -> AssignmentParser | None:
    global gemini_assignment_parser
    settings = get_settings()
    if not settings.gemini_api_key:
        return None
    if gemini_assignment_parser is None:
        gemini_assignment_parser = GeminiAssignmentParser(
            api_key=settings.gemini_api_key,
            model=settings.gemini_schedule_model,
        )
    return gemini_assignment_parser
