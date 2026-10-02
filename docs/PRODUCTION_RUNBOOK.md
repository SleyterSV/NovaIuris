# Runbook — beta controlada

1. Preparar una única instancia backend con volumen privado y persistente para `CASE_CORPUS_DB_PATH` y `TASK_DB_PATH`. Mantener backup cifrado y acceso de sistema mínimo. No arrancar dos workers sobre el mismo diario de tareas.
2. Configurar `APP_ENV=production`, `SECRET_KEY` fuerte, `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_KEY`, `OPENAI_API_KEY`, `LLM_API_KEY`, `ZEP_API_KEY`, `CORS_ALLOWED_ORIGINS` HTTPS y límites del `.env.example`. Nunca poner claves privadas en variables `VITE_*`.
3. Arrancar; un error de validación impide servir tráfico. Comprobar `/health` (proceso) y `/ready` (almacenamiento local). Ninguno llama OpenAI/Zep.
4. Ejecutar `python scripts/smoke_providers.py --dry-run` desde `backend`. Para smoke real, en entorno controlado con opt-in explícito, usar `RUN_PROVIDER_SMOKE=1` y `APP_ENV=production`; puede generar costo. Solo usa texto sintético.
5. Tras despliegue: verificar 401 sin token, documentos y tareas entre dos usuarios, CORS permitido/no permitido, legacy 410, creación y lectura de tarea, y logs por `request_id`. Confirmar políticas RLS y firma RPC en Supabase autorizado antes de abrir beta.
6. Si falla provider: buscar `request_id`, `error_code` y tipo de error; revisar rate limit/timeout y smoke controlado. Si tarea queda activa después de restart, el próximo arranque debe marcar `interrupted`. Si no ocurre, retirar instancia del tráfico.
7. Rollback: retirar tráfico, volver a versión anterior solo con backup compatible del volumen. No borrar SQLite ni expedientes. No ejecutar migración Supabase o purga automática durante rollback.

La retención de corpus, resultados y tareas requiere una operación explícita aprobada; staging temporal se elimina por prefijo/edad y se limpia tras la ingesta. El borrado completo de caso/usuario aún no existe.
