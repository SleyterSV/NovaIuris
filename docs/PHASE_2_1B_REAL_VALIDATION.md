# Fase 2.1B — validacion real y estado de cierre

## Resultado

**NO-GO — la seguridad de base de datos y la persistencia remota no se pudieron validar en esta maquina.** Se conecto el flujo de archivo privado al repositorio de servidor, se agrego recuperacion historica desde artifacts y se reforzaron pruebas deterministas. Estas pruebas no sustituyen una instancia Supabase/Postgres real.

## Entorno Supabase

- CLI instalado: Supabase `2.53.6`.
- Runtime solicitado: Supabase local.
- `docker version` reconoce el cliente Docker `29.8.0`, pero no puede conectar al daemon: `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`.
- `supabase status` informa que no puede inspeccionar `supabase_db_NovaIuris` por el mismo pipe inexistente. `supabase start` tampoco puede inicializar contenedores sin Docker Desktop Linux Engine.
- Hay un URL Supabase en la configuracion privada del backend, pero no se uso: no hay claves de Auth/service-role disponibles en la configuracion accesible ni confirmacion de que el proyecto sea staging autorizado. Produccion no se uso.
- No se aplicaron migraciones, no se ejecuto `db reset`, no se inspeccionaron grants en un catalogo vivo y no se modifico ningun proyecto remoto.

Para habilitar validacion local en Windows: iniciar Docker Desktop y esperar que el engine Linux este listo; comprobar `docker info`; desde la raiz ejecutar `supabase start`, `supabase db reset` y `supabase test db`. El resultado se debe registrar con CLI version, lista de migrations, salida de pgTAP y estado del bucket.

## Migration y RLS

Migration existente: `supabase/migrations/20261026023013_auth_workspace_history_foundation.sql`.

El archivo SQL activa RLS en `profiles`, `workspaces`, `workspace_members`, `cases`, `analysis_runs`, `case_artifacts` y `case_documents`, revoca escritura directa de artifacts/runs/documents al rol autenticado y define el bucket `case-documents` como privado. Los permisos de Storage restringen lectura por metadata/membership e insercion por path workspace/case; el backend usa service-role y por tanto hace comprobacion de scope en codigo antes de operaciones privilegiadas.

`supabase/tests/auth_workspace_rls.sql` prepara dos identidades y fixtures A/B, y contiene aserciones de lecturas propias y denegacion directa por ID para casos, perfiles, runs, artifacts, documentos y objetos. Incluye acceso de escritura a path propio y denegacion a path ajeno. **No ejecutado** por indisponibilidad del daemon. Conteo definido por pgTAP: 25 assertions; resultado real: no disponible.

| Operacion bajo RLS | Usuario A | Usuario B | Evidencia real |
| --- | --- | --- | --- |
| Perfil/workspace/caso propio | Esperado permitir | Esperado permitir | SQL escrito; sin ejecucion |
| Case/run/artifact/documento ajeno por ID | Esperado 0 filas | Esperado 0 filas | SQL escrito; sin ejecucion |
| Objeto Storage de otro usuario | Esperado denegar/no listar | Esperado denegar/no listar | SQL escrito; sin ejecucion |
| Upload en path del case propio/ajeno | Esperado permitir/denegar | Simetrico por policy | SQL escrito; sin ejecucion |

No se declara PASS de RLS, grants, constraints, indices ni migracion repetible.

## Storage y pipeline documental

- Integracion implementada en `ApplicationRepository`: el backend valida el case con el usuario autenticado, genera UUID y path `workspaces/{workspace}/cases/{case}/{document}/{safe_filename}`, valida extension/MIME, bytes y hash, sube a `case-documents` sin upsert, y crea metadata `case_documents`.
- Upload API de produccion falla cerrado si el repositorio privado no esta configurado. No acepta un `storage_path` o workspace del cliente.
- Descarga `GET /api/cases/{case_id}/documents/{document_id}/file` primero valida ownership/case y vuelve a buscar metadata en scope; responde con `private, no-store`.
- Al terminar ingestion, el callback sincroniza `processing_status`; un reemplazo elimina el objeto anterior solo despues de que el nuevo documento quede listo.
- SQLite conserva los datos derivados que requiere el pipeline vigente: manifiesto de extraccion, texto normalizado, chunks, embeddings y busqueda documental. El original, ownership y metadata principal pertenecen a Storage/Postgres cuando el repositorio esta configurado. En desarrollo sin repositorio se mantiene la ruta SQLite legacy.
- Se ejecutaron pruebas unitarias/deterministas del path, sanitizacion, validacion MIME/tamano y aislamiento por usuario, mas prueba API con repositorio y Storage falsos. No es un test de policies Storage en servidor real.

## Runs, artifacts e historial

- `TaskManager` continua siendo el journal operacional de tasks; `analysis_runs` es el historial de producto y `case_artifacts` contiene snapshots server-owned versionados. El cliente no suministra el contenido final del artifact.
- Al completar una task, el callback existente registra run y artifact; Court puede guardar `court_result`, `graph_snapshot` y `report`. La relacion padre utiliza el task NovaCase coincidente cuando existe metadata `reuse_task_id`.
- La UI de Mis casos enlaza runs completados/partial por `run_id`. `loadHistoricalRun` solo hace `GET /api/runs/{run_id}/result`, valida run/case/tool y el artifact esperado. NovaCase/NovaCourt reciben el snapshot directamente; no inician nuevo task ni llaman proveedores. Graph usa el snapshot incluido o el artifact de grafo.
- Prueba frontend determinista comprueba que reabrir Court efectua una sola peticion GET historica y ninguna llamada a rutas de analisis/tasks. No prueba sobrevivencia a un reinicio real porque no hay base remota activa.
- Las escrituras remotas y su inmutabilidad no fueron probadas contra Postgres. El journal SQLite sigue siendo necesario para el estado operacional de tasks actuales; no constituye la autoridad del historial completado.

## Auth, correo y aislamiento

- No se cambio el proveedor ni el modelo Auth de Fase 2.1. El backend deriva identidad del bearer validado.
- Signup/bootstrap, refresh, logout y recuperacion de password no se pudieron ejecutar contra Supabase local ni Inbucket. Estado: **MANUAL AUTH/EMAIL VERIFICATION REQUIRED**.
- No se creo ningun usuario externo ni se enviaron correos.
- Tests existentes de API prueban aislamiento mediante identidades fake; pgTAP con dos auth users y Storage real sigue pendiente.

## Pruebas ejecutadas

- Backend: `python -m unittest discover -s tests -v` — **388/388 PASS**.
- Frontend: `npm test -- --run` — **111/111 PASS**.
- Build: `npm run build` — PASS; Vite conserva el aviso de un chunk mayor de 500 kB.
- Python: `python -m compileall -q app tests` — PASS.
- `git diff --check` — PASS antes del commit.
- Pruebas dirigidas nuevas cubren repositorio de documentos, upload/descarga API con Storage falso y recuperacion historica sin iniciar tareas.
- Supabase DB/Storage: **no ejecutado**, `supabase test db` bloqueado por el daemon ausente. A/B E2E con dos usuarios reales: no ejecutado.

## Limitaciones reales restantes

1. Falta validar migracion, grants, RLS y Storage policies en Postgres/Supabase real.
2. Falta ejecutar el escenario real A/B de IDOR/BOLA y validar upload/list/download/overwrite/delete de Storage.
3. Falta validar persistencia de `analysis_runs` y `case_artifacts`, logout/login, y recuperacion historica despues de reiniciar el backend.
4. Falta verificacion local/real de signup, confirmacion y password reset; SMTP de produccion tambien requiere configuracion operacional.
5. Tasks activas no sobreviven a reinicio como ejecuciones continuables; el alcance solo exige recuperar resultados ya completados.
6. La experiencia de historial independiente de busquedas NovaSearch standalone no se implementa aqui.
7. La retencion/limpieza automatica de grafos Zep externos no se implementa; abrir snapshot historico no requiere reconstruir el grafo.

## Fase siguiente

Esta entrega no implementa cuotas, billing, colas, workers, autoscaling, colaboracion de organizaciones, invitaciones ni limpieza Zep automatica. Los contratos `case_id`, `task_id`, `document_id`, `analysis_runs`, `case_artifacts` y los estados actuales se conservan.
