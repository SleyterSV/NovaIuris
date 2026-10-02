# Bloque 9.5 — runtime para beta controlada

## Target y límites

Una instancia activa de Flask, con volumen local persistente y privado para `CASE_CORPUS_DB_PATH` y `TASK_DB_PATH`, más Supabase Auth y los providers configurados. No hay cola distribuida, alta disponibilidad, migración de jobs entre workers, multi-región ni garantía de cero interrupciones. `DISTRIBUTED_WORKER_QUEUE_REQUIRED_FOR_SCALE`. La metadata persistida no ejecuta jobs después de un reinicio.

## Threat model y auth

Las rutas privadas `/api/*` requieren `Authorization: Bearer <access token>` en `APP_ENV=production`. El backend consulta `/auth/v1/user` de Supabase Auth con timeout y usa exclusivamente el `id` validado. El `user_id` o `owner_id` recibido en JSON no confiere identidad. Desarrollo/test tienen una identidad local fija; los tests de producción inyectan un verificador fake. El token es Bearer, no cookie de auth: no se requiere CSRF para este mecanismo. En producción el frontend debe conectar una sesión Supabase Auth real a `setAccessToken` y refrescarla; esa experiencia de sign-in aún no está implementada.

## Ownership e aislamiento

`case_owners` vincula `case_id` a `owner_id`. La reclamación es atómica y los expedientes documentales previos sin owner permanecen inaccesibles hasta migración explícita. Las rutas Case, Court y Documents verifican ownership antes de usar el corpus. Search, Case y Court vinculan la tarea al owner. Status/cancel comparan owner; el Court reuse exige owner, case, texto, documentos y resultado válido. El corpus local almacena documentos y chunks por case; el acceso HTTP exige owner+case antes de consultar document ID. La identidad no se toma del frontend. No hay `owner_id` embebido en cada Source privada: la barrera es el repository/API context. Los servicios internos que accedan al corpus deben mantenerse detrás de esta barrera.

## Persistencia y estados

`runtime_tasks` y `document_runtime_tasks` son journals SQLite con metadata, estado y resultado limitado (8 MiB para tarea general, 1 MiB para ingesta). Se guardan en volumen privado. Una nueva instancia marca `pending`/`processing` o `queued`/`running` como `interrupted`, con mensaje público para volver a ejecutar. Estados terminales no retornan a ejecución. La cancelación evita que se publique un resultado posterior, aunque una llamada externa en curso puede terminar. El diario no es una cola; nunca iniciar dos instancias contra el mismo volumen.

## Providers, costos y timeouts

OpenAI embedding usa hasta tres intentos totales (dos reintentos), solo para timeout, conexión, 408/409/429 y 5xx temporales; verifica cancelación antes del siguiente intento y limita el backoff. Su SDK no agrega reintentos internos. El cliente LLM tiene timeout configurable, por defecto 60 s, y hasta dos reintentos del SDK. Graph/Simulation tienen timeout por subpipeline. No existe deadline total que termine forzosamente todos los threads; este límite impide afirmar protección completa ante un provider colgado fuera de los clientes auditados. Los límites de búsquedas, fuentes, contexto, archivos, tamaño, timeout y tareas activas se validan al iniciar producción. El rate limiter por identidad se aplica a creación de Search/Case/Court e ingesta; es local a la instancia. No hay pricing monetario calculado ni circuit breaker. Contadores y duraciones de los pipelines existentes son metadata de uso, no facturación.

## Uploads, paths y XSS

Se aplican tamaños por archivo/request/caso y número de archivos en servidor. El parser canónico acepta PDF, DOCX y TXT; confirma cabecera PDF, contenedor DOCX y rechaza `.doc`. Los nombres de archivo se normalizan y el staging se crea en un directorio propio; la limpieza de staging comprueba prefijo, tipo directorio, edad y evita symlinks. El render Markdown usa `html: false`; la normalización de fuentes solo admite `http`/`https` para URL oficiales almacenadas. No se construyen URL oficiales desde texto jurídico.

## Configuración, rutas y observabilidad

`APP_ENV` admite `development`, `test`, `production`. Producción falla al iniciar si falta secret fuerte, URL HTTPS de Supabase, clave publicable, claves privadas de providers, paths de DB, CORS HTTPS explícito o si DEBUG/rate limit son inseguros; valida rangos de costo. CORS solo permite los orígenes listados; el preflight OPTIONS no exige Bearer. `/health` confirma proceso; `/ready` confirma acceso local al journal de ownership sin llamar providers. Logs de HTTP: `event`, `request_id`, hash truncado de user ID, endpoint, método, status y duración. Nunca registrar textos de caso, documentos, prompts, respuestas, extracts o keys. Los errores públicos usan códigos estables y mensajes seguros. Las rutas legacy de Graph/Simulation/Report/Export y `/api/search` síncrono devuelven 410 en producción antes de ejecutar lógica. Se conservan en desarrollo para compatibilidad antigua.

## Rutas

| Route | Status in production |
|---|---|
| `/api/search/tasks`, `/api/search/tasks/<id>`, cancel | CANONICAL |
| `/api/case`, `/api/case/tasks`, `/api/tasks/<id>`, cancel | CANONICAL |
| `/api/novacourt/analyze`, `/api/novacourt/results/<id>` | CANONICAL |
| `/api/cases/<id>/documents`, document tasks/chunks | CANONICAL |
| `/api/graph/*`, `/api/simulation/*`, `/api/report/*`, `/api/export/*` | PRODUCTION_DISABLED |
| `/api/search` síncrono | PRODUCTION_DISABLED |

## Datos, DB, CI y release

La migración SQLite versionada describe las tres tablas nuevas. No se altera ninguna tabla histórica ni se aplica SQL en Supabase. La definición de `match_legal_knowledge` sigue ausente del repositorio: `RUNTIME_RPC_SIGNATURE_VALIDATION_PENDING`; no se infiere firma SQL. Las tablas legales de Supabase y sus políticas RLS no pudieron verificarse desde este entorno: `RLS_RUNTIME_VALIDATION_PENDING`. Los datos del corpus no se borran por edad en el primer acceso. Staging antiguo se limpia de forma acotada; tasks/results y corpus requieren eliminación explícita del operador. El borrado de caso completo, incluida toda referencia, sigue pendiente. CI usa fakes, compileall, tests y smoke dry-run; no necesita secretos. El smoke real puede generar costo y exige `RUN_PROVIDER_SMOKE=1`, `APP_ENV=production` y credenciales; nunca se ejecuta en suite normal.

## Limitaciones que impiden afirmar producción plena

Frontend sin flujo de inicio/refresco de sesión Supabase; comprobación de RPC y RLS pendiente; smoke real pendiente; almacenamiento SQLite requiere volumen durable y una sola instancia; falta deadline total de task y borrado integral de usuario/caso. Estos puntos deben resolverse o aceptarse explícitamente antes de abrir una beta real.
