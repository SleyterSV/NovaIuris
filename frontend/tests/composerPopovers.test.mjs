import assert from 'node:assert/strict'
import { test } from 'node:test'
import { createComposerPopovers } from '../src/utils/composerPopovers.js'

function roots() {
  const selectorInside = {}, filtersInside = {}, outside = {}
  return {
    selectorInside, filtersInside, outside,
    selectorRoot: { contains: target => target === selectorInside },
    filtersRoot: { contains: target => target === filtersInside }
  }
}

test('selector toggles and closes only on outside pointer or Escape', () => {
  const popovers = createComposerPopovers()
  const area = roots()
  popovers.toggleSelector()
  assert.equal(popovers.selectorOpen.value, true)
  popovers.outsidePointer(area.selectorInside, area.selectorRoot, area.filtersRoot)
  assert.equal(popovers.selectorOpen.value, true)
  popovers.outsidePointer(area.outside, area.selectorRoot, area.filtersRoot)
  assert.equal(popovers.selectorOpen.value, false)
  popovers.toggleSelector()
  assert.equal(popovers.closeOnEscape(), 'selector')
  assert.equal(popovers.selectorOpen.value, false)
  assert.equal(popovers.closeOnEscape(), null)
})

test('filter remains interactive inside, closes outside or on Escape', () => {
  const popovers = createComposerPopovers()
  const area = roots()
  popovers.toggleFilters()
  assert.equal(popovers.filtersOpen.value, true)
  popovers.outsidePointer(area.filtersInside, area.selectorRoot, area.filtersRoot)
  assert.equal(popovers.filtersOpen.value, true)
  popovers.outsidePointer(area.outside, area.selectorRoot, area.filtersRoot)
  assert.equal(popovers.filtersOpen.value, false)
  popovers.toggleFilters()
  assert.equal(popovers.closeOnEscape(), 'filters')
  assert.equal(popovers.filtersOpen.value, false)
})

test('opening either popover closes the other', () => {
  const popovers = createComposerPopovers()
  popovers.toggleSelector()
  popovers.toggleFilters()
  assert.equal(popovers.selectorOpen.value, false)
  assert.equal(popovers.filtersOpen.value, true)
  popovers.toggleSelector()
  assert.equal(popovers.selectorOpen.value, true)
  assert.equal(popovers.filtersOpen.value, false)
  popovers.toggleSelector()
  assert.equal(popovers.selectorOpen.value, false)
})
