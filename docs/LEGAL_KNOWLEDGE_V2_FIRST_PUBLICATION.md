# Legal Knowledge V2 — primera publicación manual (bloque 10.4B-2A)

**Estado:** bloque 10.4B-2 cerrado. La primera carga manual publicó 2 documentos, 15 unidades, 0 relaciones y 2 runs; `decree` y `auto` devolvieron `ALREADY_PRESENT_AND_IDENTICAL`. Las cuatro consultas de retrieval posteriores a la corrección fueron ejecutadas manualmente y calificadas GOOD. Codex no ejecutó la publicación ni las consultas con embeddings reales.

## Alcance cerrado

La CLI acepta solo `decree` (Decreto Supremo 006-2026-JUS, 5 unidades: cuatro artículos y una disposición) y `auto` (Auto TC 04810-2024-PA/TC, 10 unidades). Las rutas a los originales y los hashes aprobados están fijados en la allowlist; un cambio de contenido, identidad, quality gate o cantidad de unidades detiene la publicación. `inspect` no abre la base ni llama al proveedor.

El texto vectorizado es el `search_text` contextual que construye el pipeline V2 para cada unidad. `EmbeddingService.generate_embeddings()` usa `text-embedding-3-small`; `embedding_batches()` agrupa hasta 32 unidades y exige 1536 dimensiones. `PublicationAdapter.prepare()` rechaza valores no numéricos, NaN e infinitos antes de publicar. La CLI no muestra vectores.

## Configuración en la sesión del usuario

Antes de ejecutar, el PowerShell que lanzará Python debe tener **ambas** variables de proceso `MYKE_LEGAL_DATABASE_URL` y `OPENAI_API_KEY`. No se deben copiar sus valores a comandos, documentación, Git o archivos `.env`. El modelo se fija a `text-embedding-3-small`; si `OPENAI_EMBEDDING_MODEL` está definido con otro valor, la CLI falla. La DSN debe identificar `emelxkoztshmzukydqzj` en el host (conexión directa) o usuario (pooler); la CLI no usa `SUPABASE_URL` ni `DATABASE_URL` como alternativa.

`preflight`, `counts`, `idempotency-check` y `publish` abren una conexión PostgreSQL solo cuando el usuario los ejecuta. Antes de publicar comprueban las cuatro tablas V2, la función `match_legal_knowledge_v2`, la extensión vector y `autocommit=False`. La lectura de idempotencia compara documento, estado de run, hashes, UUID, secuencia, tipo, número, páginas y dimensión de cada vector. `NOT_PRESENT` permite la primera publicación; `ALREADY_PRESENT_AND_IDENTICAL` impide repetir embeddings/inserts; `CONFLICT` exige investigación. No se hace una segunda publicación para probar idempotencia.

## Secuencia de la primera publicación manual (ya completada)

Ejecutar cada comando por separado. **Detenerse y revisar** cualquier código de salida distinto de cero, conteo inesperado o estado `CONFLICT`. La CLI imprime códigos de error genéricos para no revelar mensajes del proveedor o la base.

```powershell
cd D:\NovaIuris\backend
python -m app.legal_ingestion.publication_entrypoint preflight
python -m app.legal_ingestion.publication_entrypoint counts
python -m app.legal_ingestion.publication_entrypoint inspect decree
python -m app.legal_ingestion.publication_entrypoint publish decree
python -m app.legal_ingestion.publication_entrypoint counts
python -m app.legal_ingestion.publication_entrypoint idempotency-check decree
python -m app.legal_ingestion.publication_entrypoint inspect auto
python -m app.legal_ingestion.publication_entrypoint publish auto
python -m app.legal_ingestion.publication_entrypoint counts
python -m app.legal_ingestion.publication_entrypoint idempotency-check auto
```

Antes del primer `publish`, los conteos deben ser `0/0/0/0`. Después del decreto, comprobar **1 documento, 5 unidades** y un run completado antes de avanzar al auto. Después del auto, comprobar **2 documentos, 15 unidades**; relaciones solo si el parser entregó relaciones explícitas (en este piloto la CLI envía `relations=()`). Los runs reflejarán las publicaciones efectivas y cualquier fallo auditado por el adapter.

Los comandos `counts` e `idempotency-check` son de solo lectura. `publish` llama al `PublicationAdapter` existente, que inserta documento, unidades, relaciones explícitas y run en una transacción con commit/rollback. La CLI no modifica MYKE runtime, Auth, NovaSearch ni fuentes V1.

**La secuencia anterior es histórica y no debe repetirse ahora:** `preflight` exige la base vacía y `publish` rechaza un documento idéntico ya presente. En el cierre, Codex confirmó los conteos mediante SQL remoto de solo lectura.

## Prueba manual del RPC V2 (CLI read-only)

Desde el PowerShell que tiene `MYKE_LEGAL_DATABASE_URL` y `OPENAI_API_KEY` como variables de proceso:

```powershell
cd D:\NovaIuris\backend
python -m app.legal_ingestion.publication_entrypoint search "¿Qué aprueba el Decreto Supremo 006-2026-JUS?"
python -m app.legal_ingestion.publication_entrypoint search "¿Qué norma deroga la disposición única del Decreto Supremo 006-2026-JUS?" --top-k 5 --document-type regulation
python -m app.legal_ingestion.publication_entrypoint search "¿Por qué no todos los casos conocidos por el Tribunal Constitucional vía recurso de agravio constitucional requieren sentencia?" --top-k 5 --document-type order
python -m app.legal_ingestion.publication_entrypoint search "¿Qué resuelve el Auto TC 04810-2024-PA/TC sobre el recurso de agravio constitucional?" --top-k 5 --expediente 04810-2024-PA/TC
python -m app.legal_ingestion.publication_entrypoint search "¿Cuál es la diferencia entre la aprobación del TUO de la Ley del Procedimiento Administrativo General y los criterios del TC sobre el recurso de agravio constitucional?" --top-k 5 --json
```

`search` admite `--top-k` de 1 a 50 (predeterminado 5), `--document-type regulation|order`, `--rama`, `--expediente` y `--json`. Genera un embedding nuevo para la pregunta con `text-embedding-3-small`, valida 1536 valores numéricos finitos y ejecuta `public.match_legal_knowledge_v2` con `query_text` y filtros parametrizados. La conexión se marca `readonly=True` antes del primer SQL y se cierra con rollback. No muestra el vector ni las credenciales. Cada resultado muestra rank, documento, tipo/número/encabezado de unidad, páginas, similarity, lexical score, UUID, URL oficial si existe y excerpt limitado a 240 caracteres.

Evaluar top-1 y top-3, coherencia jurídica, scores y provenance de cada consulta antes de declarar GO para 10.5. La última consulta es de control para observar si la búsqueda distingue ambos temas; no presupone que una misma unidad responda a los dos.

## Cierre 10.4B-2: diagnóstico y corrección del retrieval

Los conteos comprobados por SQL de solo lectura antes de la corrección fueron **2 documentos / 15 unidades / 0 relaciones / 2 runs**. La unidad `decision` del Auto TC conserva el fallo (“Declarar IMPROCEDENTE el pedido de nulidad, entendido como aclaración”), página 3, `search_tsv` poblado y embedding de 1536 dimensiones. En la pregunta explícita sobre la decisión, el usuario midió **rank 6**, similarity **0.682114718972083**, lexical score **0.0**. No se requiere reparsing, reinserción ni regeneración de vectores.

### Causa léxica medida en PostgreSQL

El RPC aplicado usaba `plainto_tsquery('spanish', query_text)` para candidatos y `ts_rank_cd`. PostgreSQL convirtió la pregunta “¿Dónde debe publicarse el Texto Único Ordenado de la Ley 27444?” en ocho lexemas unidos por `AND`; produjo **0 matches y rank 0** en las 15 unidades. La pregunta completa sobre la decisión también produjo **0 matches y rank 0**. `websearch_to_tsquery` de esas preguntas sin operadores explícitos mantuvo la conjunción y también produjo **0 matches**. La columna generada **sí contiene datos**: `publicación` produjo 9 matches y rank máximo 0.4; `Texto Único Ordenado`, 5 matches y máximo 0.440952; `Tribunal Constitucional`, 10 matches y máximo 0.312937; `audiencia`, 6 matches; `decisión`, 2 matches. Un `to_tsquery` formado con los lexemas españoles unidos por `OR` produjo puntajes positivos en las preguntas largas. El texto de consulta llega al RPC desde la CLI como parámetro.

La causa es la exigencia de coincidencia de **todos** los términos de la pregunta natural dentro de una sola unidad, no un fallo de `search_tsv`, idioma, embeddings o publicación. El contexto documental repetido en `search_text` puede elevar el score parcial de varias unidades; por eso el nuevo aporte léxico al orden se limita a **0.01** unidades de distancia vectorial.

### Causa y regla de intención

La pregunta “cuál fue la decisión” describe el tipo de unidad, mientras el cuerpo real empieza “RESUELVE / Declarar IMPROCEDENTE…”. El vector de la decisión obtuvo 0.682114718972083 pero quedó sexto entre los diez del Auto. El ranking anterior carecía de una regla para una intención de tipo jurídico explícita. La corrección general reconoce `decisión`, `resolvió`, `resuelve`, `fallo` y `parte resolutiva` → `decision`; `fundamento`, `razón`, `razones` o `por qué` → `foundation`; `artículo` → `article`. Se comprobaron los patrones en PostgreSQL, incluido que “derecho fundamental” **no** activa `foundation`. No hay nombres de archivos, expedientes o IDs codificados en la regla.

La migración [20261008024534_legal_knowledge_v2_retrieval_hardening.sql](../supabase/migrations/20261008024534_legal_knowledge_v2_retrieval_hardening.sql) conserva firma, filtros, HNSW, RLS y permisos del RPC. Para full-text usa `websearch_to_tsquery` si la unidad coincide con la expresión completa; si no, usa lexemas españoles parciales unidos por `OR`. `lexical_score` reporta el rank real de la expresión elegida. **Orden final:** primero la clase de unidad pedida explícitamente, si existe; dentro de esa clase, distancia vectorial menos `0.01 * min(lexical_score, 1)`, luego similitud e ID para desempate. Sin intención explícita, prevalece el vector con ese pequeño componente léxico acotado. La prioridad de tipo es una regla de orden, no un boost numérico oculto.

Las [pruebas SQL de aceptación](../supabase/tests/legal_knowledge_v2_retrieval_acceptance.sql) usan vectores **ya publicados** para comprobar coincidencia léxica de pregunta larga, prioridad de `decision` y `foundation`, artículo 3, ranking sin intención, filtro de expediente y provenance de la decisión. Son de solo lectura y no sustituyen las cuatro preguntas reales con embeddings de consulta.

**Aplicación:** `supabase db push --linked --project-ref emelxkoztshmzukydqzj --skip-vault` con CLI 2.120.0, después de un `--dry-run` que enumeró **solo** `20261008024534_legal_knowledge_v2_retrieval_hardening.sql` (sin seeds ni roles). El historial remoto confirmó foundation y corrección aplicadas. El conector MCP había rechazado `apply_migration` por permisos; se usó el flujo soportado del CLI. Los conteos posteriores permanecieron **2/15/0/2**.

**Pruebas SQL del RPC:** antes de la corrección, seis pruebas dieron 3 PASS y 3 FAIL (`decision_intent`, `foundation_intent`, `long_question_lexical`). Después de agregar una prueba de cita/provenance, dieron **7/7 PASS**. Con un vector ya publicado de un fundamento, la pregunta Q3 devolvió `decision` primero, página 3 y `lexical_score=0.6`, incluso cuando ese vector favorecía otro fundamento. Con el vector ya publicado del artículo 3, Q4 conservó artículo 3 primero y `lexical_score=1.7`. Estos controles de ranking no generaron llamadas al proveedor; la validación posterior de Q1–Q4 con embeddings de pregunta reales se documenta a continuación.

### Validación manual final: antes y después

Los resultados **después** provienen de las cuatro consultas ejecutadas manualmente por el usuario con embeddings de pregunta reales. Codex verificó por SQL de solo lectura la migración, los conteos y los campos de procedencia; no volvió a generar embeddings ni a ejecutar el RPC con esas preguntas.

| Consulta | Antes de la corrección | Después de la corrección | Evaluación |
| --- | --- | --- | --- |
| Q1: norma que aprueba el TUO y dispone su publicación | Artículos relevantes entre los tres primeros; `lexical_score=0` en las consultas previas. | Artículos relevantes entre los tres primeros; scores léxicos positivos. | GOOD |
| Q2: por qué no todo RAC requiere audiencia | Fundamento 7 en rank 1; `lexical_score=0` en las consultas previas. | Fundamento 7 en rank 1; score léxico positivo. | GOOD |
| Q3: decisión del TC en el expediente 04810-2024-PA/TC | `decision` en rank 6; similarity `0.682114718972083`; `lexical_score=0`. | `decision` en rank 1, página 3; `lexical_score=0.6`. | GOOD |
| Q4: dónde publicar el TUO de la Ley 27444 | Artículo 3 «Publicación» en rank 1; `lexical_score=0` en las consultas previas. | Artículo 3 «Publicación» en rank 1; similarity ≈ `0.713`; `lexical_score=1.7`. | GOOD |

Los valores exactos de similarity y lexical score de Q1 y Q2 posteriores no se conservaron en el reporte manual; solo se confirmó que sus scores léxicos son positivos. La comparación anterior de Q1, Q2 y Q4 refleja los resultados reales previos comunicados durante el bloque; no se atribuyen rangos o scores adicionales que no fueron registrados.

### Confirmación remota de cierre

El historial remoto de migraciones de **MYKE Legal** (`emelxkoztshmzukydqzj`) coincide con el local para `20261006162217` (foundation) y `20261008024534` (retrieval hardening). SQL de solo lectura confirmó `legal_documents=2`, `legal_units=15`, `legal_relations=0` y `legal_ingestion_runs=2`. Son los mismos conteos de la primera publicación; durante el cierre no hubo inserts ni regeneración de los vectores del corpus.

Las 15 unidades tienen embedding no nulo de dimensión 1536, identidad y hash de contenido; cinco pertenecen al Decreto Supremo 006-2026-JUS y diez al Auto TC 04810-2024-PA/TC. La unidad `decision` del Auto conserva `unit_id`, `document_id`, tipo `order`, página 3 y el texto del fallo. El artículo 3 «Publicación» conserva esos IDs, tipo `regulation`, número de artículo y heading. El DOCX del decreto no aporta paginación física confiable, por lo que sus campos de página son nulos; `official_url` es nulo en ambos documentos porque no se extrajo una URL oficial verificable. La cita futura debe usar los identificadores y metadatos presentes sin inventar página ni URL.

**Resultado:** primera publicación, embeddings 1536, idempotencia, retrieval vectorial, aporte léxico, intención `decision` y procedencia: PASS. **GO para el bloque 10.5** (comparación V1 vs V2). Este cierre no inicia 10.5 ni modifica el runtime.

Comandos empleados para la validación manual posterior a la migración (registro histórico; no es necesario repetirlos para este cierre):

```powershell
cd D:\NovaIuris\backend
python -m app.legal_ingestion.publication_entrypoint search "¿Qué norma aprueba el Texto Único Ordenado y qué dispone sobre su publicación?" --top-k 5 --json
python -m app.legal_ingestion.publication_entrypoint search "¿Por qué el Tribunal Constitucional señala que no todos los casos conocidos mediante recurso de agravio constitucional requieren audiencia?" --top-k 5 --json
python -m app.legal_ingestion.publication_entrypoint search "¿Cuál fue la decisión del Tribunal Constitucional en el expediente 04810-2024-PA/TC?" --top-k 10 --document-type order --expediente 04810-2024-PA/TC --json
python -m app.legal_ingestion.publication_entrypoint search "¿Dónde debe publicarse el Texto Único Ordenado de la Ley 27444?" --top-k 5 --json
```
