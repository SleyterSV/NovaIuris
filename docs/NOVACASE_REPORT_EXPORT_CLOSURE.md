# NovaCase Informe — cierre de exportación

Validación local: 2026-10-24, rama `feat/novacourt-v2`.

El fallo del operador no se reprodujo. Al iniciar el diagnóstico no había
listeners en 5000, 5001 ni 5173. No hay evidencia suficiente para atribuirlo
a un backend antiguo, autorización, renderer o navegador.

Se arrancó temporalmente la aplicación real con su configuración local y se
hicieron POST HTTP a `/api/export/pdf` y `/api/export/docx` para las tres tareas
NovaCase completadas del propietario local de desarrollo, tomadas de la base
persistida existente. No se sustituyeron autenticación, repositorio ni renderers.
El servidor temporal se cerró al terminar.

Resultado: 6/6 HTTP 200, MIME correcto y Content-Disposition attachment con
extensión correcta. PDF: 86601, 86611 y 290344 bytes; los tres se abrieron con
PyMuPDF, con siete páginas A4 cada uno. DOCX: 42810, 43043 y 43067 bytes;
ZIP íntegro, word/document.xml presente, apertura con python-docx y ancho A4.
Se inspeccionó visualmente la primera página del primer PDF. No se certifica
la maquetación completa de DOCX en Word ni la descarga del navegador del operador.

Se conservaron los renderers existentes `case_pdf.py` (PyMuPDF Story, HTML/CSS)
y `case_docx.py` (python-docx). La referencia histórica a LaTeX deshabilitado
en STABILIZATION_BLOCK_1 no describe el endpoint actual. No se modificó backend.

Las burbujas numéricas se activan únicamente en ReportView; los labels canónicos
con corchetes y la resolución a fuentes permanecen intactos. Copy y los archivos
exportados conservan el contenido canónico existente.

## Paso mínimo pendiente del operador

En su sesión habitual, abrir un caso completado → Informe → pulsar «Descargar
PDF» y «Descargar DOCX», y abrir ambos archivos descargados. Si falla, conservar
de DevTools → Network el estado HTTP, código público del error, X-Request-ID y
URL de la petición `/api/export/pdf` o `/api/export/docx` (sin tokens ni contenido
del caso). Esa evidencia permite distinguir el entorno del operador del backend
actual, ya validado por HTTP con tareas persistidas reales.

Estado: OPERATOR_EXPORT_SMOKE_REQUIRED.
