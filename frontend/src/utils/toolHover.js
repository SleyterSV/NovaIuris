import { nextTick, ref } from 'vue'

const CARD_GAP = 32
const VIEWPORT_MARGIN = 12

export function toolCardPosition(anchor, card, viewport) {
  const width = Math.min(card?.width || 320, Math.max(0, viewport.width - VIEWPORT_MARGIN * 2))
  const height = card?.height || 220
  return {
    left: Math.max(VIEWPORT_MARGIN, Math.min(anchor.right + CARD_GAP, viewport.width - width - VIEWPORT_MARGIN)),
    top: Math.max(VIEWPORT_MARGIN, Math.min(anchor.top, viewport.height - height - VIEWPORT_MARGIN)),
  }
}

export function createToolHoverController({ delay = 180, schedule = setTimeout, cancel = clearTimeout,
  viewport = () => ({ width:window.innerWidth, height:window.innerHeight }) } = {}) {
  const active = ref(null)
  const position = ref({ left:0, top:0 })
  let anchor = null, card = null, closeTimer = null

  function cancelClose() {
    if (closeTimer !== null) cancel(closeTimer)
    closeTimer = null
  }
  function close() {
    cancelClose()
    active.value = null
    anchor = null
    card = null
  }
  function scheduleClose() {
    cancelClose()
    closeTimer = schedule(close, delay)
  }
  function refreshPosition() {
    if (!active.value || !anchor?.isConnected) return
    position.value = toolCardPosition(anchor.getBoundingClientRect(), card?.getBoundingClientRect(), viewport())
  }
  function setCard(element) {
    card = element
    refreshPosition()
  }
  function open(tool, element) {
    cancelClose()
    if (!element) return
    anchor = element
    active.value = tool
    refreshPosition()
    void nextTick(refreshPosition)
  }
  function enterCard() { cancelClose() }
  return { active, position, open, close, cancelClose, scheduleClose, enterCard, setCard, refreshPosition, dispose:close }
}
