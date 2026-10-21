<script setup>
const props = defineProps({ filters: { type: Object, required: true }, modulos: { type: Array, default: () => ['Todos'] } })
const emit = defineEmits(['update:filters'])
function update(key, value) { emit('update:filters', { ...props.filters, [key]: value,
  ...(key === 'solo_vigentes' ? { vigencia_explicit: true } : {}) }) }
function clear() { emit('update:filters', { modulo: 'Todos', solo_vigentes: true, vigencia_explicit: false }) }
</script>

<template>
  <aside class="search-filters" aria-label="Filtros de búsqueda">
    <h3>Filtros jurídicos</h3>
    <label for="legal-area">Área jurídica</label>
    <select id="legal-area" :value="filters.modulo || 'Todos'" @change="update('modulo', $event.target.value)">
      <option v-for="item in modulos" :key="item" :value="item">{{ item }}</option>
    </select>
    <label class="vigency"><input type="checkbox" :checked="filters.solo_vigentes !== false" @change="update('solo_vigentes', $event.target.checked)"> Solo normas vigentes</label>
    <p>Se aplican al corpus jurídico disponible.</p>
    <button type="button" :disabled="filters.modulo === 'Todos' && filters.solo_vigentes !== false && !filters.vigencia_explicit" @click="clear">Restablecer filtros</button>
  </aside>
</template>

<style scoped>
.search-filters{box-sizing:border-box;width:100%;padding:15px 16px 13px;background:#fff;border:1px solid #e0e6ed;border-radius:10px;color:#24364b}
h3{margin:0 0 11px;color:#17375e;font:600 .91rem Georgia,serif}label{display:block;margin:9px 0 6px;font-size:.74rem;font-weight:650}select{width:100%;min-height:36px;padding:0 9px;border:1px solid #ced8e3;border-radius:7px;background:#fff;color:#24364b;font:inherit}.vigency{display:flex;align-items:center;gap:8px;margin-top:12px;font-weight:500}.vigency input{margin:0;accent-color:#315c97}p{margin:10px 0 5px;font-size:.69rem;line-height:1.4;color:#738194}button{margin-top:4px;padding:2px 0;border:0;background:none;color:#315c97;font-family:inherit;font-size:.73rem;font-weight:600;cursor:pointer}button:not(:disabled):hover{text-decoration:underline}button:disabled{color:#9aa5b2;cursor:default}button:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid #315c97;outline-offset:2px}
</style>
