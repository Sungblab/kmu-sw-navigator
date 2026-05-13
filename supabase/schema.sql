create extension if not exists vector;

create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  name text,
  student_id text,
  department text default '소프트웨어융합대학',
  major text,
  created_at timestamp with time zone default now()
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
  created_at timestamp with time zone default now()
);

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

