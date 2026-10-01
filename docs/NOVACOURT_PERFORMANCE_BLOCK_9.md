# Bloque 9: ejecución de NovaCourt

## Alcance y baseline

Estado inicial: rama `feat/mike-stabilization`, HEAD `c46a825`, árbol limpio. Todas las cifras de esta página son **LOCAL SYNTHETIC BENCHMARK** con fakes y demoras deterministas de 40 ms por rama. No representan latencia ni facturación de producción. Comando: `cd backend && python scripts/bench_novacourt_synthetic.py --delay 0.04`. Los cuatro fixtures mantienen las mismas entradas y demoras antes y después.

Ruta inicial, caso reutilizado: `CaseResult completado → copia de reuse_task_id → Graph → Simulation → validación de citas → resultado Court`. Ruta inicial, caso nuevo: `CaseService → CaseResult → Graph → Simulation → validación de citas → resultado Court`. El reuse comprueba `case_id`, texto y `document_ids`, y evita CaseService, parsing, investigación, ingesta y embeddings documentales. El caso nuevo llama CaseService una vez. El baseline observó 0 llamadas CaseService en cada fixture reutilizado y 1 en el nuevo.

## Mapa de llamadas lógico previo

| Etapa | Interfaz | Operaciones lógicas | Retrieval | Embeddings | Dependencia / paralelismo |
| --- | --- | ---: | ---: | ---: | --- |
| Case, reutilizado | TaskManager / CaseResult | 0 análisis | 0 | 0 | Previo |
| Case, nuevo | CaseService | 1 análisis completo; llamadas internas dependen del caso | Interno a CaseService | Interno a CaseService | Previo |
| Graph | GraphBuilderService / Zep | 1 create, 1 ontology, N add_batch, 1 fetch final | 0 en ruta Court | 0 explícitos en Court | Depende de CaseResult |
| Graph wait | Zep episode.get | P polls por episode pendiente | 0 | 0 | Tras add_batch; deadline decreciente |
| Simulation | LangGraph / ChatOpenAI | 3 generaciones: Position A, Position B, Judge | 0 canónicos | 0 canónicos | A → B → Judge; independiente del Graph |
| Court citations | `resolve_citations` local | 1 validación conjunta | 0 | 0 | Depende de Simulation |

Los tres nodos del simulador invocan `get_llm().invoke` secuencialmente. Position B usa la salida de A y Judge usa ambas; no se paralelizan. Esas son operaciones lógicas, no solicitudes físicas facturadas. Un proveedor puede reintentar internamente. La ruta canónica `simulate_prepared_case` evita el método legacy que crea embeddings y grafo de sesión. Los tests usan fakes y no instancian proveedores.

Graph proyecta `CaseResult` a entidades y relaciones con provenance e IDs estables. Serializa cada episodio una vez. Un fake GraphBuilder registró 5/11/25/11 batches, 13/33/73/33 episodios, 8/14/28/14 operaciones de create/ontology/batch/fetch y 13/33/73/33 polls en los cuatro fixtures. El fetch final ocurre una vez. La implementación real usa el mismo deadline decreciente al esperar episodios; no se alteraron batch size ni intervalo de polling sin datos reales. Los snapshots lógicos son core (v1) y final (v2); solo core se transmite mediante callback antes del resultado final.

## Cuellos de botella y decisión

Graph y Simulation leían CaseResult pero se ejecutaban secuencialmente. Además, el contexto de Simulation recibía el Graph final ya derivado de los mismos hechos, evidencia y fuentes; en el fixture documental ello elevó el contexto de 2.757 a 34.361 caracteres. El Graph no aportaba autoridad documental nueva: Zep es una proyección del CaseResult. Se eliminó esa repetición. Se conservan hechos, problemas, argumentos, evidencia, riesgos, contraargumentos, cronología, estrategia y fuentes verificadas. Las fuentes con igual `source_id` se presentan una vez y las privadas se filtran por `case_id`.

Tras CaseResult, Graph y Simulation corren en `ThreadPoolExecutor(max_workers=2)`. Cada una recibe una copia propia; solo el coordinador fusiona resultados. El callback de snapshot y la publicación de Task usan un lock corto; TaskManager ya protege sus mutaciones. Versiones de snapshot repetidas se descartan. Errores de una rama conservan la otra; ambos errores conservan CaseResult. La cancelación cooperativa se revisa antes de iniciar cada rama, durante la espera y antes de citas/finalización. Una solicitud externa ya iniciada puede continuar. No se introdujo deadline global porque los servicios ya tienen límites propios y propagar un nuevo deadline requeriría cambiar interfaces; queda como `FUTURE_OPTIMIZATION`.

No se creó cache global ni `CourtExecutionContext` persistente. El contexto de una ejecución vive en variables locales y copias por rama. El reuse de CaseResult se limita a identidad explícita. No hay retrieval ni embeddings canónicos adicionales en Court, por lo que un cache request-scoped de query no ahorraría llamadas observadas; no se introdujo. La proyección de Graph se construye una vez por ejecución. Deepcopy sigue presente en límites de rama y publicación de Task para preservar aislamiento; su costo se refleja en wall-clock pero no se elimina sin una alternativa segura.

## Instrumentación

Metadata Court publica duraciones observables: `court_total_duration_ms`, `case_duration_ms`, `graph_duration_ms`, `simulation_duration_ms`, `citation_duration_ms` y `court_timings_ms`. Graph publica `operation_count`, `poll_count` cuando GraphBuilder lo observa, `snapshot_count`, `batch_count`, `episode_count` e `input_characters`; Court agrega `graph_operation_count`, `graph_poll_count`, `graph_snapshot_count`, `graph_input_characters`, `case_source_count`, `sources_count` y `citations_count`. Simulation publica `context_characters` y Court `simulation_context_characters`. Los subtimings A/B/Judge y un contador físico de requests no se inventan: requieren callbacks de proveedor. El contador de generaciones del benchmark viene del fake. Los logs no incluyen prompts, texto del caso, extractos ni respuestas.

## LOCAL SYNTHETIC BENCHMARK: antes/después

| Escenario | Wall ms antes | Wall ms después | Δ | CaseService calls | Graph ops | Polls | Contexto Simulation chars antes → después | Graph input chars | Snapshots callback |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Pequeño reutilizado | 97.9 | 55.8 | −42.1 | 0 | 8 | 13 | 6.681 → 763 | 1.691 | 1 |
| Mediano reutilizado | 98.5 | 57.6 | −40.9 | 0 | 14 | 33 | 15.881 → 1.417 | 4.363 | 1 |
| Documental reutilizado | 109.6 | 63.7 | −45.9 | 0 | 28 | 73 | 34.361 → 2.757 | 9.723 | 1 |
| Nuevo | 117.8 | 77.3 | −40.5 | 1 | 14 | 33 | 15.881 → 1.417 | 4.363 | 1 |

Los cuatro escenarios registraron 3 generaciones lógicas del fake, 0 retrievals y 0 embeddings en la etapa Court. Graph operations, polls, payload y snapshots permanecieron iguales. El caso nuevo incluye ~15 ms de CaseService falso y no debe compararse como si fuese reuse. Variaciones de overhead del sistema pueden modificar wall-clock; el ahorro causal buscado es que las dos demoras de 40 ms se superpongan.

## Frontend, pruebas y límites

`taskService.js` ya programa el siguiente poll solo después de completar el anterior y aborta en cancelación/resultado terminal. Se mantuvo. NovaCourtView omite normalización y actualización visual para la misma versión, identidad y estado de Graph; GraphPanel no se rediseñó. Progress cuenta etapas completadas y admite Graph y Simulation simultáneamente en `running`.

Los tests cubren contrato estructural, concurrencia con delay, fallos independientes, reuse, aislamiento privado, deduplicación de fuente, snapshots y carreras de actualización; los tests existentes cubren citas, cancelación, provenance y deadline de Graph. Validación con proveedores reales y perfiles de latencia/costo siguen pendientes. Riesgos restantes: serialización/copia de Task para payloads grandes; polls Zep por episodio; proveedor remoto en curso tras cancelación. El código legacy de endpoints y simulación conserva deuda de producción ajena a este bloque. No se cambiaron modelos, reranker, ontology, fuentes ni decisión jurídica. Bloque 10 puede comenzar tras validar comportamiento y métricas con proveedores reales en un entorno controlado.
