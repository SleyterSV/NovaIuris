# Legal Knowledge V2 — calificación del corpus original (bloque 10.6A)

> Esta es la línea base histórica de 10.6A. La recalificación con parser `legal-v2.1.0`, dos fuentes aprobadas y Batch 001 se documenta en [Corpus Recovery 10.6A.1](LEGAL_KNOWLEDGE_V2_CORPUS_RECOVERY.md); no se sobrescriben los resultados originales de este bloque.

## Método y alcance

Se calificaron **135 archivos originales**: 13 DOCX normativos de `raw_docs/` y 122 PDF de `backend/raw_docs/jurisprudencia/`. El inventario anterior había identificado 13 JSON en `processed_docs`; son derivados y no se usaron. Se ejecutó `stage_file()` sobre cada fuente elegible, con `socket.connect` y `socket.create_connection` bloqueados durante todo el dry-run. No hubo OpenAI, embeddings nuevos ni escritura en ninguna base. El [JSON de auditoría](LEGAL_KNOWLEDGE_V2_CORPUS_QUALIFICATION.json) conserva ruta, tamaño, formato, hashes, metadatos extraídos, tipos y cantidad de unidades, warnings, clasificación y colas; no guarda texto jurídico completo ni vectores.

La clasificación usa el gate V2 **más revisión focalizada de los 14 candidatos `staged`**. `high` en `extraction_quality` indica volumen y ausencia de caracteres de reemplazo; no acredita por sí solo orden de columnas, identidad, ausencia de texto editorial ni integridad jurídica. Ningún candidato se promovió a `PUBLISHABLE` por pasar solo el gate automático. Las causas de review pueden solaparse y los conteos de la cola por causa **no se suman**.

El Decreto Supremo 006-2026-JUS publicado es el segmento `promulgating_instrument` dentro de `raw_docs/LEY DEL PROCEDIMIENTO ADMINISTRATIVO GENERAL.docx`: su hash aprobado y sus cinco unidades se verificaron offline. El DOCX completo se calificó también, porque contiene el TUO anexo todavía **no publicado**; por eso ese archivo físico está en `REVIEW_REQUIRED`, con el segmento publicado señalado aparte. El PDF completo del Auto TC 04810-2024-PA/TC conserva el hash aprobado, diez unidades y categoría `ALREADY_PUBLISHED`. Ambos quedan excluidos de 10.6B y de la estimación de embeddings nuevos.

## Inventario y clasificación

| Categoría del archivo físico | Normas | Jurisprudencia | Total | Interpretación |
| --- | ---: | ---: | ---: | --- |
| `PUBLISHABLE` | 0 | 0 | **0** | Gate y revisión completos. |
| `REVIEW_REQUIRED` | 13 | 116 | **129** | Incluye 14 candidatos que pasaron el gate pero tienen bloqueos manuales. |
| `OCR_REQUIRED` | 0 | 3 | **3** | PDF sin texto extraíble; no se intentó OCR. |
| `INVALID_SOURCE` | 0 | 2 | **2** | Archivos `.pdf` que contienen HTML en lugar de firma PDF. |
| `ALREADY_PUBLISHED` | 0 | 1 | **1** | PDF del Auto TC. El decreto es un segmento publicado dentro de uno de los 13 DOCX. |
| **Total físico** | **13** | **122** | **135** | Dos documentos lógicos publicados en MYKE Legal. |

Las 130 fuentes con texto recibieron `extraction_quality=high`; tres requirieron OCR y dos tenían firma inválida. La revisión encontró errores que esa métrica simple no detecta, como espacios intrapalabra, nombres incompletos, tipo de resolución equivocado y dos fallos incompatibles mezclados.

## Unidades del dry-run

El pipeline generó **12 974 unidades** sobre fuentes no marcadas como Auto ya publicado ni inválidas. Esta cifra es **bruta para auditoría, no volumen listo para embeddings**: incluye documentos en revisión, tres OCR con cero unidades y el DOCX completo cuyo decreto inicial ya fue publicado como segmento. No debe utilizarse para preparar una carga.

| Tipo | Unidades |
| --- | ---: |
| `article` | 6 135 |
| `foundation` | 5 487 |
| `decision` | 433 |
| `disposition` | 241 |
| `concordance` | 346 |
| Otros (`antecedent`, `sumilla`, `matter`, `separate_opinion`, `amendment_note`) | 332 |
| **Total bruto** | **12 974** |

Se registraron 1 894 partes de unidades subdivididas, 18 repeticiones internas de `content_hash` en seis archivos, y 90 archivos con al menos un warning de identidad/número/fecha mínima. El gate automático no emitió warnings de procedencia de página; esto **no equivale a validar visualmente todas las páginas**. En los DOCX las páginas permanecen nulas. No se inventaron URLs oficiales ni vigencia.

## Calidad y review queue

La cola completa por archivo y causas está en el JSON; `review_queue.record_indexes` remite a posiciones de `records` empezando en cero. Prioridades principales (grupos superpuestos):

| Grupo | Archivos | Trabajo necesario antes de requalificar |
| --- | ---: | --- |
| A. Parser generalizable | 52 | Entre ellos, **15** resoluciones cuyo `document_type` contradice `resolution_type`, además de decisiones no detectadas, ordinales sospechosos y fundamentos fusionados. La inferencia por nombre de archivo falla para varias casaciones y un Auto; un PDF jurisprudencial fue interpretado como constitución. Requiere fix general y tests, no override por archivo. |
| B. Límite de fuente/extracción identificado manualmente | 7 | Revisar PDF con espacios intrapalabra, números/identidades incompletos, sumilla que absorbe la apertura y muebles de página dentro de un fundamento. Es un mínimo de casos explícitamente inspeccionados, no la prevalencia total. |
| C. Versiones mezcladas | 12 | Separar texto sustituido o incorporado del texto vigente antes de publicar. |
| D. Contaminación editorial | 10 | Notas SPIJ/fe de erratas dentro de artículos y disposiciones. |
| E. Metadata mínima incompleta | 90 | Número normativo o identidad/fecha/tipo jurisprudencial insuficientes según gate. |
| Estructura u opiniones | 68 | Unidades enormes, ordinales reiniciados, fundamentos fusionados y voto separado dentro de decisión. |
| Duplicación de fuente/identidad | 10 | Confirmar canónico y cotejar expedientes compartidos con contenido distinto. |
| F. OCR | 3 | Digitalización/OCR fuera de este bloque; volver a gate y revisión. |

Los **14 `staged`** sumaban 374 unidades y aproximadamente 490 518 caracteres de `search_text` (70 431 tokens estimados por las unidades), pero todos quedaron en revisión manual. Hallazgos concretos: una casación de 6 unidades quedó como `judgment`, con sumilla que absorbe `AUTOS y VISTOS` y palabras deformadas; otra queja contiene dos decisiones contrapuestas; una sentencia TC de 37 páginas deja un antecedente aislado de ocho caracteres y un voto dentro de la decisión; un Auto TC de dos páginas quedó como `judgment` y conserva texto de autenticidad de página en un fundamento; dos PDFs TC con 38 unidades cada uno son copias byte a byte. Otros candidatos muestran nombres vacíos o palabras/números separados por la extracción PDF. Estos ejemplos prueban que `staged` todavía necesita control humano y que no sería seguro generar sus embeddings ahora.

### OCR queue

Tres PDF no entregan texto suficiente; su `document_hash` extraído corresponde a texto vacío y **no** demuestra que sean el mismo documento. Sus rutas exactas están en `ocr_queue` del JSON:

1. `Asignación_anticipada_de_alimentos_cesa_cuando_existe_sentencia_firme_que_fija___.pdf`.
2. `Corte_Suprema_ordena_reposición_de_docente_destituido_por_condena_en_delito___.pdf`.
3. `Jueces_incluyen_gráficos_en_su_resolución_para_hacerla_más_comprensible__Expediente___.pdf`.

Los otros dos archivos con extensión `.pdf` y contenido HTML quedaron `INVALID_SOURCE`; no se pasaron por el parser PDF ni se trataron como jurisprudencia publicable. Antes de calificarlos hace falta recuperar/verificar el original correcto o registrar conscientemente su formato real.

## Duplicados y variantes

Se encontraron **cinco grupos de PDF con SHA-256 de archivo idéntico**, que abarcan 11 rutas y **seis copias sobrantes**. El JSON señala representante y copias mediante `exact_duplicate_of`; ninguna se borró. Uno de esos grupos es el par TC 00697-2024-PA/TC que pasó el gate, pero ambas copias siguen en revisión por dos unidades `decision`. Hay además **dos expedientes compartidos por fuentes con hashes distintos** (`00005-2020-PI/TC` y `01350-2024-PA/TC`): requieren cotejo, pues podrían ser resoluciones o versiones distintas. **Variantes de versión confirmadas: 0.** No se deduplicó por texto ni se fusionaron decisiones.

## Embeddings y plan de 10.6B

**Elegibles hoy:** 0 documentos / 0 unidades / **0 embeddings** / 0 caracteres por vectorizar. Los 374 posibles embeddings de candidatos que superaron el gate están **bloqueados** por revisión. La cifra bruta de 12 974 unidades no es una orden de generación ni una estimación de costo. No se calculó precio monetario.

**Lotes listos para publicar: ninguno.** Por ello no hay «batch 1» ejecutable ni orden de publicación de documentos concretos. Secuencia **condicional** tras corregir y volver a calificar, sin incluir fuentes `review_required` por anticipado:

| Orden futuro | Tipo | Documentos y unidades hoy autorizados | Embeddings hoy autorizados | Condición |
| --- | --- | ---: | ---: | --- |
| 1 | Jurisprudencia TC corta y limpia | 0 / 0 | 0 | Identidad, decisión única, texto y páginas cotejados. |
| 2 | Casaciones Corte Suprema | 0 / 0 | 0 | Tipo documental corregido, sumilla/decisión y extracción limpias. |
| 3 | Normas simples | 0 / 0 | 0 | Número, versión, artículos y notas editoriales resueltos. |
| 4 | Códigos y normas complejas | 0 / 0 | 0 | Disposiciones/anexos y unidades grandes revisados. |

Para el primer lote que finalmente pase revisión, recomendar **1–3 documentos** y alrededor de **100 unidades por lote cuando sea viable**, con verificación de hash/idempotencia y conteos tras cada documento. El `PublicationAdapter` mantiene transacción por documento y batches configurables; las cifras finales se recalculan después de aprobar originales concretos. No se agrupan cientos de documentos en una transacción.

## Estado remoto y decisión

La consulta SQL remota de solo lectura al proyecto vinculado **MYKE Legal** (`emelxkoztshmzukydqzj`) confirmó `legal_documents=2`, `legal_units=15`, `legal_relations=0`, `legal_ingestion_runs=2`. Los dos documentos piloto siguen siendo los únicos publicados. Fiscal.IA, MOV.IA, Auth, NovaSearch y el runtime MYKE no se modificaron.

**NO-GO para ejecutar 10.6B ahora:** no existe aún un documento adicional que satisfaga gate **y** revisión profesional. La siguiente acción es corregir los bugs generales de clasificación/segmentación, cotejar los candidatos de mayor valor con sus originales, reejecutar el dry-run afectado y construir entonces el primer lote real. Este bloque solo califica y planifica; no inició embeddings ni publicación.
