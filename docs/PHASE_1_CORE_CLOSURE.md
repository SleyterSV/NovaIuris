# MYKE — Cierre técnico de Fase 1

Estado documentado contra el código de `feat/novacourt-v2`. Este documento describe la implementación presente; no implica despliegue, prueba con proveedores externos ni preparación multiusuario a escala.

## 1. Arquitectura actual

- El workspace de MYKE vive en `frontend/src/views/MikeView.vue`. La vista seleccionada se monta como una operación del workspace; NovaCase y NovaCourt emiten identidad de tarea al workspace. NovaSearch usa sus rutas de tarea propias.
- El frontend llama servicios HTTP bajo `/api`. El backend Flask registra las APIs de búsqueda, casos/documentos, exportación y las rutas de compatibilidad de grafo/simulación/informe.
- La recuperación jurídica V2 usa PostgreSQL/Supabase mediante `MYKE_LEGAL_DATABASE_URL` y `LegalRepositoryV2`; embeddings usan el modelo configurado y `EmbeddingService`. Supabase/Zep/OpenAI se configuran en backend; no se deben incluir claves privadas en el cliente.
- SQLite mantiene el corpus privado del caso, el registro local de ownership y el journal de tasks/documentos. En producción las rutas de esas bases deben estar fuera del árbol del proyecto y en volumen persistente.
- No hay cola distribuida ni worker separado: `TaskManager` ejecuta tareas en el proceso y limita tareas activas por owner.

## 2. NovaSearch

Ruta moderna: `POST /api/search/tasks` → `GET /api/search/tasks/{task_id}` y, para detener, `POST /api/search/tasks/{task_id}/cancel`. El endpoint crea una task; `SearchService` normaliza/analiza la consulta, genera un embedding salvo consultas directas a unidad, consulta el repositorio seleccionado, consolida/rerankea cuando corresponde, crea contexto, redacta y valida citas contra sus fuentes. V2 usa la búsqueda híbrida/rankeada del repositorio jurídico y omite una segunda fusión/reranking. Una respuesta vacía, fallo de embedding, fallo del repositorio y degradación de reranking se distinguen.

La versión de conocimiento viene de `LEGAL_KNOWLEDGE_VERSION`; producción exige `v2` y el modelo de embedding acordado. La configuración base de desarrollo permite V1: los entornos de operación que deban representar el corpus actual deben fijar V2 explícitamente. El detalle de fuente pública se vuelve a leer por `unit_id` y `document_id`; no se acepta una unidad ambigua por documento solamente. Las citas se resuelven contra el pool recuperado y los tests usan repositorios deterministas, no llamadas pagadas.

## 3. NovaCase

Ruta asíncrona: `POST /api/case/tasks` → `GET /api/tasks/{task_id}?case_id=…`; cancellation usa la ruta scoped correspondiente. El caso pasa por contexto documental privado acotado a `case_id`/`document_ids`, investigación jurídica, análisis estructurado, argumentos, evidencia, riesgos, estrategia, informe, fuentes y resolución de citas. El `CaseResult` conserva esos módulos y se guarda como resultado de task.

El corpus privado está en `CaseCorpusRepository`: lecturas de chunks, validación de documentos, reemplazo y borrado requieren tanto `case_id` como `document_id`; las APIs comprueban ownership antes de acceder. Las referencias privadas no se envían a otros casos. Las fuentes públicas V2 se reabren por identidad canónica documento+unidad. Los módulos de reporte conservan estructura si fallan generación de informe o verificación de citas, con estado/aviso controlado.

PDF y DOCX de NovaCase son generados por backend (`/api/export/pdf`, `/api/export/docx`) a partir de un resultado persistido y terminado. El cliente envía exclusivamente `{case_id, task_id, tool}`. Se comprueban owner, caso, tarea, tipo, estado y resultado canónico antes de renderizar. El DOCX es un paquete Office editable; ambos renderers usan el contenido preparado del servidor.

## 4. NovaCourt

`POST /api/novacourt/analyze` crea una task `legal_analysis` con metadata `tool=court`, owner, case y documentos. Si recibe un `reuse_task_id`, el servidor comprueba que sea una tarea NovaCase terminada del mismo owner/case, con relato y documentos coincidentes; reutiliza su resultado y no ejecuta de nuevo el análisis del caso. `/api/novacourt/results/{task_id}?case_id=…` valida scope y herramienta.

El pipeline prepara un `CaseResult` server-side y divide dos copias independientes en ramas concurrentes Graph y Simulation. Las fallas de una rama no borran la otra ni el resultado base; se exponen estados parciales. La simulación requiere posiciones de demandante, demandado y juez válidas; sus referencias se humanizan y las citas se resuelven contra fuentes verificadas. El reporte consolidado conserva secciones, IDs de citas y fuentes. Si falla su ensamblaje, se persisten el análisis y las ramas, el reporte queda vacío con estado `failed`/aviso seguro y la exportación lo rechaza.

La cancelación explícita se propaga mediante token y evita etapas/provider calls posteriores; salir o refrescar la vista solo detiene la observación local. Los timeouts de tarea, simulación y grafo tienen límites separados; el retry de LLM es acotado y respeta `Retry-After` cuando está presente. La URL del workspace solo conserva `tool`, `case_id` y `task_id`. Al refrescar, `MikeView` reconsulta la task scoped y reanuda el polling sin crear otra. Una tarea activa cuando el proceso se reinicia se marca `interrupted`; se puede recuperar su estado, no continuar el trabajo detenido.

PDF/DOCX de NovaCourt reutilizan los renderers y la autorización server-owned bajo `/api/export/court/pdf` y `/api/export/court/docx`; exigen la task Court completada y un reporte con contenido válido. La falla del documento no autoriza exportar contenido enviado por el navegador.

## 5. Grafo jurídico

La ruta activa es `NovaCourtPipelineService` → `NovaCourtGraphService` → `NovaCourtGraphOrchestrator` → proyección determinista `build_graph_input` → `GraphBuilderService`/Zep. El frontend activo es `frontend/src/components/novacourt/GraphPanel.vue`, que consume el grafo dentro del resultado Court; no consulta Zep directamente. El estado `ready` requiere procesamiento del proveedor con nodos y relaciones, y publica la proyección local; `empty` indica procesamiento completado sin datos utilizables; `failed` y `timeout` son estados distintos. Los edges se crean únicamente con extremos existentes y pares de tipos permitidos.

La proyección conserva `source_id`, `source_scope` y, para fuente V2, `provenance_version`, `document_id` y `unit_id`, además de localizadores disponibles. Las fuentes privadas de otro caso se filtran antes de construir nodos; las evidencias solo se derivan de vínculos documentales privados existentes. La identidad estable del nodo/edge incorpora `case_id`. La UI resuelve fuentes por sus IDs internos contra el pool canónico autorizado del resultado y presenta títulos/localizadores legibles; Zep sirve para procesar/relacionar datos, no como autoridad jurídica.

Las rutas heredadas `/api/graph/`, `/api/simulation/` y `/api/report/` responden `410` en producción. El grafo externo de Zep se crea por ejecución. No existe política automática de borrado/retención de esos artefactos; los tasks persistidos conservan `graph_id` para trazabilidad y la UI usa la proyección guardada. Una retención coordinada con expiración/borrado de tareas queda pendiente de una política de lifecycle explícita; no se afirma limpieza de artefactos externos.

## 6. Tasks, estados y recuperación

`TaskManager` administra `pending`, `processing`, `completed`, `failed`, `cancelled` e `interrupted`. `court_status`/estados de rama informan degradación parcial dentro de un task terminado; no equivalen a una task fallida. El journal SQLite carga resultados persistidos por `owner_id`, `case_id`, `task_id` y `task_type`; la carga scoped no depende solo de caché de proceso. Tasks activas al iniciar un nuevo manager se marcan `interrupted`; tasks terminales permanecen recuperables mientras exista el journal. El límite de tamaño del resultado fuerza fallo controlado si se excede.

La garantía es de instancia única con volumen persistente. El registro de ownership y las tasks no son un sistema distribuido; no hay continuidad de trabajo activo tras reinicio ni coordinación entre varias instancias.

## 7. Fuentes y citas

Una fuente debe ser admitida por el contrato antes de citarla. `source_contracts` normaliza fuentes públicas y privadas y rechaza citas que no resuelven a una fuente permitida. Fuentes V2 se identifican por `document_id + unit_id` y se reabren con ambos valores; fuentes privadas requieren el `case_id` esperado. `resolve_citations` genera números reutilizables por identidad de fuente y elimina referencias no verificadas con avisos. El cliente normaliza las mismas identidades y no debe fabricar URLs ni mapear un documento V2 a una unidad arbitraria.

Fuentes jurídicas públicas y documentos privados del caso permanecen diferenciados; jurisprudencia no se convierte en evidencia fáctica. IDs y UUIDs son referencias internas y no deben mostrarse como texto jurídico.

## 8. Documentos del caso

Carga, lista, reemplazo, lectura, eliminación y contexto usan el corpus local case-scoped. Los documentos autorizados se validan contra el caso antes de ingesta/retrieval y las consultas usan la lista de `document_ids` permitida. Los extractos privados se asocian a fuentes canónicas con página/sección cuando existe metadata. El staging y las tareas de ingesta tienen límites configurados y estados propios. No se usa un `document_id` manipulable sin comprobar su pertenencia al caso.

## 9. Errores y seguridad

En producción, el middleware valida Bearer token consultando Supabase Auth; una identidad ausente/inválida se rechaza. Las rutas modernas de casos, documentos, estado/cancelación y export validan ownership y scope. Los errores públicos se sanitizan; logs registran request ID, hash de identidad y tipo de error, sin cuerpo bruto del proveedor. El frontend no controla resultado final ni contenido de export.

La clave publicable se usa para verificar Auth; `SUPABASE_KEY`, claves OpenAI/Zep y URL de base de datos solo se leen desde backend/configuración de servidor. Los tests de seguridad verifican barreras de producción y export. Fuera de producción existe identidad fija `local-development-user` y la política local de creación de caso es permisiva para desarrollo/pruebas; esto no debe considerarse seguridad multiusuario de producción. Las rutas heredadas permanecen registradas para compatibilidad pero bloqueadas en producción.

## 10. Validación automatizada

La CI define backend con `python -m unittest discover -s tests -p 'test_*.py'`, `python -m compileall -q app tests` y `python scripts/smoke_providers.py --dry-run`; frontend con `npm test` y `npm run build`. En esta revisión: backend **381/381**, frontend **108/108**, `compileall` PASS, build PASS y provider dry-run PASS (sin solicitudes). Los tests de servicio reemplazan proveedores con fakes y cubren V2/citas, aislamiento, export server-owned, recuperación, ramas parciales, cancelación, timeout/retry y estados del grafo.

No se ejecutan solicitudes pagadas/reales a OpenAI, Supabase ni Zep en este cierre. La verificación real requiere un operador con credenciales y recursos de prueba autorizados. Procedimiento mínimo: iniciar backend y frontend con la configuración local autorizada; ejecutar una búsqueda NovaSearch con una unidad V2 conocida y abrir su fuente canónica; crear un caso sintético con un documento privado; completar NovaCase, descargar y abrir PDF/DOCX; iniciar NovaCourt desde el resultado NovaCase, comprobar ramas Graph/Simulation y fuentes, copiar `case_id`/`task_id`, recargar y reabrir la URL scoped. Registrar los estados terminales, `graph.status`, cantidades de nodes/edges, `source_id`/`document_id + unit_id` de una fuente pública de prueba y el `source_id` del documento privado, sin registrar credenciales ni contenido sensible. PASS requiere respuestas de búsqueda respaldadas por fuente verificable, exports que abren y derivan del resultado persistido, Court recuperado sin nueva ejecución, scopes coincidentes, citas que abren las unidades exactas y graph ready/empty coherente con datos utilizables.

## 11. Límites conocidos de Fase 1

- Tasks se ejecutan en proceso; tasks activas se interrumpen al reiniciar. No hay cola/worker distribuido ni garantía multi-instancia.
- La persistencia depende de SQLite local en volumen persistente y del identificador de owner existente; no es un historial/workspace multiusuario completo.
- Los artefactos de grafo creados en Zep no tienen borrado/retención automática.
- Una llamada real controlada a proveedores y una inspección visual de archivos exportados con datos de operación no se ejecutan automáticamente en este entorno; requieren smoke manual.
- V1 sigue disponible en configuración de desarrollo/compatibilidad; producción impone V2.

Estas son limitaciones operativas conocidas; no se presentan como resultados de pruebas fallidas ni se ocultan como características multiusuario.

## 12. Límites de Fase 1 y Fase 2 — integration boundaries

Fase 1 cierra el motor actual y mantiene sus identificadores/contratos: `case_id`, `task_id`, `document_id`, `source_id`, `document_id + unit_id` para fuente V2, IDs estables de nodo/edge, `CaseResult`, `GraphResult`, `SimulationResult`, rutas modernas y estados actuales. Fase 2 debe añadir identidad/workspace alrededor de estos límites y no cambiar la semántica de esos contratos.

- **Auth:** la validación Bearer existente está en `create_app`/`runtime_security.verify_supabase_user`; la integración de sesión de producto debe alimentar esa identidad, sin aceptar owner desde JSON.
- **Owner/usuario:** `authenticated_user_id()` es la frontera actual. La futura asociación persistente de usuario pertenece a ownership de casos, tasks y documentos, no a los payloads jurídicos.
- **Workspace:** puede asociarse en el límite de `MikeView` y la navegación/API de casos; hoy no existe workspace persistido como entidad.
- **Historial de casos:** `GET /api/cases` y el registry `CaseOwnershipRepository` son primitivas actuales. El historial completo debe construirse sobre registros case/task scoped sin cambiar `case_id` ni reescribir los resultados.
- **Analysis runs:** `TaskRepository` es el journal actual; el historial de runs debe versionar/relacionar tasks sin cambiar `task_id`, tipo, estado ni shape de resultado.
- **Documentos privados:** `CaseCorpusRepository` es el límite de asociación/storage; una futura capa de usuario/workspace debe mantener las claves compuestas y validaciones por caso/documento.
- **Endpoint con identidad:** las APIs modernas `/api/search/tasks`, `/api/case/tasks`, `/api/novacourt/analyze`, `/api/tasks/...`, `/api/novacourt/results/...`, `/api/documents/...` y `/api/export/...` deben seguir derivando identidad del token validado en backend.
- **No romper:** IDs anteriores, identidad V2 documento+unidad, source/citation mapping, rutas, estado de task, payloads canónicos, export server-owned y aislamiento case-scoped.

Fase 2 queda fuera de este cierre: alta/login de producto, perfiles, workspaces persistidos, billing/planes, cuotas comerciales, colas, workers distribuidos, autoscaling y migración a persistencia SaaS.
