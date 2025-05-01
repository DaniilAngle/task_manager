from odoo import models, fields, api
from odoo.tools import format_datetime
from datetime import timedelta, datetime
import logging

_logger = logging.getLogger(__name__)

class TaskManager(models.Model):
    _name = 'task.manager'
    _description = 'Task Manager'
    _inherit = ['mail.thread']

    # Set up the fields for the task manager
    name = fields.Char(string="Task Name", required=True)
    description = fields.Text(string="Description")
    assigned_to = fields.Many2one('res.users', string="Assigned To")
    due_date = fields.Datetime(string="Due Date")
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Priority", default='medium')
    status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string="Status", default='new')
    # Might be sensible to have additional Days Left as a computed field to emphasize remaining days - friendlier UI
    # Not leaving it here since it is out of scope, but it was useful for the testing

    def get_days_left(self):
        """
        Compute the number of days left until the due date.
        :return: Optional[int|None] Number of days until due date or None if due date is not set.
        """
        if self.due_date:
            today = datetime.now().date()
            due = self.due_date.date()
            return (due - today).days
        return None

    @api.model
    def cron_notify_upcoming_tasks(self):
        """
        Method called by the cron job to notify users about tasks that are due in 3 days.
        It searches for tasks that are due in 3 days and have not been completed.
        It sends an email to the user assigned to the task.
        """

        tasks = self.search([
            ('due_date', '!=', False),
            ('assigned_to', '!=', False),
            ('status', '!=', 'completed'),
        ])
        # Notify users about their tasks
        # I believe this needs SMTP configuration to work and actually send emails. In my consideration this is
        # outside the scope of test task


        for task in tasks:
            days_left = task.get_days_left()
            if days_left == 3 and task.assigned_to.email:
                # Could be a good idea to use a template for the email body, but for sake of simplicity this is string
                body = f"""
                     <p>Hello {task.assigned_to.name},</p>
                     <p>This is a reminder that the task <strong>{task.name}</strong> 
                     is due on {format_datetime(self.env, task.due_date)}.</p>
                     <p>Status: {task.status}</p>
                 """
                try:
                    # Alternatively can use task.message_post() but it will
                    # perform more actions than just sending an email (chat, etc.)
                    mail = self.env['mail.mail'].create({
                        'subject': 'Task Due Reminder',
                        'body_html': body,
                        'email_to': task.assigned_to.email,
                        'auto_delete': True,
                    })
                    mail.send()
                    # Log email sending
                    _logger.info(f"Sent task reminder to {task.assigned_to.email}")
                except Exception as e:
                    _logger.error(f"Failed to send reminder for task {task.name}: {e}")


    def make_tasks_report(self):
        """
        Generate a report for all tasks.
        This method retrieves all tasks and generates a report using the report action.
        The report is defined in the task_report_template.xml file.
        :return:  Action to display the report.
        """
        tasks = self.env['task.manager'].search([])
        return self.env.ref('task_manager.action_report_task').report_action(tasks)


    def action_save_and_return(self):
        """
        Save the current task and return to the previous view.
        Allows Save and Close task button to avoid creating unknown breadcrumbs during click.
        :return: Action to return to the previous view.
        """
        return self.env.ref('task_manager.action_task_manager').read()[0]