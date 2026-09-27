import assert from 'node:assert/strict'
import { normalizeGraphState } from '../src/utils/graphState.js'

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

console.log('graph state OK')
