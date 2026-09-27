# Hardening técnico — Bloque 4.5

## RPC de NovaSearch

No existe una definición SQL local de `match_legal_knowledge` en los
directorios/versiones de migraciones incluidos en este repositorio. Por ello
no es posible verificar aquí el orden, tipos, defaults ni columnas de retorno
de la función real. `LegalRepository.semantic_search` conserva el payload que
ya construía (`query_embedding`, `match_threshold`, `match_count`,
`filtro_rama`, `filtro_tipo_documento`, `filtro_jerarquia`, `solo_vigentes`);
un test local fija exactamente ese payload, pero **no demuestra la firma del
servidor**. La verificación contra el SQL de Supabase queda como
“Requiere validación runtime posterior”. No se conectó a Supabase ni se
ejecutaron migraciones.

## Dependencias reproducibles

`backend/pyproject.toml` y `backend/uv.lock` son la fuente canónica que usa CI
con `uv sync --frozen`. `backend/requirements.txt` se conserva para
instalaciones pip compatibles y declara el conjunto runtime correspondiente;
si cambia una dependencia runtime, ambos manifiestos deben actualizarse.
Python soportado es 3.11 o superior. El workflow de validación instala el lock
congelado, ejecuta toda la suite `unittest` y `compileall`; para frontend usa
Node 22, `npm ci`, `npm test` y `npm run build`. El lock npm actual coincide
con las dependencias declaradas. `npm audit` no reportó vulnerabilidades al
auditar el lockfile de este bloque; no se ejecutó `npm audit fix`.

La ruta PDF legacy de simulación y el parser documental usan `pypdf`. Se
retiró PyPDF2 de los manifiestos directos y del lock. El contrato de extracción
documental page-aware, la detección `ocr_required` y sus pruebas no cambiaron.

## Staging de documentos

Al crear `DocumentTaskManager`, se intenta limpiar únicamente directorios
reales con nombre `nova-document-task-<sufijo>` directamente dentro del
directorio temporal del sistema y con una antigüedad superior a
`DOCUMENT_STAGING_MAX_AGE_SECONDS` (por defecto 86400). Los symlinks, entradas
recientes y nombres ajenos se conservan. Los errores de limpieza son best
effort y no impiden la inicialización. La limpieza normal de cada tarea sigue
eliminando su propio staging en `finally`.

`DocumentTaskManager` y las otras colas locales continúan siendo por proceso:
un reinicio pierde el estado y varios workers no comparten tareas. No se
introdujo una cola distribuida.

## Bundle y carga por ruta

NovaCase y las vistas legacy de proceso, simulación, reporte e interacción se
cargan ahora bajo demanda. NovaSearch, NovaCourt y MIKE ya eran rutas lazy.
El build debe conservar el comportamiento del router; los chunks resultantes
se registran en el reporte de cierre. No se añadió una herramienta de análisis
de bundle ni se cambiaron dependencias frontend.

## Límites pendientes

- Obtener la definición SQL del RPC y comparar firma/retorno antes de cambiar
  parámetros.
- Validar el RPC en entorno controlado cuando se autorice una comprobación
  runtime; este bloque no hizo llamadas externas.
- Persistencia distribuida de tareas, ownership/autorización multiusuario,
  retención productiva, OCR, visor documental y benchmark productivo quedan
fuera de este hardening.

## Resultado medido de este bloque

`npm audit --json` reportó 0 vulnerabilidades (0 info, low, moderate, high o
critical); no se ejecutó ningún fix automático. Como referencia histórica, el
informe del Bloque 1 registró 7 vulnerabilidades (2 moderate, 5 high).
`package.json` y la sección raíz de `package-lock.json` coinciden.

El chunk de entrada frontend quedó en 247.61 kB (85.28 kB gzip), frente a
1,638.23 kB reportados al cierre del Bloque 4. El chunk independiente de
`MarkdownRenderer` permanece en 1,076.58 kB (359.53 kB gzip), por lo que Vite
mantiene el warning de chunks >500 kB.
