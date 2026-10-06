# Legal Knowledge V2: plan de migración

## Límites de este bloque

El proyecto Supabase MYKE Legal tiene la foundation V2 aplicada y permanece sin datos jurídicos. Este bloque no conecta el runtime, no carga la biblioteca, no copia usuarios y no cambia credenciales de `.env`. El Supabase anterior y V1 permanecen operativos. Mover la base de búsqueda no mueve Supabase Auth: usuarios, sesiones y login requieren un plan de corte separado.

## Secuencia propuesta

1. Conservar V1 y hacer inventario de documentos originales. V1 sirve para comparar cobertura y recuperar metadatos, no como fuente textual definitiva si existe el original.
2. Revisar el SQL versionado y aplicarlo **solo** al proyecto nuevo MYKE Legal, con respaldo y entorno identificados por el operador. Verificar extensión vector, cuatro tablas, RLS, índices y RPC. No aplicar a Fiscal.IA ni al proyecto V1.
3. Ejecutar dry-run local del piloto. Ejemplo desde `backend`: `python -m app.legal_ingestion.cli --dry-run "../raw_docs/CONSTITUCION POLITICA.docx" "../raw_docs/CODIGO CIVIL.docx"`. La salida contiene conteos, metadatos y advertencias, no texto completo.
4. Completar revisión humana de documentos `review_required`, especialmente extracción PDF, identidad de la resolución, precedente, colisiones de hash y unidades demasiado largas. Un adaptador de staging/publicación y pruebas de integración sobre el proyecto nuevo son trabajo posterior; **este bloque no inserta datos**.
5. Cargar un piloto pequeño desde documentos originales: Constitución, Código Civil, Código Procesal Civil, Código Tributario/SPIJ HTML, Ley General de Sociedades, Nueva Ley Procesal del Trabajo, sentencia TC, auto TC, casación Corte Suprema, precedente vinculante y documento de mala extracción. El `.doc` HTML se prueba con fixture sintético si no hay original local.
6. Comparar V1/V2 para búsquedas por artículo, número de expediente, conceptos y filtros; evaluar precisión, cobertura, citas, páginas y falsos positivos. Aprobar calidad antes de carga masiva.
7. Ingerir en lotes V2, luego incorporar dual-read con bandera futura `LEGAL_KNOWLEDGE_VERSION=v1|v2`, cambiar lectura tras verificación, estabilizar y congelar V1. La bandera no se activa aquí.

## Checklist previo a aplicar el esquema

- Confirmar que el destino CLI es el **nuevo** Supabase MYKE Legal y que el proyecto viejo no está enlazado.
- Revisar `supabase/migrations/20261006162217_legal_knowledge_v2_foundation.sql`; aplicar con procedimiento de migraciones del proyecto nuevo y verificar que ninguna tabla V1 se modifica.
- Verificar `vector(1536)`, configuración PostgreSQL `spanish`, índices GIN/HNSW, RLS habilitado y ausencia de permisos frontend sobre tablas V2.
- Mantener `SUPABASE_URL`, `SUPABASE_KEY`, `VITE_SUPABASE_URL` y `VITE_SUPABASE_ANON_KEY` actuales. Guardar cualquier service role del nuevo proyecto solo en configuración segura del backend, en una fase posterior.
- No conectar SearchService/Retriever/AnswerService hasta que el piloto y el plan de Auth estén aprobados.

## Resultado del bloque 10.4A (2026-10-06)

- Destino confirmado por `supabase projects list` y `supabase/.temp/project-ref`: **MYKE Legal**, ref `emelxkoztshmzukydqzj`, vinculado.
- Historial remoto inicial vacío. `supabase db push --dry-run --linked` enumeró únicamente `20261006162217_legal_knowledge_v2_foundation.sql`; se aplicó con `supabase db push --linked --yes`. La versión `20261006162217` figura en `supabase_migrations.schema_migrations`. No fue necesaria una migration correctiva.
- Consultas de solo lectura al PostgreSQL remoto 17.11 confirmaron la extensión `vector` 0.8.2 en `extensions`; `public.legal_units.embedding` es `vector(1536)`.
- Existen `public.legal_documents`, `public.legal_units`, `public.legal_relations` y `public.legal_ingestion_runs`, con columnas, PK, FK, UNIQUE y CHECK de la migration. `legal_units.parent_unit_id` referencia la propia tabla. `legal_documents.ingestion_run_id` referencia los runs.
- `pg_indexes` confirmó índices de filtros y metadatos documentales, `legal_units_document_type_number_idx`, `legal_units_type_number_idx`, los índices únicos de hash y secuencia, `legal_units_search_idx` GIN y `legal_units_embedding_idx` HNSW. GIN y HNSW están válidos y listos; HNSW usa `vector_cosine_ops`.
- `legal_units.search_tsv` es una columna `tsvector` generada y almacenada con `to_tsvector('spanish', coalesce(search_text,''))`. La configuración `spanish` existe en PostgreSQL.
- RLS está habilitado en las cuatro tablas, sin policies. `anon` y `authenticated` no tienen `SELECT` ni `INSERT` sobre ellas.
- El RPC real es `public.match_legal_knowledge_v2(query_embedding vector, query_text text DEFAULT NULL, match_count integer DEFAULT 10, filter_document_type text DEFAULT NULL, filter_rama text DEFAULT NULL, filter_expediente text DEFAULT NULL)`. PostgreSQL expone el argumento como `vector` en la firma de función; la migration lo declara `vector(1536)`. Devuelve `TABLE(unit_id uuid, document_id uuid, document_title text, document_type text, unit_type text, unit_number text, heading text, excerpt text, page_start integer, page_end integer, similarity double precision, lexical_score real, official_url text)`. Es `SECURITY INVOKER`; `service_role` puede ejecutarlo y `anon`/`authenticated` no. Una llamada con vector cero de 1536 dimensiones devolvió 0 filas, sin insertar datos.
- Conteos reales: `legal_documents=0`, `legal_units=0`, `legal_relations=0`, `legal_ingestion_runs=0`. `public.legal_knowledge`, `public.base_legal` y `public.expedientes_chunks` están ausentes.

**Estado: GO para iniciar el bloque 10.4B** (dry-run y carga piloto), en una fase separada. Ningún documento ni embedding se cargó en 10.4A.
