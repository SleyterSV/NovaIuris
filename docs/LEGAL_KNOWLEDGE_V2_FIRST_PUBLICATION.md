# Legal Knowledge V2 — primera publicación manual (bloque 10.4B-2A)

**Estado:** la CLI de publicación se preparó y probó offline en 10.4B-2A. El usuario confirmó posteriormente la primera carga manual: 2 documentos, 15 unidades, 0 relaciones y 2 runs; `decree` y `auto` devolvieron `ALREADY_PRESENT_AND_IDENTICAL`. Codex no ejecutó esa publicación. El retrieval real sigue pendiente de prueba manual.

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

**La secuencia anterior es histórica y no debe repetirse ahora:** `preflight` exige la base vacía y `publish` rechaza un documento idéntico ya presente. Los conteos de la carga fueron comunicados por el usuario; Codex no los consultó en esta sesión.

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
