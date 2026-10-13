# Legal Knowledge V2 — Batch 006, preparación offline

## Alcance y punto de partida

Batch 005 está cerrado con `PUBLICATION_PASS`. El estado remoto comunicado por el operador es **10 documentos / 144 unidades / 0 relaciones / 10 runs**. Esta preparación no consulta ni escribe Supabase, no publica, no genera embeddings y no habilita Batch 006 en `PUBLISH_BASELINES`. Los diez documentos publicados se reproducen con sus versiones históricas: Batch 001 `legal-v2.1.0`, Batch 002 `legal-v2.1.1`, Batches 003–004 `legal-v2.1.2` y Batch 005 `legal-v2.1.3`.

## Causas de `REVIEW_REQUIRED` antes de los fixes

Se analizaron los **121** registros `REVIEW_REQUIRED` de la [calificación Batch 005](LEGAL_KNOWLEDGE_V2_CORPUS_BATCH_005.json) antes de elegir originales. Por causa dominante del auditor: **95** con quality gate bloqueado, **16** con gate superado pero revisión manual pendiente, **6** duplicados exactos y **4** fuentes distintas del mismo caso sin reconciliar. Los indicadores siguientes se superponen; no deben sumarse como documentos distintos.

| Causa / indicador en los 121 registros | Documentos | Lectura |
| --- | ---: | --- |
| Fecha o tipo jurisprudencial incompleto | 60 | Warning del gate; combina ambos campos. |
| Identidad jurisprudencial incompleta | 49 | Warning del gate; tribunal o expediente ausente. |
| Decisión no detectada | 24 | Límite de decisión inseguro. |
| Numeración o agrupación de fundamentos | 16 | Unión de `multiple_foundations_in_one_unit` y `foundation_numbering_review_required`. |
| Voto mezclado con decisión | 5 | Límite de voto inseguro. |
| Estructura sobredimensionada | 22 | Requiere revisión de límites; puede coexistir con metadatos faltantes. |
| Sin unidades legales | 9 | Extracción o estructura no segura. |
| Hash de unidad duplicado | 5 | Estructura mixta o repetida. |
| Número de norma ausente | 11 | Metadato normativo incompleto. |
| Texto editorial o enmienda versionada mezclada con norma | 13 | Requiere separación jurídica manual. |
| Duplicado exacto / mismo caso con otra fuente | 6 / 4 | Exclusión o reconciliación pendiente. |
| Page furniture eliminado | 92 | Warning informativo de limpieza; no prueba por sí solo bloqueo residual. |

En los 94 registros jurisprudenciales no duplicados, los metadatos ausentes se desglosan en fecha **40**, tipo de resolución **26**, expediente **46** y tribunal **20**; estos conteos también se superponen. `page_issue_count` es **0** en los 121 registros, pero ese campo solo detecta paginación ausente de unidades. El auditor no etiqueta globalmente folios incrustados, cabeceras/pies residuales ni notas mezcladas: no existe un conteo exhaustivo fiable para esas tres causas. Se cotejaron en la revisión manual y son motivo de rechazo cuando afectan límites o lectura. También se observaron fuentes con tipo aparente equivocado, estructura duplicada/mixta y extracción no segura; no se reclasificaron para completar el lote.

## Fixes generalizables en `legal-v2.1.4`

1. **Fecha explícita del TC.** Solo en el encabezado de una sentencia del Tribunal Constitucional, se admite `En Lima, al 1 de octubre de 202 4` y una fecha completa en línea propia bajo `PLENO JURISDICCIONAL`. Se valida calendario y no se toma una fecha citada en los antecedentes. La separación interna del año se interpreta únicamente en este campo de metadatos; el texto canónico queda intacto.
2. **Listas numeradas citadas.** Una lista introducida expresamente con «lo siguiente», «son las siguientes» o «en los siguientes términos» permanece dentro del fundamento que la cita aunque reinicie en 1 o salte de número. La numeración principal se reanuda al aparecer el siguiente fundamento esperado. Se comprobó en varios PDFs; sin intro explícita, la regla no actúa.

Las dos reglas tienen tests positivos y negativos. `legal-v2.1.3` y versiones anteriores conservan las reglas previas por selección explícita de versión. No se unen palabras partidas ni se eliminan notas o contenido sustantivo.

## Recalificación offline del corpus completo

Tras estabilizar los fixes y registrar la revisión, se hizo **una** pasada de `python -m app.legal_ingestion.corpus_audit` sobre los 135 originales. El auditor verifica SHA-256, bloquea conexiones de red, conserva los artefactos históricos y escribe la [calificación Batch 006](LEGAL_KNOWLEDGE_V2_CORPUS_BATCH_006.json). La fuente de Batch 005 se marca como publicada. El inventario cuenta originales físicos; su hash coincide además con una copia exacta, por lo que `ALREADY_PUBLISHED` aumenta en dos filas físicas mientras la base remota añadió un documento.

| Categoría | Antes: Batch 005 | Después: Batch 006 |
| --- | ---: | ---: |
| `PUBLISHABLE` | 1 | 3 |
| `REVIEW_REQUIRED` | 121 | 117 |
| `OCR_REQUIRED` | 3 | 3 |
| `INVALID_SOURCE` | 2 | 2 |
| `ALREADY_PUBLISHED` | 8 | 10 |
| **Total** | **135** | **135** |

La selección tiene **3 sentencias TC / 130 unidades / 130 embeddings futuros**. Es menor que el objetivo orientativo de 5–15 documentos porque los demás conservan defectos o carecen de revisión suficiente.

## Revisión manual y selección

La [revisión ligada a hashes](LEGAL_KNOWLEDGE_V2_BATCH_006_REVIEW.json) registra `MANUAL_REVIEW=PASS` para cada documento seleccionado. Se cotejaron identidad, fecha, expediente, órgano, tipo, URL impresa, primera/unidad media/última, fundamentos, decisión, votos, rangos de página, cabeceras, pies, notas, ruido y warnings con los PDF originales.

| Expediente | Páginas | Fundamentos | Decisión | Votos | Unidades | Revisión |
| --- | ---: | --- | --- | --- | ---: | --- |
| 00782-2023-PHC/TC | 14 | 1–11, págs. 7–10 | IMPROCEDENTE, pág. 10 | Dos fundamentos y un singular, págs. 11–14 | 18 | PASS |
| 02047-2025-PA/TC | 11 | 1–15, págs. 3–7 | FUNDADA y reposición, pág. 7 | Uno dirimente y uno singular, págs. 8–11 | 20 | PASS |
| 02545-2023-PA/TC | 37 | 1–88, págs. 3–35 | IMPROCEDENTE en parte y FUNDADA en parte, pág. 35 | Fundamento de voto, págs. 36–37 | 92 | PASS |

Los tres cubren todas sus páginas con unidades, no tienen hash de unidad duplicado ni páginas de unidad ausentes. Después de la primera unidad, ningún bloque extraído de más de 30 caracteres queda fuera de las unidades tras la limpieza de page furniture. La calificación solo deja warnings informativos de `page_furniture_removed` (75, 38 y 153). Los nombres ocultos en el PDF de 02545 permanecen ocultos; no se reconstruye texto. Los títulos de origen editoriales y algunas notas impresas siguen documentados.

**FAIL y fuera del manifest:** 00800-2024-PHC/TC conserva referencias de folio mezcladas con el razonamiento; 00005-2025-PI/TC y 00004-2024-PI/TC pasan el gate de fecha, pero el índice inicial genera unidades falsas antes del cuerpo; 04235-2023-PHC/TC extrae como expediente principal una causa citada. El fix de fechas no convierte automáticamente estos documentos en candidatos. Otras casaciones con palabras partidas, aperturas o sumillas inseguras siguen fuera. No se corrigió `sent enciado`, `Ju sticia`, `casaci ón` ni otros cortes de palabras sin regla objetivamente segura.

## Manifest e inspección offline

El [manifest Batch 006](LEGAL_KNOWLEDGE_V2_BATCH_006.json) fija ID estable, ruta, hash original, hash documental, parser `legal-v2.1.4`, tipo `judgment`, 130 unidades en total y calidad `PUBLISHABLE`. Se coteja con la calificación, los originales y el staging antes de inspeccionar. Tras la confirmación remota del operador, Batch 006 quedó habilitado en `PUBLISH_BASELINES` con baseline **`(10, 144, 0, 10)`**. Batches 001–005 permanecen habilitados y los desconocidos bloqueados.

```powershell
cd D:\NovaIuris\backend
python -m app.legal_ingestion.corpus_cli inspect-batch ..\docs\LEGAL_KNOWLEDGE_V2_BATCH_006.json
```

Sin DSN, `PRESENCE=UNVERIFIED_OFFLINE` es el resultado correcto en una sesión offline. Después, el operador confirmó **10 documentos / 144 unidades / 0 relaciones / 10 runs** en MYKE Legal. Los tres ítems devolvieron `PUBLISHABLE`, tipo `judgment`, parser `legal-v2.1.4`, 18/20/92 unidades, hashes `ae9f33a522ba` / `4c00e176592d` / `13bc8abe6fa0` y `PRESENCE=NOT_PRESENT` para los IDs del manifest. La CLI vuelve a validar manifest, hashes, parser, identidad y conteos antes de cada embedding; una discrepancia implica NO-GO.

Esta habilitación local no ejecutó `publish-batch`, no generó embeddings ni escribió en Supabase. **GO para que el operador publique Batch 006 desde PowerShell en un paso separado**, sujeto al preflight de la CLI. No se modificaron documentos ya publicados.
