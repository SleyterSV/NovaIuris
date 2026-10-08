# Legal Knowledge V2: foundation

## Dominio y contrato

V2 almacena **normativa y jurisprudencia públicas** por documento y por unidad jurídica. El corpus privado de expedientes conserva su dominio y sus controles de propiedad. NovaSearch continúa leyendo V1 durante este bloque.

La migración `supabase/migrations/20261006162217_legal_knowledge_v2_foundation.sql` crea cuatro tablas:

| Tabla | Papel |
| --- | --- |
| `legal_documents` | Identidad del documento completo, metadatos jurídicos, vigencia, calidad y estado de publicación. `document_hash` es SHA-256 del documento normalizado completo, único junto a `parser_version`. |
| `legal_units` | Artículos, disposiciones, notas, sumillas, fundamentos, decisiones y votos. Orden, jerarquía, páginas, partes de unidades grandes, texto original/normalizado, `content_hash`, búsqueda y vector de 1536 dimensiones. |
| `legal_relations` | Relaciones explícitas entre unidades/documentos o citas aún no resueltas. El foundation no inventa relaciones automáticamente. |
| `legal_ingestion_runs` | Auditoría por archivo, versión de parser, conteos, advertencias, errores y revisión requerida, sin contenido ni secretos en los logs. |

Hay claves externas y cascada al eliminar documentos de prueba; las relaciones hacia destinos se ponen a nulo cuando corresponde. Los estados documentales (`current`, `modified`, `repealed`, `historical`, `unknown`) son independientes de la vigencia de cada unidad. Una nota «Artículo modificado por…» se separa como `amendment_note`, sin presentarla como norma vigente. `precedent_binding` queda nulo hasta encontrar evidencia explícita; falso solo cuando se haya verificado la ausencia.

## Extracción y estructura

El piloto publicado conserva `legal-v2.0.0`; la recuperación del corpus usa `legal-v2.1.0`. PDF mantiene orden y número de página; DOCX mantiene orden de párrafos y tablas, estilos de encabezado y marcadores de lista. HTML, incluso con extensión `.doc` de SPIJ, se detecta por contenido; el parser estándar elimina scripts y estilos, conserva encabezados, texto y enlaces HTTP. El limpiador reconoce encabezados/pies repetidos en las cinco primeras o últimas líneas de al menos tres páginas y protege encabezados jurídicos. PDFs con poco texto extraíble se marcan `ocr_required`; OCR no forma parte de este bloque.

`NormativeParser` identifica libro, sección, título, capítulo, artículo, disposición, modificación y concordancia. El artículo completo es la unidad primaria. `JurisprudenceParser` identifica sumilla, materia, antecedentes, fundamentos numerados, decisión y votos, con página inicial/final. Reconoce metadatos documentales cuando figuran explícitos; no sustituye la sumilla real por un extracto inventado. Un `excerpt` es solo vista previa.

Si una unidad excede el límite configurado, se divide por párrafos y después por oraciones, con `part_number`, `part_count` y hash de la unidad padre. Una oración individual que excede el límite permanece íntegra para revisión; no se trunca ni se publica. El texto de embedding incluye título, órgano, expediente, materia y número/tipo de unidad. `embedding_batches` admite una función de proveedor inyectada, agrupa solicitudes y valida exactamente 1536 dimensiones. No llama proveedores en el dry-run.

## Calidad, publicación y búsqueda

El dry-run hace extracción, parsing y validación local, sin embeddings ni inserciones. El gate exige documento identificable, al menos una unidad no vacía, secuencia válida, páginas coherentes, hash único por unidad, texto de búsqueda y calidad aceptable. Una extracción pobre, una decisión ausente en jurisprudencia o una unidad inseparable requiere revisión. Repetir un archivo produce el mismo hash/ID; la unicidad en SQL bloquea duplicados persistidos. `staged` **no** equivale a `ready`: un adaptador futuro realizará `stage → embed → quality check → publish` en transacción o con visibilidad controlada.

PostgreSQL usa `to_tsvector('spanish'::regconfig, search_text)` con GIN y `embedding vector(1536)` con HNSW/coseno. `match_legal_knowledge_v2` combina candidatos vectoriales y léxicos, filtra por tipo, rama y expediente, y solo devuelve documentos `ready`/`ready_with_warnings`. Índices B-tree sirven a búsquedas estructuradas de artículo, expediente, número y fecha. Los pesos de ranking son iniciales; se calibrarán con el piloto V1/V2. La función no reemplaza `match_legal_knowledge` de V1.

RLS está activado en las cuatro tablas, sin políticas de lectura pública ni permisos `anon`/`authenticated`; el RPC solo concede ejecución a `service_role`. Esa credencial pertenece exclusivamente al backend. La seguridad final de runtime y Auth se validará en una fase posterior. Véanse las guías oficiales de [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security) y [índices vectoriales](https://supabase.com/docs/guides/ai/vector-indexes).
