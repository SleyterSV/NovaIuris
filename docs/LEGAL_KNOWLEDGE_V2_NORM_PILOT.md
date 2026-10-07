# Legal Knowledge V2 — bloque 10.4B-1.6, norma piloto

## Alcance

Se inspeccionaron únicamente los ocho DOCX normativos originales que no habían participado en el piloto anterior. Se eligieron tres por tamaño, estructura visible e incidencia preliminar de anotaciones: `CODIGO DE EJECUCION PENAL.docx`, `LEY DEL PROCEDIMIENTO ADMINISTRATIVO GENERAL.docx` y `CODIGO DE PROTECCION Y DEFENSA DEL CONSUMIDOR.docx`, todos bajo `raw_docs/`. El dry-run de esos tres archivos y del instrumento delimitado se ejecutó con `socket.connect` y `socket.create_connection` bloqueados. No hubo embeddings, llamadas a proveedores ni escritura en Supabase.

| Candidato original | Estado del archivo completo | Unidades | Artículos | Disposiciones | Duplicados | Partes divididas | Bloqueo |
|---|---|---:|---:|---:|---:|---:|---|
| TUO Código de Ejecución Penal | review_required | 169 | 161 | 8 | 0 | 6 | `SOURCE_LIMITATION` / `STRUCTURE_ERROR`: instrumento aprobatorio y código mezclados; el tramo posterior de “TEXTO INCORPORADO” incorpora otra versión. `METADATA_INCOMPLETE`: número propio del código no identificado con seguridad. |
| DOCX de Ley del Procedimiento Administrativo General | review_required | 295 | 282 | 13 | 0 | 6 | `SOURCE_LIMITATION`: decreto aprobatorio y TUO anexo en el mismo archivo. `EDITORIAL_CONTAMINATION`: fe de erratas y `NOTA SPIJ` afectan artículos del TUO; su corrección exige cotejo. |
| Código de Protección y Defensa del Consumidor | review_required | 204 | 172 | 11 | 0 | 12 | `EDITORIAL_CONTAMINATION` / versiones: múltiples fórmulas `(*) Literal/Artículo modificado o incorporado por...` y texto histórico siguen dentro de artículos. Los 92 bloques posteriores a la promulgación se identificaron con hash y quedaron fuera de unidades jurídicas. |

Ningún archivo completo fue forzado a `staged`. El máximo de partes de una unidad fue respectivamente 6, 2 y 2; no hubo divisiones extremas. Los DOCX no ofrecen paginación real, por lo que `page_start/page_end` permanecen nulos.

## Norma publicable: Decreto Supremo 006-2026-JUS

El archivo original `raw_docs/LEY DEL PROCEDIMIENTO ADMINISTRATIVO GENERAL.docx` contiene **dos instrumentos jurídicos distintos**: primero el decreto supremo que aprueba el TUO y después el TUO anexo. `stage_file(..., segment="promulgating_instrument")` delimita el decreto mediante su identidad, la sección `DECRETA`, la fórmula formal de cierre y el título separado del anexo. Esta opción es general para un decreto supremo que promulga un TUO; no usa el nombre del archivo ni un número de norma fijo. El archivo completo y el TUO anexo continúan en revisión y **no** quedan autorizados para la carga piloto.

| Dato | Resultado comprobado |
|---|---|
| Tipo V2 | `regulation` |
| Número | `006-2026-JUS` |
| Emisor | Presidencia de la República |
| Fecha original de emisión | “Dado en la Casa de Gobierno, en Lima, a los veintiocho días del mes de abril del año dos mil veintiséis.” |
| Fecha de publicación | No estructurada: el archivo no da una fecha propia de publicación del decreto en el tramo seleccionado. |
| Alcance del original | Bloques 0–34 del DOCX; bloques 35–39 son firmas y el TUO anexo empieza en el bloque 40. El hash del archivo completo se conserva en `source_file_hash`. |
| `document_hash` del decreto | `4d4b33500e017cf5055e50a5812ea13cba25209310c85d99e5a85b076cf2b65a` |
| Unidades | 5: artículos 1–4 y disposición complementaria derogatoria única |
| Extracción / gate | `high`, `staged`, cero warnings, cero duplicados, cero unidades divididas, OCR no requerido |

La revisión manual comprobó **todas** las unidades, no solo muestras: artículo 1 objeto, artículo 2 aprobación, artículo 3 publicación, artículo 4 refrendo y disposición única que deroga el Decreto Supremo 004-2019-JUS. Los cinco textos coinciden con los bloques originales 24–31 y 33–34, tienen encabezados/secuencia coherentes y hashes de contenido distintos. No hay notas SPIJ, fe de erratas, versiones alternativas ni concordancias dentro de estas unidades. El encabezado de la disposición (bloque 32) se conserva como `provision_heading` en metadatos. Los considerandos del decreto se conservan en el hash del documento y en el archivo fuente; no se inventaron unidades jurídicas para ellos.

## Correcciones generales aplicadas

- `PARSER_BUG`: los encabezados `DISPOSICIONES COMPLEMENTARIAS FINALES/MODIFICATORIAS/TRANSITORIAS/DEROGATORIAS`, en singular o plural, ahora separan las disposiciones y conservan su clase en metadatos. `ÚNICA` es un ordinal válido. El artículo final ya no absorbe todas las disposiciones.
- `PARSER_BUG`: `TÍTULO PRELIMINAR` reinicia la jerarquía después de un índice; los encabezados breves de artículo se asignan a `heading` cuando el texto permite distinguirlos del cuerpo.
- `QUALITY_GATE_EXPECTED`: número normativo ausente, fórmulas de versiones históricas dentro de artículos y reinicios anómalos de numeración bloquean la publicación. La detección de una disposición sin cuerpo sigue siendo bloqueante.
- `SOURCE_LIMITATION`: las marcas editoriales y modificaciones incluidas en los códigos completos se conservan para revisión; no se reconstruyó una versión legal a partir de ellas.

## Adapter y decisión

Se prepararon en memoria el decreto (`regulation`, 5 unidades) y el auto TC 04810-2024-PA/TC (`order`, 10 unidades) con `PublicationAdapter.prepare()`. Ambos estaban `staged`; el auto conserva identidad, fecha, ponente y páginas 1–3. Los dos mappings preservan UUID, hash y metadatos, con `embedding=None` y `relations=[]`. La factory de conexión inyectada lanzaría un error si se invocara: no se abrió conexión ni se publicó.

El subconjunto para el siguiente bloque es **solo** este decreto segmentado y el auto TC. La publicación real deberá exigir vectores de 1536 dimensiones y validar el comportamiento transaccional contra PostgreSQL antes de cargar. Ningún código completo ni el TUO anexo está incluido en el GO.

Verificación final: `compileall` **PASS**; **205 tests backend PASS**; consulta SQL final de solo lectura a Supabase MYKE Legal: `legal_documents=0`, `legal_units=0`, `legal_relations=0`, `legal_ingestion_runs=0`. **GO para 10.4B-2** únicamente con el alcance indicado.
