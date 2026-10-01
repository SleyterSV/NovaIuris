import assert from 'node:assert/strict'
import { normalizeGraphState } from '../src/utils/graphState.js'
import { readFile } from 'node:fs/promises'

const absent = normalizeGraphState(null)
assert.equal(absent.status, 'not_requested')
assert.deepEqual(absent.nodes, [])
assert.deepEqual(absent.edges, [])

const ready = normalizeGraphState({
  status: 'ready',
  graph_id: 'zep-1',
  nodes: [{ uuid: 'node-1' }],
  edges: [{ uuid: 'edge-1' }]
})
assert.equal(ready.status, 'ready')
assert.equal(ready.graph_id, 'zep-1')
assert.equal(ready.nodes.length, 1)
assert.equal(ready.edges.length, 1)

const failed = normalizeGraphState({ status: 'failed', message: 'Servicio no disponible' })
assert.equal(failed.status, 'failed')
assert.equal(failed.message, 'Servicio no disponible')
assert.deepEqual(failed.nodes, [])

const emptyReady = normalizeGraphState({ status: 'ready', nodes: [], edges: [] })
assert.equal(emptyReady.status, 'ready')
assert.deepEqual(emptyReady.nodes, [])

const first = normalizeGraphState({
  status: 'building', case_id: 'CASE-A', graph_id: 'G-1', version: 1,
  nodes: [{ node_id: 'N-1', entity_type: 'FACT' }], edges: []
})
const second = normalizeGraphState({
  status: 'ready', case_id: 'CASE-A', graph_id: 'G-1', version: 2,
  nodes: [...first.nodes, { node_id: 'N-2', entity_type: 'LAW' }], edges: []
}, first)
assert.equal(first.is_final, false)
assert.equal(second.is_final, true)
assert.equal(second.nodes.length, 2)
assert.equal(normalizeGraphState(first, second), second)
assert.notEqual(normalizeGraphState({ ...first, case_id: 'CASE-B' }, second), second)
assert.equal(normalizeGraphState({ ...first, graph_id: null }, second), second)
assert.equal(normalizeGraphState({ ...first, graph_id: 'G-2' }, second).graph_id, 'G-2')
assert.equal(second.nodes[1].entity_type, 'LAW')
const legacy = normalizeGraphState({ status: 'ready', nodes: [{ uuid: 'old-1' }], edges: [] })
assert.equal(legacy.version, 0)
assert.equal(legacy.counts.node_count, 1)

const partial = normalizeGraphState({ status: 'failed', version: 1,
  nodes: first.nodes, edges: [], message: 'Zep unavailable' })
assert.equal(partial.is_final, false)
assert.equal(partial.nodes.length, 1)
const panel = await readFile(new URL('../src/components/novacourt/GraphPanel.vue', import.meta.url), 'utf8')
assert.match(panel, /node\?\.entity_type/)
assert.doesNotMatch(panel, /text\.includes\(/)
assert.match(panel, /selectedNode\.value = id/)
assert.match(panel, /zoomTransform\(currentSvg\.node\(\)\)/)
assert.match(panel, /<SourceModal/)
assert.match(panel, /v-model="complexity"/)
assert.match(panel, /v-model="query"/)
assert.match(panel, /Grafo parcial/)
assert.match(panel, /No hay nodos para los filtros actuales/)
assert.match(panel, /:checked="!selectedTypes\.includes\(type\)"/)
assert.match(panel, /selectedEdge\.value = normalizedLinks\.value\.find/)
assert.match(panel, /nodeTitle\(selectedEdge\.source\)/)

console.log('graph state OK')
