# NovaCourt: cierre funcional NCourt-4

## Arquitectura y contratos

La ruta moderna `POST /api/novacourt/analyze` crea una tarea Court con `case_id` y `task_id`. Puede reutilizar únicamente el `final_result` de una tarea NovaCase completada, persistida y autorizada para el mismo owner y case. NCourt-1 prepara el contexto en el servidor: documento privado del corpus del caso y fuente pública con `document_id` + `unit_id` reabierta por Legal Knowledge V2. `legal_units.text` es el contenido jurídico canónico. No existe fallback moderno a V1.

La simulación recibe ese contexto preparado y ejecuta las posiciones de demandante, demandado y juez en orden. Las citas se resuelven solo contra fuentes verificadas. En paralelo, Graph construye nodos y relaciones desde el mismo contexto; la evaluación judicial y la decisión **simulada** se incorporan cuando ambas ramas están listas. Graph conserva internamente `source_scope`, `provenance_version`, `source_id`, `document_id` y `unit_id`. Su interfaz usa nombres y localizadores humanos. El enlace oficial, si existe, es secundario al detalle interno de la fuente.

NCourt-2 persiste el resultado completo en `TaskRepository`. La URL conserva solo `tool=court`, `case_id` y `task_id`. F5 o reapertura directa consultan la tarea existente con validación server-side de owner, case, task y tool; no recalculan NovaCase, Graph ni simulación. Las tareas activas al reiniciar el `TaskManager` pasan a `interrupted`. Salir de la vista detiene observación local; solo la acción explícita de cancelar envía la cancelación al servidor.

NCourt-3 añadió integridad semántica del Graph, estado de hechos ligado a evidencia privada, fuente jurídica V2 separada de prueba fáctica, nombres y relaciones legibles, filtros, búsqueda local, detalle y controles accesibles. La vista Court recupera el grafo y sus fuentes dentro del resultado de la tarea Court autorizada; no consulta Zep mediante `graph_id`. Las rutas heredadas `/api/graph/` están bloqueadas en producción.

## Smoke integrado NCourt-4

`backend/tests/test_novacourt_closure.py` ejecuta el handoff NovaCase → Court mediante HTTP 202 y `reuse_task_id`. Usa `TaskRepository` y corpus privado persistidos, `LegalRepositoryV2.get_unit` con una conexión SQL determinista que entrega `legal_units.text`, el orquestador real del Graph, la ruta preparada de `LegalDebateSimulator` y el LangGraph real de las tres posiciones. Solo las llamadas externas al modelo generativo y a Zep se sustituyen por respuestas controladas. Verifica hecho respaldado frente a alegación, citas autorizadas, proyección judicial simulada, provenance, ausencia de V1, reanudación tras recrear `TaskManager`, resultado idéntico sin rerun, aislamiento y rechazo de fuente V2 inválida. Las pruebas frontend existentes cubren URL/F5, estados terminales, detach frente a cancelación, fuente interna V2 y presentación Graph.

Ejecutar localmente:

```powershell
cd D:\NovaIuris\backend
python -m unittest tests.test_novacourt_closure -v
python -m compileall -q app tests
python -m unittest discover -s tests -v
cd D:\NovaIuris\frontend
npm test -- --run
npm run build
```

El entorno de esta verificación no tenía `MYKE_LEGAL_DATABASE_URL`, `OPENAI_API_KEY` ni `ZEP_API_KEY`; por ello el smoke contra proveedores reales queda `OPERATOR_REQUIRED`. Para ejecutarlo después, un operador con la configuración local legítima debe iniciar backend (`cd D:\NovaIuris\backend; uv run python run.py`) y frontend (`cd D:\NovaIuris\frontend; npm run dev`), abrir MYKE, crear un caso sintético, subir un documento privado, completar NovaCase con al menos una unidad jurídica V2, iniciar Court desde esa tarea y registrar `case_id`/`task_id`. Debe comprobar en el resultado demandante, demandado, juez, Graph, citas V2 y fuente privada; recargar la URL Court y reabrirla directamente para verificar el mismo resultado sin nueva tarea. Debe reiniciar el backend con una tarea activa de prueba y comprobar `interrupted`, y probar cancelación explícita en otra tarea. Registrar solo estados e identificadores de prueba, sin credenciales ni contenido privado en logs compartidos.

## Follow-ups fuera de NCourt-4

- `PRODUCTION_JOB_QUEUE_REQUIRED`: la ejecución actual en proceso no garantiza continuidad de tareas activas entre reinicios o múltiples instancias.
- `GRAPH_ARTIFACT_RETENTION_REQUIRED`: falta una política de retención y borrado para artefactos externos de Zep.
- `LEGAL_SOURCE_ARCHIVE_REQUIRED`: el archivo jurídico es un bloque posterior, independiente del cierre funcional de Court.

Este cierre no implica despliegue ni preparación integral de MYKE para producción.
