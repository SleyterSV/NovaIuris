<script setup>
defineProps({ profile:{ type:Object, default:null }, user:{ type:Object, default:null }, loading:Boolean, error:{ type:String, default:'' } })
defineEmits(['retry'])
</script>

<template>
  <section class="account-page" aria-labelledby="account-page-title"><p class="page-kicker">ESPACIO PERSONAL</p><h1 id="account-page-title">Mi cuenta</h1><p class="account-intro">Información básica de tu perfil MYKE.</p>
    <p v-if="loading" class="profile-loading" role="status">Cargando perfil…</p>
    <div v-else-if="user" class="profile-sheet"><div class="profile-avatar" aria-hidden="true">{{ (profile?.display_name || user.email || 'M').trim().slice(0,1).toUpperCase() }}</div><dl><div><dt>Nombre</dt><dd>{{ profile?.display_name || user.user_metadata?.full_name || 'Sin nombre registrado' }}</dd></div><div><dt>Correo electrónico</dt><dd>{{ user.email || 'No disponible' }}</dd></div><div v-if="profile?.locale"><dt>Idioma</dt><dd>{{ profile.locale }}</dd></div><div v-if="profile?.created_at"><dt>Cuenta creada</dt><dd>{{ new Intl.DateTimeFormat('es-PE',{dateStyle:'long'}).format(new Date(profile.created_at)) }}</dd></div></dl></div>
    <p v-if="error" class="profile-error" role="alert">{{ error }} <button type="button" @click="$emit('retry')">Reintentar</button></p>
    <p v-else-if="!user" class="profile-error" role="alert">No fue posible cargar el perfil. <button type="button" @click="$emit('retry')">Reintentar</button></p>
  </section>
</template>

<style scoped>
.account-page{width:min(800px,100%);margin:10px auto}.page-kicker{color:#9a7c50;font-size:10px;font-weight:700;letter-spacing:.16em}.account-page h1{margin:9px 0;font:normal clamp(32px,4vw,43px) Georgia,serif;color:#15314e}.account-intro{color:#64768a;font-size:14px}.profile-sheet{display:flex;align-items:flex-start;gap:23px;margin-top:30px;padding:28px;background:#fffdfa;border:1px solid #e0e5e8;border-radius:10px}.profile-avatar{display:grid;place-items:center;flex:none;width:54px;height:54px;border-radius:50%;background:#eee5d4;color:#17324f;font:normal 23px Georgia,serif}.profile-sheet dl{display:grid;gap:21px;margin:2px 0}.profile-sheet dt{margin-bottom:5px;color:#8a9299;font-size:11px}.profile-sheet dd{margin:0;color:#263f57;font-size:14px;overflow-wrap:anywhere}.profile-error{margin-top:24px;color:#6d7882}.profile-error button{margin-left:8px;border:0;background:none;color:#284f6c;text-decoration:underline;cursor:pointer}@media(max-width:560px){.profile-sheet{padding:20px;gap:15px}.profile-avatar{width:43px;height:43px}}
.profile-loading{margin-top:24px;color:#62768a}
</style>
