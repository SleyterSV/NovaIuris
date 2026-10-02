# Production gap map — Bloque 9.5

Estado observado antes de modificar implementación. Target: producción controlada/beta, una instancia activa.

| Area | Current state | Risk | Blocks controlled production? | Action |
|---|---|---|---|---|
| Auth | No hay middleware de identidad validada en Flask ni Supabase Auth integrado en API. | Acceso anónimo privado. | Sí | Validar Bearer Supabase; identidad fake solo en tests. |
| Ownership | `case_id` del cliente identifica casos; no hay owner canónico. | IDOR transversal. | Sí | Registro persistente case→owner y autorización en cada ruta. |
| Tasks | `TaskManager` singleton en memoria; status/cancel por UUID. | IDOR y pérdida al restart. | Sí | Owner, repository persistente, transiciones e interrupción. |
| Documents | Corpus SQLite filtra por case_id, no por owner. | Filtración si se conoce case_id. | Sí | Boundary de case ownership antes de corpus y owner persistente. |
| Provider retries | Utilidad genérica reintenta `Exception`; otros clientes tienen políticas propias. | Reintentos de errores permanentes y gasto. | Sí | Limitar errores transitorios, intentos y backoff. |
| Timeouts | Algunos calls y subpipelines tienen timeout; no hay deadline global. | Jobs prolongados. | Sí, si calls sin límite | Verificar calls canónicos y documentar límite. |
| Cost guards | Hay límites de documentos y búsqueda configurables sin topes globales. | Configuración extrema o abuso. | Sí | Rangos y tareas activas por usuario. |
| Legacy endpoints | Simulation/graph/report/export expuestos. | API antigua, probabilidad numérica y errores sensibles. | Sí | Bloquear rutas no canónicas en producción. |
| Logs | Request ID; legacy loggea excepciones, algunos paths podrían incluir contenido. | PII y secretos. | Sí | Campos seguros y error público uniforme. |
| Secrets | `.env` local, variables privadas en backend; sin escaneo final aún. | Exposición accidental. | Sí | Escaneo sin valores y validación de configuración. |
| CORS | Orígenes de localhost por defecto. | Config producción incorrecta. | Sí | Orígenes explícitos y sin wildcard. |
| Rate limiting | Limitador local por IP para algunas rutas POST. | Abuso entre usuarios o instancias. | Sí | Aplicar a rutas caras y por identidad; documentar límite local. |
| Uploads | Límites y validación parcial existentes. | Parser, payload o coste excesivo. | Sí | Verificar MIME, tamaños y conteo. |
| Temporary files | Staging con edad configurable. | Retención indefinida o borrado inseguro. | Parcial | Documentar y revisar limpieza. |
| Case Corpus | SQLite local con case/doc/chunk sin owner. | Acceso cruzado y pérdida si disco efímero. | Sí | Owner boundary y volumen persistente. |
| Health | `/health` responde sin provider calls. | No distingue readiness. | No | Agregar `/ready` ligero. |
| Provider health | No hay smoke controlado. | Fallo real no detectado. | Antes de release | Harness opt-in y dry run. |
| CI | Sin SQL/migrations encontrados en inventario inicial. | Gates incompletos. | Parcial | Revisar CI y agregar pruebas. |
| Environment validation | Producción solo exige SECRET_KEY. | DEBUG, CORS y credenciales inseguras. | Sí | Fail-fast integral. |
| E2E | Tests funcionales existentes, sin usuarios A/B. | IDOR inadvertido. | Sí | Fixture de aislamiento multiusuario. |
| Data retention | Variables de retención; política integral sin documentar. | Datos acumulados. | Parcial | Política explícita sin borrado arbitrario. |

Estas filas son diagnóstico inicial y se actualizarán con los resultados verificados. No se han aplicado migraciones ni probado providers reales.

## Estado al cierre de implementación

| Area | Status | Evidence / next release step |
|---|---|---|
| Auth | CONTROLLED_BETA_LIMITATION | Backend valida Bearer con Supabase Auth; frontend propaga token en memoria. Falta conectar sign-in/refresh real antes de usuarios reales. |
| Ownership | CLOSED | Registro atómico case→owner y 404 seguro para acceso cruzado. |
| Tasks | CONTROLLED_BETA_LIMITATION | Journal SQLite y estado interrupted probados; ejecución sigue en threads de una instancia. |
| Documents | CLOSED | Acceso HTTP exige owner+case; tests A/B con ingesta sintética. |
| Provider retries | CONTROLLED_BETA_LIMITATION | Embeddings limitados a transitorios y hasta tres intentos; cliente LLM tiene timeout/retry acotado. Otros SDK internos requieren observación en release. |
| Timeouts | CONTROLLED_BETA_LIMITATION | Auth/LLM/embedding y subpipelines con límites; no existe deadline forzoso global del task. |
| Cost guards | CLOSED | Bounds de producción, tamaño/contador de uploads, tareas activas y rate limit local. |
| Legacy endpoints | CLOSED | 410 en producción para Graph/Simulation/Report/Export y Search síncrono. |
| Logs | CLOSED | Request ID, hash truncado, endpoint/status/duración; sin contenido jurídico en nuevos logs. |
| Secrets | CLOSED | Escaneo local de patrones sin coincidencias en archivos versionables; secrets reales no verificados en entorno runtime. |
| CORS | CLOSED | Orígenes HTTPS explícitos, preflight sin Bearer, test de origin denegado. |
| Rate limiting | CONTROLLED_BETA_LIMITATION | Creaciones caras limitadas por usuario en memoria; requiere limiter compartido para scale-out. |
| Uploads | CLOSED | Límites de servidor y parser/MIME verificados por tests existentes. |
| Temporary files | CLOSED | Cleanup acotado por prefijo, edad y no symlink; staging termina tras ingesta. |
| Case Corpus | CONTROLLED_BETA_LIMITATION | SQLite requiere volumen privado/durable; datos históricos sin owner no se reclaman automáticamente. |
| Health | CLOSED | `/health` sin provider calls. |
| Provider health | PENDING_RUNTIME_VALIDATION | Harness dry-run probado; smoke real requiere opt-in de release. |
| CI | CLOSED | Tests/compile/build y smoke dry-run sin secrets. |
| Environment validation | CLOSED | Startup production fail-fast con límites/secret/CORS/paths/providers. |
| E2E | CLOSED | Tests A/B de task, cancel, Court reuse, documento y task de ingesta. |
| Data retention | DEFERRED_TO_RELEASE | No hay purga del corpus por lectura; calendario de retención y borrado integral requieren decisión operativa. |
| RPC/RLS | PENDING_RUNTIME_VALIDATION | No hay SQL local de RPC ni políticas verificables; confirmar en Supabase autorizado. |
