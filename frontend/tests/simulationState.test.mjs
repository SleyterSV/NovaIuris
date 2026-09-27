import assert from 'node:assert/strict'
import { normalizeSimulationState } from '../src/utils/simulationState.js'

const empty = normalizeSimulationState(null)
assert.equal(empty.status, 'not_requested')
assert.deepEqual(empty.prosecutor, {})

const ready = normalizeSimulationState({
  status: 'ready',
  prosecutor: { content: 'Fiscalía' },
  defense: { content: 'Defensa' },
  judge: { content: 'Juzgado' },
  projection: { content: 'Proyección' }
})
assert.equal(ready.status, 'ready')
assert.equal(ready.prosecutor.content, 'Fiscalía')
assert.equal(ready.projection.content, 'Proyección')

const failed = normalizeSimulationState({ status: 'failed', message: 'Servicio no disponible' })
assert.equal(failed.status, 'failed')
assert.equal(failed.message, 'Servicio no disponible')

const partial = normalizeSimulationState({ status: 'ready', judge: { content: 'Deliberación' } })
assert.deepEqual(partial.prosecutor, {})
assert.equal(partial.judge.content, 'Deliberación')

console.log('simulation state OK')
