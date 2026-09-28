# NovaCase: performance del Bloque 6

## Alcance y baseline lógico

El flujo vigente es: recuperación inicial del expediente → análisis de hechos → estrategia inicial → investigación pública → argumentos → evidencia y riesgos en paralelo → contraargumentos → estrategia final determinista → informe → resolución determinista de citas. La vista activa usa un solo polling secuencial de `taskService.js`; el composable antiguo `useNovaCase.js` no participa en este flujo.

| Etapa | Entrada principal | Operación externa normal | Dependencia |
| --- | --- | --- | --- |
| Contexto privado | `case_id`, `document_ids`, relato | 1 embedding y 1 lectura local del corpus, si hay documentos | Recepción |
| Hechos | Relato y fragmentos privados seleccionados | 1 generación LLM | Contexto privado |
| Estrategia inicial | Análisis estructurado | 1 generación LLM | Hechos |
| Investigación | Hasta `CASE_RESEARCH_MAX_QUERIES` consultas | Por consulta: 1 embedding y 1 retrieval/RPC si no falla; sin respuesta LLM ni reranking | Estrategia |
| Argumentos | Análisis, estrategia y fuentes recuperadas | 1 generación LLM | Investigación |
| Evidencia y riesgos | Análisis, argumentos y fragmentos | 1 generación LLM por servicio, en paralelo | Argumentos |
| Contraargumentos | Argumentos, evidencia y riesgos | 1 generación LLM | Ambas evaluaciones |
| Estrategia final | Resultados anteriores | 0 llamadas externas | Contraargumentos |
| Informe | Resultado estructurado y fuentes seleccionadas | 1 generación LLM | Estrategia final |
| Citas | Informe y fuentes incluidas en el prompt | 0 llamadas externas | Informe |

En un caso exitoso hay **7 invocaciones lógicas a servicios de generación LLM**, más investigación y contexto privado. Los reintentos de embeddings (máximo 3 intentos en `EmbeddingService`) pueden elevar las llamadas físicas en caso de error; el cliente OpenAI de los servicios jurídicos tiene `max_retries=0`. No se añadió otro nivel de retry en el orquestador. Los contadores de metadata miden invocaciones de servicio y operaciones iniciadas, no consumo facturado ni requests físicos después de retries o cache interno.

## Mediciones locales antes y después

Ejecutar desde `backend`: `python -m scripts.bench_case_synthetic`. Usa exclusivamente los fakes de test, textos ficticios y demoras de 2 ms por servicio. No mide proveedores ni predice latencia real. `document_input_chars` es la suma de caracteres de la representación JSON documental que reciben argumentos, evidencia, riesgos y contraargumentos; es una medida de payload, no tokens facturados.

| Escenario | Generaciones antes → después | Búsquedas antes → después | Embedding/retrieval iniciados antes → después | Contexto privado antes → después | `document_input_chars` antes → después | Tiempo sintético antes → después |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Pequeño | 7 → 7 | 1 → 1 | 1/1 → 1/1 | 0 → 0 | 336 → 916 | 27.17 → 27.51 ms |
| Mediano, consultas equivalentes | 7 → 7 | 4 → 2 | 4/4 → 2/2 | 0 → 0 | 336 → 916 | 25.08 → 23.70 ms |
| Documental, 8 fragmentos | 7 → 7 | 4 → 2 | 5/5 → 3/3 | 1 → 1 | 68 784 → 34 580 | 24.48 → 24.36 ms |

El payload pequeño crece porque ahora lleva `source_id` y localización verificable. En el caso documental se elimina la copia repetida de cada excerpt dentro del objeto `source`, conservando el texto exacto una vez por documento y los campos de procedencia. Los tiempos de pared son muy sensibles al ruido del entorno a esta escala; las reducciones demostradas son el número de búsquedas y el tamaño del payload documental. La duración real con proveedores **requiere validación runtime posterior**.

## Cambios y salvaguardas

- Las consultas equivalentes por espacios y mayúsculas se deduplican sin reescribir la primera consulta. El máximo configurable conserva un tope de seguridad de 12; la concurrencia de investigación sigue limitada a cuatro workers.
- `CaseExecutionContext` vive solo durante `analyze_case`. Su clave privada incluye `case_id`, IDs de documentos y versión/hash del manifest. La clave de investigación incluye consulta y filtros. Los resultados de otro caso nunca comparten este cache.
- Los documentos públicos y fragmentos del expediente se proyectan una vez para los cuatro prompts posteriores. Se conserva `source_id`, texto exacto, archivo, página/sección y metadata jurídica presente. El resultado público de investigación mantiene su contrato completo.
- `CaseExecutionMetrics` registra `timings_ms` para `intake`, `case_context`, `facts`, `strategy`, `research`, `arguments`, `evidence`, `risks`, `counter_arguments`, `final_strategy`, `report`, `citations` y `total`. `counts` informa invocaciones LLM, búsquedas, embeddings y retrieval observados. `input_characters` informa tamaños de relato, contexto privado, consultas y texto documental posterior. Los logs no contienen estos textos.
- `normalize_case_result` conserva la protección frente a mutaciones del llamador con una sola copia profunda del resultado. El frontend sigue recibiendo una respuesta canónica idéntica en estructura.
- La cancelación se comprueba antes de cada nueva etapa, búsqueda, embedding y lectura privada. Una solicitud externa ya iniciada no admite interrupción dura. Los jobs permanecen en memoria por proceso.

## Trabajo secuencial y oportunidades futuras

Hechos, estrategia, investigación, argumentos, contraargumentos e informe dependen de la salida anterior. Evidencia y riesgos sí se ejecutan en paralelo. El ingreso documental usa batch embeddings durante la indexación existente; la recuperación del caso usa un embedding para su consulta. No se añadió un batch nuevo para queries de NovaSearch porque exigiría cambiar su contrato y evaluar el efecto en recuperación.

`FUTURE_OPTIMIZATION`: medir con proveedores reales, analizar consultas jurídicas redundantes más allá de coincidencias seguras, valorar la selección focalizada de fragmentos por etapa y revisar el peso del bundle Markdown. Cambiar modelos, eliminar investigación, truncar prompts agresivamente o compartir cache privado entre casos requiere una evaluación de calidad separada. También quedan pendientes workers distribuidos, persistencia de tareas y autorización multiusuario para producción.
