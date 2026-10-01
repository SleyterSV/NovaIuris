# Bloque 8: grafo jurídico progresivo de NovaCourt

## Arquitectura

Antes, NovaCourt serializaba secciones amplias del análisis, las fragmentaba y pedía a Zep que extrajera el grafo que veía el usuario. Ese resultado no conservaba de forma fiable los identificadores ni la procedencia del `CaseResult`.

Ahora `build_graph_input` proyecta directamente el `CaseResult` ya calculado a entidades y relaciones locales. No vuelve a procesar el expediente ni cambia los modelos. `NovaCourtGraphOrchestrator` publica esa proyección como snapshot parcial, la envía en lotes mediante la API existente de `GraphBuilderService` (`create_graph`, `set_ontology`, `add_text_batches`, `_wait_for_episodes`, `get_graph_data`) y entrega un estado final. Zep confirma el procesamiento; sus inferencias no sustituyen nodos, relaciones ni procedencia verificados de la proyección local. La recuperación de Zep ocurre una vez por ejecución.

## Contratos jurídicos

El input requiere `case_id` y utiliza los campos estructurados reales `summary`, `analysis`, `facts`, `issues`, `evidence`, `arguments`, `counter_arguments`, `risks`, `timeline` y las fuentes de `sources`, `sources_used` y `research.sources`. Un `CaseResult` sin contenido proyectable devuelve `not_requested`.

La ontología canónica contiene `CASE`, `PARTY`, `CLAIM`, `LEGAL_ISSUE`, `FACT`, `EVIDENCE`, `LAW`, `JURISPRUDENCE`, `ARGUMENT`, `COUNTERARGUMENT`, `RISK`, `PROCEDURAL_ACT` y `DOCUMENT`. Los aliases históricos exactos son `Parte`, `Hecho`, `Pretensión`/`Pretension`, `Norma`, `Argumento`, `Evidencia`, `Riesgo` y `Actuación`/`Actuacion`. No se deduce el tipo a partir del título.

Cada nodo expone `node_id`, `entity_type`, `title`, `source_ids`, `origin`, `metadata` y los campos jurídicos disponibles. Los identificadores son hashes de `case_id`, tipo y clave explícita (`fact_id`, `issue_id`, `argument_id`, `source_id`, `act_id`) o, si no existe, un título normalizado de forma conservadora. La normalización compacta espacios, elimina puntuación final irrelevante y artículos iniciales para claves sin ID. No hace similitud difusa; claves explícitas distintas siguen separadas. Los nodos derivados solo del análisis se marcan `case_analysis`, sin crear fuentes ficticias.

`FACT` conserva `fact_id`, estado, fecha y fuentes. `LEGAL_ISSUE` proviene de issues reales. `EVIDENCE` proviene de vínculos de evidencia existente y conserva localizadores de documento, fragmento, página, sección y extracto cuando están disponibles; `recommended_evidence` no se proyecta. `LAW` y `JURISPRUDENCE` requieren una Source pública real. `preliminary_law` y `normas_probables` no crean autoridad. Jurisprudencia conserva tribunal, número, fecha, artículo o fundamento, URL oficial y extracto disponibles. Argumentos conservan sus IDs y referencias explícitas; contraargumentos permanecen separados y solo rebaten un argumento con ID correspondiente. Riesgos no reciben probabilidades ni scores. Actuaciones requieren `act_id`; una cronología que solo reitera hechos no crea duplicados.

Cada edge expone `edge_id`, extremos existentes, `relation_type`, `label`, `source_ids` y `metadata`. Su ID deriva de `case_id`, origen, tipo de relación y destino. El catálogo es `ASSERTS`, `SUPPORTS`, `PROVES`, `CITES`, `COUNTERS`, `CREATES_RISK`, `CONTAINED_IN` y `ARGUES`. `_RELATION_PAIRS` limita los pares permitidos, y la construcción omite extremos inexistentes. No se crean enlaces genéricos para llenar el grafo. `source_ids` y localizadores en edges solo aparecen cuando el vínculo los proporciona. La lista de fuentes se filtra por `source_scope` y `case_id`; una fuente privada de otro caso no entra en el grafo ni en su modal.

## Progreso y proveedor

El estado público contiene `status`, `graph_id`, `case_id`, `version`, `stage`, `is_final`, `nodes`, `edges`, `counts`, `warnings`, `error` y `metadata` (más contadores y mensaje para compatibilidad). La versión 1 representa la proyección local observable (`core_entities`, `building`, `is_final=false`). Tras completar Zep, la versión 2 es `completed`, `ready`, `is_final=true`. Un fallo posterior conserva el snapshot local, avanza la versión, devuelve `failed` o `timeout` con aviso público seguro y permite que la simulación continúe. El callback solo se ejecuta tras producir la proyección, sin timers de progreso ni publicaciones repetidas. El pipeline valida `case_id` y publica el resultado parcial sin sobrescribir la simulación.

Los registros de nodo y relación se envían en lotes del tamaño configurado. No hay pausa fija entre lotes. El polling de episodios aplica intervalo acotado, cancelación antes de consultar y durante el backoff, y plazo restante. El orquestador descuenta el tiempo consumido antes de esperar episodios y comparte un token de cancelación con plazo global. Cada nueva operación consulta el token; una solicitud al proveedor que ya empezó no puede interrumpirse. No se usa Zep real en los tests.

## Interfaz

`normalizeGraphState(graph, previous)` es la entrada canónica del frontend. Adapta estados legacy, completa campos seguros e ignora snapshots más antiguos del mismo caso y grafo. `GraphPanel` consume `graphData`, conserva posiciones D3 y zoom/pan al actualizar, y mantiene nodo o relación seleccionados si todavía existen. Los filtros usan `entity_type`; el checkbox marcado significa visible. La vista esencial y completa, búsqueda local por título, leyenda de tipos presentes, lista accesible y detalles de nodo o relación no mutan el grafo original. Los IDs de fuente se resuelven contra fuentes canónicas del caso y abren el `SourceModal` común. Hay estados vacíos, parciales y de error con mensajes públicos.

## Límites y siguiente bloque

La proyección solo relaciona datos enlazados explícitamente por IDs y fuentes; una fuente sin vínculo con un argumento no se presenta como prueba de ese argumento. El grafo puede ser pequeño cuando el `CaseResult` carece de IDs o fuentes. La extracción de Zep queda fuera de la autoridad documental local. El Bloque 9 queda reservado para benchmark Court completo, concurrencia global y optimización de latencia, LLM y tokens; este bloque no los implementa.
