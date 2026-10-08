# Legal Knowledge V2 — recuperación de calidad del corpus (10.6A.1)

## Alcance y reproducibilidad

La fuente sigue siendo el inventario de **135 originales** de 10.6A: 13 DOCX normativos y 122 PDF jurisprudenciales. El [resultado 10.6A](LEGAL_KNOWLEDGE_V2_CORPUS_QUALIFICATION.json) permanece como línea base; el [resultado recalificado](LEGAL_KNOWLEDGE_V2_CORPUS_RECOVERY.json) se genera con `cd backend; python -m app.legal_ingestion.corpus_audit`. El comando verifica los SHA-256 físicos antes de analizar, bloquea `socket.connect` y `socket.create_connection`, usa `stage_file()` y no importa proveedores de embeddings ni adaptadores de publicación. El JSON guarda identidad, métricas, warnings y decisión; no contiene texto jurídico completo ni vectores.

La versión nueva del parser es `legal-v2.1.0`. Los dos documentos piloto que ya están en MYKE Legal permanecen en `legal-v2.0.0`; este bloque no los republicó ni regeneró sus embeddings. El Decreto Supremo 006-2026-JUS sigue siendo solo un segmento publicado dentro del DOCX completo del TUO 27444, cuyo resto permanece en revisión. El Auto TC 04810-2024-PA/TC está excluido por SHA-256 de archivo. Ninguna unidad bruta de revisión quedó autorizada para vectorizarse.

## Antes y después

| Clasificación física | 10.6A | 10.6A.1 |
| --- | ---: | ---: |
| `PUBLISHABLE` | 0 | **2** |
| `REVIEW_REQUIRED` | 129 | **127** |
| `OCR_REQUIRED` | 3 | **3** |
| `INVALID_SOURCE` | 2 | **2** |
| `ALREADY_PUBLISHED` | 1 | **1** |
| **Total** | **135** | **135** |

Los dos publicables son **autos TC**. Normas publicables: 0; casaciones publicables: 0. Los 13 DOCX completos continúan en revisión, así como 114 PDF jurisprudenciales. El gate automático dejó 24 fuentes `staged`: 2 aprobadas visualmente y 22 pendientes de revisión. **`staged` por sí solo nunca equivale a `PUBLISHABLE`.**

La extracción recalificada generó **12.346 unidades brutas**: 6.096 artículos, 4.640 fundamentos, 210 decisiones, 241 disposiciones, 346 concordancias, 534 partes de votos separados y 279 otras unidades. Frente a las 12.974 unidades de 10.6A, la diferencia responde a nueva limpieza y delimitación; no equivale a contenido publicable ni a embeddings requeridos. Incluye el DOCX completo del TUO con el segmento del decreto ya publicado. Las partes de votos extensos pueden aparecer como varias unidades técnicas.

## Correcciones generales

1. **Tipificación documental.** `document_type` toma `resolution_type` demostrado por el encabezado antes del filename. Las 15 contradicciones `judgment` frente a `auto`/`casación` observadas en 10.6A se redujeron a 0. Los conceptos permanecen separados.
2. **Fecha TC.** Se reconoce «En Lima, al día 1 del mes de diciembre de 2025» sin deducir una fecha de otra parte del PDF. El Auto de medida cautelar recuperó su fecha y pasó el gate.
3. **Tribunal y sala.** Se prioriza la primera identificación judicial del encabezado; una cita posterior a otra corte no reemplaza al emisor. Se reconocen Sala Penal Permanente/Transitoria y salas constitucionales. Esto puede aumentar warnings de identidad cuando la antigua inferencia era demasiado amplia.
4. **Votos.** Encabezados `FUNDAMENTO DE VOTO`, `VOTO DEL MAGISTRADO` y `VOTO SINGULAR DE LA MAGISTRADA`, con o sin nombre, abren `separate_opinion`. El razonamiento y la decisión del voto no vuelven a mezclarse con la decisión de mayoría. Warnings `separate_opinion_mixed_with_decision`: **34 → 5**.
5. **Límites de jurisprudencia.** `AUTOS y VISTOS` cierra la sumilla; ordinales como `Decimotercero` y `Decimocuarto` inician fundamentos nuevos. Una referencia de Auto partida entre líneas (`Auto` / `5 - 00004-2024-PCC/TC`) permanece en el fundamento que la cita. Warnings de múltiples fundamentos: **15 → 11**.
6. **Muebles de página.** Se comparan hasta cinco primeras y últimas líneas de PDF por página, contando una ocurrencia por página y protegiendo encabezados jurídicos. Se eliminaron captions multilínea reiterados que antes caían dentro de fundamentos. La identidad se extrae de los bloques originales antes de esa limpieza.
7. **Familia jurídica.** Una cabecera de Corte Superior con expediente se trata como jurisprudencia incluso si el filename no lo indica. El documento real sigue en revisión cuando carece de identidad/fecha suficiente o contiene votos complejos.

Cada cambio tiene un test positivo y casos negativos; no hay condiciones por filename, número de expediente o artículo en el parser. No se relajó `validate_staged()`.

## Bloqueos que permanecen

Los grupos se solapan; no deben sumarse como documentos distintos. Después de la recalificación hay 59 fuentes con `jurisprudence_date_or_type_missing`, 47 con `jurisprudence_identity_missing`, 27 sin decisión detectada, 22 con estructura sobredimensionada, 12 con versiones normativas mezcladas y 10 con material editorial dentro de norma. Cinco documentos aún mezclan voto y decisión según el gate. Los 3 PDF escaneados siguen en la cola OCR; no se ejecutó OCR.

Los dos `.pdf` con firma HTML son páginas editoriales con navegación del sitio, no copias confiables de una resolución. El extractor reconoce su formato real como HTML; continúan `INVALID_SOURCE` hasta obtener una fuente jurídica válida. No se renombraron ni modificaron. Los 5 grupos de SHA-256 físico idéntico mantienen **6 copias adicionales** excluidas; la fuente canónica se elige por ruta estable, sin borrar archivos. Dos expedientes con fuentes físicamente diferentes siguen `REQUIRES_REVIEW`, sin fusionar ni presumir versión. La suma de repeticiones internas de `content_hash` bajó de 18 a 13, pero las fuentes afectadas permanecen bloqueadas por el gate.

Las casaciones que ahora pasan el gate aún muestran, en muestras reales, palabras partidas por la extracción PDF o aperturas complejas; no fueron promovidas. Los códigos y leyes completos conservan contaminación editorial o versiones mezcladas. Algunas sentencias TC tienen identidades personales ausentes en la propia fuente, votos extensos o referencias que requieren cotejo visual. Esas limitaciones no se corrigieron por sustitución de texto ni por reducción del umbral de calidad.

## Revisión manual y Batch 001

La [revisión manual ligada a hashes](LEGAL_KNOWLEDGE_V2_CORPUS_RECOVERY_REVIEW.json) aprueba solo estas dos fuentes. Se contrastaron todas sus páginas renderizadas con primera, media y última unidad, fundamentos numerados, decisión, metadata y rango de páginas. No se afirma URL oficial para ninguna.

| Orden | Fuente original | Identidad | Unidades | Revisión | Observación |
| ---: | --- | --- | ---: | --- | --- |
| 1 | `_Auto__Medida_cautelar_mantiene_sus_efectos_hasta_que_se_emita_sentencia___.pdf` | Auto TC 00005-2025-PCC/TC, 01-12-2025 | 12: 1 antecedente, 10 fundamentos, 1 decisión | **PASS** | Páginas 1–4, decisión `IMPROCEDENTE`; caption repetido retirado. |
| 2 | `TC_admitió_a_Delia_Espinoza_como_tercero_con_interés_en_el___.pdf` | Auto TC 00006-2025-PCC/TC, 16-04-2026 | 11: 1 antecedente, 8 fundamentos, 1 decisión, 1 voto separado | **PASS** | Páginas 1–5, decisión `ADMITIR`; voto de magistrado separado y referencia citada intacta. |

La revisión manual observó espacios aislados introducidos por extracción PDF, pero los textos operativos, identidades y razonamientos de estos dos autos conservan sentido y orden verificables en las páginas. Ambos PDF llevan marca del redistribuidor; el documento judicial es visible, pero no se inventó una `official_url`. Otros 22 `staged` están **PENDING**, no aprobados para este lote.

El [manifest Batch 001](LEGAL_KNOWLEDGE_V2_BATCH_001.json) contiene solo identificador estable, ruta del original, SHA-256 físico, `document_hash`, `parser_version`, tipo, cantidad esperada y estado de calidad. Orden: primero el Auto de medida cautelar, luego el Auto de tercero con interés. **2 documentos / 23 unidades / 23 embeddings futuros**. Texto canónico para embedding: **18.168 caracteres**; el texto de unidades suma aproximadamente **2.382 palabras** (no es un conteo del tokenizer del proveedor). Las unidades se procesarán con batches de embedding de 32 y `PublicationAdapter` con lotes SQL de 100; cada documento tendrá su propia transacción y checkpoint.

## CLI y dry-run

Desde `D:\NovaIuris\backend`:

```powershell
python -m app.legal_ingestion.corpus_cli inspect-batch ..\docs\LEGAL_KNOWLEDGE_V2_BATCH_001.json
```

Este comando se ejecutó **sin** `MYKE_LEGAL_DATABASE_URL`: ambas fuentes devolvieron `PUBLISHABLE`, hashes y cantidades esperadas (12 y 11), con `PRESENCE=UNVERIFIED_OFFLINE`; no abrió base ni proveedor. Una consulta SQL remota independiente, de solo lectura, confirmó **0 filas** para ambos pares `document_hash` + `legal-v2.1.0`. Al ejecutar `inspect-batch` desde un PowerShell con `MYKE_LEGAL_DATABASE_URL` de MYKE Legal, la CLI hará su propia comprobación `NOT_PRESENT` / `ALREADY_PRESENT_AND_IDENTICAL` / `CONFLICT` antes de 10.6B. La ruta del manifest está cerrada; no acepta un JSON arbitrario. Revalida la calificación, hash de archivo, hash documental, versión, tipo, número de unidades, estado y mapeo offline.

La orden **futura**, que **no se ejecutó en 10.6A.1**, es:

```powershell
python -m app.legal_ingestion.corpus_cli publish-batch ..\docs\LEGAL_KNOWLEDGE_V2_BATCH_001.json
```

Requiere `MYKE_LEGAL_DATABASE_URL` del proyecto correcto y `OPENAI_API_KEY`, usa `text-embedding-3-small` y 1536 dimensiones, y reutiliza `EmbeddingService`, `embedding_batches` y `PublicationAdapter`. Omite embeddings en reanudaciones idénticas. Un conflicto o fallo detiene el resto del lote. El adapter hace commit/rollback por documento; documentos anteriores completos permanecen, el documento fallido no queda listo. No se imprimen DSN, claves ni vectores.

## Supabase y decisión

La consulta SQL vinculada a **MYKE Legal** (`emelxkoztshmzukydqzj`) confirmó `legal_documents=2`, `legal_units=15`, `legal_relations=0`, `legal_ingestion_runs=2`. Batch 001 sigue ausente. No hubo OpenAI, embeddings, inserts, publicación, OCR, migración V1, cambios Auth ni cutover de NovaSearch.

**GO limitado para 10.6B: publicar exclusivamente Batch 001 después del preflight con DSN en la sesión del operador.** Este GO no autoriza otros 22 `staged`, normas, casaciones, OCR ni carga masiva. Se deben comprobar counts e idempotencia después de cada Auto antes de ampliar lotes.
