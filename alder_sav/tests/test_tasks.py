import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os
from alder_sav.utils.tasks import (
    schedule_task,
    get_task,
    update_task,
    delete_task,
    list_tasks,
    run_task,
    get_task_status,
    cancel_task
)

class TestTaskManager(unittest.TestCase):
    """Tests unitaires pour la gestion des tâches asynchrones."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.task_data = {
            "name": "Envoi d'email",
            "type": "email",
            "status": "pending",
            "scheduled_for": (datetime.now() + timedelta(minutes=5)).isoformat(),
            "payload": {"to": "test@example.com", "subject": "Test", "body": "Ceci est un test."},
            "retries": 0,
            "max_retries": 3
        }
        self.task_id = None

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_schedule_and_get_task(self):
        task = schedule_task(self.task_data)
        self.task_id = task["id"]
        retrieved = get_task(self.task_id)
        self.assertEqual(retrieved["name"], "Envoi d'email")
        self.assertEqual(retrieved["type"], "email")

    def test_update_task(self):
        task = schedule_task(self.task_data)
        updated = update_task(task["id"], {"status": "running"})
        self.assertEqual(updated["status"], "running")

    def test_delete_task(self):
        task = schedule_task(self.task_data)
        delete_task(task["id"])
        with self.assertRaises(Exception):
            get_task(task["id"])

    def test_list_tasks(self):
        schedule_task(self.task_data)
        tasks = list_tasks()
        self.assertTrue(any(t["name"] == "Envoi d'email" for t in tasks))

    def test_run_and_status_task(self):
        task = schedule_task(self.task_data)
        run_task(task["id"])
        status = get_task_status(task["id"])
        self.assertIn(status, ["completed", "failed", "running", "pending"])

    def test_cancel_task(self):
        task = schedule_task(self.task_data)
        cancel_task(task["id"])
        status = get_task_status(task["id"])
        self.assertEqual(status, "cancelled")

if __name__ == '__main__':
    unittest.main() 