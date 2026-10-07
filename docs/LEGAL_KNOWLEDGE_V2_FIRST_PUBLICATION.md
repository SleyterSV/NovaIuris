# Legal Knowledge V2 — primera publicación manual (bloque 10.4B-2A)

**Estado:** CLI preparada y probada offline. Este bloque no ejecutó conexiones productivas, embeddings reales ni inserts. Los resultados de publicación y retrieval pertenecen al bloque 10.4B-2 y deben documentarse después de su ejecución manual.

## Alcance cerrado

La CLI acepta solo `decree` (Decreto Supremo 006-2026-JUS, 5 unidades: cuatro artículos y una disposición) y `auto` (Auto TC 04810-2024-PA/TC, 10 unidades). Las rutas a los originales y los hashes aprobados están fijados en la allowlist; un cambio de contenido, identidad, quality gate o cantidad de unidades detiene la publicación. `inspect` no abre la base ni llama al proveedor.

El texto vectorizado es el `search_text` contextual que construye el pipeline V2 para cada unidad. `EmbeddingService.generate_embeddings()` usa `text-embedding-3-small`; `embedding_batches()` agrupa hasta 32 unidades y exige 1536 dimensiones. `PublicationAdapter.prepare()` rechaza valores no numéricos, NaN e infinitos antes de publicar. La CLI no muestra vectores.

## Configuración en la sesión del usuario

Antes de ejecutar, el PowerShell que lanzará Python debe tener **ambas** variables de proceso `MYKE_LEGAL_DATABASE_URL` y `OPENAI_API_KEY`. No se deben copiar sus valores a comandos, documentación, Git o archivos `.env`. El modelo se fija a `text-embedding-3-small`; si `OPENAI_EMBEDDING_MODEL` está definido con otro valor, la CLI falla. La DSN debe identificar `emelxkoztshmzukydqzj` en el host (conexión directa) o usuario (pooler); la CLI no usa `SUPABASE_URL` ni `DATABASE_URL` como alternativa.

`preflight`, `counts`, `idempotency-check` y `publish` abren una conexión PostgreSQL solo cuando el usuario los ejecuta. Antes de publicar comprueban las cuatro tablas V2, la función `match_legal_knowledge_v2`, la extensión vector y `autocommit=False`. La lectura de idempotencia compara documento, estado de run, hashes, UUID, secuencia, tipo, número, páginas y dimensión de cada vector. `NOT_PRESENT` permite la primera publicación; `ALREADY_PRESENT_AND_IDENTICAL` impide repetir embeddings/inserts; `CONFLICT` exige investigación. No se hace una segunda publicación para probar idempotencia.

## Secuencia manual desde el PowerShell con credenciales

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

**La secuencia anterior no sustituye la validación SQL de filas, la RPC vectorial real, retrieval y provenance del bloque 10.4B-2.** No declarar GO para 10.5 hasta que esas verificaciones se completen y se documenten con resultados reales.
