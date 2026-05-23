# Supabase live schema 적용 절차

현재 로컬에는 Supabase CLI가 설치되어 있지 않으므로, live schema 적용은 Supabase Dashboard SQL Editor에서 수행한다.

## 적용 순서

1. Supabase Dashboard에서 프로젝트 `abbwnqwvvtxrizutswws`를 연다.
2. 좌측 SQL Editor로 이동한다.
3. 아래 명령으로 SQL Editor 적용용 bundle을 만든다.

```powershell
pnpm supabase:sql-bundle
```

이 명령은 bundle 생성 전에 `profiles`, `document_chunks`, `google_oauth_tokens`, `search_document_chunks_text`, `match_document_chunks`, `notify pgrst, 'reload schema'` 같은 필수 schema marker와 비밀값 marker 포함 여부를 검사한다. 검증에 실패하면 파일을 쓰지 않고 실패한다.

초기 확인용 seed까지 함께 붙여넣고 싶으면 아래 명령을 사용한다.

```powershell
pnpm supabase:sql-bundle -- --include-seed
```

적용 전 현재 env, SQL bundle, live schema blocker를 한 번에 보려면 아래 명령을 실행한다.

```powershell
pnpm live:readiness -- --include-seed --api-base http://127.0.0.1:8001
```

이 명령은 비밀값을 출력하지 않고 missing 변수 이름, SQL bundle 검증 결과, Supabase schema missing 항목, schema 준비 뒤의 API `/health` 상태, 다음 실행 명령만 보여준다.

4. 생성된 `supabase/live-schema-bundle.sql` 전체 내용을 새 query에 붙여넣는다.
5. Run을 실행한다.
6. 실행이 끝난 뒤 로컬에서 아래 명령을 순서대로 실행한다.

```powershell
pnpm supabase:schema-check
pnpm supabase:smoke
pnpm supabase:llm-smoke
pnpm supabase:login-smoke --api-base http://127.0.0.1:8001
pnpm rag:ingest:embeddings
```

`pnpm supabase:schema-check`는 기본적으로 schema check를 3회 재시도한다. 적용 직후 cache 반영을 더 짧게 확인하고 싶으면 아래처럼 조정할 수 있다.

```powershell
pnpm supabase:schema-check -- --retries 1
pnpm supabase:schema-check -- --retries 5 --retry-delay 1
```

또는 아래 명령 하나로 schema check 이후의 live smoke를 순서대로 실행할 수 있다.

```powershell
pnpm live:smoke-run --api-base http://127.0.0.1:8001
```

`--api-base`에 맞는 FastAPI 서버가 켜져 있어야 login/API smoke가 실행된다. 서버가 꺼져 있으면 `live:smoke-run`은 `/health` preflight에서 멈추고 아래 실행 명령을 안내한다.

```powershell
cd backend
uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

`supabase:create-smoke-user --write-root-env`는 이미 실행되어 root `.env`에 smoke user UUID/email/password가 준비되어 있다. root `.env`는 gitignored 파일이므로 커밋하지 않는다.

`supabase/live-schema-bundle.sql`은 적용 편의를 위한 생성 파일이므로 커밋하지 않는다. 원본은 `supabase/schema.sql`과 `supabase/seed.sql`이다.

## 성공 기준

- `pnpm supabase:schema-check`: 모든 table/function이 `[ready]`. 기본 3회 retry 뒤에도 missing이면 SQL Editor 적용 여부를 다시 확인
- `pnpm supabase:smoke`: `profile_exists=True`, `memory_status=active`
- `pnpm supabase:llm-smoke`: `created_feature=llm_usage_smoke`
- `pnpm supabase:login-smoke --api-base http://127.0.0.1:8001`: `profile_exists=True`
- `pnpm rag:ingest:embeddings`: `document_chunks` upsert와 Gemini embedding 생성 완료. 같은 자료를 다시 실행해도 `source_type,title,heading_path,chunk_index,content_hash` 기준으로 중복 chunk를 만들지 않는다.
- `supabase/seed.sql`: 초기 확인용 seed를 반복 실행해도 `document_chunks`가 같은 conflict key 기준으로 중복되지 않는다.
- `pnpm live:smoke-run --api-base http://127.0.0.1:8001`: 위 필수 smoke를 dependency 순서대로 모두 통과
- schema 적용 직후 PostgREST schema cache 반영이 늦으면 `live:smoke-run`이 schema check를 짧게 재시도한 뒤 결과를 출력
- schema 적용 뒤 `--api-base` 서버가 꺼져 있으면 `/health` preflight에서 멈추고 8001 backend 실행 명령을 출력
- schema 적용 뒤 개별 smoke가 실패하면 `live:smoke-run`은 첫 실패를 `schema`, `auth`, `env`, `code` 중 하나로 분류하고 다음 점검 명령을 출력한다.

## 현재 blocker

2026-05-23 기준 live schema check는 아래 항목을 모두 missing으로 보고한다.

- tables: `profiles`, `raw_documents`, `wiki_pages`, `wiki_logs`, `document_chunks`, `assignments`, `chat_sessions`, `chat_messages`, `chat_logs`, `llm_usage_logs`, `user_memories`, `memory_events`, `google_oauth_tokens`
- functions: `search_document_chunks_text`, `match_document_chunks`

이 상태에서는 로그인은 가능해도 profile write가 `503 supabase_schema_missing`으로 실패한다.
`pnpm live:smoke-run --api-base http://127.0.0.1:8001`도 같은 경우에는 `pnpm supabase:sql-bundle -- --include-seed`부터 다시 실행하라는 next action을 출력한다.
