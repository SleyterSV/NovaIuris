# Legal Knowledge V2: plan de migración

## Límites de este bloque

El proyecto Supabase MYKE Legal está vacío. Esta entrega prepara SQL y tooling; **no aplica la migración**, no conecta el runtime, no carga toda la biblioteca, no copia usuarios y no cambia credenciales de `.env`. El Supabase anterior y V1 permanecen operativos. Mover la base de búsqueda no mueve Supabase Auth: usuarios, sesiones y login requieren un plan de corte separado.

## Secuencia propuesta

1. Conservar V1 y hacer inventario de documentos originales. V1 sirve para comparar cobertura y recuperar metadatos, no como fuente textual definitiva si existe el original.
2. Revisar el SQL versionado y aplicarlo **solo** al proyecto nuevo MYKE Legal, con respaldo y entorno identificados por el operador. Verificar extensión vector, cuatro tablas, RLS, índices y RPC. No aplicar a Fiscal.IA ni al proyecto V1.
3. Ejecutar dry-run local del piloto. Ejemplo desde `backend`: `python -m app.legal_ingestion.cli --dry-run "../raw_docs/CONSTITUCION POLITICA.docx" "../raw_docs/CODIGO CIVIL.docx"`. La salida contiene conteos, metadatos y advertencias, no texto completo.
4. Completar revisión humana de documentos `review_required`, especialmente extracción PDF, identidad de la resolución, precedente, colisiones de hash y unidades demasiado largas. Un adaptador de staging/publicación y pruebas de integración sobre el proyecto nuevo son trabajo posterior; **este bloque no inserta datos**.
5. Cargar un piloto pequeño desde documentos originales: Constitución, Código Civil, Código Procesal Civil, Código Tributario/SPIJ HTML, Ley General de Sociedades, Nueva Ley Procesal del Trabajo, sentencia TC, auto TC, casación Corte Suprema, precedente vinculante y documento de mala extracción. El `.doc` HTML se prueba con fixture sintético si no hay original local.
6. Comparar V1/V2 para búsquedas por artículo, número de expediente, conceptos y filtros; evaluar precisión, cobertura, citas, páginas y falsos positivos. Aprobar calidad antes de carga masiva.
7. Ingerir en lotes V2, luego incorporar dual-read con bandera futura `LEGAL_KNOWLEDGE_VERSION=v1|v2`, cambiar lectura tras verificación, estabilizar y congelar V1. La bandera no se activa aquí.

## Checklist previo a aplicar el esquema

- Confirmar que el destino CLI es el **nuevo** Supabase MYKE Legal y que el proyecto viejo no está enlazado.
- Revisar `supabase/migrations/20261006162217_legal_knowledge_v2_foundation.sql`; aplicar con procedimiento de migraciones del proyecto nuevo y verificar que ninguna tabla V1 se modifica.
- Verificar `vector(1536)`, configuración PostgreSQL `spanish`, índices GIN/HNSW, RLS habilitado y ausencia de permisos frontend sobre tablas V2.
- Mantener `SUPABASE_URL`, `SUPABASE_KEY`, `VITE_SUPABASE_URL` y `VITE_SUPABASE_ANON_KEY` actuales. Guardar cualquier service role del nuevo proyecto solo en configuración segura del backend, en una fase posterior.
- No conectar SearchService/Retriever/AnswerService hasta que el piloto y el plan de Auth estén aprobados.

La aplicación remota del esquema y la carga piloto se hacen manualmente después de esta entrega; no se ejecutan en este bloque.
