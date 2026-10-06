<template>

    <section class="graph-panel">

        <!-- =====================================================
             DECORACIÓN INSTITUCIONAL
        ====================================================== -->

        <div
            class="panel-accent"
            aria-hidden="true"
        ></div>

        <div
            class="panel-orbit panel-orbit-right"
            aria-hidden="true"
        ></div>

        <div
            class="panel-orbit panel-orbit-left"
            aria-hidden="true"
        ></div>


        <!-- =====================================================
             ENCABEZADO
        ====================================================== -->

        <header class="graph-header">

            <div class="graph-heading">

                <div class="section-label">

                    <span class="label-line"></span>

                    <span>
                        NOVACOURT
                    </span>

                    <span class="label-dot"></span>

                    <span>
                        MAPA RELACIONAL
                    </span>

                </div>


                <h2>
                    Red de Relaciones del Caso
                </h2>


                <p>

                    Visualización estructurada de los actores,
                    argumentos, evidencias, normas y demás elementos
                    identificados durante el análisis judicial.

                </p>

            </div>


            <!-- =================================================
                 ESTADÍSTICAS
            ================================================== -->

            <div
                v-if="hasGraphData"
                class="graph-stats"
            >

                <div class="stat-item">

                    <span class="stat-caption">
                        ELEMENTOS
                    </span>

                    <strong>
                        {{ normalizedNodes.length }}
                    </strong>

                    <span class="stat-label">
                        Nodos
                    </span>

                </div>


                <div class="stat-divider"></div>


                <div class="stat-item">

                    <span class="stat-caption">
                        VÍNCULOS
                    </span>

                    <strong>
                        {{ normalizedLinks.length }}
                    </strong>

                    <span class="stat-label">
                        Relaciones
                    </span>

                </div>

            </div>

        </header>


        <!-- =====================================================
             LEYENDA
        ====================================================== -->

        <div
            v-if="hasGraphData"
            class="graph-legend"
        >

            <div class="legend-title">

                <span class="legend-title-mark"></span>

                <span>
                    Clasificación jurídica
                </span>

            </div>


            <div class="legend-items">

                <div
                    v-for="item in legendItems"
                    :key="item.key"
                    class="legend-item"
                >

                    <span
                        class="legend-dot"
                        :style="{
                            background: item.color,
                            boxShadow: `0 0 0 3px ${hexToRgba(item.color, .10)}`
                        }"
                    ></span>

                    <span>
                        {{ item.label }}
                    </span>

                </div>

            </div>

        </div>


        <!-- =====================================================
             ESTADO DE CARGA
        ====================================================== -->

        <div
            v-if="loading"
            class="graph-state graph-loading"
        >

            <div class="loading-visual">

                <div class="loading-ring"></div>

                <span>
                    ⚖
                </span>

            </div>


            <div class="state-content">

                <span class="state-eyebrow">
                    NOVACOURT · PROCESAMIENTO
                </span>

                <strong>
                    Construyendo red relacional
                </strong>

                <p>

                    NovaCourt está organizando los elementos
                    y relaciones identificados en el caso.

                </p>

            </div>

        </div>


        <!-- =====================================================
             ERROR
        ====================================================== -->

        <div
            v-else-if="effectiveError"
            class="graph-state graph-error"
        >

            <div class="state-icon">
                !
            </div>


            <div class="state-content">

                <span class="state-eyebrow">
                    NOVACOURT · ESTADO
                </span>

                <strong>
                    No se pudo cargar el grafo
                </strong>

                <p>
                    {{ effectiveError }}
                </p>

            </div>

        </div>


        <!-- =====================================================
             ESTADO VACÍO
        ====================================================== -->

        <div
            v-else-if="!hasGraphData"
            class="graph-empty"
        >

            <div class="empty-visual">

                <div class="empty-orbit empty-orbit-one"></div>

                <div class="empty-orbit empty-orbit-two"></div>

                <div class="empty-center">
                    ⚖
                </div>

            </div>


            <span class="empty-eyebrow">
                NOVACOURT · MAPA RELACIONAL
            </span>


            <h3>
                {{ graphData?.status === 'empty' ? 'Sin relaciones extraídas' : 'Red relacional pendiente' }}
            </h3>


            <p>

                Cuando NovaCourt procese el caso y genere
                relaciones entre sus elementos jurídicos,
                podrás visualizarlas aquí de forma interactiva.

            </p>

        </div>


        <!-- =====================================================
             GRAFO
        ====================================================== -->

        <div
            v-else
            class="graph-workspace"
        >
            <p v-if="graphData?.status === 'building'" role="status" class="graph-notice">
                Grafo parcial. Procesamiento de fuentes en curso.
            </p>
            <p v-if="['failed', 'timeout'].includes(graphData?.status)" role="alert" class="graph-notice">
                Grafo parcial: {{ graphData?.message || 'No se completó el procesamiento.' }}
            </p>
            <div class="graph-filters" aria-label="Filtros del grafo">
                <label>Buscar nodos <input v-model="query" type="search" placeholder="Título del nodo" /></label>
                <label>Complejidad <select v-model="complexity">
                    <option value="essential">Vista esencial</option>
                    <option value="complete">Vista completa</option>
                </select></label>
                <fieldset><legend>Tipos visibles</legend>
                    <label v-for="type in visibleTypes" :key="type">
                        <input type="checkbox" :checked="!selectedTypes.includes(type)"
                            @change="toggleType(type)" />
                        {{ getNodeCategoryLabel({ entity_type: type }) }}
                    </label>
                </fieldset>
            </div>
            <p v-if="!normalizedNodes.length" role="status">No hay nodos para los filtros actuales.</p>
            <details class="graph-text-list">
                <summary>Lista accesible de nodos ({{ normalizedNodes.length }})</summary>
                <ul><li v-for="node in normalizedNodes" :key="node.id">
                    <button type="button" @click="selectedNode = node">
                        {{ getNodeCategoryLabel(node) }}: {{ node.title || node.name }}
                    </button>
                </li></ul>
            </details>

            <!-- =================================================
                 BARRA DE HERRAMIENTAS
            ================================================== -->

            <div class="graph-toolbar">

                <div class="toolbar-caption">

                    <span class="toolbar-status"></span>

                    <span>
                        Exploración interactiva
                    </span>

                </div>


                <div class="toolbar-actions">

                    <button
                        type="button"
                        class="toolbar-button"
                        title="Restablecer visualización"
                        @click="resetGraph"
                    >

                        <span class="toolbar-icon">
                            ↺
                        </span>

                        <span>
                            Restablecer
                        </span>

                    </button>


                    <button
                        type="button"
                        class="toolbar-button"
                        title="Centrar grafo"
                        @click="centerGraph"
                    >

                        <span class="toolbar-icon">
                            ⊙
                        </span>

                        <span>
                            Centrar
                        </span>

                    </button>


                    <button
                        type="button"
                        class="toolbar-button"
                        :class="{
                            'is-disabled': !selectedNode
                        }"
                        title="Cerrar selección"
                        :disabled="!selectedNode"
                        @click="clearSelection"
                    >

                        <span class="toolbar-icon">
                            ×
                        </span>

                        <span>
                            Limpiar
                        </span>

                    </button>

                </div>

            </div>


            <!-- =================================================
                 ÁREA PRINCIPAL
            ================================================== -->

            <div class="graph-main">

                <!-- DECORACIÓN -->

                <div
                    class="canvas-watermark"
                    aria-hidden="true"
                >
                    NOVA
                </div>


                <!-- =================================================
                     SVG
                ================================================== -->

                <div
                    ref="graphContainer"
                    class="graph-canvas"
                >

                    <svg
                        ref="svgElement"
                        class="graph-svg"
                    ></svg>

                </div>


                <!-- =================================================
                     PANEL DEL NODO
                ================================================== -->

                <aside
                    v-if="selectedNode"
                    class="node-detail-panel"
                >

                    <div class="detail-panel-accent"></div>


                    <div class="detail-header">

                        <div class="detail-heading">

                            <span
                                class="detail-type"
                                :style="{
                                    color: getNodeColor(selectedNode)
                                }"
                            >

                                <span
                                    class="detail-type-dot"
                                    :style="{
                                        background: getNodeColor(selectedNode)
                                    }"
                                ></span>

                                {{ getNodeCategoryLabel(selectedNode) }}

                            </span>


                            <h3>

                                {{
                                    selectedNode.title || selectedNode.name ||
                                    "Elemento sin nombre"
                                }}

                            </h3>

                        </div>


                        <button
                            type="button"
                            class="close-button"
                            title="Cerrar detalle"
                            @click="clearSelection"
                        >

                            ×

                        </button>

                    </div>


                    <!-- =================================================
                         RESUMEN
                    ================================================== -->

                    <div
                        v-if="selectedNode.summary"
                        class="detail-section"
                    >

                        <span class="detail-label">
                            Resumen
                        </span>

                        <p>
                            {{ selectedNode.summary }}
                        </p>

                    </div>
                    <div v-if="selectedNode.status || selectedNode.date" class="detail-section">
                        <span v-if="selectedNode.status">Estado: {{ selectedNode.status }}</span>
                        <span v-if="selectedNode.date">Fecha: {{ selectedNode.date }}</span>
                    </div>
                    <div v-if="selectedNode.description || selectedNode.excerpt" class="detail-section">
                        <span class="detail-label">Descripción o referencia</span>
                        <p>{{ selectedNode.description || selectedNode.excerpt }}</p>
                    </div>
                    <div v-if="selectedNode.document_id || selectedNode.page_start || selectedNode.section" class="detail-section">
                        <span v-if="selectedNode.document_id">Documento: {{ selectedNode.document_id }}</span>
                        <span v-if="selectedNode.page_start">Página: {{ selectedNode.page_start }}<template v-if="selectedNode.page_end && selectedNode.page_end !== selectedNode.page_start">–{{ selectedNode.page_end }}</template></span>
                        <span v-if="selectedNode.section">Sección: {{ selectedNode.section }}</span>
                    </div>
                    <div v-if="availableSources(selectedNode.source_ids).length" class="detail-section">
                        <span class="detail-label">Fuentes</span>
                        <button v-for="sourceId in availableSources(selectedNode.source_ids)" :key="sourceId"
                            type="button" @click="openSource(sourceId)">
                            {{ sourceLabel(sourceId) }}
                        </button>
                    </div>


                    <!-- =================================================
                         CLASIFICACIÓN
                    ================================================== -->

                    <div
                        v-if="selectedNode.labels?.length"
                        class="detail-section"
                    >

                        <span class="detail-label">
                            Clasificación
                        </span>


                        <div class="label-list">

                            <span
                                v-for="label in selectedNode.labels"
                                :key="label"
                                class="node-label"
                            >

                                {{ label }}

                            </span>

                        </div>

                    </div>


                    <!-- =================================================
                         ATRIBUTOS
                    ================================================== -->

                    <div
                        v-if="attributeEntries.length"
                        class="detail-section"
                    >

                        <span class="detail-label">
                            Atributos
                        </span>


                        <div class="attributes-list">

                            <div
                                v-for="[key, value] in attributeEntries"
                                :key="key"
                                class="attribute-row"
                            >

                                <span>
                                    {{ formatAttributeKey(key) }}
                                </span>

                                <strong>
                                    {{ formatAttributeValue(value) }}
                                </strong>

                            </div>

                        </div>

                    </div>


                    <!-- =================================================
                         FOOTER DEL PANEL
                    ================================================== -->

                    <div class="detail-footer">

                        <span class="connection-indicator"></span>

                        <strong>
                            {{ selectedNodeConnectionCount }}
                        </strong>

                        <span>
                            relaciones identificadas
                        </span>

                    </div>

                </aside>
                <aside v-if="selectedEdge" class="node-detail-panel">
                    <button type="button" @click="selectedEdge = null" aria-label="Cerrar relación">×</button>
                    <h3>{{ selectedEdge.label || selectedEdge.relation_type }}</h3>
                    <p>{{ selectedEdge.relation_type }}</p>
                    <p>{{ nodeTitle(selectedEdge.source) }} → {{ nodeTitle(selectedEdge.target) }}</p>
                    <button v-for="sourceId in availableSources(selectedEdge.source_ids)" :key="sourceId"
                        type="button" @click="openSource(sourceId)">{{ sourceLabel(sourceId) }}</button>
                </aside>

            </div>

        </div>


        <!-- =====================================================
             FIRMA INSTITUCIONAL
        ====================================================== -->

        <div class="graph-footer-mark">

            <span class="footer-line"></span>

            <span>
                INTELIGENCIA JUDICIAL · NOVA IURIS
            </span>

            <span class="footer-line"></span>

        </div>

        <SourceModal :source="selectedSource" :case-id="caseId" @close="selectedSource = null" />
    </section>

</template>


<script setup>

import {

    computed,
    nextTick,
    onBeforeUnmount,
    onMounted,
    ref,
    watch

} from "vue"

import * as d3 from "d3"
import SourceModal from "../common/SourceModal.vue"


/* ============================================================
   PROPS
============================================================ */

const props = defineProps({

    graphData: {

        type: Object,

        default: () => ({})

    },
    sources: { type: Array, default: () => [] },
    caseId: { type: String, default: null },

    loading: {

        type: Boolean,

        default: false

    },

    error: {

        type: String,

        default: ""

    }

})


/* ============================================================
   REFERENCIAS
============================================================ */

const graphContainer = ref(null)

const svgElement = ref(null)

const selectedNode = ref(null)
const selectedEdge = ref(null)
const selectedSource = ref(null)
const selectedTypes = ref([])
const complexity = ref("essential")
const query = ref("")
const viewport = ref(d3.zoomIdentity)
const positions = new Map()


/* ============================================================
   INSTANCIAS D3
============================================================ */

let simulation = null

let zoomBehavior = null

let resizeObserver = null

let currentSvg = null

let currentRoot = null


/* ============================================================
   PALETA NOVACOURT
============================================================ */

const categoryColors = {

    judicial: "#0F2747",

    lawyer: "#2563EB",

    prosecution: "#B08A4C",

    party: "#725C9A",

    evidence: "#2F7D62",

    norm: "#2C6680",

    argument: "#9A4656",

    fact: "#64748B",

    default: "#475569"

}


const visibleTypes = computed(() => [...new Set((props.graphData?.nodes || [])
    .map(node => node?.entity_type).filter(Boolean))])
const legendItems = computed(() => visibleTypes.value.map(type => ({
    key: type, label: getNodeCategoryLabel({ entity_type: type }),
    color: getNodeColor({ entity_type: type })
})))
const normalizedNodes = computed(() => (props.graphData?.nodes || [])
    .filter(node => node?.node_id || node?.uuid)
    .filter(node => !selectedTypes.value.includes(node.entity_type))
    .filter(node => complexity.value === "complete" || node.importance === "core" ||
        ["EVIDENCE", "LAW", "JURISPRUDENCE"].includes(node.entity_type))
    .filter(node => !query.value || String(node.title || node.name || "")
        .toLocaleLowerCase().includes(query.value.toLocaleLowerCase()))
    .map(node => ({ ...node, id: String(node.node_id || node.uuid) })))

const normalizedLinks = computed(() => {
    const ids = new Set(normalizedNodes.value.map(node => node.id))
    return (props.graphData?.edges || [])
        .filter(edge => ids.has(String(edge.source_node_id || edge.source_node_uuid)) &&
            ids.has(String(edge.target_node_id || edge.target_node_uuid)))
        .map(edge => ({
            ...edge,
            id: String(edge.edge_id || edge.uuid),
            source: String(edge.source_node_id || edge.source_node_uuid),
            target: String(edge.target_node_id || edge.target_node_uuid)
        }))
})

const hasGraphData = computed(() => (props.graphData?.nodes || []).length > 0)
const effectiveError = computed(() => props.error || (!hasGraphData.value &&
    ["failed", "timeout"].includes(props.graphData?.status)
    ? props.graphData?.message || "No se pudo completar el grafo." : ""))
const sourceById = computed(() => new Map(props.sources
    .filter(source => source?.source_id && (source.source_scope === "public" ||
        source.source_scope === "case" && source.case_id === props.caseId))
    .map(source => [source.source_id, source])))
function availableSources(sourceIds) {
    return (Array.isArray(sourceIds) ? sourceIds : []).filter(id => sourceById.value.has(id))
}
function sourceLabel(sourceId) {
    const source = sourceById.value.get(sourceId)
    return source ? `${source.title || "Fuente"}${source.page_start ? ` · pág. ${source.page_start}` : ""}` : "Fuente"
}
function nodeTitle(nodeId) {
    const node = (props.graphData?.nodes || []).find(item =>
        String(item.node_id || item.uuid) === String(nodeId?.id || nodeId))
    return node?.title || node?.name || "Elemento no disponible"
}
function openSource(sourceId) {
    selectedSource.value = sourceById.value.get(sourceId) || null
}
function toggleType(type) {
    selectedTypes.value = selectedTypes.value.includes(type)
        ? selectedTypes.value.filter(item => item !== type)
        : [...selectedTypes.value, type]
}

/* ============================================================
   DETALLE DEL NODO
============================================================ */

const attributeEntries = computed(() => {

    if (

        !selectedNode.value ||

        !selectedNode.value.attributes ||

        typeof selectedNode.value.attributes !== "object"

    ) {

        return []

    }

    return Object.entries(

        selectedNode.value.attributes

    ).filter(([, value]) =>

        value !== null &&
        value !== undefined &&
        value !== ""

    )

})


const selectedNodeConnectionCount = computed(() => {

    if (!selectedNode.value) {

        return 0

    }

    const nodeId = selectedNode.value.id

    return normalizedLinks.value.filter(link =>

        String(link.source) === nodeId ||
        String(link.target) === nodeId

    ).length

})


/* ============================================================
   CLASIFICACIÓN
============================================================ */

function getNodeCategory(node) {
    const type = node?.entity_type
    if (type === "PARTY") return node?.legal_role === "court" ? "judicial" : "party"
    if (type === "EVIDENCE" || type === "DOCUMENT") return "evidence"
    if (type === "LAW" || type === "JURISPRUDENCE") return "norm"
    if (type === "ARGUMENT" || type === "COUNTERARGUMENT") return "argument"
    if (type === "FACT" || type === "PROCEDURAL_ACT") return "fact"
    return "default"
}

function getNodeColor(node) {
    return categoryColors[getNodeCategory(node)] || categoryColors.default
}

function getNodeCategoryLabel(node) {
    return ({
        CASE: "CASO", PARTY: "PARTE", CLAIM: "PRETENSIÓN",
        LEGAL_ISSUE: "PROBLEMA JURÍDICO", FACT: "HECHO",
        EVIDENCE: "EVIDENCIA", DOCUMENT: "DOCUMENTO", LAW: "NORMA",
        JURISPRUDENCE: "JURISPRUDENCIA", ARGUMENT: "ARGUMENTO",
        COUNTERARGUMENT: "CONTRAARGUMENTO", RISK: "RIESGO",
        PROCEDURAL_ACT: "ACTUACIÓN"
    })[node?.entity_type] || "ELEMENTO DEL CASO"
}

/* ============================================================
   UTILIDADES DE COLOR
============================================================ */
function hexToRgba(hex, alpha = 1) {

    const normalized = String(hex).replace("#", "")

    if (normalized.length !== 6) {

        return `rgba(71,85,105,${alpha})`

    }

    const r = parseInt(
        normalized.slice(0, 2),
        16
    )

    const g = parseInt(
        normalized.slice(2, 4),
        16
    )

    const b = parseInt(
        normalized.slice(4, 6),
        16
    )

    return `rgba(${r},${g},${b},${alpha})`

}


/* ============================================================
   FORMATEADORES
============================================================ */

function formatAttributeKey(key) {

    return String(key)

        .replaceAll("_", " ")

        .replace(/\b\w/g, char =>
            char.toUpperCase()
        )

}


function formatAttributeValue(value) {

    if (typeof value === "object") {

        return JSON.stringify(value)

    }

    return String(value)

}


/* ============================================================
   CREAR GRAFO
============================================================ */

function renderGraph() {

    if (

        !svgElement.value ||

        !graphContainer.value ||

        !hasGraphData.value

    ) {

        return

    }


    if (simulation) {
        for (const node of simulation.nodes()) {
            positions.set(node.id, { x: node.x, y: node.y })
        }
    }
    if (currentSvg) viewport.value = d3.zoomTransform(currentSvg.node())
    destroyGraph()


    const container = graphContainer.value


    const width = Math.max(

        container.clientWidth,

        320

    )


    const height = Math.max(

        container.clientHeight,

        520

    )


    const nodes = normalizedNodes.value.map(node => ({

        ...node,
        ...(positions.get(node.id) || {})

    }))


    const links = normalizedLinks.value.map(link => ({

        ...link

    }))


    const svg = d3

        .select(svgElement.value)

        .attr("width", width)

        .attr("height", height)

        .attr(

            "viewBox",

            `0 0 ${width} ${height}`

        )


    currentSvg = svg


    const defs = svg

        .append("defs")


    const shadowFilter = defs

        .append("filter")

        .attr("id", "node-shadow")

        .attr("x", "-50%")

        .attr("y", "-50%")

        .attr("width", "200%")

        .attr("height", "200%")


    shadowFilter

        .append("feDropShadow")

        .attr("dx", "0")

        .attr("dy", "3")

        .attr("stdDeviation", "4")

        .attr("flood-color", "#0F2747")

        .attr("flood-opacity", ".16")


    const root = svg

        .append("g")

        .attr(

            "class",

            "graph-root"

        )


    currentRoot = root


    zoomBehavior = d3

        .zoom()

        .scaleExtent([

            0.35,

            3

        ])

        .on(

            "zoom",

            event => {

                root.attr(

                    "transform",

                    event.transform

                )

            }

        )


    svg.call(zoomBehavior)
    svg.call(zoomBehavior.transform, viewport.value)


    svg.on(

        "dblclick.zoom",

        null

    )


    /* ========================================================
       LINKS
    ======================================================== */

    const linkGroup = root

        .append("g")

        .attr(

            "class",

            "graph-links"

        )


    const linkSelection = linkGroup

        .selectAll("line")

        .data(

            links,

            link => link.id

        )

        .join("line")

        .attr(

            "class",

            "graph-link"

        )
        .on("click", (event, link) => {
            event.stopPropagation()
            selectedEdge.value = link
        })
    linkSelection.append("title")
        .text(link => link.label || link.relation_type || "Relación")


    /* ========================================================
       NODES
    ======================================================== */

    const nodeGroup = root

        .append("g")

        .attr(

            "class",

            "graph-nodes"

        )


    const nodeSelection = nodeGroup

        .selectAll("g")

        .data(

            nodes,

            node => node.id

        )

        .join("g")

        .attr(

            "class",

            "graph-node"

        )

        .style(

            "cursor",

            "pointer"

        )


    /* ========================================================
       AURA
    ======================================================== */

    nodeSelection

        .append("circle")

        .attr(

            "class",

            "node-aura"

        )

        .attr(

            "r",

            33

        )

        .attr(

            "fill",

            node => hexToRgba(

                getNodeColor(node),

                .06

            )

        )


    /* ========================================================
       CÍRCULO PRINCIPAL
    ======================================================== */

    nodeSelection

        .append("circle")

        .attr(

            "class",

            "node-circle"

        )

        .attr(

            "r",

            23

        )

        .attr(

            "fill",

            node => getNodeColor(node)

        )

        .attr(

            "filter",

            "url(#node-shadow)"

        )


    /* ========================================================
       BORDE EXTERIOR
    ======================================================== */

    nodeSelection

        .append("circle")

        .attr(

            "class",

            "node-ring"

        )

        .attr(

            "r",

            29

        )

        .attr(

            "fill",

            "none"

        )


    /* ========================================================
       PUNTO CENTRAL
    ======================================================== */

    nodeSelection

        .append("circle")

        .attr(

            "class",

            "node-core"

        )

        .attr(

            "r",

            4

        )

        .attr(

            "fill",

            "#FFFFFF"

        )

        .attr(

            "opacity",

            .85

        )


    /* ========================================================
       TEXTO
    ======================================================== */

    nodeSelection

        .append("text")

        .attr(

            "class",

            "node-text"

        )

        .attr(

            "x",

            36

        )

        .attr(

            "dy",

            "0.35em"

        )

        .text(node => truncateText(

            node.name ||

            "Sin nombre",

            30

        ))


    /* ========================================================
       CLICK
    ======================================================== */

    nodeSelection

        .on(

            "click",

            (event, node) => {

                event.stopPropagation()

                selectedNode.value = {

                    ...node

                }

                updateSelectionStyles(

                    nodeSelection,

                    linkSelection,

                    node.id

                )

            }

        )


    svg.on(

        "click",

        () => {

            clearSelection()

        }

    )


    /* ========================================================
       DRAG
    ======================================================== */

    const drag = d3

        .drag()

        .on(

            "start",

            (event, node) => {

                if (!event.active) {

                    simulation

                        .alphaTarget(.3)

                        .restart()

                }

                node.fx = node.x

                node.fy = node.y

            }

        )

        .on(

            "drag",

            (event, node) => {

                node.fx = event.x

                node.fy = event.y

            }

        )

        .on(

            "end",

            (event, node) => {

                if (!event.active) {

                    simulation

                        .alphaTarget(0)

                }

                node.fx = null

                node.fy = null

            }

        )


    nodeSelection.call(drag)


    /* ========================================================
       SIMULACIÓN
    ======================================================== */

    simulation = d3

        .forceSimulation(nodes)

        .force(

            "link",

            d3

                .forceLink(links)

                .id(node => node.id)

                .distance(135)

                .strength(.62)

        )

        .force(

            "charge",

            d3

                .forceManyBody()

                .strength(-520)

        )

        .force(

            "center",

            d3.forceCenter(

                width / 2,

                height / 2

            )

        )

        .force(

            "collision",

            d3

                .forceCollide()

                .radius(72)

        )


    simulation.on(

        "tick",

        () => {

            linkSelection

                .attr(

                    "x1",

                    link => link.source.x

                )

                .attr(

                    "y1",

                    link => link.source.y

                )

                .attr(

                    "x2",

                    link => link.target.x

                )

                .attr(

                    "y2",

                    link => link.target.y

                )


            nodeSelection.attr(

                "transform",

                node =>

                    `translate(${node.x},${node.y})`

            )

        }

    )
    if (selectedNode.value) {
        updateSelectionStyles(nodeSelection, linkSelection, selectedNode.value.id)
    }

}


/* ============================================================
   SELECCIÓN
============================================================ */

function updateSelectionStyles(

    nodeSelection,

    linkSelection,

    selectedId

) {

    nodeSelection

        .classed(

            "is-selected",

            node => node.id === selectedId

        )

        .classed(

            "is-muted",

            node => {

                if (node.id === selectedId) {

                    return false

                }

                return !normalizedLinks.value.some(link =>

                    (

                        String(link.source) === selectedId &&

                        String(link.target) === node.id

                    ) ||

                    (

                        String(link.target) === selectedId &&

                        String(link.source) === node.id

                    )

                )

            }

        )


    linkSelection

        .classed(

            "is-active",

            link =>

                String(

                    link.source.id ||

                    link.source

                ) === selectedId ||

                String(

                    link.target.id ||

                    link.target

                ) === selectedId

        )

        .classed(

            "is-muted",

            link =>

                !(

                    String(

                        link.source.id ||

                        link.source

                    ) === selectedId ||

                    String(

                        link.target.id ||

                        link.target

                    ) === selectedId

                )

        )

}


/* ============================================================
   UTILIDADES
============================================================ */

function truncateText(

    text,

    maxLength

) {

    const normalized = String(

        text || ""

    )


    if (

        normalized.length <= maxLength

    ) {

        return normalized

    }


    return `${normalized.slice(

        0,

        maxLength - 1

    )}…`

}


function clearSelection() {

    selectedNode.value = null


    if (!currentRoot) {

        return

    }


    currentRoot

        .selectAll(".graph-node")

        .classed(

            "is-selected",

            false

        )

        .classed(

            "is-muted",

            false

        )


    currentRoot

        .selectAll(".graph-link")

        .classed(

            "is-active",

            false

        )

        .classed(

            "is-muted",

            false

        )

}


function centerGraph() {

    if (

        !currentSvg ||

        !zoomBehavior ||

        !graphContainer.value

    ) {

        return

    }


    currentSvg

        .transition()

        .duration(500)

        .call(

            zoomBehavior.transform,

            d3.zoomIdentity

        )

}


function resetGraph() {

    clearSelection()

    renderGraph()

}


function destroyGraph() {

    if (simulation) {

        simulation.stop()

        simulation = null

    }


    if (svgElement.value) {

        d3

            .select(svgElement.value)

            .selectAll("*")

            .remove()

    }


    currentSvg = null

    currentRoot = null

}


/* ============================================================
   WATCHERS
============================================================ */

watch(

    () => props.graphData,

    async () => {

        const id = selectedNode.value?.id
        selectedNode.value = id
            ? normalizedNodes.value.find(node => node.id === id) || null
            : null
        if (selectedEdge.value && !normalizedLinks.value.some(edge => edge.id === selectedEdge.value.id)) {
            selectedEdge.value = null
        } else if (selectedEdge.value) {
            selectedEdge.value = normalizedLinks.value.find(edge => edge.id === selectedEdge.value.id)
        }

        await nextTick()

        renderGraph()

    },

    { deep: false }

)

watch([selectedTypes, complexity, query], async () => {
    if (selectedNode.value && !normalizedNodes.value.some(node => node.id === selectedNode.value.id)) {
        selectedNode.value = null
    }
    if (selectedEdge.value && !normalizedLinks.value.some(edge => edge.id === selectedEdge.value.id)) {
        selectedEdge.value = null
    }
    await nextTick()
    renderGraph()
})


watch(

    () => props.loading,

    async loading => {

        if (!loading) {

            await nextTick()

            renderGraph()

        }

    }

)


/* ============================================================
   CICLO DE VIDA
============================================================ */

onMounted(async () => {

    await nextTick()

    renderGraph()


    if (graphContainer.value) {

        resizeObserver = new ResizeObserver(() => {

            if (

                hasGraphData.value &&

                !props.loading

            ) {

                renderGraph()

            }

        })


        resizeObserver.observe(

            graphContainer.value

        )

    }

})


onBeforeUnmount(() => {

    destroyGraph()


    if (resizeObserver) {

        resizeObserver.disconnect()

        resizeObserver = null

    }

})

</script>


<style scoped>

/* ============================================================
   VARIABLES
============================================================ */

.graph-panel {

    --court-navy: #0F2747;

    --court-navy-deep: #102238;

    --court-blue: #2563EB;

    --court-blue-dark: #1D4ED8;

    --court-blue-soft: #EFF6FF;

    --court-gold: #B08A4C;

    --court-gold-dark: #96743F;

    --court-gold-soft: #F8F4EC;

    --court-text: #334155;

    --court-muted: #64748B;

    --court-border: #E2E8F0;

    --court-border-soft: #EDF1F5;

    --court-soft: #F8FAFC;

    --court-white: #FFFFFF;

    position: relative;

    width: 100%;

    padding: 30px;

    overflow: hidden;

    isolation: isolate;

    background:

        linear-gradient(

            145deg,

            #FFFFFF 0%,

            #FCFDFE 58%,

            #F7FAFE 100%

        );

    border: 1px solid var(--court-border);

    border-radius: 22px;

    box-shadow:

        0 12px 34px

        rgba(

            15,

            39,

            71,

            .055

        );

}


/* ============================================================
   ACENTO SUPERIOR
============================================================ */

.panel-accent {

    position: absolute;

    z-index: 8;

    top: 0;

    left: 0;

    width: 100%;

    height: 3px;

    background:

        linear-gradient(

            90deg,

            var(--court-navy) 0%,

            var(--court-blue) 48%,

            var(--court-gold) 100%

        );

}


/* ============================================================
   DECORACIÓN
============================================================ */

.panel-orbit {

    position: absolute;

    z-index: -1;

    border-radius: 50%;

    pointer-events: none;

}


.panel-orbit-right {

    width: 390px;

    height: 390px;

    right: -300px;

    bottom: -270px;

    border: 1px solid

        rgba(

            37,

            99,

            235,

            .055

        );

    box-shadow:

        0 0 0 62px

        rgba(

            37,

            99,

            235,

            .014

        ),

        0 0 0 124px

        rgba(

            176,

            138,

            76,

            .009

        );

}


.panel-orbit-left {

    width: 230px;

    height: 230px;

    left: -185px;

    top: -165px;

    border: 1px solid

        rgba(

            176,

            138,

            76,

            .065

        );

}


/* ============================================================
   ENCABEZADO
============================================================ */

.graph-header {

    position: relative;

    z-index: 2;

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    gap: 30px;

    padding-bottom: 24px;

    border-bottom: 1px solid

        var(--court-border);

}


.graph-heading {

    min-width: 0;

}


/* ============================================================
   ETIQUETA INSTITUCIONAL
============================================================ */

.section-label {

    display: flex;

    align-items: center;

    gap: 8px;

    margin-bottom: 9px;

    color: var(--court-muted);

    font-size: .65rem;

    font-weight: 800;

    letter-spacing: .13em;

    line-height: 1;

}


.label-line {

    width: 24px;

    height: 2px;

    border-radius: 999px;

    background:

        var(--court-blue);

}


.label-dot {

    width: 4px;

    height: 4px;

    flex-shrink: 0;

    border-radius: 50%;

    background:

        var(--court-gold);

}


/* ============================================================
   TÍTULO
============================================================ */

.graph-heading h2 {

    margin: 0 0 9px;

    color: var(--court-navy);

    font-size: 1.55rem;

    font-weight: 720;

    line-height: 1.28;

    letter-spacing: -.025em;

}


.graph-heading p {

    max-width: 730px;

    margin: 0;

    color: var(--court-muted);

    font-size: .91rem;

    font-weight: 400;

    line-height: 1.72;

}


/* ============================================================
   ESTADÍSTICAS
============================================================ */

.graph-stats {

    display: flex;

    align-items: stretch;

    flex-shrink: 0;

    padding: 10px 14px;

    background:

        rgba(

            248,

            250,

            252,

            .78

        );

    border: 1px solid

        var(--court-border);

    border-radius: 13px;

    box-shadow:

        0 4px 14px

        rgba(

            15,

            39,

            71,

            .025

        );

}


.stat-item {

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    min-width: 72px;

    text-align: center;

}


.stat-caption {

    margin-bottom: 2px;

    color: #94A3B8;

    font-size: .48rem;

    font-weight: 800;

    letter-spacing: .11em;

}


.stat-item strong {

    color: var(--court-navy);

    font-size: 1.15rem;

    font-weight: 760;

    line-height: 1.2;

}


.stat-label {

    margin-top: 2px;

    color: var(--court-muted);

    font-size: .67rem;

}


.stat-divider {

    width: 1px;

    height: 38px;

    align-self: center;

    margin: 0 10px;

    background:

        var(--court-border);

}


/* ============================================================
   LEYENDA
============================================================ */

.graph-legend {

    position: relative;

    z-index: 2;

    display: flex;

    align-items: center;

    gap: 20px;

    flex-wrap: wrap;

    padding: 17px 0;

    border-bottom: 1px solid

        var(--court-border);

}


.legend-title {

    display: flex;

    align-items: center;

    gap: 8px;

    color: #475569;

    font-size: .73rem;

    font-weight: 750;

}


.legend-title-mark {

    width: 5px;

    height: 18px;

    border-radius: 999px;

    background:

        var(--court-gold);

}


.legend-items {

    display: flex;

    align-items: center;

    flex-wrap: wrap;

    gap: 10px 19px;

}


.legend-item {

    display: inline-flex;

    align-items: center;

    gap: 7px;

    color: #64748B;

    font-size: .72rem;

    font-weight: 500;

}


.legend-dot {

    width: 8px;

    height: 8px;

    flex-shrink: 0;

    border-radius: 50%;

}


/* ============================================================
   ESTADOS
============================================================ */

.graph-state {

    position: relative;

    display: flex;

    align-items: center;

    gap: 20px;

    min-height: 330px;

    margin-top: 22px;

    padding: 38px;

    overflow: hidden;

    border-radius: 18px;

}


.graph-loading {

    background:

        linear-gradient(

            135deg,

            #F8FAFC,

            #FDFEFE

        );

    border: 1px solid

        var(--court-border-soft);

}


.loading-visual {

    position: relative;

    display: flex;

    align-items: center;

    justify-content: center;

    width: 62px;

    height: 62px;

    flex-shrink: 0;

    border: 1px solid

        rgba(

            176,

            138,

            76,

            .22

        );

    border-radius: 50%;

    color: var(--court-gold);

    background:

        var(--court-gold-soft);

    font-size: 1.45rem;

}


.loading-ring {

    position: absolute;

    inset: -7px;

    border: 1px solid

        rgba(

            37,

            99,

            235,

            .16

        );

    border-top-color:

        var(--court-blue);

    border-radius: 50%;

    animation:

        loadingRotate

        1.2s

        linear

        infinite;

}


.state-content {

    min-width: 0;

}


.state-eyebrow {

    display: block;

    margin-bottom: 6px;

    color: var(--court-gold);

    font-size: .58rem;

    font-weight: 800;

    letter-spacing: .12em;

}


.graph-state strong {

    display: block;

    margin-bottom: 7px;

    color: var(--court-navy);

    font-size: 1rem;

    font-weight: 720;

}


.graph-state p {

    max-width: 580px;

    margin: 0;

    color: var(--court-muted);

    font-size: .87rem;

    line-height: 1.65;

}


/* ============================================================
   ERROR
============================================================ */

.graph-error {

    background:

        #FFFAFA;

    border: 1px solid

        #F2D6D6;

}


.graph-error .state-eyebrow {

    color: #A05252;

}


.graph-error strong {

    color: #7F1D1D;

}


.state-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 44px;

    height: 44px;

    flex-shrink: 0;

    border: 1px solid

        #FECACA;

    border-radius: 12px;

    color: #B91C1C;

    background: #FEF2F2;

    font-size: 1rem;

    font-weight: 800;

}


/* ============================================================
   VACÍO
============================================================ */

.graph-empty {

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    min-height: 440px;

    margin-top: 22px;

    padding: 40px;

    text-align: center;

    background:

        radial-gradient(

            circle at center,

            rgba(

                239,

                246,

                255,

                .55

            ),

            transparent 48%

        ),

        #FAFCFE;

    border: 1px dashed

        #CBD5E1;

    border-radius: 18px;

}


.empty-visual {

    position: relative;

    display: flex;

    align-items: center;

    justify-content: center;

    width: 86px;

    height: 86px;

    margin-bottom: 19px;

}


.empty-orbit {

    position: absolute;

    border: 1px solid;

    border-radius: 50%;

}


.empty-orbit-one {

    inset: 0;

    border-color:

        rgba(

            37,

            99,

            235,

            .12

        );

}


.empty-orbit-two {

    inset: 10px;

    border-color:

        rgba(

            176,

            138,

            76,

            .22

        );

}


.empty-center {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 48px;

    height: 48px;

    border: 1px solid

        var(--court-border);

    border-radius: 50%;

    color: var(--court-gold);

    background: #FFFFFF;

    box-shadow:

        0 8px 20px

        rgba(

            15,

            39,

            71,

            .07

        );

    font-size: 1.35rem;

}


.empty-eyebrow {

    margin-bottom: 7px;

    color: var(--court-gold);

    font-size: .58rem;

    font-weight: 800;

    letter-spacing: .13em;

}


.graph-empty h3 {

    margin: 0 0 9px;

    color: var(--court-navy);

    font-size: 1.08rem;

    font-weight: 720;

}


.graph-empty p {

    max-width: 530px;

    margin: 0;

    color: var(--court-muted);

    font-size: .87rem;

    line-height: 1.72;

}


/* ============================================================
   WORKSPACE
============================================================ */

.graph-workspace {

    position: relative;

    z-index: 2;

    margin-top: 22px;

}


/* ============================================================
   TOOLBAR
============================================================ */

.graph-toolbar {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 14px;

    margin-bottom: 11px;

}


.toolbar-caption {

    display: flex;

    align-items: center;

    gap: 7px;

    color: #94A3B8;

    font-size: .65rem;

    font-weight: 650;

    letter-spacing: .01em;

}


.toolbar-status {

    width: 6px;

    height: 6px;

    border-radius: 50%;

    background:

        var(--court-gold);

    box-shadow:

        0 0 0 3px

        rgba(

            176,

            138,

            76,

            .10

        );

}


.toolbar-actions {

    display: flex;

    align-items: center;

    gap: 7px;

}


.toolbar-button {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    gap: 7px;

    min-height: 35px;

    padding: 7px 11px;

    border: 1px solid

        var(--court-border);

    border-radius: 9px;

    cursor: pointer;

    background: #FFFFFF;

    color: #52647A;

    font-family: inherit;

    font-size: .71rem;

    font-weight: 700;

    transition:

        color .2s ease,

        background .2s ease,

        border-color .2s ease,

        box-shadow .2s ease,

        transform .2s ease;

}


.toolbar-icon {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    color: #64748B;

    font-size: .95rem;

    line-height: 1;

    transition:

        color .2s ease;

}


.toolbar-button:hover:not(:disabled) {

    color: var(--court-navy);

    background:

        linear-gradient(

            180deg,

            #FFFFFF,

            #F8FAFC

        );

    border-color:

        #C9D3DF;

    box-shadow:

        0 4px 12px

        rgba(

            15,

            39,

            71,

            .055

        );

    transform:

        translateY(-1px);

}


.toolbar-button:hover:not(:disabled)

.toolbar-icon {

    color: var(--court-gold-dark);

}


.toolbar-button:disabled {

    cursor: not-allowed;

    opacity: .4;

}


/* ============================================================
   ÁREA DEL GRAFO
============================================================ */

.graph-main {

    position: relative;

    min-height: 560px;

    overflow: hidden;

    background-color: #FBFCFE;

    background-image:

        radial-gradient(

            circle at 1px 1px,

            rgba(

                100,

                116,

                139,

                .13

            ) 1px,

            transparent 0

        );

    background-size: 22px 22px;

    border: 1px solid

        var(--court-border);

    border-radius: 18px;

    box-shadow:

        inset 0 1px 0

        rgba(

            255,

            255,

            255,

            .9

        );

}


.graph-main::before {

    content: "";

    position: absolute;

    z-index: 0;

    inset: 0;

    pointer-events: none;

    background:

        linear-gradient(

            90deg,

            rgba(

                255,

                255,

                255,

                .28

            ),

            transparent 20%,

            transparent 80%,

            rgba(

                255,

                255,

                255,

                .32

            )

        );

}


.canvas-watermark {

    position: absolute;

    z-index: 0;

    right: 24px;

    bottom: 16px;

    color:

        rgba(

            15,

            39,

            71,

            .035

        );

    font-family:

        Georgia,

        "Times New Roman",

        serif;

    font-size: 3.2rem;

    font-weight: 700;

    letter-spacing: -.06em;

    pointer-events: none;

}


/* ============================================================
   CANVAS
============================================================ */

.graph-canvas {

    position: relative;

    z-index: 1;

    width: 100%;

    min-height: 560px;

    overflow: hidden;

}


.graph-svg {

    display: block;

    width: 100%;

    height: 560px;

    overflow: visible;

}


/* ============================================================
   ELEMENTOS D3 — RELACIONES
============================================================ */

.graph-svg :deep(.graph-link) {

    stroke:

        #CBD5E1;

    stroke-width: 1.25;

    stroke-opacity: .72;

    transition:

        stroke .2s ease,

        stroke-width .2s ease,

        stroke-opacity .2s ease;

}


.graph-svg :deep(.graph-link.is-active) {

    stroke:

        var(--court-gold);

    stroke-width: 2.5;

    stroke-opacity: 1;

}


.graph-svg :deep(.graph-link.is-muted) {

    stroke-opacity: .10;

}


/* ============================================================
   NODOS
============================================================ */

.graph-svg :deep(.graph-node) {

    transition:

        opacity .2s ease;

}


.graph-svg :deep(.graph-node.is-muted) {

    opacity: .18;

}


.graph-svg :deep(.node-aura) {

    pointer-events: none;

}


.graph-svg :deep(.node-circle) {

    stroke:

        #FFFFFF;

    stroke-width: 2.5;

}


.graph-svg :deep(.node-ring) {

    stroke:

        var(--court-gold);

    stroke-width: 1.5;

    stroke-opacity: 0;

    transform-origin: center;

    transition:

        stroke-opacity .2s ease,

        stroke-width .2s ease,

        r .2s ease;

}


.graph-svg :deep(.graph-node.is-selected .node-ring) {

    stroke-opacity: 1;

    stroke-width: 2;

}


.graph-svg :deep(.graph-node.is-selected .node-aura) {

    opacity: 1;

}


.graph-svg :deep(.node-core) {

    pointer-events: none;

}


/* ============================================================
   TEXTO DE LOS NODOS
============================================================ */

.graph-svg :deep(.node-text) {

    fill:

        #334155;

    font-family:

        Inter,

        ui-sans-serif,

        system-ui,

        -apple-system,

        BlinkMacSystemFont,

        "Segoe UI",

        sans-serif;

    font-size: 12px;

    font-weight: 650;

    letter-spacing: -.005em;

    pointer-events: none;

}


/* ============================================================
   PANEL DE DETALLE
============================================================ */

.node-detail-panel {

    position: absolute;

    z-index: 5;

    top: 15px;

    right: 15px;

    bottom: 15px;

    width: min(

        340px,

        calc(100% - 30px)

    );

    padding: 21px;

    overflow-y: auto;

    background:

        rgba(

            255,

            255,

            255,

            .965

        );

    backdrop-filter:

        blur(18px);

    -webkit-backdrop-filter:

        blur(18px);

    border: 1px solid

        rgba(

            226,

            232,

            240,

            .92

        );

    border-radius: 16px;

    box-shadow:

        0 18px 50px

        rgba(

            15,

            39,

            71,

            .13

        ),

        0 2px 8px

        rgba(

            15,

            39,

            71,

            .04

        );

    animation:

        detailAppear

        .22s

        ease

        both;

}


.detail-panel-accent {

    position: absolute;

    top: 0;

    left: 21px;

    right: 21px;

    height: 2px;

    border-radius: 0 0 999px 999px;

    background:

        linear-gradient(

            90deg,

            var(--court-navy),

            var(--court-blue),

            var(--court-gold)

        );

}


/* ============================================================
   CABECERA DEL DETALLE
============================================================ */

.detail-header {

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    gap: 14px;

    padding-bottom: 18px;

    border-bottom: 1px solid

        var(--court-border);

}


.detail-heading {

    min-width: 0;

}


.detail-type {

    display: flex;

    align-items: center;

    gap: 6px;

    margin-bottom: 7px;

    font-size: .61rem;

    font-weight: 800;

    letter-spacing: .08em;

}


.detail-type-dot {

    width: 6px;

    height: 6px;

    border-radius: 50%;

}


.detail-header h3 {

    margin: 0;

    color: var(--court-navy);

    font-size: 1.03rem;

    font-weight: 720;

    line-height: 1.42;

    letter-spacing: -.01em;

}


/* ============================================================
   BOTÓN CERRAR
============================================================ */

.close-button {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 31px;

    height: 31px;

    flex-shrink: 0;

    border: 1px solid

        var(--court-border);

    border-radius: 8px;

    cursor: pointer;

    background: #FFFFFF;

    color: #64748B;

    font-family: inherit;

    font-size: 1.15rem;

    line-height: 1;

    transition:

        color .2s ease,

        background .2s ease,

        border-color .2s ease;

}


.close-button:hover {

    color: var(--court-navy);

    background:

        var(--court-gold-soft);

    border-color:

        rgba(

            176,

            138,

            76,

            .28

        );

}


/* ============================================================
   SECCIONES DEL DETALLE
============================================================ */

.detail-section {

    padding: 17px 0;

    border-bottom: 1px solid

        var(--court-border-soft);

}


.detail-label {

    display: block;

    margin-bottom: 8px;

    color: #94A3B8;

    font-size: .61rem;

    font-weight: 800;

    letter-spacing: .10em;

    text-transform: uppercase;

}


.detail-section p {

    margin: 0;

    color: #475569;

    font-size: .83rem;

    line-height: 1.72;

}


/* ============================================================
   ETIQUETAS
============================================================ */

.label-list {

    display: flex;

    flex-wrap: wrap;

    gap: 6px;

}


.node-label {

    display: inline-flex;

    align-items: center;

    padding: 5px 8px;

    border: 1px solid

        #D9E5F5;

    border-radius: 999px;

    color: var(--court-blue-dark);

    background:

        var(--court-blue-soft);

    font-size: .66rem;

    font-weight: 650;

}


/* ============================================================
   ATRIBUTOS
============================================================ */

.attributes-list {

    display: flex;

    flex-direction: column;

    gap: 8px;

}


.attribute-row {

    display: flex;

    flex-direction: column;

    gap: 4px;

    padding: 10px;

    background:

        #FAFBFC;

    border: 1px solid

        var(--court-border-soft);

    border-radius: 9px;

}


.attribute-row span {

    color: #94A3B8;

    font-size: .66rem;

    font-weight: 650;

}


.attribute-row strong {

    overflow-wrap: anywhere;

    color: #334155;

    font-size: .76rem;

    font-weight: 650;

    line-height: 1.5;

}


/* ============================================================
   FOOTER DEL DETALLE
============================================================ */

.detail-footer {

    display: flex;

    align-items: center;

    gap: 5px;

    padding-top: 17px;

    color: #64748B;

    font-size: .71rem;

}


.detail-footer strong {

    color: var(--court-navy);

    font-weight: 760;

}


.connection-indicator {

    width: 6px;

    height: 6px;

    margin-right: 2px;

    border-radius: 50%;

    background:

        var(--court-gold);

}


/* ============================================================
   FIRMA INSTITUCIONAL
============================================================ */

.graph-footer-mark {

    position: relative;

    z-index: 2;

    display: flex;

    align-items: center;

    justify-content: center;

    gap: 8px;

    margin-top: 17px;

    color: #A0ACBA;

    font-size: .51rem;

    font-weight: 800;

    letter-spacing: .13em;

    white-space: nowrap;

}


.footer-line {

    width: 18px;

    height: 1px;

    background:

        #D4DCE5;

}


/* ============================================================
   ANIMACIONES
============================================================ */

@keyframes loadingRotate {

    to {

        transform:

            rotate(360deg);

    }

}


@keyframes detailAppear {

    from {

        opacity: 0;

        transform:

            translateX(10px);

    }

    to {

        opacity: 1;

        transform:

            translateX(0);

    }

}


/* ============================================================
   RESPONSIVE — 900px
============================================================ */

@media (max-width: 900px) {

    .graph-header {

        flex-direction: column;

        gap: 18px;

    }


    .graph-stats {

        align-self: flex-start;

    }


    .graph-main {

        min-height: 520px;

    }


    .graph-canvas {

        min-height: 520px;

    }


    .graph-svg {

        height: 520px;

    }

}


/* ============================================================
   RESPONSIVE — 700px
============================================================ */

@media (max-width: 700px) {

    .graph-panel {

        padding: 23px;

    }


    .graph-legend {

        align-items: flex-start;

        flex-direction: column;

        gap: 12px;

    }


    .graph-toolbar {

        align-items: flex-start;

        flex-direction: column;

    }


    .toolbar-actions {

        width: 100%;

    }


    .toolbar-button {

        flex: 0 0 auto;

    }


    .graph-main {

        min-height: 480px;

    }


    .graph-canvas {

        min-height: 480px;

    }


    .graph-svg {

        height: 480px;

    }


    .node-detail-panel {

        top: auto;

        right: 10px;

        bottom: 10px;

        left: 10px;

        width: auto;

        max-height: 60%;

    }

}


/* ============================================================
   RESPONSIVE — 480px
============================================================ */

@media (max-width: 480px) {

    .graph-panel {

        padding: 18px;

        border-radius: 18px;

    }


    .section-label {

        font-size: .58rem;

        letter-spacing: .10em;

    }


    .label-line {

        width: 18px;

    }


    .graph-heading h2 {

        font-size: 1.32rem;

    }


    .graph-heading p {

        font-size: .83rem;

    }


    .graph-stats {

        width: 100%;

        justify-content: center;

    }


    .legend-items {

        gap: 9px 14px;

    }


    .legend-item {

        font-size: .68rem;

    }


    .graph-toolbar {

        gap: 9px;

    }


    .toolbar-caption {

        display: none;

    }


    .toolbar-actions {

        justify-content: flex-start;

    }


    .toolbar-button {

        min-width: 37px;

        padding: 8px;

    }


    .toolbar-button span:not(.toolbar-icon) {

        display: none;

    }


    .graph-empty {

        min-height: 370px;

        padding: 30px 20px;

    }


    .graph-empty p {

        font-size: .82rem;

    }


    .graph-footer-mark {

        font-size: .46rem;

        letter-spacing: .09em;

    }


    .footer-line {

        width: 11px;

    }

}


/* ============================================================
   REDUCED MOTION
============================================================ */

@media (prefers-reduced-motion: reduce) {

    .loading-ring,

    .node-detail-panel {

        animation: none;

    }


    .toolbar-button,

    .close-button,

    .graph-svg :deep(*) {

        transition: none;

    }

}

.graph-filters { display:flex; flex-wrap:wrap; align-items:center; gap:12px; padding:12px 20px; color:#17324f; }
.graph-filters label { display:inline-flex; align-items:center; gap:6px; font-size:.82rem; }
.graph-filters input[type="search"], .graph-filters select { max-width:220px; padding:6px; border:1px solid #b9c8d7; border-radius:5px; }
.graph-filters fieldset { display:flex; flex-wrap:wrap; gap:8px; border:1px solid #d7e0e8; border-radius:5px; }
.graph-filters legend { font-size:.75rem; }
.graph-notice { margin:10px 20px; padding:10px; background:#f8f4eb; color:#5a4732; border-left:3px solid #b08a4c; }
.graph-text-list { padding:0 20px 10px; font-size:.82rem; }
.graph-text-list ul { max-height:180px; overflow:auto; }
.graph-text-list button, .detail-section button { border:0; background:transparent; color:#244c73; text-align:left; cursor:pointer; padding:4px; }
.node-detail-panel { max-width:100%; }
@media (max-width:700px) { .graph-main { display:block; } .node-detail-panel { width:100%; } }
</style>
