-- Legal Knowledge V2 foundation. Apply only to the new MYKE Legal project.
-- No V1 tables, case corpus, or Auth objects are touched.
create schema if not exists extensions;
create extension if not exists vector with schema extensions;

create table public.legal_ingestion_runs (
  id uuid primary key default gen_random_uuid(),
  source_file_name text not null,
  source_file_hash text not null check (source_file_hash ~ '^[0-9a-f]{64}$'),
  parser_name text not null,
  parser_version text not null,
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  status text not null default 'processing' check (status in ('processing','completed','review_required','failed')),
  documents_created integer not null default 0 check (documents_created >= 0),
  units_created integer not null default 0 check (units_created >= 0),
  relations_created integer not null default 0 check (relations_created >= 0),
  duplicates_skipped integer not null default 0 check (duplicates_skipped >= 0),
  warnings_count integer not null default 0 check (warnings_count >= 0),
  errors_count integer not null default 0 check (errors_count >= 0),
  requires_review boolean not null default false,
  summary jsonb not null default '{}'::jsonb
);

create table public.legal_documents (
  id uuid primary key default gen_random_uuid(),
  ingestion_run_id uuid references public.legal_ingestion_runs(id) on delete set null,
  document_hash text not null check (document_hash ~ '^[0-9a-f]{64}$'),
  title text not null check (btrim(title) <> ''),
  short_title text,
  document_type text not null check (document_type in ('constitution','code','law','regulation','judgment','order','cassation','precedent','other_public')),
  rama text,
  hierarchy text,
  issuer text,
  court text,
  chamber text,
  number text,
  expediente text,
  resolution_type text,
  publication_date date,
  resolution_date date,
  valid_from date,
  valid_to date,
  status text not null default 'current' check (status in ('current','modified','repealed','historical','unknown')),
  precedent_binding boolean,
  materia text,
  instancia text,
  ponente text,
  sumilla text,
  official_url text,
  source_file_name text not null,
  source_format text not null,
  parser_version text not null,
  ingestion_status text not null default 'staged' check (ingestion_status in ('staged','processing','ready','ready_with_warnings','review_required','failed')),
  extraction_quality text not null check (extraction_quality in ('high','medium','low','ocr_required')),
  ocr_required boolean not null default false,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (document_hash, parser_version),
  check (valid_to is null or valid_from is null or valid_to >= valid_from),
  check (not ocr_required or extraction_quality = 'ocr_required')
);

create table public.legal_units (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.legal_documents(id) on delete cascade,
  parent_unit_id uuid references public.legal_units(id) on delete cascade,
  unit_type text not null check (unit_type in (
    'article','paragraph','inciso','literal','disposition','annex','amendment_note','concordance',
    'sumilla','matter','antecedent','fact','foundation','decision','separate_opinion')),
  unit_number text,
  heading text,
  sequence integer not null check (sequence > 0),
  part_number integer,
  part_count integer,
  book text,
  section text,
  title text,
  chapter text,
  page_start integer,
  page_end integer,
  text text not null check (btrim(text) <> ''),
  normalized_text text not null check (btrim(normalized_text) <> ''),
  excerpt text,
  search_text text not null,
  search_tsv tsvector generated always as (to_tsvector('spanish'::regconfig, coalesce(search_text,''))) stored,
  is_current boolean not null default true,
  valid_from date,
  valid_to date,
  content_hash text not null check (content_hash ~ '^[0-9a-f]{64}$'),
  token_count integer check (token_count >= 0),
  embedding extensions.vector(1536),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (document_id, sequence),
  unique (document_id, content_hash),
  check (page_start is null or page_start > 0),
  check (page_end is null or page_start is null or page_end >= page_start),
  check ((part_number is null and part_count is null) or
         (part_number between 1 and part_count)),
  check (valid_to is null or valid_from is null or valid_to >= valid_from)
);

create table public.legal_relations (
  id uuid primary key default gen_random_uuid(),
  source_unit_id uuid not null references public.legal_units(id) on delete cascade,
  target_unit_id uuid references public.legal_units(id) on delete set null,
  target_document_id uuid references public.legal_documents(id) on delete set null,
  relation_type text not null check (relation_type in (
    'CITES','MODIFIES','REPEALS','SUPERSEDES','INTERPRETS','CONCORDANT_WITH','REFERENCES')),
  citation_text text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  check (num_nonnulls(target_unit_id, target_document_id) <= 1),
  check (target_unit_id is not null or target_document_id is not null or citation_text is not null)
);

create index legal_documents_type_rama_idx on public.legal_documents (document_type, rama);
create index legal_documents_expediente_idx on public.legal_documents (expediente) where expediente is not null;
create index legal_documents_number_idx on public.legal_documents (number) where number is not null;
create index legal_documents_resolution_date_idx on public.legal_documents (resolution_date desc) where resolution_date is not null;
create index legal_documents_binding_idx on public.legal_documents (precedent_binding) where precedent_binding is true;
create index legal_units_document_type_number_idx on public.legal_units (document_id, unit_type, unit_number);
create index legal_units_type_number_idx on public.legal_units (unit_type, unit_number);
create index legal_units_parent_idx on public.legal_units (parent_unit_id) where parent_unit_id is not null;
create index legal_units_search_idx on public.legal_units using gin (search_tsv);
create index legal_units_embedding_idx on public.legal_units using hnsw (embedding extensions.vector_cosine_ops)
  where embedding is not null;
create index legal_relations_target_unit_idx on public.legal_relations (target_unit_id) where target_unit_id is not null;
create index legal_relations_target_document_idx on public.legal_relations (target_document_id) where target_document_id is not null;

alter table public.legal_documents enable row level security;
alter table public.legal_units enable row level security;
alter table public.legal_relations enable row level security;
alter table public.legal_ingestion_runs enable row level security;
revoke all on public.legal_documents, public.legal_units, public.legal_relations,
  public.legal_ingestion_runs from anon, authenticated;

-- Search contract for the server-side pilot. No public Data API execution grant.
create function public.match_legal_knowledge_v2(
  query_embedding extensions.vector(1536),
  query_text text default null,
  match_count integer default 10,
  filter_document_type text default null,
  filter_rama text default null,
  filter_expediente text default null
)
returns table (
  unit_id uuid, document_id uuid, document_title text, document_type text,
  unit_type text, unit_number text, heading text, excerpt text,
  page_start integer, page_end integer, similarity double precision,
  lexical_score real, official_url text
)
language sql stable security invoker
set search_path = pg_catalog, extensions
as $$
  with vector_candidates as (
    select u.id
    from public.legal_units u
    join public.legal_documents d on d.id = u.document_id
    where d.ingestion_status in ('ready','ready_with_warnings')
      and u.is_current and u.embedding is not null
      and (filter_document_type is null or d.document_type = filter_document_type)
      and (filter_rama is null or d.rama = filter_rama)
      and (filter_expediente is null or d.expediente = filter_expediente)
    order by u.embedding <=> query_embedding
    limit least(greatest(match_count, 1) * 8, 400)
  ), lexical_candidates as (
    select u.id
    from public.legal_units u
    join public.legal_documents d on d.id = u.document_id
    where coalesce(query_text, '') <> ''
      and d.ingestion_status in ('ready','ready_with_warnings')
      and u.is_current and u.embedding is not null
      and u.search_tsv @@ plainto_tsquery('spanish'::regconfig, query_text)
      and (filter_document_type is null or d.document_type = filter_document_type)
      and (filter_rama is null or d.rama = filter_rama)
      and (filter_expediente is null or d.expediente = filter_expediente)
    order by ts_rank_cd(u.search_tsv, plainto_tsquery('spanish'::regconfig, query_text)) desc
    limit least(greatest(match_count, 1) * 8, 400)
  ), candidates as (
    select id from vector_candidates union select id from lexical_candidates
  )
  select u.id, d.id, d.title, d.document_type, u.unit_type, u.unit_number,
         u.heading, u.excerpt, u.page_start, u.page_end,
         (1 - (u.embedding <=> query_embedding))::double precision,
         ts_rank_cd(u.search_tsv, plainto_tsquery('spanish'::regconfig, coalesce(query_text,''))),
         d.official_url
  from candidates c
  join public.legal_units u on u.id = c.id
  join public.legal_documents d on d.id = u.document_id
  order by (u.embedding <=> query_embedding) -
    0.05 * ts_rank_cd(u.search_tsv, plainto_tsquery('spanish'::regconfig, coalesce(query_text,'')))
  limit least(greatest(match_count, 1), 50)
$$;
revoke all on function public.match_legal_knowledge_v2(
  extensions.vector, text, integer, text, text, text) from public, anon, authenticated;
grant execute on function public.match_legal_knowledge_v2(
  extensions.vector, text, integer, text, text, text) to service_role;
