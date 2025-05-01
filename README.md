# Task Manager Module – Deployment and Usage Guide

This guide explains how to set up Odoo 17 and install the `task_manager` custom module from a GitHub repository, suitable for fresh environments.

---

## 1. System Requirements

Install the following:

- Python 3.10+
- PostgreSQL 15+ (with a running service)
- wkhtmltopdf 0.12.6-1 (patched Qt version)
- Node.js and npm
- Git

---

## 2. Clone Odoo and the Custom Module

Create a working directory and clone both Odoo and the custom module:

```
git clone https://github.com/odoo/odoo.git --depth 1 --branch 17.0 odoo
git clone https://github.com/<your-username>/task_manager.git custom_addons/task_manager
```

Replace `<your-username>` with your actual GitHub username.

---

## 3. Create Python Virtual Environment

Navigate to the `odoo` folder and set up a virtual environment:

```
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/macOS
```

Install dependencies from the official Odoo requirements file

---

## 4. PostgreSQL Configuration

Ensure that PostgreSQL is installed and running. You can use the default `odoo` user or create a dedicated one:

- Create a PostgreSQL user with createdb privileges.
- Create a new empty database or let Odoo do it at first run.

---

## 5. wkhtmltopdf Installation

Download the 0.12.6-1 version from the official site:

https://github.com/wkhtmltopdf/wkhtmltopdf/releases/tag/0.12.6

Make sure the `wkhtmltopdf` binary is in your system’s PATH.

---

## 6. Create Configuration File

In the root of your project, create an `odoo.conf` file with your configuration settings. You can use `odoo.conf.template` as a template:

```
[options]
admin_passwd = admin_pwd
db_host = localhost
db_port = 5432
db_user = your_postgres_user
db_password = your_postgres_password
addons_path = addons, ../custom_addons
logfile = odoo.log
log_level = info

```

---

## 7. Launch Odoo

Start Odoo using the config file:

```
python odoo/odoo-bin -c odoo.conf
```

Visit [http://localhost:8069](http://localhost:8069) in your browser and create a new database.

---

## 8. Install the Task Manager Module

- Activate developer mode.
- Go to Apps and click “Update Apps List”.
- Search for `task_manager` or `Task Odoo17` and install it.

---

## 9. Features Overview

Once installed, the module provides:

- A “Task Manager” main menu
- Create and manage tasks with fields: name, assignee, priority, status, due date
- Automatic email reminders for tasks due in 3 days
- A printable PDF report of all tasks
- A “Save and Close” button for faster workflow

---

## 10. Running Tests

Run tests after installation using:

```
python odoo/odoo-bin --test-enable --init mail,task_manager --stop-after-init --test-tags /task_manager
```

---

## Notes

- If email sending doesn’t work, ensure the `mail` module is initialized and Odoo has SMTP configured.
- The cron job for reminders is included in `task_cron.xml` and activates automatically upon module installation.
- Restart Odoo after cloning or modifying custom modules to ensure proper loading.


# Development and Testing documentation for Task Manager Module

## System Setup

The development environment was based on the following preinstalled components:

- **PostgreSQL 17.0**
- **Node.js and npm**
- **wkhtmltopdf 0.12.6-1**

An issue was encountered during the initial Odoo startup due to `wkhtmltopdf` not being in the system’s environment path. This resulted in Odoo failing to render pages correctly (404 error). Once the binary was correctly registered in the system path, Odoo loaded successfully.

## Odoo Environment Setup

1. **Virtual Environment Setup**  
   A virtual environment was created using Python’s built-in `venv` module.

2. **Odoo Source Code Cloning**  
   The official Odoo 17.0 source code was cloned using GitHub with minimal depth for performance.

3. **Configuration File Creation**  
   An `odoo.conf` configuration file was created with paths to the custom module directory and necessary database settings.

4. **Odoo Launch**  
   Odoo was launched using the configuration file, and accessed via `http://localhost:8069`.

## Custom Module: Task Manager

The module is located under the `custom_addons/task_manager` directory and follows the standard Odoo module structure.

### Folder Structure Overview

```
task_manager/
├── __init__.py
├── __manifest__.py
├── data/
├── __init__.py
│   └── task_cron.xml
├── models/
├── __init__.py
│   └── task_manager.py
├── report/
├── __init__.py
│   ├── task_report.xml
│   ├── task_report_template.xml
│   └── task_report_server_action.xml
├── security/
├── __init__.py
│   └── ir.model.access.csv
├── tests/
├── __init__.py
│   └── test_task_manager.py
├── views/
├── __init__.py
│   └── task_views.xml
```

## Functionality Overview

The module provides a simple task management system with the following features:

- A `task.manager` model with fields for task name, description, assigned user, due date, priority (low/medium/high), and status (new/in progress/completed).
- Form and list views for interacting with tasks.
- User access rights based on group assignments.
- A Python method to calculate the number of days left until a task’s due date.
- A cron job that runs daily to notify assigned users of tasks due in exactly three days.
- A printable PDF report listing all tasks, with fields: name, description, assigned user, and priority.
- A menu item under “Task Manager” `Tasks Report` that triggers the report generation.
- A custom “Save and Close” button on the task form that saves the record and redirects back to the task list view.

## Testing and Debugging

### Email Delivery

The email notification system did not work initially due to improper initialization of the `mail` module. Although it was correctly declared in the module manifest, only a clean restart of Odoo allowed it to fully recognize and load the email handling logic. This may be related to how Odoo caches module dependencies during partial restarts.

### Report Generation

The most time-consuming issue was related to implementing the task report. The core misunderstanding was assuming that the report could be registered and invoked directly using `model="task.manager"` via a menu item. This approach resulted in an id errors and later no report being shown.

The resolution involved:

- Registering a proper `ir.actions.report` record with `model="task.manager"` and linking it to a `qweb-pdf` template.
- Creating a server action in Python that explicitly searches all task records and returns the report action with the recordset.
- Connecting the server action to a menu item, which resolved the report not appearing and fixed the issue of it generating empty content.

These changes ensured the report template received the correct context (`docs`) and generated a usable PDF.

## Testing Coverage

Unit tests were implemented using `TransactionCase` and include:

- Task creation, validation of default field values.
- Access control tests for users with and without appropriate permissions.
- A cron job test to verify that email notifications are triggered when expected, using `unittest.mock` to avoid sending real emails.
- A test for the report method to ensure it returns the expected report action dictionary.

Tests were tagged to run post-installation and are executable through the Odoo CLI with test mode enabled.