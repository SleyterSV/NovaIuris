# NovaCase NC-4: persistencia y retención técnica actual

## Estado de almacenamiento

- Los dueños de casos (`case_owners`), manifiestos privados (`case_documents`) y fragmentos con texto y embeddings (`case_chunks`) viven en `CASE_CORPUS_DB_PATH`, un SQLite local. Las lecturas privadas se acotan por `case_id` y el API verifica al dueño autenticado. El corpus jurídico público V2 permanece separado en PostgreSQL.
- Las tasks de análisis y sus resultados finales canónicos viven en `TASK_DB_PATH` (`runtime_tasks`). Cada entrada conserva `task_id`, dueño, caso, tipo, estado, fechas, etapa, metadata y resultado. Las tasks documentales usan `document_runtime_tasks` en el mismo archivo. En producción ambos SQLite deben estar en un volumen persistente externo al repositorio.
- Un proceso nuevo rehidrata tasks completadas. Las que estaban pendientes o ejecutándose pasan a `interrupted`; no se reanuda automáticamente trabajo de proveedores. La exportación del caso vuelve a leer el journal acotado por dueño, caso y task, y solo acepta resultados completados.
- Los archivos originales de upload se guardan temporalmente durante la extracción y luego se eliminan. Se conserva el texto, chunks, embeddings y metadata, no el binario original. El staging abandonado se limpia después del límite configurado (24 horas por defecto).

## Límites y eliminación

- Tamaño por archivo: 45 MiB por defecto; total por caso: 200 MiB; solicitud: 201 MiB; máximo: 20 archivos. Formatos aceptados: PDF, DOCX y TXT. La extensión se contrasta con la firma o contenido; DOCX tiene límite de expansión y PDF de páginas. El servidor sanea el nombre y usa rutas temporales aleatorias.
- Existe eliminación explícita por documento que borra manifiesto y chunks. Hay métodos internos para borrar corpus de un caso o purgar documentos por antigüedad, pero no se ejecuta purga automática al leer. El valor `CASE_CORPUS_RETENTION_DAYS` no constituye hoy una política de eliminación activa.
- No existe aún eliminación pública completa de caso, dueño, tasks o resultados. El journal persistente no usa TTL automático. Una política de conservación y borrado coordinado entre ambos SQLite queda pendiente de definición operativa y legal.
- La preparación de exportación devuelve datos de informe canónico para una task autorizada. Imprimir y copiar están disponibles en navegador. PDF y DOCX permanecen deshabilitados; `/api/export/pdf` responde `EXPORT_NOT_AVAILABLE`.

## Operación

- SQLite local está soportado para un solo worker con volumen persistente. Despliegues con varios workers o réplicas requieren una decisión posterior de almacenamiento compartido y coordinación de tareas. No se debe montar un volumen efímero como si fuera persistente.
- Producción requiere Legal Knowledge V2 explícito, la conexión V2 configurada, modelo de embeddings compatible, autenticación, CORS HTTPS explícito, límites de upload y journal persistente. Una fuente jurídica se lee internamente desde `legal_units.text` por `document_id` y `unit_id`; `official_url` es referencia externa secundaria.
- Sigue pendiente `LEGAL_SOURCE_ARCHIVE_REQUIRED`. NC-4 no conserva PDFs públicos ni implementa R2 o Supabase Storage.
