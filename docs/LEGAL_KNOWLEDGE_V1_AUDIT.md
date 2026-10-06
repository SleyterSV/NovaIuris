# Legal Knowledge V1: auditoría de ingesta

## Flujo reconstruido

`raw_docs` → parser histórico o JSON preprocesado en `processed_docs` → `LegalKnowledgeProcessor.process_article` → representación de búsqueda → embedding individual → `VectorStoreManager` → `legal_knowledge`.

El `VectorStoreManager` actual importa `LegalParser`, pero `app/utils/file_parser.py` actual no define esa clase ni `parse_articles`. El parser histórico está en `a0ff538:backend/app/utils/file_parser.py`; `0ec173b` conserva referencias, no la clase. Se inspeccionó con `git show`, sin restaurar archivos. Reconocía líneas que comenzaban con «Artículo» y número, acumulaba líneas hasta el siguiente artículo, descartaba repeticiones del mismo número, marcaba todo como vigente y escribía JSON en `processed_docs`. No preservaba libro/capítulo, páginas, modificaciones, versiones ni procedencia. No era un parser jurisprudencial.

`JurisprudenceDocument` sí tiene metadatos documentales: órgano emisor, expediente, tipo de resolución, ponente, fecha, sumilla, precedente vinculante, materia e instancia. `jurisprudence_processor.py` intenta inferirlos; `ingest_jurisprudencia.py` corta texto en fragmentos de 1800 caracteres con solapamiento de 250, genera un embedding por fragmento e inserta esos campos repetidos en `legal_knowledge`. Su heurística de precedente y su resumen generado requieren comprobación contra el documento original. V2 conserva la sumilla original y solo marca precedente vinculante con declaración explícita.

## Deuda y límites

- `expedientes_chunks` corta alrededor de 1000 caracteres; pertenece al corpus privado, no a la biblioteca pública V2.
- `TextProcessor` también divide por tamaño. `LegalKnowledgeProcessor` asume artículos; `MAX_EMBED_CHARS=8000` trunca texto de búsqueda; `generate_summary` usa los primeros 400 caracteres y `extract_keywords` palabras en mayúsculas.
- El PDF genérico concatena páginas. El DOCX genérico pierde estilos y tablas. El actual `FileParser` no interpreta `.doc` con HTML SPIJ.
- `legal_knowledge` mezcla propiedades de documento con unidad. `hash_documento` del flujo normativo es el hash del texto de la unidad. La ruta jurisprudencial sí inserta columnas jurisprudenciales, pero repite esos datos por fragmento; la ruta normativa de `VectorStoreManager` no los inserta.
- Un comentario antiguo menciona borrar `base_legal`, pero el código actual no efectúa ese borrado. `retriever.py` aún consulta `match_base_legal`; `legal_repository.py` consulta `match_legal_knowledge`. `base_legal` queda como candidato legacy pendiente de inventario de datos, sin eliminación.

Las tablas V1 `legal_knowledge`, `expedientes_chunks` y `base_legal` permanecen intactas. Los expedientes privados siguen en el corpus de casos con `owner_id`, `case_id`, `document_id` y procedencia privada. Ninguno pasa a `legal_documents`.
