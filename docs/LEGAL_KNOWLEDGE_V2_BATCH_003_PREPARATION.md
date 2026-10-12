# Legal Knowledge V2 — preparación controlada de Batch 003

## Checkpoint 10.7

NovaSearch V2 quedó cerrado en el commit local `1fa68b2` (`feat: finalize NovaSearch V2 runtime`). El operador confirmó desde MYKE frontend cuatro consultas correctas y cuatro modales con unidad completa: artículo 3 de Ley 27444; decisión del Auto 04810-2024-PA/TC; fundamento Cuarto de Casación 915-2022/ICA (págs. 5–6); y decisión de STC 04826-2025-PHC/TC (pág. 9, URL oficial). No reapareció el aviso de detalle incompleto. Baseline: 289 tests backend, 37 frontend, `compileall`, build y `git diff --check` PASS.

## Alcance del parser `legal-v2.1.2`

El nuevo cleaner retira números físicos de página **solo** cuando son una línea numérica aislada igual a la página del PDF, aparecen en la misma posición superior en al menos el 70 % de tres o más páginas (mínimo tres) y comparten otra línea de cabecera reiterada. El número no se infiere de un texto jurídico ni se elimina una cifra aislada sin ese patrón. Se mantienen los `page_start` y `page_end` de las unidades. En resoluciones de dos páginas, se retira un encabezado repetido solo cuando hay dos líneas independientes iguales en la parte superior de ambas páginas; una sola frase repetida no basta. Los tests protegen números de fundamentos, citas y líneas legales. No se cambiaron los pesos de retrieval, el RPC, el modelo de embedding ni documentos publicados.

Los manifests históricos siguen invocando `legal-v2.1.0` (Batch 001) y `legal-v2.1.1` (Batch 002). Solo candidatos nuevos usan `legal-v2.1.2`. El Auto TC 00102-2022-Q/TC pasó de un fundamento cuarto contaminado por la cabecera de la segunda página a un fundamento continuo de páginas 1–2. En otras casaciones, la línea de folio secuencial desaparece, pero siguen defectos distintos que impiden aprobarlas.

**Palabras partidas:** se comprobó que `sent enciado`, `Ju sticia`, `casaci ón` y variantes ya aparecen en la extracción PDF. Una unión por diccionario o por longitud podría cambiar nombres, citas o términos jurídicos válidos. No se aplicó reparación agresiva ni extractor layout global. La casación ya publicada que contiene ruido queda como `REINGESTION_CANDIDATE`, sin cambio de fila, hash, versión ni vector en este bloque. También permanecen intactos los otros cinco documentos publicados.

## Recalificación offline de 135 originales

Se ejecutó **una** pasada completa de `python -m app.legal_ingestion.corpus_audit` tras los tests. El audit verifica SHA-256 de cada original, bloquea conexiones de red y no llama a OpenAI, embeddings ni base de datos. El resultado está en [calificación Batch 003](LEGAL_KNOWLEDGE_V2_CORPUS_BATCH_003.json); el artefacto histórico de Batch 002 permanece intacto.

| Clasificación | Artefacto anterior | Batch 003 |
| --- | ---: | ---: |
| `PUBLISHABLE` | 2 | 2 |
| `REVIEW_REQUIRED` | 125 | 123 |
| `OCR_REQUIRED` | 3 | 3 |
| `INVALID_SOURCE` | 2 | 2 |
| `ALREADY_PUBLISHED` | 3 | 5 |
| **Total** | **135** | **135** |

Los dos `PUBLISHABLE` anteriores se publicaron en Batch 002 y pasan a `ALREADY_PUBLISHED`; dos fuentes nuevas superan gate y revisión. El sexto documento V2 publicado es un segmento normativo de un original mayor, por eso el inventario físico cuenta cinco originales `ALREADY_PUBLISHED`. Hay 12.324 unidades brutas en el audit; **solo 28** unidades corresponden a los dos candidatos aprobados.

## Revisión manual contra originales

La [revisión ligada a hashes](LEGAL_KNOWLEDGE_V2_BATCH_003_REVIEW.json) conserva las dos aprobaciones y los rechazos de casaciones. Se cotejaron páginas renderizadas, identidad, tribunal/sala, expediente, fecha, apertura, unidad media, cierre, fundamentos, decisión, páginas, cabeceras y avisos. Las redacciones de nombres del TC son parte visible de los originales y no se completaron.

| Candidato | Resultado | Hallazgo |
| --- | --- | --- |
| Auto TC 00102-2022-Q/TC, 09-04-2026 | **PASS** | 2/2 páginas; 6 unidades (antecedente, cuatro fundamentos, decisión). Fundamento cuarto continuo, sin cabecera repetida; `IMPROCEDENTE` y apercibimiento coinciden con la página 2. URL oficial impresa. |
| Sentencia TC Sala Primera 1910/2025, Exp. 03902-2023-PHC/TC, 01-12-2025 | **PASS** | 9/9 páginas; 22 unidades (dos antecedentes, 19 fundamentos, decisión). `FUNDADA` y nulidad de dos resoluciones cotejadas con página 9; páginas 1–9 y URL oficial impresas. Marcadores de notas y firmas formales se conservan tal como figuran; no aparece cabecera ni pie de verificación dentro de unidades. |
| Casaciones 1913-2023/VENTANILLA, 1027-2025/SAN, 13554-2025, 767-2025 y 496-2025/LA LIBERTAD; Queja 1944-2025 | **FAIL** | Persisten palabras partidas extensas, apertura ausente, decisiones de dos casos mezcladas o límites jurídicos inseguros. Ninguna entra al manifest. |

Se priorizó jurisprudencia de Corte Suprema, pero ningún caso nuevo alcanzó calidad suficiente. El tamaño del lote queda en dos documentos; no se fuerza la meta orientativa de 5–15.

## Manifest e inspección

El [manifest Batch 003](LEGAL_KNOWLEDGE_V2_BATCH_003.json) contiene identificadores estables, rutas, SHA-256 físico y documental, parser, tipo, estado y cantidad esperada. Son **2 documentos / 28 unidades / 28 embeddings futuros**, si se autoriza una publicación posterior. No contiene texto jurídico, vectores ni secretos.

`python -m app.legal_ingestion.corpus_cli inspect-batch ..\docs\LEGAL_KNOWLEDGE_V2_BATCH_003.json` devolvió `PUBLISHABLE`, parser `legal-v2.1.2`, hashes correctos y 6/22 unidades en la sesión offline de Codex. Después, el operador verificó en su PowerShell privada de MYKE Legal **6 documentos / 64 unidades / 0 relaciones / 6 runs** y confirmó para ambos candidatos `PUBLISHABLE`, `PRESENCE=NOT_PRESENT`, 6 y 22 unidades. La habilitación posterior añadió exclusivamente Batch 003 a la allowlist de `publish-batch`, con baseline `(6, 64, 0, 6)`; 001 y 002 permanecen habilitados y manifests ajenos o alterados siguen bloqueados. La habilitación de código no generó embeddings ni insertó documentos.

## Tests y siguiente gate

`python -m compileall -q app tests` y suite backend completa **296/296 PASS**. El frontend no se modificó durante Batch 003, por lo que sus 37 tests y build del checkpoint 10.7 conservan su resultado. Se agregaron tests positivos y negativos para folio secuencial, cabeceras de dos páginas y reproducibilidad del parser 2.1.1; la CLI verifica que 003 está habilitado para publicar solo con manifest aprobado y baseline remoto exacto.

**GO para que el operador publique Batch 003 en un paso separado desde PowerShell**, sujeto a que el preflight de la CLI siga encontrando los conteos y la identidad esperados. Este bloque únicamente habilita el safety gate y ejecuta tests; no ejecuta `publish-batch`, OpenAI, embeddings, inserts ni push.

Comando reservado al operador, desde una PowerShell con `MYKE_LEGAL_DATABASE_URL` de MYKE Legal y `OPENAI_API_KEY` configuradas:

```powershell
cd D:\NovaIuris\backend
python -m app.legal_ingestion.corpus_cli publish-batch ..\docs\LEGAL_KNOWLEDGE_V2_BATCH_003.json
```
