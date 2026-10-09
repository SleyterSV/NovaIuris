# Legal Knowledge V2 — preparación Batch 002 (10.6A.2)

## Alcance y checkout

Checkout `D:\NovaIuris`, rama `feat/legal-knowledge-v2`, sobre `4071cd3` al iniciar el bloque; `fc09e8d` y `4071cd3` pertenecen al historial. Batch 001 permanece cerrado y sus dos Autos TC no fueron modificados ni republicados. Esta preparación no ejecutó embeddings, OpenAI, publicación, inserts ni push.

## Parser y reproducibilidad

El parser actual es `legal-v2.1.1`. `stage_file(..., parser_version="legal-v2.1.0")` conserva la interpretación histórica del Batch 001. La CLI toma la versión declarada por cada entrada del manifest. Se verificaron directamente los dos hashes documentales, IDs estables y conteos de 12 y 11 unidades del [manifest Batch 001](LEGAL_KNOWLEDGE_V2_BATCH_001.json), sin restaging implícito a la versión nueva.

Los cambios generales de `legal-v2.1.1` reconocen **Séptimo** como ordinal de fundamento, unen un subtítulo corto al siguiente fundamento numerado, retiran el pie completo de verificación TC cuando se reconoce su secuencia y URL, amplían la detección de cabeceras repetidas en las primeras líneas de página y preservan la URL oficial TC solo cuando está impresa en la fuente. La identidad se obtiene de los bloques originales antes de limpiar cabeceras. No se activó PyMuPDF como extractor global, ni reglas por filename. El gate conserva bloqueos ante fundamentos mezclados, votos combinados, calidad insuficiente y referencias ambiguas.

## Corpus: antes y después

El único audit offline de los **135 originales** comprobó cada SHA-256 físico y bloqueó conexiones de red. Su salida automática, previa a la revisión de este lote, fue: 0 `PUBLISHABLE`, 129 `REVIEW_REQUIRED`, 3 `OCR_REQUIRED`, 2 `INVALID_SOURCE`, 1 `ALREADY_PUBLISHED`. La revisión histórica de Batch 001 se había ligado a `legal-v2.1.0`; por eso sus dos fuentes aparecieron temporalmente como pendientes bajo la versión nueva. Se reclasificaron por los hashes del manifest **ya publicado**, sin volver a analizarlas. La aprobación manual de Batch 002 se aplicó solo a los dos candidatos documentados abajo, con la misma versión, hash y cantidad de unidades obtenidos en el audit. El archivo [de calificación](LEGAL_KNOWLEDGE_V2_CORPUS_RECOVERY.json) conserva las métricas y clasificación final:

| Estado | Antes de 10.6A.2 | Después de revisión |
| --- | ---: | ---: |
| `PUBLISHABLE` | 2 (Batch 001, ya publicado) | 2 (Batch 002, pendiente) |
| `REVIEW_REQUIRED` | 127 | 125 |
| `OCR_REQUIRED` | 3 | 3 |
| `INVALID_SOURCE` | 2 | 2 |
| `ALREADY_PUBLISHED` | 1 | 3 |
| **Total** | **135** | **135** |

La calificación final contiene 12.350 unidades brutas, de las que solo **26** corresponden a fuentes aprobadas para este lote. Las unidades brutas pendientes no quedan autorizadas para embeddings.

## Revisión manual

Se contrastaron todos los folios renderizados, la extracción de los originales y las primeras, intermedias y últimas unidades. Las aprobaciones están ligadas a hash de archivo, hash documental, parser y cantidad en [Batch 002 review](LEGAL_KNOWLEDGE_V2_BATCH_002_REVIEW.json).

| Fuente | Revisión | Evidencia y límite |
| --- | --- | --- |
| Casación **915-2022/ICA**, Corte Suprema, Sala Penal Permanente, 09-10-2025 | **PASS** | 8/8 páginas; 15 unidades: antecedente, 13 fundamentos en dos series, decisión `INFUNDADO` y `NO CASARON`. `Séptimo` queda separado; páginas 1–8 conservadas. El resumen inicial no lleva rótulo formal `Sumilla` y no se atribuyó ese metadato. La fuente redistribuida mantiene marca editorial; aparecen cifras aisladas de folio, notas al pie y espacios de extracción en algunas unidades, sin alterar el sentido jurídico verificado. |
| Sentencia TC **04826-2025-PHC/TC**, Pleno, 31-03-2026 | **PASS** | 9/9 páginas; 11 unidades: tres partes técnicas de antecedentes, fundamentos 1–7 y decisión `IMPROCEDENTE`. Se verificaron court, caso, fecha, fallo, folios 1–9 y URL oficial impresa. El pie TC de verificación no se incorpora a las unidades. Redacciones de nombres son parte visible del original; no se completaron por inferencia. |
| Casación 1913-2023/VENTANILLA | **FAIL** | La fecha entra en la sumilla y la extracción parte palabras extensamente. |
| Casación 1027-2025/SAN | **FAIL** | La primera unidad recuperada comienza en la página 7 de 12; falta apertura jurídica. |
| Queja 1944-2025 | **FAIL** | Voto y decisión se mezclan, y numerales citados se convierten en fundamentos. |
| Casación 13554-2025 | **FAIL** | Pérdida de sala y límites erróneos entre antecedentes, fundamentos y decisión. |
| Casación 767-2025 | **FAIL** | Encabezados aislados y fundamento sexto fragmentado; referencias del PDF entran en unidades. |
| Casación 496-2025/LA LIBERTAD | **FAIL** | Sumilla absorbe apertura y hay fundamentos partidos artificialmente. |
| Auto TC 00102-2022-Q/TC | **FAIL** | Cabecera repetida de página 2 entra en el fundamento cuarto. |

Se priorizaron casaciones. No se forzó el tamaño hacia 5 documentos ni se aprobó una norma con versiones o material editorial mezclado.

## Manifest e inspección

El [manifest Batch 002](LEGAL_KNOWLEDGE_V2_BATCH_002.json) incluye 2 documentos: una casación y una sentencia, **26 unidades y 26 embeddings futuros** (`text-embedding-3-small`, dimensión 1536 si se autoriza 10.6B). Solo contiene identificador estable, ruta, hashes, versión, tipo, cantidad y calidad; no hay texto jurídico, vectores o secretos.

`python -m app.legal_ingestion.corpus_cli inspect-batch ..\docs\LEGAL_KNOWLEDGE_V2_BATCH_002.json` devolvió `PUBLISHABLE` para ambas fuentes, parser `legal-v2.1.1`, hashes `1d039f2be5f2` y `7f21ea2da5cb`, 15 y 11 unidades, y requerimiento estimado de 15 y 11 embeddings. La primera inspección local registró `PRESENCE=UNVERIFIED_OFFLINE` porque no había DSN en esa sesión. Posteriormente, el operador ejecutó la verificación manual desde PowerShell contra MYKE Legal (`emelxkoztshmzukydqzj`) y comunicó el resultado de solo lectura: **4 documentos / 38 unidades / 0 relaciones / 4 runs**; para `f69b94ba-0dcb-5c4b-a53a-e614cc31e2d1` y `6ec04617-5a6f-5f5f-aca4-aa4dac4c7846`, `STATUS=PUBLISHABLE`, `PARSER=legal-v2.1.1` y **`PRESENCE=NOT_PRESENT`**, con 15 y 11 embeddings requeridos respectivamente. La CLI bloquea `publish-batch` para Batch 002 en este bloque.

## Tests y decisión

El test focalizado inicial pasó (60 tests), la compilación pasó y la suite completa inicial pasó con **253 tests** (base anterior: 248). Después de habilitar el manifest 002 y el replay de Batch 001, el conjunto focalizado de CLI y audit pasó con **12 tests**. La compilación final y la suite backend completa pasaron con **255 tests**.

**10.6A.2 CLOSED — GO para iniciar 10.6B (embeddings y publicación de Batch 002).** El GO se basa en el manifest, la revisión manual, los 255 tests PASS y la verificación remota de solo lectura comunicada por el operador. No se generaron embeddings ni se ejecutó `publish-batch` en 10.6A.2; la publicación corresponde exclusivamente al bloque posterior.
