# Bloque 10 — MYKE Unified Conversational Workspace

## Entrada y estructura

`/` carga `MikeView.vue`: MYKE es el workspace principal. `/mike` redirige a `/`. `/novasearch`, `/novacase` y `/novacourt` redirigen a `/?tool=search`, `/?tool=case` y `/?tool=court`. Los alias `/buscar`, `/analizar` y `/simular` continúan. `/about` carga `MainView.vue`, ahora **Acerca de MYKE**. `/process/:projectId` redirige a Analizar; las rutas históricas de simulación y reportes se conservan. Una query `tool` desconocida deja el Home sin herramienta seleccionada.

La vista conserva el diseño MYKE: sidebar navy con tres cards, chats recientes, perfil inferior, topbar clara, saludo, composer amplio, acciones rápidas, tipografía serif y sans, tonos champagne y fondo jurídico sutil. El **Home mode** aparece con el hilo vacío. Al enviar, la misma vista presenta **Conversation mode**: los turnos de usuario y los resultados de MYKE se agregan al hilo; sidebar, topbar y composer permanecen.

## Herramientas y conversación

`workspace.activeTool` es la única fuente de verdad para sidebar, selector del composer, acciones rápidas y query de ruta. Seleccionar una herramienta muestra su mini card y enfoca el composer; no crea ninguna tarea. **Conocer más** abre `ToolDetailModal`, que explica entradas, salidas, fuentes, conexiones y un ejemplo. Su CTA selecciona la herramienta sin enviarla. El modal admite cierre, ESC y navegación de teclado.

Cada operación crea turnos livianos con `id`, rol, herramienta, texto, `task_id`, `case_id`, `document_ids`, `result_ref`, estado y fecha. El turno de respuesta conserva una referencia a su solicitud; el resultado completo permanece en el estado canónico del panel embebido. Los tres motores se montan como paneles dentro de turnos del mismo hilo. Cada panel conserva su polling; el shell escucha `task-state` y no inicia otra cadena. Hay guardas para doble envío y composición IME. Enter envía y Shift+Enter inserta una línea.

- **Buscar / NovaSearch:** respuesta, citas, fuentes, advertencias y progreso del motor existente.
- **Analizar / NovaCase:** resumen, análisis, argumentos, evidencia, riesgos, estrategia, fuentes e informe en sus pestañas existentes.
- **Simular / NovaCourt:** posiciones, decisión simulada, grafo, fuentes, informe y progreso.

Pasar de Buscar a Analizar conserva la búsqueda visible y prepara una nueva consulta; no crea un `CaseResult` ficticio. **Simular este caso** toma el `case_id`, el texto, los `document_ids` y el `reuse_task_id` emitidos por NovaCase. NovaCourt reutiliza el análisis solo cuando texto y documentos coinciden; no vuelve a ejecutar CaseService desde MYKE.

## Documentos, fuentes y aislamiento

`CaseDocumentUpload` conserva estados reales de envío, procesamiento, listo y error para PDF, DOCX y TXT. La selección de documentos continúa de Analizar a Simular dentro del mismo caso. **Nuevo chat** crea un nuevo `workspace.id` y `case_id`, vacía turnos, borrador, tareas, resultados montados, documentos seleccionados y contexto de reuse. Al desmontarse, los paneles abortan su tarea activa. No se elimina información persistente del backend.

`CitationLink`, `SourcesList` y `SourceModal` siguen siendo el sistema de citas. `SourcesList` deduplica por `source_id`. `TraceabilityChain` presenta relaciones explícitas de `issue_id`, `fact_ids` y `source_ids` del resultado de Case; su selección abre el mismo `SourceModal` y conserva página o sección cuando existe. No infiere enlaces. NovaCourt mantiene `GraphPanel` y su propia interacción de fuentes; MYKE no inventa enlaces a nodos sin contrato de enfoque.

## Sesión, cuenta y límites

`supabaseSession.js` usa `getSession` y `onAuthStateChange` para actualizar el Bearer token mediante `setAccessToken`. En producción, el Auth Gate impide mostrar el workspace sin sesión; durante el bootstrap aparece un estado de carga. El login usa el método email/contraseña configurado. Cerrar sesión limpia el token y el workspace privado. El menú de cuenta muestra solo nombre, iniciales y correo reales, abre `/about` y permite salir. No se muestra plan inventado. Chats recientes presenta un estado vacío: el historial persistente pertenece al Bloque 11.

La entrada por voz está deshabilitada hasta el Bloque 11. El Bloque 11 también incluye historial completo y gestión de conversaciones. El Bloque 12 comprende validación de runtime en entorno real, `RLS_RUNTIME_VALIDATION_PENDING`, `RUNTIME_RPC_SIGNATURE_VALIDATION_PENDING` y despliegue. Este bloque no instala proveedores reales ni despliega.
