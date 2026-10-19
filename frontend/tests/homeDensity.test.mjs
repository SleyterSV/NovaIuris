import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'

test('home retains functional composer, tool discovery and navigation controls', async () => {
  const view = await readFile(new URL('../src/views/MikeView.vue', import.meta.url), 'utf8')
  assert.match(view,/class="mic"[\s\S]*?:aria-label="voice\.state\.value === 'recording' \? 'Detener grabación' : 'Grabar consulta por voz'"/)
  assert.match(view,/@click="voice\.state\.value === 'recording' \? voice\.stop\(\) : voice\.start\(\)"/)
  assert.match(view,/<svg v-else class="mic-icon"[\s\S]*?<rect x="9" y="2" width="6" height="12" rx="3"\/>/)
  assert.match(view,/aria-haspopup="listbox" :aria-expanded="selectorOpen"/)
  assert.match(view,/class="send" type="submit"[\s\S]*?aria-label="Enviar consulta"/)
  assert.match(view,/class="quick-actions"[\s\S]*?@click="selectTool\(key,false\)"/)
  assert.match(view,/<Teleport to="body">[\s\S]*?class="mini-card"/)
  assert.match(view,/<ToolDetailModal/)
  assert.match(view,/workspace\.value\.activeTool = tool/)
})

test('density uses local layout tokens and leaves browser scale untouched', async () => {
  const view = await readFile(new URL('../src/views/MikeView.vue', import.meta.url), 'utf8')
  assert.match(view,/--home-sidebar-width:/)
  assert.match(view,/--home-content-max:/)
  assert.match(view,/--home-topbar-height:/)
  assert.match(view,/--home-hero-title:/)
  assert.match(view,/\.mic-icon\{display:block/)
  assert.doesNotMatch(view,/(?:^|[;{])\s*zoom\s*:/m)
  assert.doesNotMatch(view,/transform:\s*scale\(/)
})
