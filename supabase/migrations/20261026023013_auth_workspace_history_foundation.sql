-- Auth-linked personal workspace and durable case/history foundation.
-- Authorization decisions never use user-editable user_metadata.

create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  avatar_path text,
  locale text not null default 'es' check (locale in ('es', 'en')),
  onboarding_completed boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.workspaces (
  id uuid primary key default gen_random_uuid(),
  name text not null check (length(trim(name)) between 1 and 120),
  workspace_type text not null default 'personal' check (workspace_type in ('personal', 'organization')),
  owner_user_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create unique index if not exists ux_workspaces_personal_owner
  on public.workspaces(owner_user_id) where workspace_type = 'personal';

create table if not exists public.workspace_members (
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('owner', 'admin', 'member')),
  created_at timestamptz not null default now(),
  primary key (workspace_id, user_id)
);
create index if not exists ix_workspace_members_user on public.workspace_members(user_id);

create table if not exists public.cases (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  created_by uuid not null references auth.users(id),
  title text not null check (length(trim(title)) between 1 and 240),
  description text,
  status text not null default 'active' check (status in ('active', 'archived')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  archived_at timestamptz,
  unique (workspace_id, id)
);
create index if not exists ix_cases_workspace_updated on public.cases(workspace_id, updated_at desc);
create index if not exists ix_cases_creator on public.cases(created_by);

create table if not exists public.analysis_runs (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  case_id uuid references public.cases(id) on delete set null,
  created_by uuid not null references auth.users(id),
  tool text not null check (tool in ('search', 'case', 'court')),
  task_id text,
  status text not null check (status in ('pending', 'queued', 'processing', 'completed', 'partial', 'failed', 'cancelled', 'timeout', 'interrupted')),
  parent_run_id uuid references public.analysis_runs(id) on delete set null,
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb,
  error_code text,
  unique(task_id),
  unique (workspace_id, id),
  foreign key (workspace_id, case_id) references public.cases(workspace_id, id),
  foreign key (workspace_id, parent_run_id) references public.analysis_runs(workspace_id, id)
);
create index if not exists ix_analysis_runs_workspace_created on public.analysis_runs(workspace_id, created_at desc);
create index if not exists ix_analysis_runs_case_created on public.analysis_runs(case_id, created_at desc);
create index if not exists ix_analysis_runs_task on public.analysis_runs(task_id);

create table if not exists public.case_artifacts (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  case_id uuid references public.cases(id) on delete set null,
  run_id uuid not null references public.analysis_runs(id) on delete cascade,
  artifact_type text not null check (artifact_type in ('search_result', 'case_result', 'court_result', 'graph_snapshot', 'report')),
  schema_version text not null,
  content jsonb,
  content_text text,
  created_at timestamptz not null default now(),
  check (content is not null or content_text is not null),
  foreign key (workspace_id, case_id) references public.cases(workspace_id, id),
  foreign key (workspace_id, run_id) references public.analysis_runs(workspace_id, id)
);
create index if not exists ix_case_artifacts_run on public.case_artifacts(run_id);
create index if not exists ix_case_artifacts_case on public.case_artifacts(case_id);
create unique index if not exists ux_case_artifact_run_type on public.case_artifacts(run_id, artifact_type);

create table if not exists public.case_documents (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  case_id uuid not null references public.cases(id) on delete cascade,
  uploaded_by uuid not null references auth.users(id),
  storage_bucket text not null default 'case-documents' check (storage_bucket = 'case-documents'),
  storage_path text not null unique,
  original_filename text not null,
  mime_type text not null,
  size_bytes bigint not null check (size_bytes > 0),
  sha256 text,
  processing_status text not null default 'uploaded' check (processing_status in ('uploaded', 'processing', 'ready', 'failed')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  foreign key (workspace_id, case_id) references public.cases(workspace_id, id)
);
create index if not exists ix_case_documents_case on public.case_documents(case_id);
create index if not exists ix_case_documents_workspace on public.case_documents(workspace_id);

-- Signup bootstrap is transactional and idempotent. Security definer is limited to this
-- auth.users trigger because Auth's insert role cannot write application tables directly.
create or replace function public.bootstrap_auth_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_workspace_id uuid;
  display_name text;
begin
  display_name := left(nullif(trim(coalesce(new.raw_user_meta_data ->> 'full_name', new.raw_user_meta_data ->> 'name', '')), ''), 120);
  insert into public.profiles(user_id, display_name)
    values (new.id, display_name)
    on conflict (user_id) do nothing;
  insert into public.workspaces(name, workspace_type, owner_user_id)
    values (left(coalesce(display_name, split_part(coalesce(new.email, 'Mi espacio'), '@', 1)), 112) || ' - MYKE', 'personal', new.id)
    on conflict (owner_user_id) where workspace_type = 'personal' do nothing;
  select id into v_workspace_id from public.workspaces
    where owner_user_id = new.id and workspace_type = 'personal';
  insert into public.workspace_members(workspace_id, user_id, role)
    values (v_workspace_id, new.id, 'owner')
    on conflict (workspace_id, user_id) do nothing;
  return new;
end;
$$;
revoke all on function public.bootstrap_auth_user() from public, anon, authenticated;
drop trigger if exists on_auth_user_bootstrap on auth.users;
create trigger on_auth_user_bootstrap after insert on auth.users
  for each row execute function public.bootstrap_auth_user();

-- Existing Auth users receive the same idempotent bootstrap during migration.
insert into public.profiles(user_id, display_name)
select id, left(nullif(trim(coalesce(raw_user_meta_data ->> 'full_name', raw_user_meta_data ->> 'name', '')), ''), 120)
from auth.users where true on conflict (user_id) do nothing;
insert into public.workspaces(name, workspace_type, owner_user_id)
select left(coalesce(nullif(trim(coalesce(raw_user_meta_data ->> 'full_name', raw_user_meta_data ->> 'name', '')), ''),
  split_part(coalesce(email, 'Mi espacio'), '@', 1)), 112) || ' - MYKE', 'personal', id
from auth.users where true on conflict (owner_user_id) where workspace_type = 'personal' do nothing;
insert into public.workspace_members(workspace_id, user_id, role)
select w.id, u.id, 'owner' from auth.users u join public.workspaces w on w.owner_user_id = u.id
where w.workspace_type = 'personal' on conflict (workspace_id, user_id) do nothing;

create or replace function public.touch_updated_at()
returns trigger language plpgsql set search_path = '' as $$
begin new.updated_at = now(); return new; end;
$$;
revoke all on function public.touch_updated_at() from public, anon, authenticated;
create trigger profiles_touch_updated_at before update on public.profiles
  for each row execute function public.touch_updated_at();
create trigger workspaces_touch_updated_at before update on public.workspaces
  for each row execute function public.touch_updated_at();
create trigger cases_touch_updated_at before update on public.cases
  for each row execute function public.touch_updated_at();
create trigger documents_touch_updated_at before update on public.case_documents
  for each row execute function public.touch_updated_at();

alter table public.profiles enable row level security;
alter table public.workspaces enable row level security;
alter table public.workspace_members enable row level security;
alter table public.cases enable row level security;
alter table public.analysis_runs enable row level security;
alter table public.case_artifacts enable row level security;
alter table public.case_documents enable row level security;

revoke all on public.profiles, public.workspaces, public.workspace_members, public.cases,
  public.analysis_runs, public.case_artifacts, public.case_documents from anon;
grant select on public.profiles to authenticated;
grant update (display_name, avatar_path, locale, onboarding_completed) on public.profiles to authenticated;
grant select on public.workspaces, public.workspace_members, public.analysis_runs,
  public.case_artifacts, public.case_documents to authenticated;
grant select on public.cases to authenticated;
grant insert (workspace_id, created_by, title, description) on public.cases to authenticated;
grant update (title, description, status, archived_at) on public.cases to authenticated;

create policy profiles_select_self on public.profiles for select to authenticated using ((select auth.uid()) = user_id);
create policy profiles_update_self on public.profiles for update to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy workspaces_select_member on public.workspaces for select to authenticated
  using (owner_user_id = (select auth.uid()) or exists (
    select 1 from public.workspace_members wm where wm.workspace_id = id and wm.user_id = (select auth.uid())));
create policy members_select_self on public.workspace_members for select to authenticated
  using (user_id = (select auth.uid()));
create policy cases_select_member on public.cases for select to authenticated using (exists (
  select 1 from public.workspace_members wm where wm.workspace_id = cases.workspace_id and wm.user_id = (select auth.uid())));
create policy cases_insert_member on public.cases for insert to authenticated with check (
  created_by = (select auth.uid()) and exists (select 1 from public.workspace_members wm
    where wm.workspace_id = cases.workspace_id and wm.user_id = (select auth.uid()) and wm.role in ('owner', 'admin', 'member')));
create policy cases_update_member on public.cases for update to authenticated
  using (exists (select 1 from public.workspace_members wm where wm.workspace_id = cases.workspace_id and wm.user_id = (select auth.uid())))
  with check (exists (select 1 from public.workspace_members wm where wm.workspace_id = cases.workspace_id and wm.user_id = (select auth.uid())));
create policy runs_select_member on public.analysis_runs for select to authenticated using (exists (
  select 1 from public.workspace_members wm where wm.workspace_id = analysis_runs.workspace_id and wm.user_id = (select auth.uid())));
create policy artifacts_select_member on public.case_artifacts for select to authenticated using (exists (
  select 1 from public.workspace_members wm where wm.workspace_id = case_artifacts.workspace_id and wm.user_id = (select auth.uid())));
create policy documents_select_member on public.case_documents for select to authenticated using (exists (
  select 1 from public.workspace_members wm where wm.workspace_id = case_documents.workspace_id and wm.user_id = (select auth.uid())));

-- Only the trusted backend records runs, immutable artifacts and document metadata.
revoke insert, update, delete on public.analysis_runs, public.case_artifacts, public.case_documents from authenticated;

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('case-documents', 'case-documents', false, 52428800,
  array['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown'])
on conflict (id) do update set public = false, file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;
revoke all on storage.objects from anon, authenticated;
grant select, insert on storage.objects to authenticated;

create policy case_documents_read_member on storage.objects for select to authenticated using (
  bucket_id = 'case-documents' and exists (
    select 1 from public.case_documents d join public.workspace_members wm on wm.workspace_id = d.workspace_id
    where d.storage_path = name and wm.user_id = (select auth.uid())));
create policy case_documents_insert_member on storage.objects for insert to authenticated with check (
  bucket_id = 'case-documents' and exists (
    select 1 from public.cases c join public.workspace_members wm on wm.workspace_id = c.workspace_id
    where c.id::text = (storage.foldername(name))[4] and c.workspace_id::text = (storage.foldername(name))[2]
      and wm.user_id = (select auth.uid()) and (storage.foldername(name))[1] = 'workspaces'
      and (storage.foldername(name))[3] = 'cases'));
