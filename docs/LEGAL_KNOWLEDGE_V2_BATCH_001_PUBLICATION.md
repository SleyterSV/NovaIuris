# Legal Knowledge V2 — publicación Batch 001

## Alcance y resultado

**Batch ID:** `001`

**Proyecto:** MYKE Legal (`emelxkoztshmzukydqzj`)

**Manifest aprobado:** [LEGAL_KNOWLEDGE_V2_BATCH_001.json](LEGAL_KNOWLEDGE_V2_BATCH_001.json)

**Parser:** `legal-v2.1.0`

**Publicación:** 8 de octubre de 2026, entre 21:51:46 y 21:51:54 UTC, según los `legal_ingestion_runs` remotos.
**Resultado:** PASS. Solo los dos Autos TC del manifest; 23 unidades nuevas y ninguna relación.

La publicación real se ejecutó manualmente desde el PowerShell del operador mediante `corpus_cli publish-batch`. Cada documento devolvió `COMPLETED_AND_VERIFIED`. Esta auditoría posterior utilizó exclusivamente consultas SQL de lectura; no regeneró embeddings ni modificó filas.

| Orden | Documento | `document_id` | `run_id` | Unidades | Estado remoto |
| ---: | --- | --- | --- | ---: | --- |
| 1 | Auto TC 00005-2025-PCC/TC, medida cautelar | `06d3feaf-c763-5fca-8541-5e7bcf1e7cb1` | `d302a08f-6898-42bb-bc26-06cb52e1e932` | 12 | `ready`; run `completed` |
| 2 | Auto TC 00006-2025-PCC/TC, tercero con interés | `29f79ea9-91ad-5eb2-838c-3970930d69f0` | `c86f655c-fdef-490d-b9ce-2de52cabc74c` | 11 | `ready`; run `completed` |

Los `document_hash` remotos coinciden con los del manifest. Cada run registra un documento, su cantidad exacta de unidades y cero relaciones. La CLI comprueba identidad, run y conteos después del commit de cada documento y detiene el lote ante una discrepancia; `PublicationAdapter` mantiene la transacción por documento.

## Embeddings y conteos

Se generaron **23 embeddings** nuevos, uno por unidad, con `text-embedding-3-small` y 1536 dimensiones. La consulta SQL remota confirmó `extensions.vector_dims(embedding)=1536` en las 23 unidades del lote; no se consultaron ni guardaron vectores completos.

| Estado | `legal_documents` | `legal_units` | `legal_relations` | `legal_ingestion_runs` |
| --- | ---: | ---: | ---: | ---: |
| Antes | 2 | 15 | 0 | 2 |
| Después, confirmado por SQL read-only | **4** | **38** | **0** | **4** |

La inspección manual posterior de `inspect-batch` informó `ALREADY_PRESENT_AND_IDENTICAL` para ambos y `EMBEDDINGS_REQUIRED=0`. Esta comprobación no republicó documentos ni generó vectores adicionales.

## Retrieval y provenance

Los siguientes resultados proceden de las pruebas reales ejecutadas por el operador después de publicar:

| Consulta | Resultado | Evidencia |
| --- | --- | --- |
| «¿Hasta cuándo mantiene sus efectos la medida cautelar del Tribunal Constitucional?» | **PASS** | Auto correcto rank 1; fundamento 8 rank 1; página 4; similarity ≈ 0,7300; lexical score 1,0. |
| «¿Por qué se admitió a Delia Espinoza como tercero con interés en el proceso competencial?» | **PASS** | Auto correcto rank 1; fundamento 6 rank 1 y fundamento 7 rank 2; provenance de página presente. |

La lectura SQL de las 23 unidades confirmó `unit_id`, `document_id`, `unit_type`, numeración de fundamentos y `page_start/page_end` válidos. El primer Auto contiene un antecedente, 10 fundamentos y una decisión, en páginas 1–4. El segundo contiene un antecedente, 8 fundamentos, una decisión y un voto separado, en páginas 1–5. Ambos conservan enlace a su documento y run de ingestión. El título, tipo documental e identidad se recuperan de `legal_documents` mediante `document_id`.

## Limitaciones conocidas

- `official_url` es `null` en los dos documentos: las fuentes aprobadas no aportaban una URL oficial verificable. No se inventó una.
- El título remoto del segundo Auto termina en «... tercero con interés en el», por lo que está truncado como etiqueta editorial. Su identidad, unidades y provenance están completos para este lote; el cierre no altera filas publicadas.
- Las pruebas anteriores son smoke tests de dos preguntas, no una evaluación exhaustiva del corpus ni una autorización para cambiar NovaSearch a V2.

## Validación de código y alcance

La validación posterior al commit incorporada a `corpus_cli.py` lee de nuevo identidad, run y conteos antes de pasar al siguiente documento. Sus pruebas offline cubren éxito, reanudación idempotente y detención antes del segundo embedding si falla la comprobación del primero. `python -m compileall -q app tests` y la suite backend completa pasaron con **248 tests**.

Batch 001 queda **CERRADO**. Se puede preparar Batch 002 o continuar corpus recovery como trabajo separado. Este cierre no publica más documentos, no ejecuta OCR, no modifica Fiscal.IA, Auth ni el runtime, y no hace cutover de NovaSearch.
