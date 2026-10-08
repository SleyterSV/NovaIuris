-- Keep the V2 RPC signature, security model, filters and vector index contract.
-- Natural-language questions often contain words absent from any single unit;
-- exact websearch matching is retained, with an OR-lexeme fallback per unit.
-- Explicit legal-unit intent is a ranking tier; vector distance still orders
-- units within a tier. The lexical contribution is capped at 0.01 so repeated
-- document context in search_tsv cannot overwhelm useful semantic ranking.
create or replace function public.match_legal_knowledge_v2(
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
  with query_features as (
    select
      websearch_to_tsquery('spanish'::regconfig, coalesce(query_text, '')) as exact_q,
      coalesce(
        to_tsquery('spanish'::regconfig, (
          select string_agg(quote_literal(lexeme), ' | ')
          from unnest(tsvector_to_array(
            to_tsvector('spanish'::regconfig, coalesce(query_text, '')))) as lexeme
        )),
        plainto_tsquery('spanish'::regconfig, coalesce(query_text, ''))
      ) as partial_q,
      case
        when lower(coalesce(query_text, '')) ~
          '(\mdecisi[oó]n\M|\mresolvi[oó]\M|\mresuelve\M|\mfallo\M|parte resolutiva)' then 'decision'
        when lower(coalesce(query_text, '')) ~
          '(\mfundamentos?\M|\mrazones\M|\mraz[oó]n\M|por qu[eé])' then 'foundation'
        when lower(coalesce(query_text, '')) ~ '\mart[ií]culos?\M' then 'article'
        else null
      end as intended_unit_type
  ), vector_candidates as (
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
    cross join query_features q
    where d.ingestion_status in ('ready','ready_with_warnings')
      and u.is_current and u.embedding is not null
      and (u.search_tsv @@ q.exact_q or u.search_tsv @@ q.partial_q)
      and (filter_document_type is null or d.document_type = filter_document_type)
      and (filter_rama is null or d.rama = filter_rama)
      and (filter_expediente is null or d.expediente = filter_expediente)
    order by (case when u.search_tsv @@ q.exact_q
                   then ts_rank_cd(u.search_tsv, q.exact_q)
                   else ts_rank_cd(u.search_tsv, q.partial_q) end) desc
    limit least(greatest(match_count, 1) * 8, 400)
  ), candidates as (
    select id from vector_candidates union select id from lexical_candidates
  ), scored as (
    select u.id as unit_id, d.id as document_id, d.title as document_title,
           d.document_type, u.unit_type, u.unit_number, u.heading, u.excerpt,
           u.page_start, u.page_end,
           (1 - (u.embedding <=> query_embedding))::double precision as similarity,
           (case when u.search_tsv @@ q.exact_q
                 then ts_rank_cd(u.search_tsv, q.exact_q)
                 else ts_rank_cd(u.search_tsv, q.partial_q) end)::real as lexical_score,
           d.official_url, q.intended_unit_type
    from candidates c
    join public.legal_units u on u.id = c.id
    join public.legal_documents d on d.id = u.document_id
    cross join query_features q
  )
  select s.unit_id, s.document_id, s.document_title, s.document_type,
         s.unit_type, s.unit_number, s.heading, s.excerpt, s.page_start,
         s.page_end, s.similarity, s.lexical_score, s.official_url
  from scored s
  order by
    case when s.intended_unit_type is null then 0
         when s.unit_type = s.intended_unit_type then 0
         else 1 end,
    (1 - s.similarity) - 0.01 * least(s.lexical_score, 1),
    s.similarity desc, s.unit_id
  limit least(greatest(match_count, 1), 50)
$$;

revoke all on function public.match_legal_knowledge_v2(
  extensions.vector, text, integer, text, text, text) from public, anon, authenticated;
grant execute on function public.match_legal_knowledge_v2(
  extensions.vector, text, integer, text, text, text) to service_role;
