{
    'name': 'Task Odoo17',
    'version': '1.0',
    'author': 'Daniils Sturis',
    'depends': ['base', 'mail'],
    'category': 'Test',
    'data': [
        'report/task_report_template.xml',
        'report/task_report_server_action.xml',
        'report/task_report.xml',
        'security/ir.model.access.csv',
        'data/task_cron.xml',
        'views/task_views.xml',
    ],
    'installable': True,
    'application': True,

}
