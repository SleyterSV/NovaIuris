import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createToolHoverController, toolCardPosition } from '../src/utils/toolHover.js'

function hoverHarness() {
  let nextId = 0
  const timers = new Map()
  const hover = createToolHoverController({
    schedule(callback, delay) { assert.equal(delay,180); const id = ++nextId; timers.set(id,callback); return id },
    cancel(id) { timers.delete(id) },
    viewport:() => ({ width:1280, height:720 }),
  })
  const anchors = {
    search:{ isConnected:true, getBoundingClientRect:() => ({ right:288, top:210 }) },
    case:{ isConnected:true, getBoundingClientRect:() => ({ right:288, top:280 }) },
    court:{ isConnected:true, getBoundingClientRect:() => ({ right:288, top:350 }) },
  }
  function expire() { const callbacks = [...timers.values()]; timers.clear(); callbacks.forEach(callback => callback()) }
  return { hover, anchors, timers, expire }
}

test('trigger to floating card shares one close timer and keeps Conocer más reachable', () => {
  const { hover, anchors, timers, expire } = hoverHarness()
  hover.open('case', anchors.case)
  hover.setCard({ getBoundingClientRect:() => ({ width:320, height:190 }) })
  assert.equal(hover.active.value,'case')
  assert.deepEqual(hover.position.value,{ left:320, top:280 })
  hover.scheduleClose() // pointer leaves trigger
  assert.equal(timers.size,1)
  hover.enterCard() // pointer crosses gap and enters card
  assert.equal(timers.size,0)
  expire()
  assert.equal(hover.active.value,'case')
  hover.scheduleClose() // pointer leaves card too
  expire()
  assert.equal(hover.active.value,null)
})

test('switching tools cancels closure and updates content without an empty state', () => {
  const { hover, anchors, expire } = hoverHarness()
  hover.open('search',anchors.search)
  hover.scheduleClose()
  hover.open('case',anchors.case)
  expire()
  assert.equal(hover.active.value,'case')
  hover.open('court',anchors.court)
  assert.equal(hover.active.value,'court')
  assert.equal(hover.position.value.top,350)
  hover.close() // Escape / modal launch
  assert.equal(hover.active.value,null)
})

test('floating position clamps to viewport without changing layout width', () => {
  assert.deepEqual(toolCardPosition({ right:1190, top:680 }, { width:320, height:190 },
    { width:1280, height:720 }), { left:948, top:518 })
  const small = toolCardPosition({ right:260, top:450 }, { width:320, height:600 },
    { width:300, height:500 })
  assert.ok(small.left >= 12 && small.left + 276 <= 300)
  assert.equal(small.top,12)
})

test('teleport layer and shared pointer/focus handlers keep modal above hover card', async () => {
  const view = await readFile(new URL('../src/views/MikeView.vue',import.meta.url),'utf8')
  const modal = await readFile(new URL('../src/components/common/ToolDetailModal.vue',import.meta.url),'utf8')
  assert.match(view,/<Teleport to="body">[\s\S]*?class="mini-card"/)
  assert.match(view,/position:fixed;z-index:120;width:min\(320px,calc\(100vw - 24px\)\)/)
  assert.match(modal,/z-index:1000/)
  assert.match(view,/@pointerenter="openToolCard\(key,\$event\)"/)
  assert.match(view,/@pointerenter="hover\.enterCard\(\)"/)
  assert.match(view,/@pointerleave="hover\.scheduleClose\(\)"/)
  assert.match(view,/@focusin="hover\.enterCard\(\)"/)
  assert.match(view,/@focusout="hover\.scheduleClose\(\)"/)
  assert.match(view,/event\.key === 'Tab' && !event\.shiftKey/)
  assert.match(view,/nextTick\(\(\) => hoverCard\.value\?\.querySelector\('\.mini-learn'\)\?\.focus\(\)\)/)
  assert.match(view,/event\.key === 'Escape'/)
  assert.match(view,/function openToolDetail\(\) \{\s*detailTool\.value = infoTool\.value\s*hover\.close\(\)/)
  assert.match(view,/@click="openToolDetail"/)
  assert.match(view,/@click="selectTool\(key,false\)"/)
  assert.match(view,/workspace\.value\.activeTool = tool/)
})
