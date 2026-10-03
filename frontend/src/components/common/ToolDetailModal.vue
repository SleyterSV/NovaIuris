<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
const props = defineProps({ tool:{ type:Object, required:true } })
const emit = defineEmits(['close','use'])
const closeButton = ref(null)
const detail = ref(null)
const previousFocus = typeof document === 'undefined' ? null : document.activeElement
function keydown(event) {
  if (event.key === 'Escape') emit('close')
  if (event.key === 'Tab') {
    const controls = [...(detail.value?.querySelectorAll('button') || [])]
    if (!controls.length) return
    const first = controls[0], last = controls.at(-1)
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
  }
}
onMounted(async () => { await nextTick(); closeButton.value?.focus(); window.addEventListener('keydown', keydown) })
onUnmounted(() => { window.removeEventListener('keydown', keydown); previousFocus?.focus?.() })
</script>

<template>
  <Teleport to="body">
    <div class="backdrop" @click.self="emit('close')">
      <section ref="detail" class="detail" role="dialog" aria-modal="true" aria-labelledby="tool-detail-title">
        <button ref="closeButton" class="close" type="button" aria-label="Cerrar información" @click="emit('close')">×</button>
        <p class="eyebrow">{{ tool.category }}</p>
        <h2 id="tool-detail-title">{{ tool.name }}</h2>
        <p class="lead">{{ tool.about }}</p>
        <div class="grid">
          <section><h3>Para qué sirve</h3><p>{{ tool.purpose }}</p></section>
          <section><h3>Cuándo usarla</h3><p>{{ tool.when }}</p></section>
          <section><h3>Qué puede recibir</h3><p>{{ tool.input }}</p></section>
          <section><h3>Qué produce</h3><p>{{ tool.output }}</p></section>
          <section><h3>Fuentes y trazabilidad</h3><p>{{ tool.sources }}</p></section>
          <section><h3>Cómo se conecta</h3><p>{{ tool.connection }}</p></section>
        </div>
        <p class="example"><strong>Ejemplo</strong> “{{ tool.example }}”</p>
        <button class="use" type="button" @click="emit('use')">Usar esta herramienta →</button>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.backdrop{position:fixed;inset:0;z-index:1000;display:grid;place-items:center;padding:24px;background:#0b1d2db8}.detail{position:relative;width:min(760px,100%);max-height:88vh;overflow:auto;padding:36px 42px;background:#fffdf9;border:1px solid #d9c7a5;border-radius:18px;box-shadow:0 24px 80px #051c3655;color:#17324f}.close{position:absolute;right:22px;top:18px;border:0;background:none;color:#17324f;font-size:29px;cursor:pointer}.eyebrow{color:#9b7947;font-size:11px;font-weight:700;letter-spacing:.17em}.detail h2{font:normal 38px Georgia,serif;margin:8px 0}.lead{font-size:17px;line-height:1.6}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px 30px;margin:26px 0}.grid section{border-top:1px solid #e4e8ed;padding-top:12px}.grid h3{font-size:13px;margin:0 0 6px}.grid p,.example{color:#52657b;font-size:14px;line-height:1.6}.example{padding:14px;background:#f4f6f8;border-radius:8px}.example strong{display:block;color:#17324f}.use{padding:13px 20px;background:#17324f;color:white;border:0;border-radius:8px;cursor:pointer}button:focus-visible{outline:2px solid #b68a3a;outline-offset:3px}@media(max-width:650px){.detail{padding:28px 22px}.grid{grid-template-columns:1fr}}
</style>
