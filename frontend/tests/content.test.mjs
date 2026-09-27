import assert from 'node:assert/strict'
import { hasRenderableContent, normalizeRenderableContent } from '../src/utils/content.js'

assert.equal(normalizeRenderableContent(null), '')
assert.equal(normalizeRenderableContent(undefined), '')
assert.equal(normalizeRenderableContent('texto'), 'texto')
assert.match(normalizeRenderableContent({ risk_analysis: ['plazo'] }), /Risk analysis/)
assert.equal(hasRenderableContent(null), false)
assert.equal(hasRenderableContent({ summary: 'válido' }), true)
console.log('content normalization OK')
