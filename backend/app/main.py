from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError

from app.api import assignments, chat, integrations, llm_logs, memories, profile, recommendations
from app.core.config import get_settings
from app.core.supabase_errors import is_schema_cache_error

settings = get_settings()

app = FastAPI(
    title="kmu-sw-navigator API",
    description="국민대학교 소프트웨어융합대학 학생을 위한 개인화 RAG 기반 AI 내비게이터 API",
    version="0.1.0",
)

app.include_router(profile.router, prefix="/api")
app.include_router(memories.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(assignments.router, prefix="/api")
app.include_router(integrations.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(llm_logs.router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):51[0-9]{2}$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(APIError)
async def postgrest_api_error_handler(_: Request, exc: APIError) -> JSONResponse:
    if is_schema_cache_error(exc):
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Supabase schema is not applied. Apply supabase/schema.sql.",
                "code": "supabase_schema_missing",
            },
        )
    return JSONResponse(status_code=502, content={"detail": "Supabase request failed."})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "kmu-sw-navigator-backend"}
