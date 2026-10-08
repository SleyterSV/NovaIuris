-- Read-only post-migration regression checks using already-published pilot vectors.
-- These exercise ranking mechanics; real question embeddings must be reviewed separately.
with decree_article as (
  select u.embedding
  from public.legal_units u join public.legal_documents d on d.id=u.document_id
  where d.number='006-2026-JUS' and u.unit_type='article' and u.unit_number='3'
), case_foundation as (
  select u.embedding
  from public.legal_units u join public.legal_documents d on d.id=u.document_id
  where d.expediente='04810-2024-PA/TC' and u.unit_type='foundation'
  order by u.sequence limit 1
), case_decision as (
  select u.embedding
  from public.legal_units u join public.legal_documents d on d.id=u.document_id
  where d.expediente='04810-2024-PA/TC' and u.unit_type='decision'
)
select 'long_question_lexical' as check_name,
  (select count(*) > 0 from decree_article e,
   lateral public.match_legal_knowledge_v2(e.embedding,
     '¿Dónde debe publicarse el Texto Único Ordenado de la Ley 27444?',
     5, 'regulation', null, null) r where r.lexical_score > 0) as passed
union all
select 'decision_intent',
  (select r.unit_type='decision' from case_foundation e,
   lateral public.match_legal_knowledge_v2(e.embedding,
     '¿Cuál fue la decisión del Tribunal Constitucional?',
     10, 'order', null, '04810-2024-PA/TC') r limit 1)
union all
select 'foundation_intent',
  (select r.unit_type='foundation' from case_decision e,
   lateral public.match_legal_knowledge_v2(e.embedding,
     '¿Por qué no se realizó audiencia?',
     10, 'order', null, '04810-2024-PA/TC') r limit 1)
union all
select 'article_three_still_first',
  (select r.unit_type='article' and r.unit_number='3' from decree_article e,
   lateral public.match_legal_knowledge_v2(e.embedding,
     '¿Dónde debe publicarse el Texto Único Ordenado de la Ley 27444?',
     5, 'regulation', null, null) r limit 1)
union all
select 'neutral_query_keeps_vector_first',
  (select r.unit_type='article' and r.unit_number='3' from decree_article e,
   lateral public.match_legal_knowledge_v2(e.embedding,
     'Texto Único Ordenado de la Ley 27444',
     5, 'regulation', null, null) r limit 1)
union all
select 'expediente_filter_preserved',
  (select count(*)=10 from case_decision e,
   lateral public.match_legal_knowledge_v2(e.embedding,
     'Tribunal Constitucional',
     10, 'order', null, '04810-2024-PA/TC') r
   where r.document_type='order')
union all
select 'decision_citation_provenance',
  (select r.unit_id is not null and r.document_id is not null
          and r.document_title is not null and r.document_type='order'
          and r.unit_type='decision' and r.page_start=3 and r.page_end=3
   from case_foundation e,
   lateral public.match_legal_knowledge_v2(e.embedding,
     '¿Cuál fue la decisión del Tribunal Constitucional?',
     10, 'order', null, '04810-2024-PA/TC') r limit 1)
order by check_name;
