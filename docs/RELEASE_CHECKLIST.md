# Release checklist — beta controlada

- [ ] `git status` limpio, diff revisado y `git diff --check` sin errores.
- [ ] Backend unittest completo, compileall, frontend tests/build y `npm audit` revisados.
- [ ] Migración SQLite revisada sobre copia local; backup y rollback preparados.
- [ ] `APP_ENV=production`, `DEBUG=false`, secreto fuerte, claves server-side y CORS HTTPS explícito.
- [ ] Volumen persistente privado, una sola instancia activa y permisos de archivo revisados.
- [ ] Supabase Auth y refresh frontend conectados; 401/403 comprensibles.
- [ ] RLS de datos legales y RPC `match_legal_knowledge` verificados en entorno autorizado.
- [ ] `/health`, `/ready`, preflight CORS y rutas legacy 410 verificados.
- [ ] Smoke dry-run y smoke real controlado con opt-in, sin expediente real.
- [ ] Prueba A/B: cases, documents, tasks, cancel y Court reuse aislados.
- [ ] Post-deploy: leer tarea completada, simular restart y comprobar `interrupted`; revisar logs por request ID.
- [ ] Plan de rollback y política de retención/borrado definidos antes de usuarios reales.
