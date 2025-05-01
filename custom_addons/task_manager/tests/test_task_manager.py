from odoo.tests.common import TransactionCase, tagged
from datetime import datetime, timedelta
from odoo.exceptions import AccessError
from unittest.mock import patch

class TestTaskLogic(TransactionCase):

    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, mail_notrack=True))
        self.user = self.env.ref('base.user_admin')

    def test_task_creation_and_days_left(self):
        task = self.env['task.manager'].create({
            'name': 'Test Task',
            'description': 'Some description',
            'assigned_to': self.user.id,
            'due_date': datetime.now() + timedelta(days=5),
            'priority': 'high',
            'status': 'new'
        })
        self.assertEqual(task.name, 'Test Task')
        self.assertEqual(task.status, 'new')
        self.assertEqual(task.priority, 'high')

    def test_task_defaults(self):
        task = self.env['task.manager'].create({
            'name': 'Test Default Values',
        })
        self.assertEqual(task.priority, 'medium')
        self.assertEqual(task.status, 'new')

    def test_get_days_left(self):
        task = self.env['task.manager'].create({
            'name': 'Deadline Test Task',
            'due_date': datetime.now() + timedelta(days=4),
        })
        days_left = task.get_days_left()
        self.assertGreaterEqual(days_left, 3)
        self.assertLessEqual(days_left, 5)


class TestTaskAccess(TransactionCase):
    def setUp(self):
        super().setUp()
        self.model = self.env['task.manager']
        self.user_with_access = self.env.ref('base.user_demo')
        self.user_no_access = self.env['res.users'].create({
            'name': 'No Access User',
            'login': 'noaccessuser',
            'groups_id': [(6, 0, [])],
        })

        self.task = self.model.create({
            'name': 'Secure Task',
            'description': 'Confidential',
        })

    def test_user_with_access_can_create(self):
        env = self.env(user=self.user_with_access)
        record = env['task.manager'].create({'name': 'With Access'})
        self.assertEqual(record.name, 'With Access')

    def test_user_without_access_cannot_create(self):
        env = self.env(user=self.user_no_access)
        with self.assertRaises(AccessError):
            env['task.manager'].create({'name': 'No Access'})

    def test_user_with_access_can_read_and_write(self):
        env = self.env(user=self.user_with_access)
        task = env['task.manager'].browse(self.task.id)
        self.assertEqual(task.name, 'Secure Task')  # read

        task.name = 'Updated by demo'
        self.assertEqual(task.name, 'Updated by demo')  # write

    def test_user_without_access_cannot_read(self):
        env = self.env(user=self.user_no_access)
        task = env['task.manager'].browse(self.task.id)
        with self.assertRaises(AccessError):
            _ = task.name

    def test_user_without_access_cannot_write(self):
        env = self.env(user=self.user_no_access)
        task = env['task.manager'].browse(self.task.id)
        with self.assertRaises(AccessError):
            task.name = 'You Shall Not Pass'


@tagged('post_install', '-at_install')
class TestTaskCron(TransactionCase):

    def setUp(self):
        super().setUp()
        self.task_model = self.env['task.manager']
        self.user = self.env['res.users'].create({
            'name': 'Cron Test User',
            'login': 'cron_user',
            'email': 'cron.user@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

        self.task = self.task_model.create({
            'name': 'Cron Reminder Task',
            'assigned_to': self.user.id,
            'due_date': datetime.now() + timedelta(days=3),
        })

    def test_cron_creates_email(self):
        with patch('odoo.addons.mail.models.mail_mail.MailMail.send') as mock_send:
            self.task_model.cron_notify_upcoming_tasks()
            self.assertTrue(mock_send.called)


@tagged('post_install', '-at_install')
class TestTaskReport(TransactionCase):

    def setUp(self):
        super().setUp()
        self.task_model = self.env['task.manager']
        self.task1 = self.task_model.create({
            'name': 'Report Task 1',
        })
        self.task2 = self.task_model.create({
            'name': 'Report Task 2',
        })

    def test_make_tasks_report(self):
        with patch('odoo.addons.task_manager.models.task_manager.TaskManager.make_tasks_report') as mock_report:
            self.task_model.make_tasks_report()
            self.assertTrue(mock_report.called)

    def test_report_returns_action(self):
        action = self.task_model.make_tasks_report()
        self.assertIsInstance(action, dict)
        self.assertIn('type', action)
        self.assertEqual(action['type'], 'ir.actions.act_window')