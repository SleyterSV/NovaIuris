# Bloque 7 — NovaCourt profesional

NovaCourt es una **simulación jurídica argumentativa** preparada para revisión humana. Su decisión simulada compara posiciones bajo los hechos, la prueba y las fuentes disponibles; no predice la resolución de un órgano jurisdiccional.

## Flujo y reutilización

`POST /api/novacourt/analyze` conserva `case_id` y `document_ids` explícitos. Para continuar desde NovaCase, la UI entrega además `reuse_task_id`, obtenido de una tarea Case completada. El servidor comprueba tipo de tarea, estado, `tool`, `case_id`, texto, documentos y resultado antes de tomar una copia del CaseResult. Si falla alguna comprobación o la tarea caducó tras un reinicio, devuelve `CASE_MISMATCH` sin buscar otro caso. Cambiar el relato o la selección documental inicia un análisis nuevo en el `case_id` explícito. «Nueva simulación independiente» aborta el polling anterior, limpia el estado visible y genera otro `case_id` sin documentos ni `reuse_task_id` anteriores.

El TaskManager sigue siendo local al proceso. El identificador de tarea no sustituye autorización multiusuario; ownership y almacenamiento distribuido son requisitos de producción.
`GET /api/tasks/<task_id>` y la cancelación exigen además el `case_id` correspondiente; una consulta con otro caso responde 404.

## Simulación

El CaseResult conserva hechos con estado `alleged`, `supported`, `disputed` o `unclear`, problemas jurídicos, evidencia, argumentos, contraargumentos y fuentes. El contexto de Court proyecta esos campos y los fragmentos exactos de Sources autorizadas. Si ya existen hechos estructurados, no reenvía el relato bruto completo; no carga el expediente completo ni vuelve a parsear documentos.

La ruta canónica de NovaCourt invoca `simulate_prepared_case` en `LegalDebateSimulator`: utiliza los tres nodos LangGraph existentes (posición promotora, contraria y síntesis judicial) y los modelos existentes. Esta ruta **no** ejecuta la ingesta vectorial legacy, no inserta chunks otra vez y no ejecuta el generador de porcentajes. El método legacy `simulate_case` se conserva temporalmente para endpoints antiguos fuera del flujo canónico; requiere revisión antes de exposición productiva. El simulador no añade fuentes o prueba fuera del dossier. La posición contraria recibe la posición promotora y el dossier para desarrollar una teoría propia; la síntesis judicial recibe ambas posiciones. Los checks de cancelación existentes impiden comenzar el siguiente nodo tras una cancelación cooperativa.

`resolve_court_roles` decide etiquetas a partir de la materia declarada: penal, civil/laboral/comercial/arbitral, constitucional, administrativa, o etiquetas neutrales si no hay materia clara. Las claves internas `prosecutor`, `defense` y `judge` se mantienen por compatibilidad; la UI usa `role_label`.

## Contrato y procedencia

`simulation.status` indica `ready`, `failed`, `timeout` o `not_requested`; conserva `case_id`, roles, posiciones, `judicial_analysis`, `decision`, `citations`, `sources`, `warnings`, `error` y metadata. `projection` permanece vacío para evitar duplicar la decisión como si fuera una predicción. No hay scores de victoria ni confianza judicial en la ruta canónica.

Los marcadores `[SRC-…]` se validan contra Sources públicas recuperadas y Sources privadas cuyo `case_id` coincide. Solo los marcadores presentes en ese conjunto generan citas visuales `[1]`, `[2]`; IDs falsos se descartan y producen warning. Las etiquetas son coherentes entre posiciones y decisión. `court_report_document` contiene secciones existentes, citas y Sources realmente usadas, sin llamada LLM adicional y sin acoplamiento a PDF/DOCX. No se publica texto residual de una simulación fallida.

El grafo conserva el adaptador existente y `graphData` llega al panel común. Grafo fallido con simulación lista, simulación fallida con grafo listo, y ambos fallidos producen `court_status: partial` conservando el análisis Case. Nunca se utiliza `strategy` como simulación. El resultado registra `case_reused`, estados de grafo/simulación, conteos de fuentes/citas y duraciones medidas de Court. El progreso marca `graph_build`, `simulation` y `court_citations` según trabajo real; no marca subetapas de roles sin callbacks reales. La cancelación/timeout es cooperativa y no detiene por fuerza una llamada externa ya iniciada.

## Interfaz

NovaCourt muestra el caso continuado o nuevo, carga documental seleccionada, progreso real y pestañas para resumen, análisis, evidencia, riesgos, posiciones, decisión simulada, informe y grafo. `CourtSimulation` y `CourtReport` reutilizan `MarkdownRenderer`, `SourcesList` y `SourceModal`; los enlaces privados exigen el `case_id` correcto. El informe de Court se deriva de `court_report_document` y se puede copiar como texto. PDF/DOCX siguen deshabilitados.

## Límites siguientes

**BLOCK_8_GRAPH:** trazabilidad más fina en nodos/aristas y grafo progresivo, sin alterar el contrato del grafo actual.

**BLOCK_9_PERFORMANCE:** benchmark de latencia, volumen de contexto, concurrencia segura de grafo y simulación, y callbacks reales por nodo. No se midieron tiempos ni costes con proveedores reales en este bloque.

Antes de producción: autorización por propietario de caso/tarea, persistencia de tareas entre workers, revisión o retirada de endpoints legacy y validación real del comportamiento jurídico con expedientes de prueba autorizados.
