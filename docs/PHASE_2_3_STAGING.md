# MYKE — Staging Environment

## Status

**HOLD — isolated hosted staging is not provisioned.** The feature branch checkpoint was pushed successfully, but no application or database deployment was performed. Existing hosted Supabase projects and the existing Vercel production project were not reused because neither was explicitly identified as MYKE staging.

## Architecture

| Component | Intended staging service | Current state |
| --- | --- | --- |
| Vue 3/Vite frontend | Vercel preview project for `frontend/` | Not created; no feature-branch deployment exists. The connected `novaiuris` project is a production-target project with a different detected framework and is not a safe staging target. |
| Python API | Render Web Service | Not created; Render CLI/MCP authentication is unavailable in this environment. |
| Database, Auth, Storage | Dedicated hosted Supabase project | Not created. No connected project was explicitly identified as MYKE staging. |
| Auth email | Real SMTP provider | Not configured; no staging SMTP credentials or sender-domain verification were provided. |
| Providers | Server-side staging/test credentials | Not configured; no staging credentials were provided. |

No staging URLs exist yet. Local services remain separate and are used only for local development and tests.

## Environment Separation

- **Local:** Supabase CLI stack, local keys, and Mailpit.
- **Staging:** must use a newly provisioned Supabase project, Vercel preview/frontend, Render backend, test identities and synthetic cases/documents, and server-side staging provider credentials.
- **Production:** not accessed or changed in this phase.

Do not connect a staging frontend or backend to an existing project until its staging ownership and isolation are explicitly confirmed.

## Required Configuration

Use the exact variable names and public/server-only split in `frontend/.env.example`, `backend/.env.example`, and `docs/PHASE_2_3_PRODUCTION_READINESS.md`.

- Vercel receives only the frontend's public `VITE_*` values: staging Supabase URL, publishable key, and HTTPS backend API URL.
- Render receives backend-only credentials and explicit `APP_ENV=staging`, HTTPS Supabase URL, allowed frontend origin, provider credentials, and persistent-volume paths required by the current backend configuration.
- Supabase Auth receives the staging Site URL, exact HTTPS redirect allow-list, email confirmation settings, and SMTP credentials through its protected project settings.
- Secrets must be set in provider secret stores, never committed or prefixed with `VITE_`.

## Auth Configuration

After the dedicated Vercel preview URL exists, set the Supabase staging Site URL to that exact HTTPS origin and add only the exact confirmation and recovery callback URLs required by the application. Keep localhost redirects only in local configuration. No hosted Auth URLs were changed.

Local Auth email continues to use Mailpit. Staging requires a real transactional SMTP provider and a sender identity authorized by that provider. No SMTP delivery is claimed here.

## Database and Storage

The local migration chain currently contains the ordered versions `20261006162217`, `20261008024534`, and `20261026023013`; `supabase migration list --local` completed successfully. Local pgTAP validation passed (32 tests, including 25 RLS assertions). No remote migration was applied.

For staging, provision a fresh dedicated project, review its migration baseline, and apply only repository migrations through the approved staging release procedure. Then verify all application tables, RLS, grants, and the private `case-documents` bucket using authenticated A/B checks. Do not use a production project or `db reset --linked`.

## Deployment Procedure

1. Confirm the organization and isolated staging Supabase project; review any project creation cost before provisioning.
2. Create a separate Vercel staging/preview project configured for the repository's `frontend/` Vite app and feature branch.
3. Create a Render staging Web Service for the Python backend with the documented Python version, frozen `uv.lock` install, production Gunicorn entry point, persistent writable volumes, and `/health` check.
4. Configure secrets independently in Supabase and Render; configure only public values in Vercel.
5. Apply reviewed migrations to the confirmed staging project; configure Auth redirect allow-list, private Storage, and SMTP.
6. Deploy backend, verify `/health` and `/ready`, exact-origin CORS, and safe logs.
7. Build/deploy frontend over HTTPS and verify it calls only the staging backend and Supabase project.
8. Run controlled Auth, account bootstrap, case, document, A/B isolation, and historical-reopen E2E with synthetic data.
9. Record evidence and monitor staging before considering a separate production release.

None of these hosted provisioning, migration, Auth, SMTP, or deployment steps was performed in this phase.

## E2E Results

- Local frontend suite: 133/133 passed.
- Local frontend production build: passed; existing large-chunk warning remains.
- Local backend suite: 396/396 passed (`uv run --frozen pytest -q` from `backend/`; running only `tests/` omits the script test and yields 395).
- Local Python compile: passed.
- Python lock validation: `uv lock --check` passed.
- Local Supabase suite: 32/32 passed; RLS: 25/25 passed.
- Hosted staging E2E: not run because the isolated project and services are not provisioned.
- Visual staging smoke: not run; no staging URL exists.

## Rollback / Redeploy

Use immutable Vercel and Render revisions for application rollback, retaining the matching environment configuration. Do not roll back schema by ad-hoc SQL. If a migration fails, stop the staging release, preserve its database state, inspect the migration, and use a reviewed recovery or forward-fix plan. No automatic down-migrations are promised.

## Current Blockers and Required Operator Inputs

1. Select/confirm the Supabase organization for a new dedicated staging project. The connected Supabase account currently has no project identified as MYKE staging. The provider's project-creation cost must be checked before proceeding.
2. Provide authenticated Render access or create the staging Web Service in the authorized Render account.
3. Provide authorized staging SMTP and provider credentials through their secret stores; no values should be sent in chat or committed.
4. Once a preview URL is available, configure exact Supabase redirect URLs and backend CORS origins.

The feature branch remote checkpoint is present at `origin/feat/phase-2-3-production-readiness`. No merge was made.

## Production Safety

- Remote Supabase modified: **NO**
- Production modified or deployed: **NO**
- Production domain configured: **NO**
- Git push: **only** `feat/phase-2-3-production-readiness`, as the requested controlled checkpoint; no other branch was pushed.
- `tmp/` modified: **NO**
