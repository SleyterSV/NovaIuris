import { ref } from 'vue'

export function createComposerPopovers() {
  const selectorOpen = ref(false)
  const filtersOpen = ref(false)

  function toggleSelector() {
    const opening = !selectorOpen.value
    filtersOpen.value = false
    selectorOpen.value = opening
  }

  function toggleFilters() {
    const opening = !filtersOpen.value
    selectorOpen.value = false
    filtersOpen.value = opening
  }

  function outsidePointer(target, selectorRoot, filtersRoot) {
    if (selectorOpen.value && !selectorRoot?.contains(target)) selectorOpen.value = false
    if (filtersOpen.value && !filtersRoot?.contains(target)) filtersOpen.value = false
  }

  function closeOnEscape() {
    const focus = filtersOpen.value ? 'filters' : selectorOpen.value ? 'selector' : null
    selectorOpen.value = false
    filtersOpen.value = false
    return focus
  }

  return { selectorOpen, filtersOpen, toggleSelector, toggleFilters, outsidePointer, closeOnEscape }
}
