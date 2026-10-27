begin;
select plan(25);

insert into auth.users (id, aud, role, email, encrypted_password, email_confirmed_at)
values
  ('10000000-0000-0000-0000-000000000001', 'authenticated', 'authenticated', 'phase21-a@example.test', 'test-only', now()),
  ('20000000-0000-0000-0000-000000000002', 'authenticated', 'authenticated', 'phase21-b@example.test', 'test-only', now())
on conflict (id) do nothing;

select is((select count(*)::int from public.profiles where user_id in
  ('10000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000002')), 2, 'signup trigger creates each profile');
select is((select count(*)::int from public.workspaces where owner_user_id in
  ('10000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000002') and workspace_type = 'personal'), 2, 'signup trigger creates one personal workspace per user');
select is((select count(*)::int from public.workspace_members where user_id in
  ('10000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000002') and role = 'owner'), 2, 'signup trigger adds owner membership');
select is((select count(*)::int from storage.buckets where id = 'case-documents' and public = false), 1, 'case document bucket is private');

insert into public.cases(id, workspace_id, created_by, title)
select '90000000-0000-0000-0000-000000000009', id, owner_user_id, 'Caso de prueba A' from public.workspaces where owner_user_id = '10000000-0000-0000-0000-000000000001';
insert into public.cases(id, workspace_id, created_by, title)
select 'a0000000-0000-0000-0000-00000000000a', id, owner_user_id, 'Caso de prueba B' from public.workspaces where owner_user_id = '20000000-0000-0000-0000-000000000002';
insert into public.case_documents(id, workspace_id, case_id, uploaded_by, storage_path,
  original_filename, mime_type, size_bytes)
select '30000000-0000-0000-0000-000000000003', c.workspace_id, c.id,
  '20000000-0000-0000-0000-000000000002',
  'workspaces/' || c.workspace_id::text || '/cases/' || c.id::text || '/30000000-0000-0000-0000-000000000003/document.pdf',
  'documento.pdf', 'application/pdf', 1
from public.cases c where c.title = 'Caso de prueba B';
insert into public.case_documents(id, workspace_id, case_id, uploaded_by, storage_path,
  original_filename, mime_type, size_bytes)
select '60000000-0000-0000-0000-000000000006', c.workspace_id, c.id,
  '10000000-0000-0000-0000-000000000001',
  'workspaces/' || c.workspace_id::text || '/cases/' || c.id::text || '/60000000-0000-0000-0000-000000000006/document.pdf',
  'documento-a.pdf', 'application/pdf', 1
from public.cases c where c.title = 'Caso de prueba A';
insert into public.analysis_runs(id, workspace_id, case_id, created_by, tool, task_id, status)
select '70000000-0000-0000-0000-000000000007', c.workspace_id, c.id, c.created_by,
  'case', 'test-run-a', 'completed' from public.cases c where c.title = 'Caso de prueba A';
insert into public.analysis_runs(id, workspace_id, case_id, created_by, tool, task_id, status)
select '80000000-0000-0000-0000-000000000008', c.workspace_id, c.id, c.created_by,
  'case', 'test-run-b', 'completed' from public.cases c where c.title = 'Caso de prueba B';
insert into public.case_artifacts(workspace_id, case_id, run_id, artifact_type, schema_version, content)
select workspace_id, case_id, id, 'case_result', 'novacase.v1', '{"fixture":true}'::jsonb
from public.analysis_runs where id = '70000000-0000-0000-0000-000000000007';
insert into public.case_artifacts(workspace_id, case_id, run_id, artifact_type, schema_version, content)
select workspace_id, case_id, id, 'case_result', 'novacase.v1', '{"fixture":true}'::jsonb
from public.analysis_runs where id = '80000000-0000-0000-0000-000000000008';
insert into storage.objects(bucket_id, name)
select 'case-documents', storage_path
from public.case_documents
where id in (
  '30000000-0000-0000-0000-000000000003',
  '60000000-0000-0000-0000-000000000006'
);

set local role authenticated;
select set_config('request.jwt.claim.sub', '10000000-0000-0000-0000-000000000001', true);
select is((select count(*)::int from public.cases), 1, 'user A only sees their case');
select is((select count(*)::int from public.cases where title = 'Caso de prueba B'), 0, 'user A cannot read user B case by title');
select is((select count(*)::int from public.workspaces), 1, 'user A only sees their workspace');
select is((select count(*)::int from public.workspace_members), 1, 'user A only sees their membership');
select is((select count(*)::int from public.profiles), 1, 'user A only sees their profile');
select is((select count(*)::int from public.cases where id = 'a0000000-0000-0000-0000-00000000000a'), 0, 'user A cannot fetch user B case by id');
select is((select count(*)::int from public.profiles where user_id = '20000000-0000-0000-0000-000000000002'), 0, 'user A cannot fetch user B profile by id');
select is((select count(*)::int from public.analysis_runs), 1, 'user A sees their run');
select is((select count(*)::int from public.analysis_runs where id = '80000000-0000-0000-0000-000000000008'), 0, 'user A cannot read user B run by id');
select is((select count(*)::int from public.case_artifacts), 1, 'user A sees their artifact');
select is((select count(*)::int from public.case_artifacts where run_id = '80000000-0000-0000-0000-000000000008'), 0, 'user A cannot read user B artifact by run id');
select is((select count(*)::int from public.case_documents), 1, 'user A sees their document metadata');
select is((select count(*)::int from public.case_documents where id = '30000000-0000-0000-0000-000000000003'), 0, 'user A cannot read user B document metadata by id');
select is((select count(*)::int from storage.objects where bucket_id = 'case-documents'), 1, 'user A only lists their private object');
select lives_ok($$insert into storage.objects(bucket_id, name)
  select 'case-documents', 'workspaces/' || c.workspace_id::text || '/cases/' || c.id::text ||
    '/40000000-0000-0000-0000-000000000004/upload.pdf'
  from public.cases c where c.title = 'Caso de prueba A'$$,
  'user A can upload under their own case path');
select throws_ok($$insert into storage.objects(bucket_id, name) values (
  'case-documents',
  'workspaces/00000000-0000-0000-0000-000000000000/cases/a0000000-0000-0000-0000-00000000000a/50000000-0000-0000-0000-000000000005/upload.pdf')$$,
  '42501', 'new row violates row-level security policy for table "objects"',
  'user A cannot upload under user B case path');
select set_config('request.jwt.claim.sub', '20000000-0000-0000-0000-000000000002', true);
select is((select count(*)::int from public.cases), 1, 'user B sees their case');
select is((select count(*)::int from public.analysis_runs), 1, 'user B sees their run');
select is((select count(*)::int from public.case_artifacts), 1, 'user B sees their artifact');
select is((select count(*)::int from public.case_documents), 1, 'user B sees their document metadata');
select is((select count(*)::int from storage.objects where bucket_id = 'case-documents'), 1, 'user B only lists their private object');

reset role;
select * from finish();
rollback;
