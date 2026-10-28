# MYKE — Phase 2.1 Final Closure

## Decision

GO — PHASE 2.1 CLOSED.

## Scope

Authentication, personal workspaces, case ownership, private documents,
persisted analysis history, cross-user isolation and historical reopening.

## Final Architecture

```text
Supabase auth.users
        ↓
profiles
        ↓
workspaces
        ↓
workspace_members
        ↓
cases
        ↓
analysis_runs
        ↓
case_artifacts
        ↓
graph snapshots
```

Private documents follow this path:

```text
authenticated user
        ↓
case/workspace authorization
        ↓
private Supabase Storage (case-documents)
        ↓
case_documents metadata
        ↓
derived/indexed local processing
```

Supabase Storage and the application tables are the durable, authoritative
records for original files, ownership metadata and completed history. SQLite
and the local corpus remain operational or derived processing components where
the existing ingestion path needs them; they are not the authority for private
original files.

```text
NEW ANALYSIS
→ pipeline/provider
→ analysis_run
→ case_artifact

HISTORICAL OPEN
→ persisted analysis_run
→ persisted case_artifact
→ render
```

Opening a historical run uses the scoped history read path and does not start
the analysis pipeline.

## Authentication E2E

Against the local Supabase Auth and Mailpit services, signup, confirmation,
profile/workspace/member bootstrap, login, refresh, resend, logout and password
recovery were exercised. The original password was rejected after reset and
the new password authenticated successfully. Bootstrap produced one profile,
one personal workspace and its owner membership per test user.

## Storage and Document Persistence

The private `case-documents` bucket and `case_documents` metadata were validated
with authenticated User A operations. Upload persisted the Storage object and
metadata with the expected workspace, case, uploader, path, MIME type, size and
SHA-256. User A downloaded the file and its bytes matched the uploaded file.
Persistence and download were confirmed again after logout and a fresh login.
Anonymous access was denied.

## User Isolation

Authenticated User B could not read User A's case or document metadata, nor
download, update or delete User A's Storage object. RLS and Storage policy tests
passed. No public bucket or broad `USING (true)` policy was found in the
reviewed migrations.

## Historical Persistence

After a fresh User A login, the existing case and its runs were listed through
the application API. Opening the persisted NovaCourt run returned its saved
court result and graph snapshot. Counts remained unchanged: two
`analysis_runs` before and after, three artifacts before and after, and zero
new tasks in the task journal. The run, task and parent run identifiers were
preserved. Reopen made zero OpenAI and zero Zep calls. User B's run and artifact
reads were denied.

## NovaCase / NovaCourt Persistence

A persisted NovaCase run was linked as the parent of the NovaCourt run using
`parent_run_id`. The NovaCourt result and graph snapshot were persisted as
server-owned artifacts and recovered from history without rebuilding the graph
or rerunning simulation.

## Security Validation

- No Supabase `service_role` or secret key reference was found in frontend
  source/public files or frontend environment files; the frontend environment
  files contain only the API base URL.
- The `case-documents` bucket is private.
- RLS is enabled on the account, workspace, case, run, artifact and document
  tables validated in the local Supabase test suite.
- The only reviewed `SECURITY DEFINER` function is the restricted Auth signup
  bootstrap trigger. It has an empty `search_path` and execution is revoked from
  `PUBLIC`, `anon` and `authenticated`; it is not an authorization bypass.
- Two-user authenticated API and Storage tests denied cross-user access.
- No credential, token or password values are recorded in this document.

## Regression Results

| Validation | Result |
| --- | ---: |
| Targeted history/frontend tests | 22/22 PASS |
| Frontend full suite | 116/116 PASS, 0 skipped |
| Frontend production build | PASS |
| Backend full suite | 390/390 PASS |
| Python compileall | PASS |
| Supabase local pgTAP suite | 32/32 PASS |
| Auth/workspace RLS tests | 25/25 PASS |

## Git State

- Branch: `feat/auth-history-foundation`
- Code baseline: `ba60f83 fix: persist case documents to private storage`
- Final commit: see repository history for the documentation-only closure commit.
- The pre-existing untracked `tmp/` directory was preserved and excluded.

## Production Safety

Remote Supabase modified: NO

Production modified: NO

Git push performed: NO

## Remaining Non-Blocking Item

Visual browser smoke was not executed because the agent environment did not
expose a controllable browser. Functional API E2E was completed against the
real local Supabase/Auth/Mailpit stack.

## Phase 2.2 Readiness

READY.
