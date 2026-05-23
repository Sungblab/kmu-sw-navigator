create extension if not exists vector;

create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  name text,
  student_id text,
  department text not null default 'unknown' check (department in ('software', 'ai', 'unknown', 'other')),
  major text,
  grade int not null default 1 check (grade between 1 and 4),
  curriculum_year text not null default 'unknown' check (curriculum_year in ('2023', '2024', '2025', 'unknown')),
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

create table if not exists raw_documents (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  title text not null,
  category text not null default 'general',
  source text,
  collected_at date,
  content text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

create table if not exists wiki_pages (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  title text not null,
  category text not null default 'general',
  type text not null default 'topic' check (type in ('index', 'concept', 'topic', 'entity', 'synthesis')),
  status text not null default 'active' check (status in ('active', 'archived')),
  content text not null,
  source_count int not null default 0,
  related_slugs text[] not null default '{}'::text[],
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

create table if not exists wiki_logs (
  id uuid primary key default gen_random_uuid(),
  action text not null check (action in ('build', 'ingest', 'update', 'query', 'lint')),
  summary text not null,
  affected_pages text[] not null default '{}'::text[],
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamp with time zone default now()
);

create table if not exists document_chunks (
  id uuid primary key default gen_random_uuid(),
  source_type text not null check (source_type in ('raw_document', 'wiki_page')),
  source_id uuid,
  title text not null,
  source text,
  category text,
  department text default '소프트웨어융합대학',
  heading_path text not null default '',
  chunk_index int not null default 0,
  content text not null,
  content_hash text,
  embedding vector(768),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamp with time zone default now()
);

create index if not exists raw_documents_category_idx on raw_documents(category);
create index if not exists wiki_pages_category_idx on wiki_pages(category);
create index if not exists wiki_logs_created_at_idx on wiki_logs(created_at desc);
create index if not exists document_chunks_source_idx on document_chunks(source_type, source_id);
create index if not exists document_chunks_category_idx on document_chunks(category);
create unique index if not exists document_chunks_unique_chunk_idx on document_chunks(
  source_type,
  title,
  heading_path,
  chunk_index,
  content_hash
);
create index if not exists document_chunks_text_idx on document_chunks
  using gin (to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(heading_path, '') || ' ' || content));
create index if not exists document_chunks_embedding_idx on document_chunks
  using hnsw (embedding vector_cosine_ops)
  where embedding is not null;

create table if not exists assignments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  course text,
  due_at timestamp with time zone not null,
  memo text,
  status text default 'todo' check (status in ('todo', 'done')),
  calendar_event_id text,
  calendar_synced_at timestamp with time zone,
  created_at timestamp with time zone default now()
);

create table if not exists chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text,
  intent text,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

create table if not exists chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references chat_sessions(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  evidence jsonb not null default '{}'::jsonb,
  memory_updates jsonb not null default '[]'::jsonb,
  created_at timestamp with time zone default now()
);

create table if not exists chat_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  question text not null,
  answer text not null,
  sources jsonb default '[]'::jsonb,
  created_at timestamp with time zone default now()
);

create table if not exists llm_usage_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  feature text not null,
  input_text text not null,
  output_text text,
  model text,
  purpose text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamp with time zone default now()
);

create table if not exists user_memories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  category text not null,
  key text not null,
  value_json jsonb not null default '{}'::jsonb,
  natural_text text not null,
  embedding vector(768),
  embedding_status text not null default 'pending' check (embedding_status in ('pending', 'ready', 'failed')),
  confidence numeric not null default 0.5 check (confidence >= 0 and confidence <= 1),
  sensitivity text not null default 'low' check (sensitivity in ('low', 'medium', 'high')),
  status text not null default 'active' check (status in ('candidate', 'active', 'archived', 'rejected')),
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

create table if not exists memory_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  memory_id uuid references user_memories(id) on delete set null,
  event_type text not null check (event_type in ('created', 'candidate_created', 'confirmed', 'rejected', 'updated', 'archived')),
  reason text,
  snapshot jsonb not null default '{}'::jsonb,
  created_at timestamp with time zone default now()
);

create table if not exists google_oauth_tokens (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  provider text not null default 'google' check (provider = 'google'),
  encrypted_access_token text not null,
  encrypted_refresh_token text,
  scope text,
  expires_at timestamp with time zone,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now(),
  unique (user_id, provider)
);

create index if not exists assignments_user_due_idx on assignments(user_id, due_at);
create index if not exists chat_sessions_user_created_idx on chat_sessions(user_id, created_at desc);
create index if not exists chat_messages_session_created_idx on chat_messages(session_id, created_at);
create index if not exists user_memories_user_status_idx on user_memories(user_id, status);
create index if not exists user_memories_user_category_idx on user_memories(user_id, category);
create index if not exists memory_events_user_created_idx on memory_events(user_id, created_at desc);
create index if not exists google_oauth_tokens_user_idx on google_oauth_tokens(user_id);

create or replace function match_document_chunks (
  query_embedding vector(768),
  match_count int default 5,
  match_threshold float default 0.0,
  filter_source_type text default null
)
returns table (
  id uuid,
  source_type text,
  source_id uuid,
  title text,
  source text,
  category text,
  heading_path text,
  content text,
  similarity float
)
language sql stable
as $$
  select
    document_chunks.id,
    document_chunks.source_type,
    document_chunks.source_id,
    document_chunks.title,
    document_chunks.source,
    document_chunks.category,
    document_chunks.heading_path,
    document_chunks.content,
    1 - (document_chunks.embedding <=> query_embedding) as similarity
  from document_chunks
  where document_chunks.embedding is not null
    and (filter_source_type is null or document_chunks.source_type = filter_source_type)
    and 1 - (document_chunks.embedding <=> query_embedding) >= match_threshold
  order by
    case when document_chunks.source_type = 'wiki_page' then 0 else 1 end,
    document_chunks.embedding <=> query_embedding
  limit match_count;
$$;

alter table profiles enable row level security;
alter table assignments enable row level security;
alter table chat_sessions enable row level security;
alter table chat_messages enable row level security;
alter table chat_logs enable row level security;
alter table llm_usage_logs enable row level security;
alter table user_memories enable row level security;
alter table memory_events enable row level security;
alter table google_oauth_tokens enable row level security;

drop policy if exists "profiles_select_own" on profiles;
create policy "profiles_select_own" on profiles
  for select using (auth.uid() = id);
drop policy if exists "profiles_insert_own" on profiles;
create policy "profiles_insert_own" on profiles
  for insert with check (auth.uid() = id);
drop policy if exists "profiles_update_own" on profiles;
create policy "profiles_update_own" on profiles
  for update using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists "assignments_own" on assignments;
create policy "assignments_own" on assignments
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "chat_sessions_own" on chat_sessions;
create policy "chat_sessions_own" on chat_sessions
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "chat_messages_own" on chat_messages;
create policy "chat_messages_own" on chat_messages
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "chat_logs_own" on chat_logs;
create policy "chat_logs_own" on chat_logs
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "llm_usage_logs_own" on llm_usage_logs;
create policy "llm_usage_logs_own" on llm_usage_logs
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "user_memories_own" on user_memories;
create policy "user_memories_own" on user_memories
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "memory_events_own" on memory_events;
create policy "memory_events_own" on memory_events
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "google_oauth_tokens_own" on google_oauth_tokens;
create policy "google_oauth_tokens_own" on google_oauth_tokens
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create or replace function search_document_chunks_text (
  search_query text,
  match_count int default 5,
  filter_source_type text default null
)
returns table (
  id uuid,
  source_type text,
  source_id uuid,
  title text,
  source text,
  category text,
  heading_path text,
  content text,
  rank float
)
language sql stable
as $$
  select
    document_chunks.id,
    document_chunks.source_type,
    document_chunks.source_id,
    document_chunks.title,
    document_chunks.source,
    document_chunks.category,
    document_chunks.heading_path,
    document_chunks.content,
    ts_rank(
      to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(heading_path, '') || ' ' || content),
      plainto_tsquery('simple', search_query)
    )::float as rank
  from document_chunks
  where (filter_source_type is null or document_chunks.source_type = filter_source_type)
    and to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(heading_path, '') || ' ' || content)
      @@ plainto_tsquery('simple', search_query)
  order by
    case when document_chunks.source_type = 'wiki_page' then 0 else 1 end,
    rank desc
  limit match_count;
$$;

notify pgrst, 'reload schema';
