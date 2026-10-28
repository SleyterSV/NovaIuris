# MYKE — Phase 2.2 Final Closure

## Decision

GO — PHASE 2.2 CLOSED.

## Starting Point

Phase 2.1 closure commit: `cfb4642`.

Phase 2.2 was completed on `feat/phase-2-2-product-ux`:

- 2.2A: `f16c3a0` — authenticated product navigation and personal workspace.
- 2.2B: `608337a` — case management.
- 2.2C: `76bb968` — history and documents experience.

## Phase 2.2A — Product UX Foundation

Added authenticated navigation, account menu and profile, plus the real
`Mis casos` list with loading, empty, populated and safe error states. Case
selection opens a stable case detail route. Existing MYKE tools and their
analysis pipelines remain intact.

## Phase 2.2B — Case Management

Users can create and rename their cases, search by title, filter active and
archived cases, and archive or restore cases. Direct case navigation is
supported and remains scoped to the signed-in user. Permanent case deletion
and favorites remain deferred.

## Phase 2.2C — History + Documents UX

Case detail presents persisted NovaCase and NovaCourt runs and their historical
artifacts, including graph snapshots where present. Opening history reads the
stored run and artifact; it does not start a task or call providers.

Documents are listed from durable `case_documents` metadata. Upload uses the
existing private Storage pipeline and shows queued/processing states; download
uses the authorized private path. Refresh and relogin recover persisted
documents. Permanent document deletion remains deferred.

## Case Lifecycle

Supported lifecycle: create, rename, search, archive and restore. Permanent
deletion is intentionally deferred until retention, legal-history and private
Storage cleanup semantics are designed together.

## History UX

History is sourced from persisted `analysis_runs` and `case_artifacts`, ordered
with the latest activity first, and distinguishes NovaCase from NovaCourt.
Historical reopen invariants were validated:

```text
new analysis_runs: 0
new tasks: 0
OpenAI calls: 0
Zep calls: 0
```

## Document UX

`case_documents` is the durable metadata source and `case-documents` remains a
private bucket. The UI does not expose storage paths. Existing authorization
and cross-user isolation checks remain in force.

## Security and Isolation

The final source scan found no service-role or secret key references in the
frontend and no token/password logging candidates. The document bucket is
configured private; RLS is enabled on the application tables and policies bind
access to the authenticated user’s workspace membership. No universal
`USING (true)` policy or RLS disablement was introduced. The existing
`SECURITY DEFINER` function is limited to the transactional Auth bootstrap,
uses an empty `search_path`, and revokes execution from client roles; it was
not added as an authorization bypass in Phase 2.2D.

## Batch 002 Reproducibility Fix

The source PDF and its source-file SHA-256 were unchanged. The approved
manifest hash was produced with `pypdf 6.14.2`; the lock had `pypdf 6.4.2`.
Those versions differ in extraction of one line (`corpus 2` versus `corpus2`),
which changed the text hash and stable identifier. The manifest and legal
content were not rewritten. `pypdf` is now pinned to `6.14.2` in
`backend/pyproject.toml` and `backend/uv.lock`, matching the already reviewed
manifest output. The targeted test and the complete backend suite pass using
the locked environment.

Regression fix commit: `0dd0d39 fix: pin pypdf for reproducible corpus identities`.

## Regression Results

- Frontend: 131/131 passed.
- Frontend production build: passed. Vite retains its existing large-chunk warning.
- Backend: 394/394 passed in the locked virtual environment.
- Python compileall: passed.
- Supabase local database tests: 32/32 passed, including RLS 25/25.
- `uv lock --check`: passed.
- `git diff --check`: passed.

## Deferred Scope

- Permanent case deletion.
- Favorites.
- Permanent document deletion.
- Full visual browser smoke; the agent environment did not expose a controllable
  browser. Functional tests and persisted API behavior were validated separately.

## Production Safety

Remote Supabase modified: NO
Production modified: NO
Git push performed: NO

## Next Phase Readiness

READY.
