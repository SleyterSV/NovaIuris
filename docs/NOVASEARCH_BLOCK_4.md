# NovaSearch — Bloque 4

## Flujo y contratos

El endpoint síncrono `POST /api/search` se conserva por compatibilidad. La interfaz usa `POST /api/search/tasks` y consulta secuencialmente `GET /api/search/tasks/<task_id>`; `POST .../<task_id>/cancel` solicita cancelación cooperativa. Las tareas usan el `TaskManager` existente, viven en memoria del proceso y no sobreviven un reinicio ni están compartidas entre workers.

El resultado mantiene `query`, `query_normalizada`, `analysis`, `answer`, `documents`, `sources`, `citations`, `warnings`, `result_status` y `metadata`. `metadata.counts` distingue fuentes recuperadas, priorizadas y citadas; `metadata.timings_ms` mide análisis, embedding, recuperación, fusión, reranking, contexto, respuesta, validación de citas y total.

## Pipeline, degradación y progreso

QueryAnalyzer normaliza solo espacios en blanco y conserva nombres, números, artículos y capitalización. La clasificación es determinista; keywords se limitan a términos presentes en la consulta. El pipeline es secuencial: análisis → un embedding de consulta → una consulta vectorial → fusión → reranking opcional → contexto trazable → respuesta → validación de marcadores Source/Citation. El frontend muestra los hitos confirmados por el backend, no un reloj ni una estimación de tiempo.

Una recuperación exitosa con cero filas devuelve `no_results` y no genera una respuesta sin fuentes. Un fallo del repositorio devuelve `SEARCH_FAILED`; los fallos de embedding y respuesta tienen códigos separados. El reranker conserva el orden base cuando su propio servicio agota sus reintentos y añade un warning. Una solicitud externa iniciada puede finalizar después de cancelar; el token evita empezar etapas posteriores.

## Filtros y fuentes

Los únicos filtros expuestos son `modulo` y `solo_vigentes`, que se pasan a `LegalRepository.semantic_search` y a los parámetros ya usados por el RPC `match_legal_knowledge`. Tipo de documento y fechas no aparecen en la interfaz ni se aceptan en el endpoint porque el repositorio actual no ofrece esos filtros. No se añadió una firma RPC alternativa ni se llamó a Supabase. La definición SQL local no está presente para verificar opciones adicionales.

Los documentos relacionados se presentan aparte de las fuentes citadas por la respuesta. Las citas usan el contrato de Bloque 3, el extracto exacto y los marcadores de fuente validados. Las menciones legales detectadas siguen siendo informativas y no se convierten automáticamente en citas. La UI no presenta similitud vectorial como porcentaje o confianza jurídica.

## Latencia y siguientes medidas

Cada búsqueda hace hasta una llamada de embedding, una consulta al repositorio, una llamada de reranking (con los reintentos configurados en ese servicio) y una llamada de respuesta. Sin resultados, el pipeline se detiene antes del reranking y del modelo de respuesta. No se modificaron modelos, prompts jurídicos, top-k, ni políticas de reintento. Los tiempos recogidos son instrumentación; no se midieron proveedores reales en este bloque.

Después de recoger métricas de runtime, revisar: la latencia/reintentos de cada proveedor; si la búsqueda vectorial ya incorpora filtros de vigencia correctamente; los límites de contexto del reranker; la reutilización segura de una única embedding por task; y una alternativa durable al manager en memoria si se escala a múltiples workers. No se debe paralelizar recuperación, ranking y respuesta, porque cada etapa depende de los resultados de la anterior.
