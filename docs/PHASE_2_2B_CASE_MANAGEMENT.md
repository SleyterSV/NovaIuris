# MYKE — Phase 2.2B Case Management

## Scope

Adds user-facing case creation, title editing, title/description search, active and archived filters, archive/restore actions, and a case detail action area. Existing authenticated case APIs and the current `cases` schema are reused. No database migration or RLS change is required.

## Authorization and persistence

The client sends only case fields (`title`, optional `description`) when creating a case, and only `title` or `status` for updates. The backend derives the user from the validated Auth context and obtains the personal workspace from the membership/owner records. Updates are scoped by the user's workspace; requests for another user's case return the same opaque not-found response used by the existing API.

The schema supports `status` (`active` / `archived`) and `archived_at`. Archiving updates those existing fields and preserves the case, runs, artifacts, document metadata, and private Storage objects. Restoring returns the case to `active` and clears `archived_at`.

## Permanent deletion

Permanent deletion is deferred. Case documents have private Storage objects whose lifecycle is not transactionally tied to the Postgres case row. Cascading a database delete could therefore leave private objects orphaned, while removing runs/artifacts would also erase legal history. A safe delete flow requires a separately defined retention and cleanup policy; this phase does not expose a delete action or endpoint.

## Favorites

Favorites are deferred because the current case schema has no favorite field and this phase does not add schema solely for a cosmetic preference.

## Historical results

Case detail uses the existing authenticated runs and documents read APIs. Opening a completed or partial historical run links to the existing `run_id` loader; it does not start an analysis task or provider pipeline.
