import tempfile
import unittest
from pathlib import Path

from app.models.task import TaskManager, TaskStatus
from app.services.task_repository import TaskRepository, DocumentTaskRepository
from app.services.document_tasks import DocumentTaskManager


class TaskRepositoryTests(unittest.TestCase):
    def test_completed_survives_restart(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'tasks.sqlite3'
            manager = TaskManager(TaskRepository(path))
            with self.assertRaises(ValueError):
                manager.create_task('search')
            task_id = manager.create_task('search', {'owner_id': 'user-a'})
            manager.update_task(task_id, status=TaskStatus.PROCESSING)
            manager.complete_task(task_id, {'success': True})
            restored = TaskManager(TaskRepository(path)).get_task(task_id)
            self.assertEqual(restored.status, TaskStatus.COMPLETED)
            self.assertEqual(restored.result, {'success': True})

    def test_running_interrupted_and_terminal_immutable(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'tasks.sqlite3'
            manager = TaskManager(TaskRepository(path))
            task_id = manager.create_task('legal_analysis', {'owner_id': 'user-a', 'case_id': 'case-a'})
            manager.update_task(task_id, status=TaskStatus.PROCESSING)
            restored = TaskManager(TaskRepository(path))
            task = restored.get_task(task_id)
            self.assertEqual(task.status, TaskStatus.INTERRUPTED)
            self.assertEqual(task.error['code'], 'TASK_INTERRUPTED')
            restored.update_task(task_id, status=TaskStatus.COMPLETED)
            self.assertEqual(restored.get_task(task_id).status, TaskStatus.INTERRUPTED)

    def test_invalid_transition_and_active_count(self):
        manager = TaskManager()
        task_id = manager.create_task('search', {'owner_id': 'user-a'})
        manager.update_task(task_id, status=TaskStatus.COMPLETED)
        self.assertEqual(manager.active_count('user-a'), 1)
        self.assertEqual(manager.get_task(task_id).status, TaskStatus.PENDING)
        manager.cancel_task(task_id)
        self.assertEqual(manager.active_count('user-a'), 0)

    def test_document_task_interrupted_after_restart(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'tasks.sqlite3'
            TaskRepository(path)
            repo = DocumentTaskRepository(path)
            repo.save({'task_id': 'doc-task', 'owner_id': 'user-a', 'case_id': 'case-a',
                       'tool': 'documents', 'status': 'running', 'updated_at': 1.0})
            manager = DocumentTaskManager(repository=DocumentTaskRepository(path))
            self.assertEqual(manager.status('case-a', 'doc-task', 'user-a')['status'], 'interrupted')
            self.assertIsNone(manager.status('case-a', 'doc-task', 'user-b'))


if __name__ == '__main__':
    unittest.main()
