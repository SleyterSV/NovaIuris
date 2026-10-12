# Legal Knowledge V2 — preparación offline de Batch 004

## Punto de partida y alcance

Batch 003 tiene **STATUS=PUBLICATION_PASS**, según comprobación del operador: MYKE Legal contiene **8 documentos, 92 unidades, 0 relaciones y 8 runs**. El Auto TC 00102-2022-Q/TC (documento `ce873ccd-0117-578b-8b23-8d29b5c45cfd`, run `81c99019-e647-4df5-aa58-7855ec2b2284`) aportó 6 unidades; la STC 03902-2023-PHC/TC (documento `110aeca8-5837-526a-8e84-6b7579f0fdf2`, run `ef56c95d-8d8d-4879-8239-afd6c3b3138f`) aportó 22. Se generaron 28 embeddings durante la publicación ejecutada por el operador. La comprobación posterior dio `ALREADY_PRESENT_AND_IDENTICAL` y `EMBEDDINGS_REQUIRED=0` en ambos; las dos consultas de decisión quedaron en rank 1. Ningún documento publicado se modificó durante Batch 004.

Esta preparación usa el parser existente **`legal-v2.1.2`**. Las versiones declaradas por Batch 001 (`legal-v2.1.0`), Batch 002 (`legal-v2.1.1`) y Batch 003 (`legal-v2.1.2`) siguen siendo reproducibles. No se cambió el parser, cleaner, extractor, ranking, SQL ni modelo de embedding. La exploración mostró que los defectos restantes de numeración dentro de citas, listas jurídicas y separación de votos requieren reglas más seguras; forzar una unión de palabras o una segmentación nueva en este lote degradaría otros casos. Las ocho publicaciones son inmutables; la casación ya publicada con espacios PDF defectuosos permanece como `REINGESTION_CANDIDATE`, sin intervención.

## Recalificación completa de 135 originales

Se ejecutó una sola pasada de `python -m app.legal_ingestion.corpus_audit` sobre los originales después de la revisión y los tests focalizados. El auditor verificó SHA-256 de cada archivo, bloqueó conexiones de red y escribió la [calificación Batch 004](LEGAL_KNOWLEDGE_V2_CORPUS_BATCH_004.json). No llamó proveedores ni base de datos. El artefacto de Batch 003 se conservó.

| Clasificación | Antes: Batch 003 | Después: Batch 004 |
| --- | ---: | ---: |
| `PUBLISHABLE` | 2 | 1 |
| `REVIEW_REQUIRED` | 123 | 122 |
| `OCR_REQUIRED` | 3 | 3 |
| `INVALID_SOURCE` | 2 | 2 |
| `ALREADY_PUBLISHED` | 5 | 7 |
| **Total** | **135** | **135** |

Los dos aprobados anteriores pasaron a `ALREADY_PUBLISHED` tras Batch 003; uno nuevo pasó revisión. El inventario cuenta originales físicos: uno de los ocho documentos V2 publicados proviene de un segmento normativo de un original mayor, por lo que son siete fuentes físicas publicadas en el audit.

## Revisión manual contra el original

La [revisión](LEGAL_KNOWLEDGE_V2_BATCH_004_REVIEW.json) liga la aprobación a ruta, hash de fuente, hash documental, parser y cantidad de unidades. Se inspeccionaron las **9/9 páginas** del PDF de la STC Sala Segunda 0741/2026, Exp. **04677-2025-PHC/TC**, 17-04-2026. El original y el staging coinciden en identidad, tribunal, sala, fecha y URL oficial impresa. El antecedente ocupa páginas 1–2; los fundamentos 1–8, páginas 2–4; la decisión **IMPROCEDENTE**, página 4; el voto concurrente, páginas 5–8; y el voto singular, página 9. Primera, unidades intermedias y última unidad, límites jurídicos, paginación y `page_furniture_removed:32` fueron cotejados. No quedó folio físico aislado dentro de una unidad.

**MANUAL_REVIEW=PASS** para 04677-2025-PHC/TC. El voto concurrente supera el límite de tamaño de una unidad y se conserva en dos partes contiguas (`part_number` 1/2); no se presenta como dos votos de distinta autoría. Los marcadores y notas al pie visibles en el original permanecen en el texto extraído, incluso junto al fundamento 1; son una limitación documentada de lectura, no texto jurídico reconstruido ni un fundamento inventado.

**MANUAL_REVIEW=FAIL**, fuera del manifest: 01736-2025-PHC/TC (numerales de citas como fundamentos); 00215-2024-PHC/TC (votos y espacios inseguros); Casación 496-2025/LA LIBERTAD (sumilla y apertura); 01649-2024-PHC/TC (citas numeradas); 04852-2023-PA/TC (encabezado y voto); 00800-2024-PHC/TC (cita judicial y footer); 02047-2025-PA/TC (lista interna numerada); 04068-2023-PA/TC (citas normativas y palabras partidas); Casaciones 1913-2023/VENTANILLA y 1027-2025/SAN (sumilla/espacios y apertura faltante, respectivamente); 02248-2020-PA/TC (órgano y encabezados); y 00782-2023-PHC/TC (fecha sin validar por parser). Son rechazos estructurales, no reclasificaciones para completar tamaño.

## Manifest, inspección y gate remoto

El [manifest Batch 004](LEGAL_KNOWLEDGE_V2_BATCH_004.json) contiene **1 sentencia / 13 unidades / 13 embeddings futuros**. Incluye ID estable, ruta, hashes de fuente y documento, versión `legal-v2.1.2`, tipo `judgment`, unidades esperadas y `PUBLISHABLE`; no contiene texto jurídico completo, vectores ni secretos. La CLI admite esta ruta exclusivamente para `inspect-batch`; **Batch 004 no está habilitado para `publish-batch`**. Batches 001–003 conservan su allowlist histórica.

La inspección offline devolvió `BATCH=004`, ID `cd87b86e-e91e-501b-8491-8b9a39079f9d`, `PUBLISHABLE`, `judgment`, 13 unidades, parser `legal-v2.1.2`, hash documental prefijo `ea4bdd2026a7` y `EMBEDDINGS_REQUIRED=13`. **PRESENCE=UNVERIFIED_OFFLINE**: esta sesión no comprobó MYKE Legal remotamente y no se debe presentar como `NOT_PRESENT`. El operador debe hacer `inspect-batch` remoto read-only antes de considerar una habilitación separada de publicación. Un `CONFLICT`, hash distinto o conteo inesperado implica NO-GO.

Comando de inspección para el operador, con `MYKE_LEGAL_DATABASE_URL` de MYKE Legal ya cargada en su PowerShell:

```powershell
cd D:\NovaIuris\backend
python -m app.legal_ingestion.corpus_cli inspect-batch ..\docs\LEGAL_KNOWLEDGE_V2_BATCH_004.json
```

No se ejecutó `publish-batch`, no se generaron embeddings y no hubo inserts/updates de Supabase en esta preparación. El gate de publicación permanece deshabilitado para 004.
