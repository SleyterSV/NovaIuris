# Legal Knowledge V2 — Batch 005, preparación offline

## Estado confirmado y alcance

El operador confirmó **Batch 004 STATUS=PUBLICATION_PASS** para la STC Exp. 04677-2025-PHC/TC, documento `cd87b86e-e91e-501b-8491-8b9a39079f9d`, run `bb6677a6-97f1-4b30-babc-022a6e52cc5f`. MYKE Legal quedó en **9 documentos / 105 unidades / 0 relaciones / 9 runs**. La inspección posterior fue `ALREADY_PRESENT_AND_IDENTICAL`, con cero embeddings pendientes. En el smoke test, la decisión ocupó rank 1, página 4, con expediente exacto, URL oficial y los cinco primeros resultados del mismo documento. Esta es evidencia del operador; Batch 005 no consultó ni modificó Supabase.

Los nueve documentos publicados y sus embeddings permanecen intactos. Los manifests históricos fijan Batch 001 a `legal-v2.1.0`, Batch 002 a `legal-v2.1.1`, y Batches 003–004 a `legal-v2.1.2`. Batch 005 usa **`legal-v2.1.3`**.

## Fix conservador del parser

En una STC pendiente, la línea narrativa «fundamento de voto del magistrado … . Los magistrados» del preámbulo era aceptada como si fuera un encabezado de voto. El parser pasaba a `separate_opinion` desde la primera página y absorbía fundamentos y decisión. `legal-v2.1.3` exige que el encabezado de voto aislado no contenga una continuación de oración con punto; el encabezado auténtico posterior sigue abriendo el voto. El cambio se limita a documentos nuevos: staging explícito con `legal-v2.1.2` conserva el comportamiento histórico y la limpieza de páginas de Batches 003–004. Tests positivos y negativos cubren la distinción; el test del manifest comprueba expediente, fundamentos 1–34, decisión en página 13 y voto desde página 14.

No se cambió la extracción PDF global, el SQL, ranking, runtime NovaSearch ni modelo de embeddings. El fix no intenta unir palabras partidas, eliminar notas impresas o reconstruir texto jurídico.

## Recalificación offline de 135 originales

Tras tests focalizados se ejecutó **una** pasada de `python -m app.legal_ingestion.corpus_audit`. Verificó SHA-256 de originales y bloqueó conexiones de red. La [calificación de Batch 005](LEGAL_KNOWLEDGE_V2_CORPUS_BATCH_005.json) conserva el artefacto anterior y clasifica la fuente de Batch 004 como publicada.

| Clasificación | Antes: Batch 004 | Después: Batch 005 |
| --- | ---: | ---: |
| `PUBLISHABLE` | 1 | 1 |
| `REVIEW_REQUIRED` | 122 | 121 |
| `OCR_REQUIRED` | 3 | 3 |
| `INVALID_SOURCE` | 2 | 2 |
| `ALREADY_PUBLISHED` | 7 | 8 |
| **Total** | **135** | **135** |

El inventario cuenta fuentes físicas; una de las nueve publicaciones es un segmento de un original normativo mayor. Solo la nueva sentencia supera gate y revisión manual, con **39 unidades**. Otros documentos afectados potencialmente por el parser permanecen en `REVIEW_REQUIRED` sin aprobación manual.

## Revisión manual

La [revisión ligada a hashes](LEGAL_KNOWLEDGE_V2_BATCH_005_REVIEW.json) registra **PASS** para la STC Sala Segunda 0831/2026, Exp. **00697-2024-PA/TC**, de 13-05-2026. Se cotejaron **17/17 páginas** del original: identidad, tribunal, sala, fecha, URL oficial, antecedente (páginas 1–3), fundamentos 1–34 (3–13), decisión `FUNDADA` con nulidad y órdenes (13), y fundamento de voto de Domínguez Haro (14–17). Se revisaron primera, intermedias y últimas unidades, paginación, notas, cabeceras y pie de verificación. El voto largo se divide en dos partes por tamaño y mantiene continuidad/páginas; no se confunde con la decisión. `page_furniture_removed:73` es el único warning. No quedó un folio físico aislado ni una cabecera repetida dentro de una unidad.

**FAIL y excluidos:** Casación 1331-2022/LAMBAYEQUE (palabras partidas, folio dentro de fundamento y fecha extraída incompleta); sentencia de vista Exp. 02974-2023-0-1801-JR-FC-17 (identidad truncada, «Página 7 de 7» dentro de un fundamento y división arbitraria); los rechazos anteriores, incluida STC 01736 y casaciones con sumilla o apertura inseguras, no quedan resueltos por este fix. No se forzó el tamaño del lote.

## Manifest, inspección y siguientes gates

El [manifest Batch 005](LEGAL_KNOWLEDGE_V2_BATCH_005.json) contiene **1 sentencia / 39 unidades / 39 embeddings futuros**, con ID estable, ruta, hashes, parser `legal-v2.1.3`, tipo y estado de calidad. No contiene texto jurídico completo, vectores ni secretos. La CLI admite `inspect-batch` y, tras la confirmación remota del operador, Batch 005 quedó habilitado en `PUBLISH_BASELINES` con baseline `(9, 105, 0, 9)`. Batches 001–004 siguen habilitados y los desconocidos bloqueados.

La inspección offline confirmó `PUBLISHABLE`, ID `44dd7306-8ee4-5d7f-91dd-ce2683bc3b53`, tipo `judgment`, 39 unidades, hash prefijo `6504c064ca37`, parser `legal-v2.1.3` y `EMBEDDINGS_REQUIRED=39`. **PRESENCE=UNVERIFIED_OFFLINE** en esa sesión local. Después, el operador confirmó `PRESENCE=NOT_PRESENT` y **9 documentos / 105 unidades / 0 relaciones / 9 runs** en MYKE Legal. La CLI vuelve a comprobar el manifest, los hashes, el parser, la identidad y los conteos antes de generar embeddings. Un `CONFLICT` o discrepancia implica NO-GO.

```powershell
cd D:\NovaIuris\backend
python -m app.legal_ingestion.corpus_cli inspect-batch ..\docs\LEGAL_KNOWLEDGE_V2_BATCH_005.json
```

La habilitación local no ejecutó `publish-batch`, no generó embeddings ni escribió en Supabase. La publicación corresponde al operador desde PowerShell en un paso separado.

**Limitaciones conocidas:** notas al pie impresas siguen dentro de algunas unidades; títulos editoriales de los PDFs no sustituyen la identidad jurídica estructurada; las casaciones con espacios rotos, folios o límites ambiguos permanecen pendientes. No se reingestó ningún documento, no se generaron embeddings ni se escribió en Supabase.
