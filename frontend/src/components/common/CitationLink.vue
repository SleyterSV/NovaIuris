<template>
  <button class="citation-link" type="button" :aria-label="`Abrir fuente ${label}`" @click="$emit('select', citation)">
    {{ label }}
  </button>
</template>

<script setup>
defineProps({ citation: { type: Object, required: true }, label: { type: String, required: true } })
defineEmits(['select'])
</script>

<style scoped>
.citation-link{border:0;background:#edf3f8;color:#173b61;border-radius:4px;padding:1px 5px;margin:0 2px;font-family:inherit;font-size:.78em;font-weight:600;line-height:1.4;cursor:pointer;vertical-align:baseline}
.citation-link:hover{background:#dce8f2}.citation-link:focus-visible{outline:2px solid #b68a3a;outline-offset:2px}
</style>
