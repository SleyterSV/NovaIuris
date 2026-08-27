<template>

    <section class="graph-panel">

        <!-- =========================================
             ENCABEZADO
        ========================================== -->

        <header class="graph-header">

            <div class="graph-heading">

                <span class="section-label">

                    NOVACOURT · MAPA RELACIONAL

                </span>

                <h2>

                    Red de Relaciones del Caso

                </h2>

                <p>

                    Visualización estructurada de los actores,
                    argumentos, evidencias, normas y demás elementos
                    identificados durante el análisis judicial.

                </p>

            </div>

            <div
                v-if="hasGraphData"
                class="graph-stats"
            >

                <div class="stat-item">

                    <strong>

                        {{ normalizedNodes.length }}

                    </strong>

                    <span>

                        Nodos

                    </span>

                </div>

                <div class="stat-divider"></div>

                <div class="stat-item">

                    <strong>

                        {{ normalizedLinks.length }}

                    </strong>

                    <span>

                        Relaciones

                    </span>

                </div>

            </div>

        </header>


        <!-- =========================================
             LEYENDA
        ========================================== -->

        <div
            v-if="hasGraphData"
            class="graph-legend"
        >

            <div class="legend-title">

                <span>

                    Clasificación

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
                            background: item.color
                        }"
                    ></span>

                    <span>

                        {{ item.label }}

                    </span>

                </div>

            </div>

        </div>


        <!-- =========================================
             ESTADO DE CARGA
        ========================================== -->

        <div
            v-if="loading"
            class="graph-state graph-loading"
        >

            <div class="loading-spinner"></div>

            <div>

                <strong>

                    Construyendo red relacional

                </strong>

                <p>

                    NovaCourt está organizando los elementos
                    y relaciones identificados en el caso.

                </p>

            </div>

        </div>


        <!-- =========================================
             ERROR
        ========================================== -->

        <div
            v-else-if="error"
            class="graph-state graph-error"
        >

            <div class="state-icon">

                !

            </div>

            <div>

                <strong>

                    No se pudo cargar el grafo

                </strong>

                <p>

                    {{ error }}

                </p>

            </div>

        </div>


        <!-- =========================================
             ESTADO VACÍO
        ========================================== -->

        <div
            v-else-if="!hasGraphData"
            class="graph-empty"
        >

            <div class="empty-icon">

                ◌

            </div>

            <h3>

                Red relacional pendiente

            </h3>

            <p>

                Cuando NovaCourt procese el caso y genere
                relaciones entre sus elementos jurídicos,
                podrás visualizarlas aquí de forma interactiva.

            </p>

        </div>


        <!-- =========================================
             GRAFO
        ========================================== -->

        <div
            v-else
            class="graph-workspace"
        >

            <!-- CONTROLES -->

            <div class="graph-toolbar">

                <button
                    type="button"
                    class="toolbar-button"
                    title="Restablecer visualización"
                    @click="resetGraph"
                >

                    ↺

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

                    ⊙

                    <span>

                        Centrar

                    </span>

                </button>

                <button
                    type="button"
                    class="toolbar-button"
                    title="Cerrar selección"
                    :disabled="!selectedNode"
                    @click="clearSelection"
                >

                    ×

                    <span>

                        Limpiar

                    </span>

                </button>

            </div>


            <!-- ÁREA PRINCIPAL -->

            <div class="graph-main">

                <!-- SVG -->

                <div
                    ref="graphContainer"
                    class="graph-canvas"
                >

                    <svg
                        ref="svgElement"
                        class="graph-svg"
                    ></svg>

                </div>


                <!-- PANEL DEL NODO -->

                <aside
                    v-if="selectedNode"
                    class="node-detail-panel"
                >

                    <div class="detail-header">

                        <div>

                            <span
                                class="detail-type"
                                :style="{
                                    color: getNodeColor(selectedNode)
                                }"
                            >

                                {{ getNodeCategoryLabel(selectedNode) }}

                            </span>

                            <h3>

                                {{ selectedNode.name || "Elemento sin nombre" }}

                            </h3>

                        </div>

                        <button
                            type="button"
                            class="close-button"
                            @click="clearSelection"
                        >

                            ×

                        </button>

                    </div>


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


                    <div class="detail-footer">

                        <span>

                            {{ selectedNodeConnectionCount }}

                        </span>

                        relaciones identificadas

                    </div>

                </aside>

            </div>

        </div>

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


/* =========================================
   PROPS
========================================= */

const props = defineProps({

    graphData: {

        type: Object,

        default: () => ({})

    },

    loading: {

        type: Boolean,

        default: false

    },

    error: {

        type: String,

        default: ""

    }

})


/* =========================================
   REFERENCIAS
========================================= */

const graphContainer = ref(null)

const svgElement = ref(null)

const selectedNode = ref(null)


/* =========================================
   INSTANCIAS D3
========================================= */

let simulation = null

let zoomBehavior = null

let resizeObserver = null

let currentSvg = null

let currentRoot = null


/* =========================================
   COLORES JURÍDICOS
========================================= */

const categoryColors = {

    judicial: "#1D4ED8",

    lawyer: "#2563EB",

    prosecution: "#B45309",

    party: "#7C3AED",

    evidence: "#15803D",

    norm: "#0369A1",

    argument: "#BE123C",

    fact: "#64748B",

    default: "#475569"

}


const legendItems = [

    {

        key: "judicial",

        label: "Órgano judicial",

        color: categoryColors.judicial

    },

    {

        key: "lawyer",

        label: "Defensa / abogado",

        color: categoryColors.lawyer

    },

    {

        key: "prosecution",

        label: "Fiscalía",

        color: categoryColors.prosecution

    },

    {

        key: "party",

        label: "Parte procesal",

        color: categoryColors.party

    },

    {

        key: "evidence",

        label: "Evidencia",

        color: categoryColors.evidence

    },

    {

        key: "norm",

        label: "Norma / jurisprudencia",

        color: categoryColors.norm

    },

    {

        key: "argument",

        label: "Argumento",

        color: categoryColors.argument

    },

    {

        key: "fact",

        label: "Hecho / general",

        color: categoryColors.fact

    }

]


/* =========================================
   NORMALIZAR DATOS
========================================= */

const normalizedNodes = computed(() => {

    const nodes = props.graphData?.nodes

    if (!Array.isArray(nodes)) {

        return []

    }

    return nodes

        .filter(node => node?.uuid)

        .map(node => ({

            ...node,

            id: String(node.uuid)

        }))

})


const normalizedLinks = computed(() => {

    const edges = props.graphData?.edges

    if (!Array.isArray(edges)) {

        return []

    }

    const validNodeIds = new Set(

        normalizedNodes.value.map(node => node.id)

    )

    return edges

        .filter(edge => {

            const source = String(

                edge?.source_node_uuid || ""

            )

            const target = String(

                edge?.target_node_uuid || ""

            )

            return (

                source &&
                target &&
                validNodeIds.has(source) &&
                validNodeIds.has(target)

            )

        })

        .map(edge => ({

            ...edge,

            id: String(

                edge.uuid ||

                `${edge.source_node_uuid}-${edge.target_node_uuid}-${edge.name || ""}`

            ),

            source: String(edge.source_node_uuid),

            target: String(edge.target_node_uuid)

        }))

})


const hasGraphData = computed(() =>

    normalizedNodes.value.length > 0

)


/* =========================================
   DETALLE DEL NODO
========================================= */

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


/* =========================================
   CLASIFICACIÓN DEL NODO
========================================= */

function getNodeText(node) {

    return [

        ...(Array.isArray(node?.labels) ? node.labels : []),

        node?.name || "",

        node?.summary || ""

    ]

        .join(" ")

        .toLowerCase()

}


function getNodeCategory(node) {

    const text = getNodeText(node)


    if (

        text.includes("juez") ||

        text.includes("tribunal") ||

        text.includes("corte") ||

        text.includes("sala") ||

        text.includes("magistrado") ||

        text.includes("judicial")

    ) {

        return "judicial"

    }


    if (

        text.includes("abogado") ||

        text.includes("defensa") ||

        text.includes("defensor")

    ) {

        return "lawyer"

    }


    if (

        text.includes("fiscal") ||

        text.includes("ministerio público") ||

        text.includes("acusación")

    ) {

        return "prosecution"

    }


    if (

        text.includes("demandante") ||

        text.includes("demandado") ||

        text.includes("imputado") ||

        text.includes("acusado") ||

        text.includes("agraviado") ||

        text.includes("parte")

    ) {

        return "party"

    }


    if (

        text.includes("evidencia") ||

        text.includes("prueba") ||

        text.includes("documento") ||

        text.includes("pericia") ||

        text.includes("testimonio")

    ) {

        return "evidence"

    }


    if (

        text.includes("norma") ||

        text.includes("ley") ||

        text.includes("artículo") ||

        text.includes("jurisprudencia") ||

        text.includes("precedente") ||

        text.includes("constitución")

    ) {

        return "norm"

    }


    if (

        text.includes("argumento") ||

        text.includes("pretensión") ||

        text.includes("alegato")

    ) {

        return "argument"

    }


    if (

        text.includes("hecho") ||

        text.includes("evento") ||

        text.includes("suceso")

    ) {

        return "fact"

    }


    return "default"

}


function getNodeColor(node) {

    return categoryColors[

        getNodeCategory(node)

    ] || categoryColors.default

}


function getNodeCategoryLabel(node) {

    const category = getNodeCategory(node)


    const labels = {

        judicial: "ÓRGANO JUDICIAL",

        lawyer: "DEFENSA / ABOGADO",

        prosecution: "FISCALÍA",

        party: "PARTE PROCESAL",

        evidence: "EVIDENCIA",

        norm: "NORMA / JURISPRUDENCIA",

        argument: "ARGUMENTO",

        fact: "HECHO / ELEMENTO",

        default: "ELEMENTO DEL CASO"

    }


    return labels[category]

}


/* =========================================
   FORMATEADORES
========================================= */

function formatAttributeKey(key) {

    return String(key)

        .replaceAll("_", " ")

        .replace(/\b\w/g, char => char.toUpperCase())

}


function formatAttributeValue(value) {

    if (typeof value === "object") {

        return JSON.stringify(value)

    }

    return String(value)

}


/* =========================================
   CREAR GRAFO
========================================= */

function renderGraph() {

    if (

        !svgElement.value ||

        !graphContainer.value ||

        !hasGraphData.value

    ) {

        return

    }


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

        ...node

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


    svg.on(

        "dblclick.zoom",

        null

    )


    const linkGroup = root

        .append("g")

        .attr(

            "class",

            "graph-links"

        )


    const nodeGroup = root

        .append("g")

        .attr(

            "class",

            "graph-nodes"

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


    nodeSelection

        .append("circle")

        .attr(

            "class",

            "node-circle"

        )

        .attr(

            "r",

            24

        )

        .attr(

            "fill",

            node => getNodeColor(node)

        )


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


    const drag = d3

        .drag()

        .on(

            "start",

            (event, node) => {

                if (!event.active) {

                    simulation.alphaTarget(

                        0.3

                    ).restart()

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

                    simulation.alphaTarget(

                        0

                    )

                }

                node.fx = null

                node.fy = null

            }

        )


    nodeSelection.call(drag)


    simulation = d3

        .forceSimulation(nodes)

        .force(

            "link",

            d3

                .forceLink(links)

                .id(node => node.id)

                .distance(130)

                .strength(0.7)

        )

        .force(

            "charge",

            d3

                .forceManyBody()

                .strength(-500)

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

                .radius(70)

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

}


/* =========================================
   RESALTAR SELECCIÓN
========================================= */

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


/* =========================================
   UTILIDADES
========================================= */

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


/* =========================================
   OBSERVAR CAMBIOS
========================================= */

watch(

    () => props.graphData,

    async () => {

        selectedNode.value = null

        await nextTick()

        renderGraph()

    },

    {

        deep: true

    }

)


watch(

    () => props.loading,

    async loading => {

        if (!loading) {

            await nextTick()

            renderGraph()

        }

    }

)


/* =========================================
   CICLO DE VIDA
========================================= */

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

/* =========================================
   CONTENEDOR PRINCIPAL
========================================= */

.graph-panel{

    width:100%;

    padding:30px;

    background:#FFFFFF;

    border:1px solid #E2E8F0;

    border-radius:22px;

    box-shadow:

        0 10px 30px

        rgba(
            15,
            39,
            71,
            .06
        );

}


/* =========================================
   ENCABEZADO
========================================= */

.graph-header{

    display:flex;

    align-items:flex-start;

    justify-content:space-between;

    gap:28px;

    padding-bottom:24px;

    border-bottom:1px solid #E2E8F0;

}

.graph-heading{

    min-width:0;

}

.section-label{

    display:block;

    margin-bottom:8px;

    color:#2563EB;

    font-size:.72rem;

    font-weight:700;

    letter-spacing:1px;

}

.graph-heading h2{

    margin:0 0 8px;

    color:#0F2747;

    font-size:1.5rem;

    font-weight:700;

    line-height:1.3;

}

.graph-heading p{

    max-width:720px;

    margin:0;

    color:#64748B;

    font-size:.95rem;

    line-height:1.7;

}


/* =========================================
   ESTADÍSTICAS
========================================= */

.graph-stats{

    display:flex;

    align-items:center;

    flex-shrink:0;

    padding:12px 16px;

    background:#F8FAFC;

    border:1px solid #E2E8F0;

    border-radius:14px;

}

.stat-item{

    display:flex;

    flex-direction:column;

    min-width:62px;

    text-align:center;

}

.stat-item strong{

    color:#0F2747;

    font-size:1.1rem;

    font-weight:750;

}

.stat-item span{

    margin-top:3px;

    color:#64748B;

    font-size:.72rem;

}

.stat-divider{

    width:1px;

    height:30px;

    margin:0 14px;

    background:#E2E8F0;

}


/* =========================================
   LEYENDA
========================================= */

.graph-legend{

    display:flex;

    align-items:center;

    gap:18px;

    flex-wrap:wrap;

    padding:18px 0;

    border-bottom:1px solid #E2E8F0;

}

.legend-title{

    color:#475569;

    font-size:.78rem;

    font-weight:700;

}

.legend-items{

    display:flex;

    align-items:center;

    flex-wrap:wrap;

    gap:12px 18px;

}

.legend-item{

    display:inline-flex;

    align-items:center;

    gap:7px;

    color:#64748B;

    font-size:.78rem;

}

.legend-dot{

    width:9px;

    height:9px;

    border-radius:50%;

    box-shadow:

        0 0 0 3px

        rgba(
            15,
            23,
            42,
            .04
        );

}


/* =========================================
   ESTADOS
========================================= */

.graph-state{

    display:flex;

    align-items:center;

    gap:18px;

    min-height:300px;

    margin-top:22px;

    padding:32px;

    border-radius:18px;

}

.graph-loading{

    color:#475569;

    background:#F8FAFC;

    border:1px dashed #CBD5E1;

}

.graph-error{

    color:#991B1B;

    background:#FEF2F2;

    border:1px solid #FECACA;

}

.graph-state strong{

    display:block;

    margin-bottom:6px;

    color:#0F2747;

    font-size:.98rem;

}

.graph-error strong{

    color:#991B1B;

}

.graph-state p{

    margin:0;

    color:#64748B;

    font-size:.9rem;

    line-height:1.6;

}

.state-icon{

    width:40px;

    height:40px;

    display:flex;

    align-items:center;

    justify-content:center;

    flex-shrink:0;

    border-radius:50%;

    color:#B91C1C;

    background:#FEE2E2;

    font-size:1.1rem;

    font-weight:800;

}

.loading-spinner{

    width:34px;

    height:34px;

    flex-shrink:0;

    border:3px solid #DBEAFE;

    border-top-color:#2563EB;

    border-radius:50%;

    animation:spin .9s linear infinite;

}


/* =========================================
   VACÍO
========================================= */

.graph-empty{

    display:flex;

    flex-direction:column;

    align-items:center;

    justify-content:center;

    min-height:430px;

    margin-top:22px;

    padding:40px;

    text-align:center;

    background:#F8FAFC;

    border:1px dashed #CBD5E1;

    border-radius:18px;

}

.empty-icon{

    width:68px;

    height:68px;

    display:flex;

    align-items:center;

    justify-content:center;

    margin-bottom:18px;

    border-radius:20px;

    color:#2563EB;

    background:#EFF6FF;

    font-size:2rem;

}

.graph-empty h3{

    margin:0 0 10px;

    color:#0F2747;

    font-size:1.08rem;

    font-weight:700;

}

.graph-empty p{

    max-width:500px;

    margin:0;

    color:#64748B;

    font-size:.93rem;

    line-height:1.7;

}


/* =========================================
   WORKSPACE
========================================= */

.graph-workspace{

    margin-top:22px;

}

.graph-toolbar{

    display:flex;

    align-items:center;

    justify-content:flex-end;

    gap:8px;

    margin-bottom:12px;

}

.toolbar-button{

    display:inline-flex;

    align-items:center;

    justify-content:center;

    gap:7px;

    min-height:36px;

    padding:8px 12px;

    border:1px solid #E2E8F0;

    border-radius:9px;

    cursor:pointer;

    background:#FFFFFF;

    color:#475569;

    font-family:inherit;

    font-size:.78rem;

    font-weight:650;

    transition:

        color .2s ease,
        background .2s ease,
        border-color .2s ease;

}

.toolbar-button:hover:not(:disabled){

    color:#0F2747;

    background:#F8FAFC;

    border-color:#CBD5E1;

}

.toolbar-button:disabled{

    cursor:not-allowed;

    opacity:.45;

}


/* =========================================
   ÁREA DEL GRAFO
========================================= */

.graph-main{

    position:relative;

    display:grid;

    grid-template-columns:minmax(0,1fr);

    min-height:560px;

    overflow:hidden;

    background:

        radial-gradient(
            circle at 1px 1px,
            rgba(148,163,184,.18) 1px,
            transparent 0
        );

    background-size:22px 22px;

    border:1px solid #E2E8F0;

    border-radius:18px;

}

.graph-canvas{

    width:100%;

    min-height:560px;

    overflow:hidden;

}

.graph-svg{

    display:block;

    width:100%;

    height:560px;

}


/* =========================================
   ELEMENTOS D3
========================================= */

.graph-svg :deep(.graph-link){

    stroke:#CBD5E1;

    stroke-width:1.5;

    stroke-opacity:.8;

    transition:

        stroke .2s ease,
        stroke-opacity .2s ease;

}

.graph-svg :deep(.graph-link.is-active){

    stroke:#2563EB;

    stroke-width:2.5;

    stroke-opacity:1;

}

.graph-svg :deep(.graph-link.is-muted){

    stroke-opacity:.15;

}

.graph-svg :deep(.graph-node){

    transition:opacity .2s ease;

}

.graph-svg :deep(.graph-node.is-muted){

    opacity:.22;

}

.graph-svg :deep(.graph-node.is-selected .node-ring){

    stroke:#0F2747;

    stroke-width:2;

    opacity:1;

}

.graph-svg :deep(.node-circle){

    stroke:#FFFFFF;

    stroke-width:3;

    filter:

        drop-shadow(
            0 4px 8px
            rgba(15,23,42,.16)
        );

}

.graph-svg :deep(.node-ring){

    stroke:#2563EB;

    stroke-width:0;

    opacity:0;

}

.graph-svg :deep(.node-text){

    fill:#334155;

    font-family:inherit;

    font-size:12px;

    font-weight:600;

    pointer-events:none;

}


/* =========================================
   PANEL DE DETALLE
========================================= */

.node-detail-panel{

    position:absolute;

    top:16px;

    right:16px;

    bottom:16px;

    z-index:5;

    width:min(340px,calc(100% - 32px));

    padding:22px;

    overflow-y:auto;

    background:

        rgba(
            255,
            255,
            255,
            .96
        );

    backdrop-filter:blur(14px);

    border:1px solid #E2E8F0;

    border-radius:16px;

    box-shadow:

        0 18px 45px

        rgba(
            15,
            23,
            42,
            .12
        );

}

.detail-header{

    display:flex;

    align-items:flex-start;

    justify-content:space-between;

    gap:14px;

    padding-bottom:18px;

    border-bottom:1px solid #E2E8F0;

}

.detail-type{

    display:block;

    margin-bottom:7px;

    font-size:.68rem;

    font-weight:750;

    letter-spacing:.8px;

}

.detail-header h3{

    margin:0;

    color:#0F2747;

    font-size:1.05rem;

    line-height:1.45;

}

.close-button{

    width:32px;

    height:32px;

    flex-shrink:0;

    border:1px solid #E2E8F0;

    border-radius:8px;

    cursor:pointer;

    background:#FFFFFF;

    color:#64748B;

    font-size:1.2rem;

    transition:

        background .2s ease,
        color .2s ease;

}

.close-button:hover{

    color:#0F2747;

    background:#F8FAFC;

}

.detail-section{

    padding:18px 0;

    border-bottom:1px solid #E2E8F0;

}

.detail-label{

    display:block;

    margin-bottom:9px;

    color:#64748B;

    font-size:.7rem;

    font-weight:750;

    letter-spacing:.6px;

    text-transform:uppercase;

}

.detail-section p{

    margin:0;

    color:#475569;

    font-size:.88rem;

    line-height:1.7;

}

.label-list{

    display:flex;

    flex-wrap:wrap;

    gap:7px;

}

.node-label{

    display:inline-flex;

    align-items:center;

    padding:5px 8px;

    border:1px solid #DBEAFE;

    border-radius:999px;

    color:#1D4ED8;

    background:#EFF6FF;

    font-size:.72rem;

    font-weight:650;

}

.attributes-list{

    display:flex;

    flex-direction:column;

    gap:10px;

}

.attribute-row{

    display:flex;

    flex-direction:column;

    gap:4px;

    padding:10px;

    background:#F8FAFC;

    border:1px solid #E2E8F0;

    border-radius:9px;

}

.attribute-row span{

    color:#64748B;

    font-size:.72rem;

    font-weight:600;

}

.attribute-row strong{

    overflow-wrap:anywhere;

    color:#334155;

    font-size:.8rem;

    font-weight:650;

    line-height:1.5;

}

.detail-footer{

    padding-top:18px;

    color:#64748B;

    font-size:.78rem;

}

.detail-footer span{

    margin-right:3px;

    color:#0F2747;

    font-weight:750;

}


/* =========================================
   ANIMACIONES
========================================= */

@keyframes spin{

    to{

        transform:rotate(360deg);

    }

}


/* =========================================
   RESPONSIVE
========================================= */

@media(max-width:900px){

    .graph-header{

        flex-direction:column;

        gap:18px;

    }

    .graph-stats{

        align-self:flex-start;

    }

    .graph-main{

        min-height:520px;

    }

    .graph-canvas{

        min-height:520px;

    }

    .graph-svg{

        height:520px;

    }

}


@media(max-width:700px){

    .graph-panel{

        padding:22px;

    }

    .graph-legend{

        align-items:flex-start;

        flex-direction:column;

        gap:12px;

    }

    .graph-toolbar{

        justify-content:flex-start;

        overflow-x:auto;

    }

    .toolbar-button span{

        display:none;

    }

    .toolbar-button{

        width:38px;

        padding:8px;

    }

    .graph-main{

        min-height:480px;

    }

    .graph-canvas{

        min-height:480px;

    }

    .graph-svg{

        height:480px;

    }

    .node-detail-panel{

        top:auto;

        right:10px;

        bottom:10px;

        left:10px;

        width:auto;

        max-height:60%;

    }

}


@media(max-width:480px){

    .graph-panel{

        padding:18px;

        border-radius:18px;

    }

    .graph-heading h2{

        font-size:1.3rem;

    }

    .graph-stats{

        width:100%;

        justify-content:center;

    }

    .graph-empty{

        min-height:360px;

        padding:30px 20px;

    }

}
</style>