-- Versioned local SQLite schema for controlled, single-instance beta.
-- Schema mirrored by idempotent repository constructors on the configured volume.
-- Existing case_documents/case_chunks rows are preserved and remain unclaimed.
CREATE TABLE IF NOT EXISTS case_owners (
  case_id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_case_owners_owner ON case_owners(owner_id);
CREATE TABLE IF NOT EXISTS runtime_tasks (
  task_id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL,
  case_id TEXT,
  task_type TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_runtime_tasks_owner_status ON runtime_tasks(owner_id,status);
CREATE INDEX IF NOT EXISTS ix_runtime_tasks_case ON runtime_tasks(case_id);
CREATE INDEX IF NOT EXISTS ix_runtime_tasks_created ON runtime_tasks(created_at);
CREATE TABLE IF NOT EXISTS document_runtime_tasks (
  task_id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  status TEXT NOT NULL,
  updated_at REAL NOT NULL,
  payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_document_runtime_tasks_owner ON document_runtime_tasks(owner_id,case_id);
