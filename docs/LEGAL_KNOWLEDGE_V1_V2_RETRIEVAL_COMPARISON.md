# Legal Knowledge V1 vs V2 — comparación de retrieval (bloque 10.5)

## Alcance y método

Comparación de solo lectura sobre las cuatro preguntas Q1–Q4 del primer piloto V2. V1 es `public.legal_knowledge` de Fiscal.IA; V2 es `public.legal_documents`/`public.legal_units` de MYKE Legal. No se copiaron filas ni vectores entre proyectos, no se modificó ningún corpus y no se cambió NovaSearch.

Para V1 se generó un embedding nuevo por pregunta con `text-embedding-3-small` (1536 dimensiones) y se llamó al RPC vigente `match_legal_knowledge` con `match_count=5`, `match_threshold=0`, `solo_vigentes=true`, sin filtros. El umbral cero evita excluir resultados por un umbral distinto del RPC V2. La búsqueda V2 procede de las consultas reales ejecutadas manualmente en 10.4B-2 y registradas en [la primera publicación](LEGAL_KNOWLEDGE_V2_FIRST_PUBLICATION.md): Q1, Q2 y Q4 sin filtros, `top-k=5`; Q3 con `document_type=order`, expediente `04810-2024-PA/TC` y `top-k=10`. **Esa diferencia de filtro y tamaño de salida impide atribuir toda la mejora operativa de Q3 exclusivamente al ranking.** En ambas versiones se evalúa el retrieval directo, sin reranker, respuesta generada ni cutover del producto.

Se hizo una segunda medición V1 con los mismos textos de pregunta y el mismo modelo, ordenando por distancia vectorial únicamente **ocho filas equivalentes**: cuatro artículos del decreto (`id` 8482–8485) y cuatro fragmentos del Auto (`id` 10915–10918). Es un control analítico de ranking, no el RPC operativo ni una modificación de la base. Cada medición usó un embedding de consulta generado de nuevo; no se reutilizaron embeddings V1 del corpus ni se imprimieron vectores.

El contraste operativo tiene tamaños distintos: V1 busca en **11 448** filas de `legal_knowledge`; V2 contiene **2 documentos y 15 unidades**. Los rangos de ambos corpus completos no son una comparación aislada del algoritmo. La medición de ocho filas ayuda a separar ese efecto del de estructura, aunque V1 conserva un artículo contaminado por texto adicional y fragmentos jurisprudenciales de tamaño fijo.

## Cobertura real del mismo contenido

| Contenido | V1, Fiscal.IA | V2, MYKE Legal |
| --- | --- | --- |
| Decreto Supremo 006-2026-JUS | Sus artículos 1–4 figuran como `id` 8482–8485 bajo la fuente genérica «TUO Ley del Procedimiento Administrativo General», tipo `Ley`, sin número del decreto. El artículo 4 mide 16 964 caracteres y absorbe la disposición derogatoria, texto editorial y comienzo del TUO. La fuente completa contiene 267 filas; solo estas cuatro representan el decreto piloto. | Documento `regulation` identificado como `006-2026-JUS`: cuatro artículos y una disposición única en cinco unidades separadas. |
| Auto TC 04810-2024-PA/TC | Cuatro filas (`id` 10915–10918) de una misma fuente; `Fragmento 3` contiene el fundamento 7 y `Fragmento 4` contiene `RESUELVE Declarar IMPROCEDENTE`. Están etiquetadas `Sentencia`/`Fragmento N`; `expediente` y `ponente` están vacíos, `numero=ERA`, `metadata={}`. | Documento `order` con expediente estructurado, ocho fundamentos, antecedente y decisión; diez unidades, páginas 1–3. |

La cobertura V1 existe para **ambos contenidos**. Una búsqueda por `006-2026-JUS` en todo V1 también encuentra citas en otro precedente: esas menciones no se contaron como el documento piloto. El Auto no se marcó como ausente: su fallo está completo en `Fragmento 4`, aunque el número de expediente no está estructurado y solo aparece en el texto de los fragmentos anteriores.

## Preguntas y resultados

| ID | Pregunta | Unidad o conjunto necesario |
| --- | --- | --- |
| Q1 | ¿Qué norma aprueba el Texto Único Ordenado y qué dispone sobre su publicación? | Decreto, artículos 2 y 3; identidad del instrumento. |
| Q2 | ¿Por qué el Tribunal Constitucional señala que no todos los casos conocidos mediante recurso de agravio constitucional requieren audiencia? | Auto, fundamento 7. |
| Q3 | ¿Cuál fue la decisión del Tribunal Constitucional en el expediente 04810-2024-PA/TC? | Auto, decisión `Declarar IMPROCEDENTE` el pedido de nulidad entendido como aclaración. |
| Q4 | ¿Dónde debe publicarse el Texto Único Ordenado de la Ley 27444? | Decreto, artículo 3 «Publicación». |

### V1 operativo: Top 5 de 11 448 filas

| Consulta | Resultado correcto y rango | Observación de los cinco primeros |
| --- | --- | --- |
| Q1 | Artículo 2 en **rank 3**; artículo 1 en rank 5; artículo 3 **fuera de Top 5**. Documento hit, respuesta de dos partes incompleta. | Rank 1 es un artículo del Código Procesal Civil y rank 2 uno del Código Tributario, ambos sobre otro TUO. |
| Q2 | El Auto y su fundamento 7 **fuera de Top 5**. | Los cinco resultados pertenecen a otras tres fuentes TC; dos pares son fragmentos distintos de una misma fuente. No son duplicados textuales. |
| Q3 | El Auto y su `Fragmento 4` decisorio **fuera de Top 5**. | Los cinco resultados son fragmentos de otras dos fuentes TC: tres de una y dos de otra. Hay ruido de identidad, no una decisión del expediente pedido. |
| Q4 | Artículo 3, `id` 8484, **rank 1** (similarity ≈0.67583). | Artículos 2 y 1 en ranks 2 y 3; otros TUO en ranks 4–5. Recuperación sustantiva correcta. |

Las 17 filas distintas observadas en esos cuatro Top 5 tienen 17 textos distintos según hash de texto calculado en SQL: **no se observó duplicación textual exacta** en la muestra. La repetición de fuentes en Q2/Q3 es concentración de fragmentos, no copia idéntica. Los fragmentos V1 sí cortan prosa a mitad de oración: por ejemplo, el Auto pasa de `Fragmento 1` a `Fragmento 2` entre «etapa de la» y «convocatoria obligatoria», y de `Fragmento 2` a `Fragmento 3` dentro de la cita del fundamento `211` de otra sentencia.

### V1 limitado a ocho filas equivalentes

| Consulta | Rangos V1 controlados | Lectura causal |
| --- | --- | --- |
| Q1 | Artículo 2 **1**, artículo 1 **2**, artículo 3 **3**, artículo 4 **4**. | V1 puede reunir aprobación y publicación al retirar el ruido de otros TUO; el fallo operativo del artículo 3 es principalmente de tamaño/competencia del corpus. |
| Q2 | `Fragmento 3` con fundamento 7 **1**; `Fragmento 2` **2**. | La señal vectorial de V1 para este fundamento sí funciona en corpus limitado. La omisión operativa Top 5 es principalmente competencia con miles de fragmentos, agravada por falta de filtro de expediente y unidad tipada. |
| Q3 | `Fragmento 2` **1**, `Fragmento 3` **2**, `Fragmento 1` **3**, **`Fragmento 4` con `RESUELVE` 4**. | Incluso entre equivalentes, V1 prioriza tres fragmentos no decisorios. Aquí hay un problema de ranking/estructura adicional al tamaño del corpus: no existe `unit_type=decision` ni expediente utilizable como filtro. |
| Q4 | Artículo 3 **1**, artículo 2 **2**, artículo 1 **3**. | V1 ya resuelve bien esta referencia exacta; V2 no debe atribuirse una mejora de rank aquí. |

No se interpretan diferencias pequeñas de similarity entre ejecuciones como cambios de calidad: se generaron vectores de pregunta nuevos para la medición controlada. Los rangos y el contenido, no los decimales del score, fundamentan la conclusión.

### V2 real y scorecard

| Consulta | V1 operativo: rango / calidad | V1 controlado: rango de unidad objetivo | V2 real: rango / calidad | Ganador y motivo |
| --- | --- | --- | --- | --- |
| Q1 | Art. 2 **3**, art. 3 **>5** / **ACCEPTABLE parcial** | Arts. 2 y 3: **1 y 3** | Artículos relevantes en **Top 3**, lexical positivo / **GOOD** | **V2 en operación**: responde las dos partes y conserva identidad del decreto; V1 también recupera ambas en el control. |
| Q2 | Fundamento 7 **>5** / **BAD** | `Fragmento 3`: **1** | Fundamento 7 **1**, lexical positivo / **GOOD** | **V2 en operación**; el control muestra que gran parte de la brecha proviene del tamaño del corpus, con mejor estructura/cita en V2. |
| Q3 | Decisión **>5** / **BAD** | `Fragmento 4`: **4** | `decision` **1**, página 3, lexical 0.6 / **GOOD** | **V2**: unidad decisoria explícita e intención reconocida. Q3 V2 usó filtro de tipo y expediente; V1 no dispone de esos metadatos fiables. |
| Q4 | Artículo 3 **1** / **GOOD** | Artículo 3: **1** | Artículo 3 **1**, similarity ≈0.713, lexical 1.7 / **GOOD** | **Empate de retrieval**; V2 mejora la identidad del documento y el tipo de unidad. |

**Definiciones:** `document hit` exige la fuente jurídica correcta entre Top 5; `unit hit completo` exige todas las unidades necesarias para responder (dos artículos en Q1); Top 1/3/5 se refieren a presencia de esa evidencia completa. Con estas definiciones, V1 operativo tiene document hit **2/4** y unit hit completo **1/4**; V1 controlado, **4/4** y **4/4 en Top 5**, pero Q3 solo en rank 4; V2, según la revisión manual registrada, **4/4** y evidencia relevante en **Top 3**. La muestra de cuatro preguntas y los filtros desiguales de Q3 no justifican extrapolar esos cocientes a todo el corpus.

| Métrica en estas cuatro preguntas | V1 operativo | V1, ocho filas | V2 piloto |
| --- | --- | --- | --- |
| Documento correcto en Top 5 | 2/4 | 4/4 | 4/4, revisión manual |
| Evidencia completa en Top 1 | 1/4 | 2/4 | 3/4; Q1 requiere dos artículos |
| Evidencia completa en Top 3 | 1/4 | 3/4 | 4/4, revisión manual de Q1 |
| Evidencia completa en Top 5 | 1/4 | 4/4 | 4/4, revisión manual |
| Duplicado textual exacto | 0 entre 17 filas distintas observadas en los cuatro Top 5 | No se midió por separado | No se midió en resultados de las cuatro consultas |

La completitud de procedencia se mide por campos disponibles, no por similarity: V1 conserva `id`/fuente en las dos fuentes, pero **0/2** tienen número del decreto o expediente del Auto estructurado y **0/2** ofrecen página/URL en estas filas. V2 conserva documento y unidad identificables en **2/2**; la página existe para el Auto (**1/1 PDF**), mientras el DOCX no aporta paginación verificable; la URL oficial está ausente en **2/2**. Estas cifras describen este piloto, no tasas del corpus total.

## Integridad, estructura y procedencia

| Criterio | V1 observado | V2 observado |
| --- | --- | --- |
| Integridad | Artículos 1–3 del decreto son legibles. Artículo 4 mezcla 16 964 caracteres de refrendo, disposición, texto editorial y TUO. El Auto se fragmenta por tamaño y corta oraciones; el fallo queda al final del cuarto fragmento. | Cinco unidades semánticas del decreto y diez del Auto; artículo, disposición, fundamento y decisión separados. |
| Metadatos jurídicos | Decreto registrado como `Ley` bajo título del TUO, sin número del DS. Auto registrado como `Sentencia`, expediente vacío, `numero=ERA`, ponente vacío. El número del expediente se lee en el texto de algunos fragmentos, no en un campo fiable. | Decreto `regulation` con número; Auto `order` con expediente y decisión tipada. |
| Página y URL | Las filas V1 observadas no tienen columnas de página ni de URL oficial; `metadata={}`. | Auto con páginas 1–3 y decisión en página 3. El DOCX del decreto carece de página física verificable. `official_url` es nulo en ambos documentos piloto. |
| Cita trazable | `id`, fuente y etiqueta `ARTÍCULO N` o `Fragmento N` permiten localizar un registro, pero el Auto no ofrece fundamento/decisión como identidad de unidad ni página; una cita jurídica precisa exige cotejo manual del original. | `unit_id`, `document_id`, título, tipo documental, tipo/número de unidad y página cuando existe permiten citar sin inventar esos campos. Se debe omitir URL y página si son nulas. |

La fortaleza V1 demostrada es la recuperación exacta del artículo 3 en Q4 y, dentro del subconjunto equivalente, del fundamento 7 y los dos artículos de Q1. Su corpus amplio aporta cobertura temática que V2 aún no tiene. Las debilidades demostradas son la pérdida de identidad del decreto y del expediente, la clasificación errónea del Auto, los cortes de texto, la megaunidad y la incapacidad operativa de recuperar el Auto en Top 5 para Q2/Q3.

V2 gana en unidades jurídicas, procedencia, filtros e intención de decisión en este piloto. Sus límites siguen siendo importantes: **solo dos documentos**, ningún vínculo `legal_relations`, URL oficial ausente en ambos y página no verificable en el DOCX. La superioridad operativa de Q2 puede reducirse al ampliar el corpus; la comparación controlada muestra que V1 ya tenía buena similitud para ese fundamento. La mejora de Q3 es más estructural, aunque su prueba manual V2 usó filtros que V1 no puede replicar.

## Decisión

**GO para iniciar el bloque 10.6, reingesta completa V2, con publicación por lotes sometida a los quality gates existentes.** La evidencia de dos tipos documentales justifica ampliar cobertura: V2 resuelve los cuatro casos revisados y conserva la procedencia que V1 pierde. Este GO autoriza abordar la reingesta como trabajo de calidad y cobertura; no presupone que todos los originales sean publicables ni autoriza carga masiva sin revisión. Los documentos previamente marcados `review_required` u OCR siguen bloqueados hasta resolver sus causas. El resultado del bloque 10.6 deberá medirse de nuevo con un corpus V2 comparable en tamaño antes de considerar el cutover 10.7.

Durante 10.5 no se modificaron datos V1/V2, no se cargaron documentos, no se cambiaron SearchService/AnswerService y no se inició 10.6.
