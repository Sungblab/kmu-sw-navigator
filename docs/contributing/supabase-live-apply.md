# Supabase live schema 적용 절차

현재 로컬에는 Supabase CLI가 설치되어 있지 않으므로, live schema 적용은 Supabase Dashboard SQL Editor에서 수행한다.

## 적용 순서

1. Supabase Dashboard에서 프로젝트 `abbwnqwvvtxrizutswws`를 연다.
2. 좌측 SQL Editor로 이동한다.
3. 아래 명령으로 SQL Editor 적용용 bundle을 만든다.

```powershell
pnpm supabase:sql-bundle
```

이 명령은 bundle 생성 전에 `profiles`, `document_chunks`, `google_oauth_tokens`, `search_document_chunks_text`, `match_document_chunks` 같은 필수 schema marker와 비밀값 marker 포함 여부를 검사한다. 검증에 실패하면 파일을 쓰지 않고 실패한다.

초기 확인용 seed까지 함께 붙여넣고 싶으면 아래 명령을 사용한다.

```powershell
pnpm supabase:sql-bundle -- --include-seed
```

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

또는 아래 명령 하나로 schema check 이후의 live smoke를 순서대로 실행할 수 있다.

```powershell
pnpm live:smoke-run --api-base http://127.0.0.1:8001
```

`supabase:create-smoke-user --write-root-env`는 이미 실행되어 root `.env`에 smoke user UUID/email/password가 준비되어 있다. root `.env`는 gitignored 파일이므로 커밋하지 않는다.

`supabase/live-schema-bundle.sql`은 적용 편의를 위한 생성 파일이므로 커밋하지 않는다. 원본은 `supabase/schema.sql`과 `supabase/seed.sql`이다.

## 성공 기준

- `pnpm supabase:schema-check`: 모든 table/function이 `[ready]`
- `pnpm supabase:smoke`: `profile_exists=True`, `memory_status=active`
- `pnpm supabase:llm-smoke`: `created_feature=llm_usage_smoke`
- `pnpm supabase:login-smoke --api-base http://127.0.0.1:8001`: `profile_exists=True`
- `pnpm rag:ingest:embeddings`: `document_chunks` upsert와 Gemini embedding 생성 완료. 같은 자료를 다시 실행해도 `source_type,title,heading_path,chunk_index,content_hash` 기준으로 중복 chunk를 만들지 않는다.
- `supabase/seed.sql`: 초기 확인용 seed를 반복 실행해도 `document_chunks`가 같은 conflict key 기준으로 중복되지 않는다.
- `pnpm live:smoke-run --api-base http://127.0.0.1:8001`: 위 필수 smoke를 dependency 순서대로 모두 통과

## 현재 blocker

2026-05-23 기준 live schema check는 아래 항목을 모두 missing으로 보고한다.

- tables: `profiles`, `raw_documents`, `wiki_pages`, `wiki_logs`, `document_chunks`, `assignments`, `chat_sessions`, `chat_messages`, `chat_logs`, `llm_usage_logs`, `user_memories`, `memory_events`, `google_oauth_tokens`
- functions: `search_document_chunks_text`, `match_document_chunks`

이 상태에서는 로그인은 가능해도 profile write가 `503 supabase_schema_missing`으로 실패한다.
`pnpm live:smoke-run --api-base http://127.0.0.1:8001`도 같은 경우에는 `pnpm supabase:sql-bundle -- --include-seed`부터 다시 실행하라는 next action을 출력한다.
