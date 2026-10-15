# Legal Knowledge V2 — Batch 007, preparación y cierre

## Estado y alcance

**La preparación offline quedó READY para inspección remota de solo lectura.** MYKE Legal contiene, según el operador, 13 documentos, 274 unidades, 0 relaciones y 13 runs después de Batch 006. No se consultó ni escribió Supabase en esta preparación. Tampoco se publicaron documentos ni se generaron embeddings. El código mantiene las versiones históricas seleccionables: 001 `legal-v2.1.0`, 002 `legal-v2.1.1`, 003–004 `legal-v2.1.2`, 005 `legal-v2.1.3` y 006 `legal-v2.1.4`. Las fuentes publicadas se reconocen por hash antes de calificar; no se reingestaron ni modificaron.

## Auditoría de 135 originales

Se completó una calificación fresca con `legal-v2.1.4` antes del fix y una calificación final con `legal-v2.1.5` después de estabilizarlo y registrar la revisión. El auditor coteja SHA-256 y bloquea conexiones de red. [Resultado final](LEGAL_KNOWLEDGE_V2_CORPUS_BATCH_007.json). `ALREADY_PUBLISHED` representa **14 archivos físicos**: los 13 documentos remotos incluyen un original que tiene una copia idéntica en el corpus. No representa un decimocuarto documento publicado.

| Categoría | Antes (`legal-v2.1.4`) | Después (`legal-v2.1.5`) |
| --- | ---: | ---: |
| `PUBLISHABLE` | 0 | 1 |
| `REVIEW_REQUIRED` | 116 | 115 |
| `OCR_REQUIRED` | 3 | 3 |
| `INVALID_SOURCE` | 2 | 2 |
| `ALREADY_PUBLISHED` | 14 | 14 |
| **TOTAL** | **135** | **135** |

El único cambio de categoría es STC 04852-2023-PA/TC tras la regla estructural y el cotejo manual. Otros documentos cuyo staging cambia permanecen bloqueados; el fix no convierte automáticamente el gate en aprobación.

## Causas dominantes de los 116 `REVIEW_REQUIRED` iniciales

Clasificación exclusiva por causa dominante, con prioridades explícitas sobre los warnings del auditor y la revisión de los 18 casos que pasaban el gate automático. Puede haber varias causas en un mismo documento; estos conteos no representan todos los indicios concurrentes.

| Causa dominante | Documentos | Ejemplo o evidencia |
| --- | ---: | --- |
| Identidad jurisprudencial incompleta | 39 | Falta expediente u órgano identificable. |
| Fecha o tipo documental incompleto | 13 | Fecha o tipo de resolución no verificable por el gate. |
| Estructura normativa mixta | 13 | Código Procesal Civil con material editorial y enmiendas. |
| Extracción insegura o sin unidades | 11 | Casación 1027-2025/SAN comienza en Cuarto; palabras partidas. |
| Numeración o límites de fundamentos | 9 | 01649-2024-PHC/TC mezcla secuencias citadas y principales. |
| Duplicado exacto de fuente | 4 | Copias de 00004-2024-PI/TC y otros casos. |
| Identidad normativa incompleta | 4 | Número de norma no acreditado. |
| Fuentes distintas del mismo caso sin reconciliar | 4 | 00005-2020-PI/TC. |
| Límites de votos | 4 | 00215-2024-PHC/TC no separa un voto singular. |
| Límites de decisión | 3 | Casación 13554-2025 crea siete unidades de decisión. |
| Índice interpretado como unidades | 3 | 00004-2024-PI/TC, 0008-2025-PI/TC y 00005-2025-PI/TC. |
| Estructura sobredimensionada | 2 | 02939-2025-PHC/TC. |
| Folios/notas mezclados | 1 | 00800-2024-PHC/TC. |
| Estructura de expedientes acumulados | 1 | 01191-2025-PHC/TC incluye 01192-2025-PHC/TC. |
| Estructura mixta | 1 | Casación 1944-2025 abre con una decisión y produce dos. |
| Precedente no verificado | 1 | 34397-2023. |
| Órgano equivocado | 1 | 02248-2020-PA/TC leído como Corte Superior. |
| Expediente principal equivocado | 1 | 04235-2023-PHC/TC toma una causa citada como identidad. |
| Subtítulo independiente antes de fundamento | 1 | 04852-2023-PA/TC; resuelto y revisado manualmente. |
| **TOTAL** | **116** | |

Los 18 casos con gate automático superado requerían revisión manual. Uno recibió cotejo integral y `PASS`; los otros 17 se excluyeron ante defectos concretos, sin forzar su publicación. En varios pendientes se encontraron folios incrustados (`01649`, `04068`, `01191`, `00800`, `01736`) y subtítulos numerados o independientes (`01191`, procesos PI y `04852`). No se eliminan folios o notas: no hay una regla general lo bastante segura. Tampoco se corrigen palabras partidas ni se reconstruyen decisiones, expedientes o votos por intuición. Los problemas de identidad, índices y fuentes múltiples siguen sin solución segura.

## Regla generalizable `legal-v2.1.5`

El parser reconoce subtítulos independientes breves, como «Análisis del caso en concreto» y «Efectos de la presente sentencia». Si aparecen inmediatamente antes del siguiente fundamento numerado consecutivo, los adjunta a ese fundamento. También conserva el encabezado `FUNDAMENTOS` y un subtítulo introductorio corto junto al fundamento 1. El texto se conserva literalmente en las unidades; no se añade ni se suprime razonamiento. La regla no se activa para prosa con puntuación, saltos de numeración, votos ni texto ajeno al contexto de fundamentos. Los tests cubren casos positivos, negativos, páginas cruzadas, preservación textual y selección reproducible de `legal-v2.1.4`. Beneficia la estructura de más de un original, pero **solo uno** quedó seguro para el lote; los demás conservan problemas independientes. La posible mejora de un documento ya publicado queda como deuda para una reingestión futura versionada, fuera de Batch 007.

## Selección y revisión manual

La [revisión ligada a hashes](LEGAL_KNOWLEDGE_V2_BATCH_007_REVIEW.json) registra 18 candidatos evaluados: **1 PASS y 17 EXCLUDED**. En los excluidos se hizo un cotejo suficiente para localizar un bloqueo; no se les atribuye una revisión integral. Ninguno se añadió al manifest.

| Expediente | Tipo | Páginas cotejadas | Unidades | Resultado |
| --- | --- | ---: | ---: | --- |
| 04852-2023-PA/TC | Sentencia TC | 9/9 | 12 | **PASS** |

En el PDF original constan Sala Segunda, Sentencia 420/2026, expediente, fecha 06-03-2026 y URL oficial. Se cotejaron antecedente en páginas 1–3, fundamentos 1–7 continuos en páginas 3–5, decisión FUNDADA y nulidad con nuevos pronunciamientos en página 5, voto Hernández Chávez en página 6 y voto singular Gutiérrez Ticse en páginas 7–9. Primera, unidad intermedia y última, límites y cruces de página se compararon contra el original. Las notas impresas se mantienen; cabeceras y pies repetidos se retiran con el warning informativo `page_furniture_removed:32`. El título del archivo es editorial y no sustituye la identidad jurídica. No hay unidades vacías ni hashes de unidad duplicados.

## Manifest e inspección

El [manifest Batch 007](LEGAL_KNOWLEDGE_V2_BATCH_007.json) contiene exclusivamente la sentencia aprobada: ID estable `0538ba67-bdad-5056-b647-6476657f58b1`, hash documental `d51354c2a420272a32900b35cec387d52cfa54d67158a25373d1faaf498fecca`, parser `legal-v2.1.5`, tipo `judgment`, **12 unidades y 12 embeddings futuros**. La CLI comprueba manifest, calificación, SHA-256 de fuente, hash documental, versión, ID y unidades al volver a staging. Durante la preparación, `PUBLISH_BASELINES` estaba limitado a 001–006 y `publish-batch` 007 se rechazaba antes de crear proveedor de embeddings.

```powershell
cd D:\NovaIuris\backend
python -m app.legal_ingestion.corpus_cli inspect-batch ..\docs\LEGAL_KNOWLEDGE_V2_BATCH_007.json
```

Inspección offline: `STATUS=PUBLISHABLE`, `PARSER=legal-v2.1.5`, `UNITS=12`, `HASH=d51354c2a420`, `EMBEDDINGS_REQUIRED=12`, `PRESENCE=UNVERIFIED_OFFLINE`. En esa fase, el resultado fue **GO únicamente para `inspect-batch` remoto de solo lectura**.

## Habilitación posterior a la inspección remota

El operador confirmó por inspección remota de solo lectura el baseline **13 documentos / 274 unidades / 0 relaciones / 13 runs** y, para el único documento, `PUBLISHABLE`, `judgment`, 12 unidades, `legal-v2.1.5`, hash `d51354c2a420`, `PRESENCE=NOT_PRESENT`. Se habilitó exclusivamente Batch 007 en `PUBLISH_BASELINES` con `(13, 274, 0, 13)`, manteniendo 001–006. La CLI exige ese conteo exacto antes de crear el proveedor de embeddings o efectuar escrituras; un batch desconocido continúa bloqueado. Esta habilitación local no ejecutó publicación, no generó embeddings y no escribió en Supabase.

## Cierre de publicación — confirmación del operador

**BATCH 007 STATUS=PUBLICATION_PASS.** El operador confirmó `STATUS=COMPLETED_AND_VERIFIED` para la **STC 04852-2023-PA/TC**, documento `0538ba67-bdad-5056-b647-6476657f58b1`, run `5a5d9aa1-220d-4742-9e6e-287bdd5dbbad`, parser `legal-v2.1.5` y hash prefijo `d51354c2a420`. La preparación offline, la revisión manual de 9/9 páginas y la inspección remota previa fueron **PASS**. La publicación ejecutada por el operador añadió **12 unidades y 12 embeddings**. Los conteos finales comunicados de MYKE Legal son **14 documentos / 286 unidades / 0 relaciones / 14 ingestion runs**. **PUBLICATION=PASS.**

La inspección posterior devolvió `STATUS=PUBLISHABLE`, `UNITS=12`, `PARSER=legal-v2.1.5`, `HASH=d51354c2a420`, `PRESENCE=ALREADY_PRESENT_AND_IDENTICAL` y `EMBEDDINGS_REQUIRED=0`: **POST-INSPECT=PASS; IDEMPOTENCY=PASS**. En el smoke test real de «¿Qué resolvió el Tribunal Constitucional en el expediente 04852-2023-PA/TC?», coincidieron expediente, documento y URL oficial. La unidad `decision` de la página 5 ocupó **rank 1**; fundamentos y votos permanecieron diferenciados: **DECISION SMOKE=PASS**. Todos estos resultados remotos fueron comunicados por el operador; este cierre no volvió a consultar la base.

Como limitación no bloqueante, un voto separado puede conservar ruido menor de extracción del PDF, incluidas palabras partidas. También puede persistir ruido editorial o de folios en algunos documentos. Estas observaciones no alteran `PUBLICATION_PASS`. Cualquier mejora futura deberá ser generalizable y versionada; este cierre no modifica texto canónico, metadatos, parser, ranking ni embeddings publicados. **BATCH 007 CLOSED.** La integración de NovaCase queda para una tarea posterior.
