-- Deterministic local fixtures exercise retrieval ranking/filter mechanics.
-- These do not replace review against production corpus or real question embeddings.
begin;
select plan(7);

insert into public.legal_documents (
  document_hash, title, document_type, number, expediente, court,
  source_file_name, source_format, parser_version, ingestion_status,
  extraction_quality
) values
  (repeat('a', 64), 'Reglamento de prueba 006-2026-JUS', 'regulation',
   '006-2026-JUS', null, null, 'fixture-regulation.pdf', 'pdf', 'test.v1', 'ready', 'high'),
  (repeat('b', 64), 'Resolución de prueba 04810-2024-PA/TC', 'order',
   null, '04810-2024-PA/TC', 'Tribunal Constitucional', 'fixture-order.pdf', 'pdf', 'test.v1', 'ready', 'high');

insert into public.legal_units (
  document_id, unit_type, unit_number, sequence, page_start, page_end,
  text, normalized_text, search_text, excerpt, content_hash, embedding
)
select d.id, fixture.unit_type, fixture.unit_number, fixture.sequence,
       fixture.page_start, fixture.page_end, fixture.body, fixture.body,
       fixture.search_text, fixture.body,
       md5(d.id::text || fixture.sequence::text) || md5(fixture.body),
       ('[' || fixture.vector_first::text || ',' ||
          array_to_string(array_fill(0::real, array[1535]), ',') || ']')::extensions.vector
from public.legal_documents d
cross join (values
  ('article'::text, '2'::text, 1, null::integer, null::integer,
   'Publicación del texto normativo.', 'Texto normativo y publicación de la ley.', 0::real),
  ('article'::text, '3'::text, 2, null::integer, null::integer,
   'El Texto Único Ordenado de la Ley 27444 debe publicarse en el diario oficial.',
   'Texto Único Ordenado Ley 27444 publicación diario oficial.', 1::real)
) as fixture(unit_type, unit_number, sequence, page_start, page_end, body, search_text, vector_first)
where d.number = '006-2026-JUS'
union all
select d.id, fixture.unit_type, null, fixture.sequence,
       fixture.page_start, fixture.page_end, fixture.body, fixture.body,
       fixture.search_text, fixture.body,
       md5(d.id::text || fixture.sequence::text) || md5(fixture.body),
       ('[1,' || array_to_string(array_fill(0::real, array[1535]), ',') || ']')::extensions.vector
from public.legal_documents d
cross join (values
  ('foundation'::text, 1, null::integer, null::integer,
   'La causa se evaluó sin audiencia por la documentación incorporada.',
   'Fundamento razones por qué no se realizó audiencia Tribunal Constitucional.'),
  ('decision'::text, 2, 3, 3,
   'El Tribunal Constitucional declaró fundada la demanda.',
   'Decisión del Tribunal Constitucional declarar fundada la demanda.'),
  ('fact'::text, 3, null::integer, null::integer, 'Hecho procesal de prueba 3.', 'Tribunal Constitucional expediente hechos.'),
  ('fact'::text, 4, null::integer, null::integer, 'Hecho procesal de prueba 4.', 'Tribunal Constitucional expediente hechos.'),
  ('fact'::text, 5, null::integer, null::integer, 'Hecho procesal de prueba 5.', 'Tribunal Constitucional expediente hechos.'),
  ('fact'::text, 6, null::integer, null::integer, 'Hecho procesal de prueba 6.', 'Tribunal Constitucional expediente hechos.'),
  ('fact'::text, 7, null::integer, null::integer, 'Hecho procesal de prueba 7.', 'Tribunal Constitucional expediente hechos.'),
  ('fact'::text, 8, null::integer, null::integer, 'Hecho procesal de prueba 8.', 'Tribunal Constitucional expediente hechos.'),
  ('fact'::text, 9, null::integer, null::integer, 'Hecho procesal de prueba 9.', 'Tribunal Constitucional expediente hechos.'),
  ('fact'::text, 10, null::integer, null::integer, 'Hecho procesal de prueba 10.', 'Tribunal Constitucional expediente hechos.')
) as fixture(unit_type, sequence, page_start, page_end, body, search_text)
where d.expediente = '04810-2024-PA/TC';

select ok(passed, check_name)
from (
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
 ) checks
order by check_name;
select * from finish();
rollback;
