# NovaCase — Bloque 5

## Flujo

NovaCase conserva su orquestador existente. El flujo analiza el relato y los fragmentos seleccionados del Case Corpus, genera estrategia inicial, ejecuta consultas de investigación limitadas, produce argumentos, analiza evidencia y riesgos en paralelo, genera contraargumentos, deriva una estrategia final de forma determinista y prepara una sola generación del informe. Las etapas `facts`, `research`, `arguments`, `evidence`, `risks`, `counter_arguments`, `final_strategy`, `report` y `citations` informan el progreso.

## Datos y procedencia

`case_professional.py` crea hechos con IDs deterministas y estados `alleged`, `supported`, `disputed` o `unclear`; fechas explícitas; cuestiones jurídicas con IDs estables; cronología ordenada; y asociaciones de hechos, cuestiones y fuentes filtradas contra el resultado del caso. La existencia de un marcador no convierte automáticamente una alegación en hecho probado. Fuentes privadas se aceptan solo si contienen el mismo `case_id`; las normas preliminares no se incorporan a las fuentes verificadas.

Las consultas de investigación están limitadas por `CASE_RESEARCH_MAX_QUERIES`. NovaSearch se llama sin respuesta generada y las fuentes conservan el contrato común. El informe recibe un conjunto limitado de fuentes y sus fragmentos, incluidos documentos privados del caso correspondiente. Los marcadores `[SRC-…]` se resuelven contra ese conjunto; los marcadores desconocidos se descartan. Referencias numéricas ordinarias se conservan como texto y no se vuelven citas activas.

## Workspace e informe

El contrato Case incluye `facts`, `issues`, `timeline`, `final_strategy`, `report_status`, `report_error`, `report_document`, `citations` y `sources_used` además de los campos anteriores. `report_document` usa el perfil `analysis_report`, separa secciones Markdown, conserva `case_id`, fecha de generación, citas y únicamente fuentes citadas. Es independiente de PDF, DOCX y HTML y no provoca una segunda llamada al modelo.

La vista NovaCase organiza resumen, análisis, argumentos, evidencia, riesgos, contraargumentos, estrategia, fuentes e informe; oculta pestañas sin contenido. El informe comparte Markdown, `SourcesList` y `SourceModal`. Copiar conserva el texto Markdown del informe; impresión usa el navegador. PDF y DOCX permanecen deshabilitados hasta disponer de un renderer seguro. Si falla el informe o la validación de citas, el resultado conserva el análisis estructurado con estado parcial.

## Limitaciones y trabajo posterior

Las asociaciones de hechos y fuentes dependen de los IDs que produzcan los servicios; requieren revisión humana. La calidad editorial y la selección de fuentes deben evaluarse con casos de referencia aprobados. La recuperación privada sigue limitada por los fragmentos seleccionados para cada operación. No se cambian modelos ni prompts para reducir costes. La optimización de latencia y tokens, la revisión jurídica peruana con documentos de referencia, el visor de documentos y la exportación profesional PDF/DOCX quedan para fases posteriores.
