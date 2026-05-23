from types import SimpleNamespace

from app.api import dependencies
from app.core.config import get_settings
from app.services.assignment_service import InMemoryAssignmentStore
from app.services.chat_store import InMemoryChatStore
from app.services.google_oauth_token_service import InMemoryGoogleOAuthTokenStore
from app.services.llm_usage_log_service import InMemoryLLMUsageLogStore
from app.services.memory_service import InMemoryMemoryStore
from app.services.profile_service import InMemoryProfileStore
from app.services.retrieval_service import LocalDocumentRetriever


class MissingSchemaClient:
    def table(self, _name: str) -> "MissingSchemaClient":
        return self

    def select(self, *_args: str) -> "MissingSchemaClient":
        return self

    def limit(self, _count: int) -> "MissingSchemaClient":
        return self

    def execute(self) -> object:
        raise RuntimeError("Could not find the table in the schema cache")


class ReadySchemaClient:
    def table(self, _name: str) -> "ReadySchemaClient":
        return self

    def select(self, *_args: str) -> "ReadySchemaClient":
        return self

    def limit(self, _count: int) -> "ReadySchemaClient":
        return self

    def execute(self) -> object:
        return SimpleNamespace(data=[])


def _enable_supabase_env(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role")
    get_settings.cache_clear()
    dependencies.is_supabase_schema_ready.cache_clear()


def test_dependencies_use_supabase_adapters_when_supabase_env_exists(monkeypatch) -> None:
    _enable_supabase_env(monkeypatch)
    monkeypatch.setattr(dependencies, "get_supabase_client", lambda: MissingSchemaClient())

    assert dependencies.get_profile_store().__class__.__name__ == "SupabaseProfileStore"
    assert dependencies.get_memory_store().__class__.__name__ == "SupabaseMemoryStore"
    assert dependencies.get_chat_store().__class__.__name__ == "SupabaseChatStore"
    assert dependencies.get_assignment_store().__class__.__name__ == "SupabaseAssignmentStore"
    assert (
        dependencies.get_google_oauth_token_store().__class__.__name__
        == "SupabaseGoogleOAuthTokenStore"
    )
    assert dependencies.get_llm_usage_log_store().__class__.__name__ == "SupabaseLLMUsageLogStore"


def test_dependencies_use_supabase_adapters_when_schema_probe_succeeds(monkeypatch) -> None:
    _enable_supabase_env(monkeypatch)
    monkeypatch.setattr(dependencies, "get_supabase_client", lambda: ReadySchemaClient())

    assert dependencies.get_profile_store().__class__.__name__ == "SupabaseProfileStore"
    assert dependencies.get_memory_store().__class__.__name__ == "SupabaseMemoryStore"
    assert dependencies.get_chat_store().__class__.__name__ == "SupabaseChatStore"
    assert dependencies.get_assignment_store().__class__.__name__ == "SupabaseAssignmentStore"
    assert (
        dependencies.get_google_oauth_token_store().__class__.__name__
        == "SupabaseGoogleOAuthTokenStore"
    )
    assert dependencies.get_llm_usage_log_store().__class__.__name__ == "SupabaseLLMUsageLogStore"


def test_dependencies_keep_in_memory_adapters_without_supabase_env(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "")
    get_settings.cache_clear()
    dependencies.is_supabase_schema_ready.cache_clear()

    assert isinstance(dependencies.get_profile_store(), InMemoryProfileStore)
    assert isinstance(dependencies.get_memory_store(), InMemoryMemoryStore)
    assert isinstance(dependencies.get_chat_store(), InMemoryChatStore)
    assert isinstance(dependencies.get_assignment_store(), InMemoryAssignmentStore)
    assert isinstance(dependencies.get_google_oauth_token_store(), InMemoryGoogleOAuthTokenStore)
    assert isinstance(dependencies.get_llm_usage_log_store(), InMemoryLLMUsageLogStore)
    assert isinstance(dependencies.get_document_retriever(), LocalDocumentRetriever)
