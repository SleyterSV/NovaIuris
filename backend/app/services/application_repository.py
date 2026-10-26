"""Supabase-backed application records with explicit user scoping.

This repository uses the server-only key, so every read and write includes a
workspace membership / owner check in application code as well as the database
RLS policies. Client supplied owner IDs are never accepted here.
"""
from supabase import create_client
from datetime import timezone


class ApplicationRepository:
    def __init__(self, url, service_key, client=None):
        if not url or not service_key:
            raise RuntimeError('Application persistence is not configured')
        self.client = client or create_client(url, service_key)

    @staticmethod
    def _data(response):
        return response.data or []

    def workspace_ids(self, user_id):
        rows = self._data(self.client.table('workspace_members').select('workspace_id').eq('user_id', user_id).execute())
        return list(dict.fromkeys(row['workspace_id'] for row in rows if row.get('workspace_id')))

    def profile(self, user_id):
        rows = self._data(self.client.table('profiles').select('user_id,display_name,avatar_path,locale,onboarding_completed,created_at,updated_at').eq('user_id', user_id).limit(1).execute())
        if not rows:
            return None
        return rows[0]

    def personal_workspace(self, user_id):
        rows = self._data(self.client.table('workspaces').select('id,name,workspace_type,created_at,updated_at').eq('owner_user_id', user_id).eq('workspace_type', 'personal').limit(1).execute())
        return rows[0] if rows else None

    def list_cases(self, user_id):
        workspace_ids = self.workspace_ids(user_id)
        if not workspace_ids:
            return []
        return self._data(self.client.table('cases').select('id,workspace_id,title,description,status,created_at,updated_at,archived_at').in_('workspace_id', workspace_ids).order('updated_at', desc=True).execute())

    def create_case(self, user_id, title, description=None, case_id=None):
        if case_id:
            existing = self.get_case(user_id, case_id)
            if existing:
                return existing
        rows = self._data(self.client.table('workspaces').select('id').eq('owner_user_id', user_id).eq('workspace_type', 'personal').limit(1).execute())
        if not rows:
            raise LookupError('PERSONAL_WORKSPACE_NOT_FOUND')
        workspace_id = rows[0]['id']
        payload = {
            'workspace_id': workspace_id, 'created_by': user_id,
            'title': title.strip(), 'description': description
        }
        if case_id:
            payload['id'] = case_id
        result = self._data(self.client.table('cases').insert(payload).select('id,workspace_id,title,description,status,created_at,updated_at,archived_at').execute())
        if not result:
            raise RuntimeError('CASE_CREATE_FAILED')
        return result[0]

    def get_case(self, user_id, case_id):
        workspace_ids = self.workspace_ids(user_id)
        if not workspace_ids:
            return None
        rows = self._data(self.client.table('cases').select('id,workspace_id,title,description,status,created_at,updated_at,archived_at').eq('id', case_id).in_('workspace_id', workspace_ids).limit(1).execute())
        return rows[0] if rows else None

    def update_case(self, user_id, case_id, patch):
        case = self.get_case(user_id, case_id)
        if not case:
            return None
        rows = self._data(self.client.table('cases').update(patch).eq('id', case_id).eq('workspace_id', case['workspace_id']).select('id,workspace_id,title,description,status,created_at,updated_at,archived_at').execute())
        return rows[0] if rows else None

    def list_runs(self, user_id, case_id):
        case = self.get_case(user_id, case_id)
        if not case:
            return None
        return self._data(self.client.table('analysis_runs').select('id,case_id,tool,task_id,status,parent_run_id,started_at,completed_at,created_at,metadata,error_code').eq('case_id', case_id).eq('workspace_id', case['workspace_id']).order('created_at', desc=True).execute())

    def historical_result(self, user_id, run_id):
        workspace_ids = self.workspace_ids(user_id)
        if not workspace_ids:
            return None
        runs = self._data(self.client.table('analysis_runs').select('id,workspace_id,case_id,status').eq('id', run_id).in_('workspace_id', workspace_ids).limit(1).execute())
        if not runs or runs[0]['status'] not in {'completed', 'partial'}:
            return None
        artifacts = self._data(self.client.table('case_artifacts').select('artifact_type,schema_version,content,content_text,created_at').eq('run_id', run_id).eq('workspace_id', runs[0]['workspace_id']).order('created_at').execute())
        return {'run': runs[0], 'artifacts': artifacts} if artifacts else None

    def record_task(self, task):
        """Persist a server-owned task snapshot; never accepts browser result data."""
        metadata = task.metadata or {}
        user_id = metadata.get('owner_id')
        if not user_id or user_id == 'local-development-user':
            return
        workspace = self.personal_workspace(user_id)
        if not workspace:
            return
        tool = metadata.get('tool') if task.task_type == 'legal_analysis' else task.task_type
        if tool not in {'search', 'case', 'court'}:
            return
        case_id = metadata.get('case_id')
        if case_id and not self.get_case(user_id, case_id):
            return
        def utc_iso(value):
            if value is None:
                return None
            aware = value.astimezone() if value.tzinfo is None else value
            return aware.astimezone(timezone.utc).isoformat()
        started_at = utc_iso(task.created_at)
        completed_at = utc_iso(task.finished_at)
        status = task.status.value
        if status not in {'queued', 'processing', 'completed', 'partial', 'failed', 'cancelled', 'timeout', 'interrupted'}:
            status = 'failed'
        parent_run_id = None
        parent_task_id = metadata.get('reuse_task_id') if tool == 'court' else None
        if parent_task_id:
            parents = self._data(self.client.table('analysis_runs').select('id').eq('workspace_id', workspace['id']).eq('case_id', case_id).eq('task_id', parent_task_id).limit(1).execute())
            parent_run_id = parents[0]['id'] if parents else None
        run_rows = self._data(self.client.table('analysis_runs').upsert({
            'workspace_id': workspace['id'], 'case_id': case_id, 'created_by': user_id,
            'tool': tool, 'task_id': task.task_id, 'status': status, 'parent_run_id': parent_run_id,
            'started_at': started_at, 'completed_at': completed_at,
            'metadata': {'task_type': task.task_type},
            'error_code': ((task.error or {}).get('code') if isinstance(task.error, dict) else
                           ('TASK_FAILED' if status == 'failed' else None))
        }, on_conflict='task_id').select('id').execute())
        if status not in {'completed', 'partial'} or not run_rows or not isinstance(task.result, dict):
            return
        run_id = run_rows[0]['id']
        artifact_type = {'search':'search_result', 'case':'case_result', 'court':'court_result'}[tool]
        version = {'search':'novasearch.v1', 'case':'novacase.v1', 'court':'novacourt.v1'}[tool]
        artifacts = [{'workspace_id': workspace['id'], 'case_id': case_id, 'run_id': run_id,
                      'artifact_type': artifact_type, 'schema_version': version, 'content': task.result}]
        if tool == 'court':
            result = task.result
            if isinstance(result.get('graph'), dict):
                artifacts.append({'workspace_id': workspace['id'], 'case_id': case_id, 'run_id': run_id,
                    'artifact_type':'graph_snapshot', 'schema_version':'graph.v1', 'content':result['graph']})
            if isinstance(result.get('court_report_document'), dict):
                artifacts.append({'workspace_id': workspace['id'], 'case_id': case_id, 'run_id': run_id,
                    'artifact_type':'report', 'schema_version':'novacourt-report.v1', 'content':result['court_report_document']})
        for artifact in artifacts:
            self.client.table('case_artifacts').upsert(artifact, on_conflict='run_id,artifact_type',
                ignore_duplicates=True).execute()
