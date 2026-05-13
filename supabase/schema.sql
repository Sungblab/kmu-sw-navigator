create extension if not exists vector;

create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  name text,
  student_id text,
  department text default '소프트웨어융합대학',
  major text,
  created_at timestamp with time zone default now()
);

create table if not exists document_chunks (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  source text,
  category text,
  department text default '소프트웨어융합대학',
  content text not null,
  embedding vector(768),
  created_at timestamp with time zone default now()
);

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
  match_threshold float default 0.0
)
returns table (
  id uuid,
  title text,
  source text,
  category text,
  content text,
  similarity float
)
language sql stable
as $$
  select
    document_chunks.id,
    document_chunks.title,
    document_chunks.source,
    document_chunks.category,
    document_chunks.content,
    1 - (document_chunks.embedding <=> query_embedding) as similarity
  from document_chunks
  where 1 - (document_chunks.embedding <=> query_embedding) >= match_threshold
  order by document_chunks.embedding <=> query_embedding
  limit match_count;
$$;

