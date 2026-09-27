<script setup>
const props = defineProps({ filters: { type: Object, required: true }, modulos: { type: Array, default: () => ['Todos'] } })
const emit = defineEmits(['update:filters'])
function update(key, value) { emit('update:filters', { ...props.filters, [key]: value }) }
function clear() { emit('update:filters', { modulo: 'Todos', solo_vigentes: true }) }
</script>

<template>
  <aside class="search-filters" aria-label="Filtros de búsqueda">
    <h3>Filtros jurídicos</h3>
    <label for="legal-area">Área jurídica</label>
    <select id="legal-area" :value="filters.modulo || 'Todos'" @change="update('modulo', $event.target.value)">
      <option v-for="item in modulos" :key="item" :value="item">{{ item }}</option>
    </select>
    <label class="vigency"><input type="checkbox" :checked="filters.solo_vigentes !== false" @change="update('solo_vigentes', $event.target.checked)"> Solo normas vigentes</label>
    <p>Los filtros se aplican en el repositorio jurídico disponible.</p>
    <button type="button" :disabled="filters.modulo === 'Todos' && filters.solo_vigentes !== false" @click="clear">Restablecer filtros</button>
  </aside>
</template>

<style scoped>
.search-filters{box-sizing:border-box;width:100%;padding:20px;background:#fff;border:1px solid #e0e6ed;border-radius:11px;color:#24364b}
h3{margin:0 0 18px;color:#17375e;font:600 1.05rem Georgia,serif}label{display:block;margin:12px 0 7px;font-size:.78rem;font-weight:650}select{width:100%;min-height:40px;padding:0 10px;border:1px solid #ced8e3;border-radius:7px;background:#fff;color:#24364b;font:inherit}.vigency{display:flex;align-items:center;gap:8px;font-weight:500}.vigency input{accent-color:#315c97}p{font-size:.72rem;line-height:1.5;color:#738194}button{margin-top:6px;padding:0;border:0;background:none;color:#315c97;font-family:inherit;font-size:.75rem;font-weight:600;cursor:pointer}button:disabled{color:#9aa5b2;cursor:default}button:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid #315c97;outline-offset:2px}
</style>
