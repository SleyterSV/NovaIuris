# NovaSearch → Legal Knowledge V2: cutover local

## Flujo actual antes del cambio

MYKE > Buscar usa `frontend/src/composables/useNovaSearch.js` y `frontend/src/services/searchTasks.js`: crea una tarea con `POST /api/search/tasks` y consulta `GET /api/search/tasks/<id>` hasta recibir `final_result`. El endpoint síncrono `POST /api/search` utiliza el mismo `SearchService`. En V1, `SearchService` analiza la consulta, genera un embedding con `EmbeddingService`, y `LegalRepository` consulta el RPC `match_legal_knowledge` en el proyecto configurado por `SUPABASE_URL` y `SUPABASE_KEY`. Después aplica fusión, reranking, construcción de contexto, generación de respuesta y validación de citas. El frontend consume `documents`, `sources`, `citations`, `answer`, `warnings` y `metadata`.

## Estado previo de Batch 002

El operador confirmó 6 documentos, 64 unidades, 0 relaciones y 6 runs en MYKE Legal. Las pruebas reales de MYKE > Buscar encontraron recuperación correcta de Casación 915-2022/ICA (fundamento Cuarto, páginas 5–6) y Sentencia TC 04826-2025-PHC/TC (decisión, página 9), además del artículo 3 de la Ley 27444. La prueba de 04810-2024-PA/TC reveló contaminación entre expedientes; la generación para 04826 agregó un motivo no sustentado. Esas pruebas son evidencia previa al endurecimiento descrito abajo y deben repetirse.

## Flujo V2 preparado

`LEGAL_KNOWLEDGE_VERSION=v2` hace que **solo la ruta NovaSearch** cree `SearchService(knowledge_version="v2")` y seleccione `LegalRepositoryV2`. El valor predeterminado es `v1`; NovaCase crea `SearchService()` sin selector y continúa en V1, y NovaCourt conserva su flujo actual. El servicio genera únicamente el embedding de la consulta mediante `EmbeddingService` y exige `text-embedding-3-small` y un vector de 1536 dimensiones. El repositorio V2 valida `MYKE_LEGAL_DATABASE_URL` contra la referencia del proyecto MYKE Legal (`emelxkoztshmzukydqzj`), abre una transacción de solo lectura, llama a `public.match_legal_knowledge_v2`, hace rollback y cierra la conexión. No utiliza `SUPABASE_URL` ni `SUPABASE_KEY` del corpus V1/Fiscal.IA. La CLI de búsqueda del piloto comparte la misma llamada SQL.

El RPC recibe `query_embedding`, `query_text`, `match_count`, `filter_document_type`, `filter_rama` y `filter_expediente`. El repositorio soporta los tres filtros; Buscar acepta `modulo`, `solo_vigentes` y el indicador de selección explícita `vigencia_explicit`. El módulo se traduce a `filter_rama`. V2 mantiene el orden híbrido del RPC: omite la fusión y el reranker propios de V1. En preguntas por la decisión de un expediente exacto se adelanta la unidad `decision` del mismo documento para presentarla como fuente primaria; no cambia el RPC ni sus pesos. No existe fallback automático V2 → V1. Una falla técnica produce `SEARCH_FAILED` (HTTP 503 en `/api/search`, estado `failed` en tareas).

## Contrato y citas

Cada unidad V2 usa `unit_id` como identidad del resultado y `chunk_id` de la fuente; `document_id` conserva la identidad del documento. Se conservan título, tipo de documento, tipo y número de unidad, encabezado, extracto exacto, páginas, similitud, puntuación léxica y URL oficial. Una lectura adicional de `legal_documents`, en la misma transacción de solo lectura, aporta metadata verificada para identidad exacta y `display_title` sin cambiar filas publicadas; el título editorial sigue disponible como metadata secundaria. El resultado mantiene `documents`, `sources`, `citations`, `answer`, `warnings` y `metadata`. `ContextBuilder` crea un marcador independiente por unidad; `AnswerService` recibe solo las unidades V2 seleccionadas y `resolve_citations` verifica los marcadores contra ese contexto. Una fuente V2 es verificable por `document_id`, `unit_id`/`chunk_id` y título, con página si existe en el documento; `official_url` agrega procedencia pero no es requisito. La cita muestra `page_start` únicamente cuando existe. No se fabrica URL, página, tribunal, cámara, fecha, materia ni expediente. `documents` son resultados recuperados; `sources` y `citations` incluyen exclusivamente unidades citadas en la respuesta. Por eso `retrieved_count` puede exceder `used_source_count`.

El RPC V2 devuelve unidades actuales de documentos listos, pero **no** certifica vigencia normativa. `VIGENCIA_FILTER_UNAVAILABLE` aparece solo si la consulta trata sobre vigencia o si el operador activó expresamente ese filtro (`vigencia_explicit=true` y `solo_vigentes=true`). El valor predeterminado del checkbox no dispara el aviso en preguntas ordinarias. La vigencia no se filtra en V2; no interpretar la búsqueda como certificación de vigencia.

## Endurecimiento 10.7.1

`explicit_tc_expediente` reconoce de modo determinista los identificadores TC visibles en la pregunta, incluidos espacios, guiones Unicode, `EXP.`, `EXPEDIENTE`, `N.º` y `N°`; normaliza el número y pasa `filter_expediente` al RPC. El repositorio verifica además que cada resultado pertenezca al expediente solicitado. Si no hay unidades de ese expediente, devuelve `no_exact_case_found` con `NO_EXACT_CASE_FOUND`, sin sustituirlo por otro caso. Si la pregunta pide la decisión pero no se recupera una unidad `decision`, devuelve `no_exact_decision_found` con un estado vacío específico, sin inferir el fallo de fundamentos ni presentar un resultado sin cita. Si hay decisión, solo esa unidad entra al contexto de respuesta; otros expedientes jamás entran. Las búsquedas abiertas sin expediente conservan la recuperación híbrida normal.

Las respuestas V2 abiertas reciben instrucciones de vincular cada afirmación jurídica sustantiva con una unidad citada. Las preguntas de decisión con expediente exacto usan una cita textual de la unidad `decision`, evitando agregar una causa no probada por esa unidad. Si el modelo omite marcadores, la respuesta se sustituye por un extracto atribuido y verificable. Esto impide el motivo especulativo observado en 04826. No equivale a verificación semántica automática de todas las afirmaciones del modelo en preguntas abiertas; esas respuestas aún necesitan revisión humana.

MYKE presenta `regulation`, `judgment`, `order`, `cassation` y `jurisprudence` con etiquetas españolas y conserva los valores canónicos en la API. Las unidades V2 muestran un único **EXTRACTO RELEVANTE** con texto fuente, sin duplicar preview y detalle ni llamarlo síntesis. El preview de backend, cuando se usa, corta al final de una palabra u oración y añade puntos suspensivos; no cambia el extracto canónico. El tiempo visible mide la búsqueda completa en el cliente (`performance.now`), expresado en ms o s. La normalización agresiva de palabras partidas por extracción PDF queda fuera del bloque: cadenas como `r ecurrente` o `sent encia` requieren corregir la fuente/parser con evidencia suficiente, y no se alteran aquí por heurística.

## Completitud y presentación de fuentes 10.7.2

Las cuatro preguntas reales Q1–Q4 pasaron funcionalmente según la aceptación del operador: artículo 3 de Ley 27444; decisión solo del expediente 04810; fundamento Cuarto, páginas 5–6, de Casación 915-2022/ICA; y decisión solo del expediente 04826, página 9 y URL oficial. La inspección del modal de cada pregunta queda pendiente antes del commit y cierre.

**Causa del corte:** los parsers preparan `LegalUnit.text` completo y `LegalUnit.excerpt = normalized_text[:240]`; la publicación guarda ambos campos separados. El RPC V2 selecciona `u.excerpt` sin recortarlo de nuevo; `LegalRepositoryV2` y `SearchService` lo conservan como texto de resultado. `ContextBuilder` recibe ese extracto ya limitado y la fuente citada, la API y el modal mostraban el mismo fragmento de 240 caracteres. La CLI de búsqueda del piloto además lo limita a 240 para su propia salida; no es la ruta del frontend. Así, los finales `normati` y `decisión jud` proceden de la construcción del excerpt, no del CSS ni de una mutación del texto canónico. No hay DSN de MYKE Legal disponible en este entorno para comparar directamente las filas publicadas `text`/`excerpt`; la lectura remota conectada fue denegada. La verificación de completitud de Q1–Q4 se hará en los modales reales.

La tarjeta V2 utiliza `resumen_ia` como preview, cortado en palabra u oración a un máximo de 220 caracteres y con `…`; evita mostrar el `excerpt` de 240 caracteres que puede acabar a mitad de palabra. Al abrir la fuente citada, `GET /api/search/sources/<unit_id>` obtiene **una sola unidad actual de un documento publicado** desde `legal_units.text`, en transacción de solo lectura y sin consultar embeddings. Se comprueban `unit_id` y `document_id` antes de mostrarla. Si falla la lectura, el modal indica claramente que solo muestra el fragmento citado; no lo presenta como texto íntegro. Ni la respuesta ni las citas ya emitidas se reescriben al abrir la fuente. V1 y las fuentes privadas de NovaCase siguen usando su modal existente sin llamada a este endpoint.

El título principal se compone únicamente con metadata verificada: para casación, `number` o `expediente`; para decreto supremo, `resolution_type` y `number`; para Auto y STC, el expediente y el tribunal. El título editorial se conserva como metadata secundaria. Los labels de unidad incluyen `Disposición`, `Antecedente`, `Decisión`, `Sumilla`, `Materia` y `Voto u opinión separada`, además de `Artículo` y `Fundamento`. La ficha muestra tipo, tribunal/entidad, expediente o número, unidad, encabezado, página, metadata disponible y enlace **ABRIR FUENTE OFICIAL** solo si hay URL verificada.

**Limitación conocida:** el espaciado defectuoso de algunas palabras de la casación ya estaba registrado en la revisión manual de Batch 002 como artefacto de extracción PDF. Sin acceso de lectura a las filas publicadas, este bloque no afirma en qué filas aparece. No se aplicó una unión heurística de palabras ni se modificaron el parser, el corpus publicado, el RPC o el ranking.

## Configuración local y API

### Diagnóstico del detalle de fuente 10.7.3

Las cuatro consultas Q1–Q4 siguen pasando en recuperación. El fallo común del modal se reprodujo en el backend local que escuchaba en `localhost:5001`: `GET /api/search/sources/<unit_id>` y `OPTIONS` para esa ruta devolvían HTTP 404 (`REQUEST_FAILED`). El proceso Python había arrancado antes de añadirse la ruta. En el checkout actual, el mapa de rutas de Flask sí registra `GET /api/search/sources/<uuid:unit_id>`; por ello, el proceso en ejecución debe reiniciarse desde este checkout con las variables privadas del operador. El 404 observado se produjo antes de cualquier lectura de `legal_units` y no demuestra un problema con el texto canónico ni con la conexión de MYKE Legal.

El flujo actual del modal es: clic en la fuente citada → `loadLegalUnitSource(unit_id, document_id)` → `GET /api/search/sources/<unit_id>?document_id=<document_id>` con la sesión existente → ruta Flask → `LegalRepositoryV2.get_unit` → lectura de una fila `legal_units` unida a su `legal_documents` publicado, en transacción de solo lectura con `MYKE_LEGAL_DATABASE_URL` → validación de las dos identidades en el cliente → presentación de `text` íntegro. La consulta valida el `document_id` en SQL y no devuelve una unidad de otro documento. UUID inválido da 400; unidad ausente o identidad discordante, 404; error de base de datos, 503. Durante la carga se muestra un estado discreto; si falla, queda visible el fragmento citado con aviso. No se modifica el texto canónico ni se descargan documentos completos.

Tras reiniciar el backend, un `OPTIONS` a la ruta con un UUID de prueba debe dejar de devolver 404; después hay que verificar las cuatro unidades reales por sus `unit_id` y `document_id`. La respuesta debe contener `unit.text` completo, identidad y páginas correctas. Comparar `unit.text` con el extracto RPC para demostrar la diferencia donde la unidad sea más larga. El entorno de trabajo no dispone del DSN privado ni de los cuatro UUID reales, así que esa comprobación conectada y la aceptación visual siguen pendientes del operador. No se declarará 10.7 cerrado ni se hará el commit final hasta obtener las cuatro inspecciones.

En una consola PowerShell del backend, con las variables de entorno privadas ya configuradas por el operador:

```powershell
cd D:\NovaIuris\backend
$secureDsn = Read-Host 'DSN privado de MYKE Legal' -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureDsn)
try { $env:MYKE_LEGAL_DATABASE_URL = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
Remove-Variable -Name secureDsn,pointer
$env:LEGAL_KNOWLEDGE_VERSION = 'v2'
$env:OPENAI_EMBEDDING_MODEL = 'text-embedding-3-small'
python -m app.legal_ingestion.publication_entrypoint search "¿Por qué la lectura de la sentencia es un acto formal en la Casación 915-2022/ICA?" --top-k 5 --json
python -m app.legal_ingestion.publication_entrypoint search "¿Qué resolvió el Tribunal Constitucional en el expediente 04826-2025-PHC/TC sobre la demanda de hábeas corpus?" --top-k 5 --json
uv run python run.py
```

`MYKE_LEGAL_DATABASE_URL` debe apuntar al proyecto MYKE Legal. `backend/.env` ya contiene `OPENAI_API_KEY`, `LLM_API_KEY` y `ZEP_API_KEY`; el proceso backend las carga localmente. Verificar su disponibilidad sin imprimir valores. Las claves permanecen en el servidor; el frontend no recibe el DSN ni el vector. Para la interfaz:

```powershell
cd D:\NovaIuris\frontend
npm run dev
```

Vite declara el puerto 3000 y proxy `/api` hacia `http://localhost:5001`; usar la URL que Vite muestre si toma otro puerto. El cliente usa `VITE_API_BASE_URL` o `VITE_API_URL` cuando están definidos. La interfaz crea `POST /api/search/tasks` con `{query, filtros}` y consulta `GET /api/search/tasks/<task_id>`. El endpoint directo `POST /api/search` devuelve `success`, `result_status`, `documents`, `sources`, `citations`, `answer`, `warnings` y `metadata.knowledge_version`.

Con el backend local encendido, abrir una tercera consola PowerShell para verificar el endpoint real antes de abrir MYKE:

```powershell
$body = @{ query = '¿Por qué la lectura de la sentencia es un acto formal en la Casación 915-2022/ICA?'; filtros = @{ modulo = 'Todos'; solo_vigentes = $false } } | ConvertTo-Json -Depth 4
$response = Invoke-RestMethod -Uri 'http://localhost:5001/api/search' -Method Post -ContentType 'application/json; charset=utf-8' -Body $body
$response.success
$response.metadata.knowledge_version
$response.documents | Select-Object titulo, unit_id, document_id, unit_type, page_start, official_url
$response.citations | Select-Object source_id, locator
```

Confirmar HTTP 200, `success=true`, `knowledge_version=v2`, documento/unidad correctos, fuente y página reales y una respuesta que cite la unidad. No usar este endpoint legacy en producción.

## Prueba manual de MYKE > Buscar

Antes de probar la interfaz, revisar las dos salidas JSON de la consola backend: rank, unidad relevante, `unit_type`, páginas, `document_id` y `unit_id`. Detener el proceso si alguno de los dos documentos no aparece con una unidad jurídicamente pertinente.

Luego probar estas preguntas en MYKE > Buscar y comparar respuesta, fuente, unidad y página con el original:

1. ¿Dónde debe publicarse el Texto Único Ordenado de la Ley 27444?
2. ¿Cuál fue la decisión del Tribunal Constitucional en el expediente 04810-2024-PA/TC?
3. ¿Por qué la lectura de la sentencia es un acto formal en la Casación 915-2022/ICA?
4. ¿Qué resolvió el Tribunal Constitucional en el expediente 04826-2025-PHC/TC sobre la demanda de hábeas corpus?

La recuperación con los seis documentos reales requiere la conexión privada del operador. Los tests automatizados usan filas V2 simuladas y verifican el contrato y las citas; no sustituyen el smoke remoto ni la revisión jurídica de las respuestas generadas.

## Verificación, observabilidad y rollback

Verificación local tras 10.7.3: `python -m compileall -q app tests` PASS; `python -m unittest discover -s tests -v` **289 PASS**; `npm test` **37 PASS**; `npm run build` PASS. Los tests cubren RPC y filtros, transacción de solo lectura, vector, mapeo de artículo/fundamento/decisión/casación, identidad exacta de expedientes, aislamiento del contexto, ausencia de sustitución semántica, citas con/sin URL, página real, resultados recuperados frente a fuentes citadas, lectura de unidad completa por ID, selector V1/V2, NovaCase, endpoints y estados vacíos. Los tests de Node y el build necesitaron ejecutarse fuera del sandbox porque el sandbox bloqueó `spawn` con `EPERM`. La suite incluyó una corrección semántica de un test preexistente de timeout de NovaCourt: una tarea cancelada antes de empezar no puede señalizar su finalización; si llega a empezar, se comprueba su salida y que no ejecute la siguiente operación. El log de NovaSearch registra versión, cantidad, tipos documentales, resultado vacío y tiempos; no registra vector ni credenciales.

**Aceptación real completada (10.7):** el operador repitió Q1–Q4 desde MYKE frontend. Q1 recuperó el artículo 3 de Ley 27444 y su modal cargó la unidad completa. Q2 recuperó solo el expediente 04810-2024-PA/TC, con su decisión correcta y unidad completa. Q3 recuperó Casación 915-2022/ICA, fundamento Cuarto, páginas 5–6 y unidad completa. Q4 recuperó solo 04826-2025-PHC/TC, su decisión, página 9, URL oficial y unidad completa. En ningún modal apareció el aviso de error. **Retrieval acceptance 4/4 PASS; source detail acceptance 4/4 PASS.** Esta evidencia procede de la inspección real comunicada por el operador; los tests automatizados usan proveedores simulados.

**Limitación conocida:** algunas unidades ya publicadas contienen ruido de extracción PDF, incluidos números físicos de página dentro del texto y palabras partidas como `sent enciado`, `Ju sticia` y `casaci ón`. Es una deuda de extracción del corpus, no un fallo del retrieval ni del runtime. Los seis documentos publicados permanecen intactos; cualquier corrección futura exige validación generalizable y decisión separada de versionado/reingesta.

Para volver a V1 sin revertir código, detener el backend local, establecer `$env:LEGAL_KNOWLEDGE_VERSION = 'v1'` y reiniciarlo. Quitar la variable también selecciona V1. El frontend no requiere cambios de configuración para el rollback. No se elimina V1, no se altera Auth y no se publica en producción desde este bloque.
