# Bloque 1: base estabilizada

Estado inicial: working tree limpio, rama `feat/mike-stabilization`, checkpoint `c0611f7`.
No se ejecutaron proveedores externos, migraciones, despliegues ni push. Modelos, embeddings y prompts jurídicos conservados.

## Dependencias y validación reproducible

Frontend: `package.json` + `package-lock.json`; Node 22; `npm ci`, `npm test`, `npm run build`.
Se declararon markdown-it 14.1.0 y highlight.js 11.11.1, ya utilizados por componentes activos.
La instalación local usó `npm ci --ignore-scripts --cache D:/NovaIuris/.npm-cache`; build posterior comprobó las herramientas instaladas.

Backend: Python 3.11; fuente canónica `pyproject.toml` + `uv.lock`, utilizada por Docker y ahora CI mediante `uv sync --frozen`.
`requirements.txt` queda como compatibilidad para consumidores pip; sus rangos NO constituyen un lock reproducible.
Validación local en el virtualenv existente: `python -m unittest discover -s tests -v` y `python -m compileall -q app tests`.
No se reinstaló el backend ni se ejecutó Docker/CI remotamente.

## Contratos y rutas

NovaCase devuelve `success`, `case_id`, `case`, `analysis`, `summary`, `research`, `arguments`, `evidence`, `risks`, `counter_arguments`, `strategy`, `timeline`, `report`, `citations`, `metadata`.
Los aliases heredados permanecen. Los contratos internos incorporan hechos/facts, problemas_juridicos/issues, normas_probables/law, evidence documents/testimonies, riesgos, contraargumentos y estrategia.
Las normas probables se presentan como preliminares, no como fuentes verificadas. Los campos vacíos muestran “No identificado con la información disponible.”
El frontend muestra también investigación, argumentos, cronología, citas y elementos complementarios de estrategia. No inventa fechas, fuentes ni probabilidades.
Se retiraron porcentajes de confianza por defecto, indicadores arbitrarios de riesgo/calidad y tarjetas de probabilidad sin sustento.

HTTP: `frontend/src/config/api.js` es la fuente única. `VITE_API_BASE_URL` es el origen sin `/api`; compatibilidad temporal con `VITE_API_URL`.
Base vacía en producción usa mismo origen; desarrollo usa localhost exclusivamente en configuración central. Se eliminó la ruta NovaSearch duplicada.

Rutas: `/api/case` conserva ejecución síncrona; `/api/case/tasks` y `/api/novacourt/analyze` crean jobs; `/api/tasks/<id>` consulta; `/api/tasks/<id>/cancel` cancela; `/api/novacourt/results/<id>` es alias real.
Una tarea tiene un único polling secuencial frontend, abortado al desmontar. Los IDs de caso, tarea y herramienta se verifican antes de renderizar.

## NovaCourt

Pipeline: CaseService → contrato canónico → GraphBuilder real → simulador real → resultado.
El análisis Case se publica como `partial_result` antes de los pasos secundarios. Graph/Simulation fallidos o timeout no borran ese análisis.

Graph adapter utiliza `create_graph`, `set_ontology`, `add_text_batches`, `_wait_for_episodes`, `get_graph_data`; nunca `build_graph_sync` ficticio.
Contrato: status, graph_id, nodes, edges, node_count, edge_count, error, metadata. Estados: not_requested/building/ready/failed/timeout.
GraphPanel recibe `graphData`. No se añadieron snapshots progresivos.
Se conservan únicamente rutas HTTP mínimas `/api/graph/data/<id>` y `/api/graph/project/<id>` para vistas todavía en router. No se reactivaron ontology/build/task del flujo antiguo sin uso.

Simulation: status, prosecutor, defense, judge, projection, metadata, error; estados not_requested/running/ready/failed/timeout.
CourtSimulation consume posiciones reales. Strategy jamás sustituye simulation. Una salida sin posiciones completas falla de forma segura.
La búsqueda de conocimiento jurídico del simulador delega en LegalRepository; no conserva su firma RPC antigua de tres parámetros. Firma desplegada requiere validación runtime posterior.

## Progreso, cancelación y aislamiento

Progreso de Case: recepción, hechos, estrategia inicial, investigación, argumentos, evidencia, riesgos, contraargumentos, informe. Court añade grafo y simulación.
Porcentaje representa hitos terminados, no estimación de tiempo. El orden respeta las dependencias actuales; evidencia y riesgos conservan su concurrencia existente.

Tokens cooperativos se comprueban entre etapas, búsquedas, embeddings, reintentos propios, lotes/páginas Zep y nodos LangGraph. Los reintentos automáticos OpenAI se deshabilitan para no iniciar trabajo oculto después de cancelar.
Una llamada externa ya iniciada NO se interrumpe. Puede seguir hasta su timeout; el hilo termina cuando vuelve a un checkpoint. Cancelar no revierte inserciones externas ya realizadas.
La tarea queda cancelada inmediatamente y no acepta resultados tardíos. Graph usa deadline cooperativo; no tiene corte forzoso de socket. Simulation limita espera y cancela cooperativamente el trabajo posterior.

Cada nueva tarea obtiene case_id explícito o UUID nuevo; owner queda preparado como metadata, sin autenticación.
No hay last_case, contexto privado global ni reutilización implícita. EmbeddingService se crea por búsqueda con cache de instancia/request; no se comparte entre casos. No se implementó cache persistente.
El simulador conserva su session_id único para filtrar sus propios chunks. Autorización y políticas de retención/borrado de datos externos quedan pendientes.

## Seguridad y operación

DEBUG seguro por defecto; SECRET_KEY obligatorio cuando APP_ENV=production; dotenv no sobrescribe entorno suministrado.
CORS configurable mediante CORS_ALLOWED_ORIGINS. Rate limit por IP/proceso para POST de costo; polling GET no consume ese cupo.
Request IDs en respuestas; errores públicos estructurados code/message/request_id. Se eliminan payloads legacy de error y trazas públicas.
Se retiraron logs del texto de casos y respuestas jurídicas completas en los parsers activos; logs nuevos usan IDs, etapas y tipos de error.
Credenciales permanecen en entorno; no se editaron ni imprimieron secretos.

TaskManager es memoria por proceso: pierde jobs al reiniciar, no admite reparto entre workers, no implementa owner/autorización, no limita globalmente hilos activos. Usa locks y copias de snapshots; limpieza de terminales al iniciar tareas. Despliegue escalado requiere bloque posterior.
El servicio se debe usar en entorno controlado mientras no exista autorización de acceso a jobs/resultados. IDs UUID no sustituyen permisos.

## Document Output

`prepare_document(case_id, result, tool)` valida identidad del resultado y metadata, copia datos existentes y produce contrato versionado de informe Case/Court con título, fecha UTC y secciones.
`/api/export/prepare` expone ese contrato. DocumentRenderer define la frontera futura; no invoca IA.
CASE-A/CASE-B quedan aislados por validación explícita; exportación utiliza 0 tokens adicionales.
La compilación pdflatex heredada se deshabilitó; `/api/export/pdf` responde 501 DOCUMENT_OUTPUT_PENDING. El formateador legacy no se ejecuta.
PENDIENTE BLOQUE DOCUMENT OUTPUT: renderer PDF/DOCX, templates, paginación y snapshots de grafos. No hay descarga PDF terminada en este bloque.
Diseño futuro: blanco, márgenes profesionales, títulos serif/cuerpo sans-serif, azul marino, dorado mínimo, páginas y encabezados discretos; links solo oficiales existentes. No reinterpretar datos jurídicos.

## Pendientes y aceptación

Pruebas: contratos internos, callbacks, cancelación, pipeline y degradación, interfaz real GraphBuilder con autospec, nodos reales LangGraph con modelo fake, aislamiento concurrente y de exportación, errores públicos, HTTP, un polling y render SSR real de paneles Vue.
No se ha validado contra proveedores, ni precisión jurídica con expedientes reales: requiere validación runtime posterior autorizada.
Warnings: npm reporta 7 vulnerabilidades (2 moderate, 5 high); no se hizo actualización general. Vite advierte bundle principal grande. PyPDF2 deprecado. Docker sigue siendo configuración de desarrollo, no producción escalada.

PENDIENTE NOVASEARCH: citas/fuentes avanzadas, filtros RPC, progreso por etapas, UX y performance.
PENDIENTE BLOQUE FUTURO: OCR/expedientes masivos, redacción peruana con referencias reales, benchmarks, optimización de modelos, grafos progresivos, MIKE workspace, historial, voz, autenticación y producción escalada.
MIKE `/mike` se conserva; no se integraron visualmente las herramientas.

GO para revisión y siguiente bloque local. No implica GO de producción. No iniciar Bloque 2 automáticamente.

## Resultado de validación local

Backend: 30 tests OK; compileall OK; create_app y rutas verificados con factories simuladas.
Frontend: 9 tests/subtests OK, incluido render SSR de componentes Vue; build Vite OK.
`git diff --check`: OK. No proveedores reales ejecutados.

## Archivos del bloque

- `.github/workflows/ci.yml`
- `.gitignore`
- `backend/app/__init__.py`
- `backend/app/api/case.py`
- `backend/app/api/export.py`
- `backend/app/api/graph.py`
- `backend/app/api/search.py`
- `backend/app/api/simulation.py`
- `backend/app/config.py`
- `backend/app/models/task.py`
- `backend/app/services/answer_service.py`
- `backend/app/services/case_analyzer.py`
- `backend/app/services/case_report_service.py`
- `backend/app/services/case_service.py`
- `backend/app/services/counter_argument_service.py`
- `backend/app/services/court_simulation.py`
- `backend/app/services/embedding_service.py`
- `backend/app/services/evidence_analyzer.py`
- `backend/app/services/graph_builder.py`
- `backend/app/services/langgraph_engine.py`
- `backend/app/services/legal_argument_service.py`
- `backend/app/services/novacourt_graph_service.py`
- `backend/app/services/novacourt_pipeline_service.py`
- `backend/app/services/novacourt_simulation_service.py`
- `backend/app/services/reranker_service.py`
- `backend/app/services/risk_analyzer.py`
- `backend/app/services/search_service.py`
- `backend/app/services/strategy_builder.py`
- `backend/app/utils/api_response.py`
- `backend/app/utils/case_contract.py`
- `backend/app/utils/novacourt_graph.py`
- `backend/app/utils/novacourt_simulation.py`
- `backend/app/utils/rate_limit.py`
- `backend/app/utils/zep_paging.py`
- `backend/requirements.txt`
- `backend/tests/test_case_contract.py`
- `backend/tests/test_novacourt_graph.py`
- `backend/tests/test_novacourt_simulation.py`
- `frontend/package-lock.json`
- `frontend/package.json`
- `frontend/src/api/index.js`
- `frontend/src/components/Step1CaseInput.vue`
- `frontend/src/components/Step2Results.vue`
- `frontend/src/components/Step4Report.vue`
- `frontend/src/components/common/AnalysisSection.vue`
- `frontend/src/components/common/ExecutiveSummary.vue`
- `frontend/src/components/common/MarkdownRenderer.vue`
- `frontend/src/components/novacase/AnalysisView.vue`
- `frontend/src/components/novacase/CounterArgumentsView.vue`
- `frontend/src/components/novacase/EvidenceView.vue`
- `frontend/src/components/novacase/RiskView.vue`
- `frontend/src/components/novacase/StrategyView.vue`
- `frontend/src/components/novacourt/CourtSimulation.vue`
- `frontend/src/components/novacourt/CourtSummary.vue`
- `frontend/src/composables/useNovaCourt.js`
- `frontend/src/composables/useNovaSearch.js`
- `frontend/src/config/api.js`
- `frontend/src/router/index.js`
- `frontend/src/services/caseService.js`
- `frontend/src/services/novaCourtService.js`
- `frontend/src/utils/caseContract.js`
- `frontend/src/utils/content.js`
- `frontend/src/utils/exportUtils.js`
- `frontend/src/views/NovaCaseView.vue`
- `frontend/src/views/NovaCourtView.vue`
- `frontend/tests/caseContract.test.mjs`
- `backend/app/services/document_output.py`
- `backend/app/utils/cancellation.py`
- `backend/tests/test_stabilization.py`
- `docs/STABILIZATION_BLOCK_1.md`
- `frontend/src/config/apiBase.js`
- `frontend/src/services/taskService.js`
- `frontend/tests/stabilization.test.mjs`
