# MYKE — Production Readiness

## Scope and status

Phase 2.3A prepares the existing frontend, API, Supabase project definition, and provider configuration for a controlled staging deployment. It does not deploy or change any hosted project. Local configuration and automated checks are the only validated environment in this phase.

## Architecture

| Component | Runtime | Local endpoint | External dependencies |
| --- | --- | --- | --- |
| Vue 3 frontend | Static Vite build; Vite dev server locally | `http://localhost:3000` | MYKE API, Supabase Auth/REST/Storage |
| Python API | Flask application factory; Gunicorn for Linux hosting | `http://localhost:5001` | Supabase, legal PostgreSQL, OpenAI-compatible LLM, Zep |
| Supabase | PostgreSQL, Auth, PostgREST, Storage, Kong | API `http://127.0.0.1:54321`; DB `127.0.0.1:54322` | Docker locally; SMTP in hosted environments |
| Email | Supabase Auth email | Local Inbucket/Mailpit at `http://127.0.0.1:54324` | Real SMTP for hosted staging/production |
| Legal corpus | PostgreSQL V2 | configured by `MYKE_LEGAL_DATABASE_URL` | pgvector/schema and published corpus |

The repository root Dockerfile and `npm run dev` are development workflows. They are not production deployment artifacts.

## Environments

- **Local:** `APP_ENV=development`; Supabase CLI local stack; Mailpit captures Auth emails. Use only local public keys in the browser. Local development identity remains disabled unless deliberately enabled for a local-only workflow.
- **Tests:** `APP_ENV=test`; deterministic test doubles and isolated test databases are used by the suites.
- **Staging:** `APP_ENV=staging`; same strict runtime/security checks as production, explicit HTTPS Supabase URL and browser origins, V2 legal knowledge, persistent external task/corpus volumes, and real staging secrets. Staging must use an isolated Supabase project and test accounts.
- **Production:** `APP_ENV=production`; same strict checks, production-specific keys/origins/data, private storage, backups, and operational monitoring. This phase did not configure or deploy it.

Strict environments fail app initialization for missing/unsafe critical configuration. `/health` reports process liveness; `/ready` reports availability of the application repository, Supabase Auth and Storage, legal PostgreSQL, and local persistent ownership database. Readiness returns a generic unavailable response and logs only a safe error type.

## Environment variables

Copy the appropriate example and supply values through a secret manager or private local environment file. `.env.example` files contain placeholders only.

Configuration classes are:

- **PUBLIC:** the three browser `VITE_*` values; the Supabase publishable key is public and must be paired with RLS.
- **SERVER_SECRET:** `SECRET_KEY`, backend Supabase credentials, legal database DSN, OpenAI/LLM/Zep credentials, and hosted SMTP credentials.
- **LOCAL_ONLY:** localhost URLs, Mailpit, and local volume/database paths. Do not carry these defaults into hosted environments.
- **STAGING / PRODUCTION:** explicit environment selection, HTTPS Supabase URL, HTTPS CORS origin allow-list, secret-store values, and external persistent writable paths.

### Frontend — public values only

`frontend/.env.example` documents:

- `VITE_API_BASE_URL`: browser-visible API origin (or empty when a same-origin proxy is configured).
- `VITE_SUPABASE_URL`: Supabase project URL.
- `VITE_SUPABASE_PUBLISHABLE_KEY`: publishable/legacy anon key intended for browser use, protected by RLS.

Never define `VITE_*` values for database credentials, service-role/secret keys, OpenAI, Zep, or SMTP. Vite embeds `VITE_*` variables into browser assets.

### Backend — server-only values

`backend/.env.example` lists exact runtime names:

- Environment/security: `APP_ENV`, `SECRET_KEY`, `LOCAL_DEV_AUTH_ENABLED`, `FLASK_DEBUG`, `CORS_ALLOWED_ORIGINS`, `RATE_LIMIT_ENABLED`.
- Supabase: `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_KEY`, `APP_SUPABASE_SERVICE_ROLE_KEY`.
- Legal data: `LEGAL_KNOWLEDGE_VERSION`, `MYKE_LEGAL_DATABASE_URL`.
- Providers: `OPENAI_API_KEY`, `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL_NAME`, `ZEP_API_KEY`.
- Runtime: `AUTH_TIMEOUT_SECONDS`, `CASE_CORPUS_DB_PATH`, `TASK_DB_PATH`.

`SUPABASE_KEY` and `APP_SUPABASE_SERVICE_ROLE_KEY` are backend-only credentials used by server integrations; privileged operations must continue enforcing resource ownership in application code. Use distinct least-privilege project credentials where the integration permits. `OPENAI_API_KEY`, `LLM_API_KEY`, and `ZEP_API_KEY` remain server-side.

### Supabase and email

Supabase CLI reads its project configuration from `supabase/config.toml`. Local Auth redirects point to Vite's current port 3000. Before a hosted deployment, set the hosted project's Site URL and allow-list only the exact staging or production callback URLs required by MYKE; do not allow arbitrary external redirects. Hosted redirect settings are managed in the Supabase project configuration and were not changed in this phase. See [Supabase redirect URL guidance](https://supabase.com/docs/guides/auth/redirect-urls).

Local email uses the Supabase local mail catcher. For hosted Auth, configure SMTP at the Supabase project level using `MYKE_AUTH_SMTP_HOST`, `MYKE_AUTH_SMTP_PORT`, `MYKE_AUTH_SMTP_USER`, `MYKE_AUTH_SMTP_PASSWORD`, `MYKE_AUTH_SMTP_FROM_ADDRESS`, and sender name `MYKE Legal Intelligence`. The commented `[auth.email.smtp]` example in `supabase/config.toml` uses CLI environment substitution; keep SMTP values in a secret store, never Git or frontend variables. Configure and verify sender-domain DNS and test delivery in staging before production. See [Supabase custom SMTP guidance](https://supabase.com/docs/guides/auth/auth-smtp).

## Local development

1. Install root and frontend Node dependencies with `npm ci` in the root and `frontend` directories.
2. Install backend dependencies with `cd backend; uv sync --frozen`.
3. Copy the example files to private environment files and set local Supabase values from `supabase status`.
4. Start the local Supabase stack with the repository's normal local workflow.
5. Start the development app with root `npm run dev`.

Do not use actual hosted service secrets in local example files. Keep `.env`, `.env.local`, and other environment files untracked.

## Staging and production commands

### Frontend

From `frontend`, reproducible build commands are `npm ci` and `npm run build`. Deploy the resulting `dist/` directory to a static host that supports SPA history fallback. Configure only the public `VITE_*` values at build time. The browser API URL must target the corresponding backend.

### Backend

On a Linux host, from the repository root:

```sh
cd backend
uv sync --frozen --no-dev
uv run --frozen --no-dev gunicorn --chdir . --bind 0.0.0.0:${PORT} --workers 2 --timeout 90 'app:create_app()'
```

Gunicorn is pinned in `backend/pyproject.toml` and `backend/uv.lock`. `backend/run.py` is explicitly development-only and refuses staging/production. Provision writable persistent volumes outside the checkout for the case corpus and task journal and point `CASE_CORPUS_DB_PATH` / `TASK_DB_PATH` to them. Confirm worker count and resource budgets against the selected host before rollout; this phase does not claim multi-instance job safety.

## Supabase migration strategy

Versioned migrations under `supabase/migrations/` are the source of truth. Their order is timestamped and local migration status can be inspected with `supabase migration list --local`. Validate migrations and RLS against a disposable local/test database before staging. This phase does not run a remote push and does not destroy the existing local database to demonstrate a clean reset. The known applied local migration sequence is recorded in the Phase 2.3A validation report; any clean-room reproduction gap remains a staging gate.

For a future staging rollout, provision a separate Supabase project, review its baseline and migration history, take a recoverable backup where applicable, and apply only reviewed migrations through the approved staging release procedure. Never point a local reset/test command at a linked hosted project.

## Deployment order

1. Provision isolated staging infrastructure and persistent volumes.
2. Configure backend and Supabase secrets in their secret managers.
3. Apply verified migrations to staging using the controlled release procedure.
4. Configure Auth Site URL, exact redirect allow-list, email confirmations, and private Storage policies.
5. Configure and verify staging SMTP and sender identity.
6. Deploy backend and verify `/health` and `/ready`.
7. Build and deploy frontend with public staging values and SPA fallback.
8. Run authenticated staging smoke tests, including A/B isolation, documents, and history.
9. Observe errors, readiness, latency, provider failures, and email delivery.
10. Consider production only after the staging evidence is reviewed.

None of these remote steps was performed in Phase 2.3A.

## Rollback considerations

- **Frontend:** redeploy the preceding immutable static build and restore its matching public API URL.
- **Backend:** redeploy the preceding application image/revision with compatible settings. Keep task/corpus volumes mounted; do not replace them during rollback.
- **Migration failure:** stop the release, preserve database state, inspect the migration and take a recovery decision with an operator. No automatic down-migrations are promised; schema changes may be irreversible.
- **Provider/email failure:** use safe user-facing failure states and repair or roll back provider configuration. Do not expose credentials or replay private document contents in diagnostics.

## Security and readiness notes

- CORS must contain explicit HTTPS origins in staging/production; wildcard origins are rejected.
- Strict runtime config requires HTTPS Supabase, explicit origins, server credentials, V2 legal data configuration, rate limiting, safe runtime bounds, and external persistent SQLite paths.
- `/ready` checks critical data services without returning connection details; `/health` is process liveness only.
- Keep RLS enabled and the `case-documents` bucket private. Do not broaden policies to make deployments pass.
- Frontend environment examples contain public-only variables. Secrets belong in backend/Supabase secret stores.
- SMTP settings are a readiness model only; no real provider or domain was configured or delivery-tested in this phase.

## Deferred scope

- Permanent case deletion.
- Permanent document deletion.
- Favorites.
- Full browser visual smoke.
- Staging or production deployment.
- Distributed workers, crash-safe active-job continuation, multi-instance task processing, and autoscaling.

## Production safety

Remote Supabase modified: **NO**
Production modified: **NO**
Git push performed: **NO**

## Validation evidence

Final local frontend, backend, Supabase/RLS, dependency-lock, and build results are recorded in the Phase 2.3A final report and commit. This document describes preparation, not a claim that staging or production has been deployed.
