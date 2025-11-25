"""Command-line interface for task manager."""
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from tabulate import tabulate
from models import Priority, RecurrenceType
from storage import JSONStorage, SQLiteStorage
from business_logic import TaskManager


class TaskCLI:
    """CLI handler for task management."""

    def __init__(self, use_sqlite: bool = False):
        if use_sqlite:
            self.storage = SQLiteStorage()
        else:
            self.storage = JSONStorage()
        self.manager = TaskManager(self.storage)

    def run(self):
        """Run the CLI application."""
        parser = argparse.ArgumentParser(description='Task Manager CLI')
        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Task CRUD commands
        self._add_task_commands(subparsers)

        # Priority commands
        self._add_priority_commands(subparsers)

        # Due date and reminder commands
        self._add_due_date_commands(subparsers)

        # Category and tag commands
        self._add_category_tag_commands(subparsers)

        # Recurring task commands
        self._add_recurring_commands(subparsers)

        # Dependency commands
        self._add_dependency_commands(subparsers)

        # Time tracking commands
        self._add_time_tracking_commands(subparsers)

        # Template commands
        self._add_template_commands(subparsers)

        # Bulk operation commands
        self._add_bulk_commands(subparsers)

        # Search and filter commands
        self._add_search_commands(subparsers)

        # Export commands
        self._add_export_commands(subparsers)

        # Statistics command
        stats_parser = subparsers.add_parser('stats', help='Show task statistics')

        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            return

        # Route to appropriate handler
        handler_name = f'handle_{args.command}'
        handler = getattr(self, handler_name, None)

        if handler:
            handler(args)
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()

    def _add_task_commands(self, subparsers):
        """Add basic task CRUD commands."""
        # Create task
        create = subparsers.add_parser('create', help='Create a new task')
        create.add_argument('title', help='Task title')
        create.add_argument('-d', '--description', default='', help='Task description')
        create.add_argument('-p', '--priority', choices=['low', 'medium', 'high', 'urgent'],
                          default='medium', help='Task priority')
        create.add_argument('--due', help='Due date (ISO format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)')
        create.add_argument('-c', '--categories', nargs='*', default=[], help='Categories')
        create.add_argument('-t', '--tags', nargs='*', default=[], help='Tags')

        # List tasks
        list_parser = subparsers.add_parser('list', help='List all tasks')
        list_parser.add_argument('-s', '--status', help='Filter by status')
        list_parser.add_argument('-p', '--priority', help='Filter by priority')

        # Show task details
        show = subparsers.add_parser('show', help='Show task details')
        show.add_argument('task_id', help='Task ID')

        # Update task
        update = subparsers.add_parser('update', help='Update a task')
        update.add_argument('task_id', help='Task ID')
        update.add_argument('-t', '--title', help='New title')
        update.add_argument('-d', '--description', help='New description')
        update.add_argument('-p', '--priority', choices=['low', 'medium', 'high', 'urgent'],
                          help='New priority')
        update.add_argument('-s', '--status', help='New status')

        # Complete task
        complete = subparsers.add_parser('complete', help='Mark task as completed')
        complete.add_argument('task_id', help='Task ID')

        # Delete task
        delete = subparsers.add_parser('delete', help='Delete a task')
        delete.add_argument('task_id', help='Task ID')

    def _add_priority_commands(self, subparsers):
        """Add priority management commands."""
        priority = subparsers.add_parser('priority', help='Set task priority')
        priority.add_argument('task_id', help='Task ID')
        priority.add_argument('level', choices=['low', 'medium', 'high', 'urgent'],
                            help='Priority level')

        list_priority = subparsers.add_parser('list-priority', help='List tasks by priority')
        list_priority.add_argument('level', choices=['low', 'medium', 'high', 'urgent'],
                                  help='Priority level')

    def _add_due_date_commands(self, subparsers):
        """Add due date and reminder commands."""
        due = subparsers.add_parser('set-due', help='Set task due date')
        due.add_argument('task_id', help='Task ID')
        due.add_argument('date', help='Due date (ISO format)')
        due.add_argument('-r', '--reminder', type=int, help='Reminder minutes before due')

        overdue = subparsers.add_parser('overdue', help='List overdue tasks')

        due_soon = subparsers.add_parser('due-soon', help='List tasks due soon')
        due_soon.add_argument('--hours', type=int, default=24,
                            help='Hours to look ahead (default: 24)')

        reminders = subparsers.add_parser('reminders', help='Check and show reminders')

    def _add_category_tag_commands(self, subparsers):
        """Add category and tag management commands."""
        add_cat = subparsers.add_parser('add-category', help='Add category to task')
        add_cat.add_argument('task_id', help='Task ID')
        add_cat.add_argument('category', help='Category name')

        rem_cat = subparsers.add_parser('remove-category', help='Remove category from task')
        rem_cat.add_argument('task_id', help='Task ID')
        rem_cat.add_argument('category', help='Category name')

        add_tag = subparsers.add_parser('add-tag', help='Add tag to task')
        add_tag.add_argument('task_id', help='Task ID')
        add_tag.add_argument('tag', help='Tag name')

        rem_tag = subparsers.add_parser('remove-tag', help='Remove tag from task')
        rem_tag.add_argument('task_id', help='Task ID')
        rem_tag.add_argument('tag', help='Tag name')

        list_cats = subparsers.add_parser('list-categories', help='List all categories')
        list_tags = subparsers.add_parser('list-tags', help='List all tags')

    def _add_recurring_commands(self, subparsers):
        """Add recurring task commands."""
        recurring = subparsers.add_parser('make-recurring', help='Make task recurring')
        recurring.add_argument('task_id', help='Task ID')
        recurring.add_argument('type', choices=['daily', 'weekly', 'monthly', 'yearly'],
                             help='Recurrence type')
        recurring.add_argument('-i', '--interval', type=int, default=1,
                             help='Recurrence interval (default: 1)')

        list_recurring = subparsers.add_parser('list-recurring', help='List all recurring tasks')

    def _add_dependency_commands(self, subparsers):
        """Add dependency management commands."""
        add_dep = subparsers.add_parser('add-dependency', help='Add task dependency')
        add_dep.add_argument('task_id', help='Task ID')
        add_dep.add_argument('depends_on', help='ID of task this depends on')

        rem_dep = subparsers.add_parser('remove-dependency', help='Remove task dependency')
        rem_dep.add_argument('task_id', help='Task ID')
        rem_dep.add_argument('depends_on', help='ID of task this depends on')

        blocked = subparsers.add_parser('blocked', help='List blocked tasks')

        deps = subparsers.add_parser('dependencies', help='Show task dependencies')
        deps.add_argument('task_id', help='Task ID')

    def _add_time_tracking_commands(self, subparsers):
        """Add time tracking commands."""
        start_time = subparsers.add_parser('start-timer', help='Start time tracking')
        start_time.add_argument('task_id', help='Task ID')
        start_time.add_argument('-n', '--notes', default='', help='Notes for this session')

        stop_time = subparsers.add_parser('stop-timer', help='Stop time tracking')
        stop_time.add_argument('task_id', help='Task ID')
        stop_time.add_argument('entry_id', help='Time entry ID')

        show_time = subparsers.add_parser('show-time', help='Show time tracking for task')
        show_time.add_argument('task_id', help='Task ID')

    def _add_template_commands(self, subparsers):
        """Add template management commands."""
        create_template = subparsers.add_parser('create-template', help='Create task template')
        create_template.add_argument('name', help='Template name')
        create_template.add_argument('title', help='Task title')
        create_template.add_argument('-d', '--description', default='', help='Task description')
        create_template.add_argument('-p', '--priority', choices=['low', 'medium', 'high', 'urgent'],
                                   default='medium', help='Task priority')
        create_template.add_argument('-c', '--categories', nargs='*', default=[], help='Categories')
        create_template.add_argument('-t', '--tags', nargs='*', default=[], help='Tags')

        from_template = subparsers.add_parser('from-template', help='Create task from template')
        from_template.add_argument('template_name', help='Template name')
        from_template.add_argument('-t', '--title', help='Override title')
        from_template.add_argument('-d', '--description', help='Override description')
        from_template.add_argument('--due', help='Set due date')

        list_templates = subparsers.add_parser('list-templates', help='List all templates')

    def _add_bulk_commands(self, subparsers):
        """Add bulk operation commands."""
        bulk_update = subparsers.add_parser('bulk-update', help='Update multiple tasks')
        bulk_update.add_argument('task_ids', nargs='+', help='Task IDs')
        bulk_update.add_argument('-p', '--priority', help='Set priority')
        bulk_update.add_argument('-s', '--status', help='Set status')

        bulk_complete = subparsers.add_parser('bulk-complete', help='Complete multiple tasks')
        bulk_complete.add_argument('task_ids', nargs='+', help='Task IDs')

        bulk_delete = subparsers.add_parser('bulk-delete', help='Delete multiple tasks')
        bulk_delete.add_argument('task_ids', nargs='+', help='Task IDs')

        bulk_cat = subparsers.add_parser('bulk-category', help='Add category to multiple tasks')
        bulk_cat.add_argument('category', help='Category name')
        bulk_cat.add_argument('task_ids', nargs='+', help='Task IDs')

        bulk_tag = subparsers.add_parser('bulk-tag', help='Add tag to multiple tasks')
        bulk_tag.add_argument('tag', help='Tag name')
        bulk_tag.add_argument('task_ids', nargs='+', help='Task IDs')

    def _add_search_commands(self, subparsers):
        """Add search and filter commands."""
        search = subparsers.add_parser('search', help='Search tasks')
        search.add_argument('query', help='Search query')
        search.add_argument('-f', '--fields', nargs='*', default=['title', 'description'],
                          help='Fields to search')

        filter_parser = subparsers.add_parser('filter', help='Filter tasks')
        filter_parser.add_argument('-s', '--status', help='Filter by status')
        filter_parser.add_argument('-p', '--priority', help='Filter by priority')
        filter_parser.add_argument('-c', '--category', help='Filter by category')
        filter_parser.add_argument('-t', '--tag', help='Filter by tag')

    def _add_export_commands(self, subparsers):
        """Add export commands."""
        export_csv = subparsers.add_parser('export-csv', help='Export tasks to CSV')
        export_csv.add_argument('filepath', help='Output file path')
        export_csv.add_argument('-s', '--status', help='Filter by status before export')

        export_json = subparsers.add_parser('export-json', help='Export tasks to JSON')
        export_json.add_argument('filepath', help='Output file path')
        export_json.add_argument('-s', '--status', help='Filter by status before export')

    # Command handlers
    def handle_create(self, args):
        """Handle create command."""
        task = self.manager.create_task(
            title=args.title,
            description=args.description,
            priority=args.priority,
            due_date=args.due,
            categories=args.categories,
            tags=args.tags
        )
        print(f"Task created successfully!")
        print(f"ID: {task.id}")
        print(f"Title: {task.title}")
        print(f"Priority: {task.priority}")

    def handle_list(self, args):
        """Handle list command."""
        tasks = self.manager.filter_tasks(status=args.status, priority=args.priority)

        if not tasks:
            print("No tasks found.")
            return

        table_data = []
        for task in tasks:
            table_data.append([
                task.id[:8],
                task.title[:40],
                task.priority,
                task.status,
                task.due_date[:10] if task.due_date else 'None',
                ','.join(task.categories[:2]) if task.categories else ''
            ])

        headers = ['ID', 'Title', 'Priority', 'Status', 'Due Date', 'Categories']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        print(f"\nTotal: {len(tasks)} tasks")

    def handle_show(self, args):
        """Handle show command."""
        task = self.manager.get_task(args.task_id)
        if not task:
            print(f"Task not found: {args.task_id}")
            return

        print(f"\n{'='*60}")
        print(f"ID: {task.id}")
        print(f"Title: {task.title}")
        print(f"Description: {task.description}")
        print(f"Priority: {task.priority}")
        print(f"Status: {task.status}")
        print(f"Created: {task.created_at}")
        print(f"Updated: {task.updated_at}")
        print(f"Due Date: {task.due_date or 'None'}")
        print(f"Completed: {task.completed_at or 'None'}")
        print(f"Categories: {', '.join(task.categories) or 'None'}")
        print(f"Tags: {', '.join(task.tags) or 'None'}")
        print(f"Recurring: {task.is_recurring}")
        if task.is_recurring:
            print(f"Recurrence: {task.recurrence_type} (every {task.recurrence_interval})")
        print(f"Dependencies: {len(task.depends_on)}")
        print(f"Time Spent: {task.total_time_spent():.2f} minutes")
        print(f"{'='*60}\n")

    def handle_update(self, args):
        """Handle update command."""
        updates = {}
        if args.title:
            updates['title'] = args.title
        if args.description:
            updates['description'] = args.description
        if args.priority:
            updates['priority'] = args.priority
        if args.status:
            updates['status'] = args.status

        task = self.manager.update_task(args.task_id, **updates)
        if task:
            print(f"Task updated: {task.title}")
        else:
            print(f"Task not found: {args.task_id}")

    def handle_complete(self, args):
        """Handle complete command."""
        task = self.manager.complete_task(args.task_id)
        if task:
            print(f"Task completed: {task.title}")
            if task.is_recurring:
                print("New recurring instance created.")
        else:
            print(f"Task not found: {args.task_id}")

    def handle_delete(self, args):
        """Handle delete command."""
        if self.manager.delete_task(args.task_id):
            print("Task deleted successfully.")
        else:
            print(f"Task not found: {args.task_id}")

    def handle_priority(self, args):
        """Handle priority command."""
        task = self.manager.set_priority(args.task_id, args.level)
        if task:
            print(f"Priority set to {args.level}: {task.title}")
        else:
            print(f"Task not found: {args.task_id}")

    def handle_list_priority(self, args):
        """Handle list-priority command."""
        tasks = self.manager.get_tasks_by_priority(args.level)
        print(f"\n{args.level.upper()} priority tasks:")
        for task in tasks:
            print(f"  [{task.id[:8]}] {task.title} ({task.status})")
        print(f"Total: {len(tasks)}")

    def handle_set_due(self, args):
        """Handle set-due command."""
        task = self.manager.set_due_date(args.task_id, args.date, args.reminder)
        if task:
            print(f"Due date set: {task.title}")
            if args.reminder:
                print(f"Reminder set for {args.reminder} minutes before due date")
        else:
            print(f"Task not found: {args.task_id}")

    def handle_overdue(self, args):
        """Handle overdue command."""
        tasks = self.manager.get_overdue_tasks()
        print(f"\nOverdue tasks: {len(tasks)}")
        for task in tasks:
            print(f"  [{task.id[:8]}] {task.title} - Due: {task.due_date}")

    def handle_due_soon(self, args):
        """Handle due-soon command."""
        tasks = self.manager.get_tasks_due_soon(args.hours)
        print(f"\nTasks due within {args.hours} hours: {len(tasks)}")
        for task in tasks:
            print(f"  [{task.id[:8]}] {task.title} - Due: {task.due_date}")

    def handle_reminders(self, args):
        """Handle reminders command."""
        tasks = self.manager.check_reminders()
        print(f"\nReminder notifications: {len(tasks)}")
        for task in tasks:
            print(f"  REMINDER: {task.title} - Due: {task.due_date}")

    def handle_add_category(self, args):
        """Handle add-category command."""
        task = self.manager.add_category(args.task_id, args.category)
        if task:
            print(f"Category added: {args.category}")
        else:
            print(f"Task not found: {args.task_id}")

    def handle_remove_category(self, args):
        """Handle remove-category command."""
        task = self.manager.remove_category(args.task_id, args.category)
        if task:
            print(f"Category removed: {args.category}")
        else:
            print(f"Task not found: {args.task_id}")

    def handle_add_tag(self, args):
        """Handle add-tag command."""
        task = self.manager.add_tag(args.task_id, args.tag)
        if task:
            print(f"Tag added: {args.tag}")
        else:
            print(f"Task not found: {args.task_id}")

    def handle_remove_tag(self, args):
        """Handle remove-tag command."""
        task = self.manager.remove_tag(args.task_id, args.tag)
        if task:
            print(f"Tag removed: {args.tag}")
        else:
            print(f"Task not found: {args.task_id}")

    def handle_list_categories(self, args):
        """Handle list-categories command."""
        categories = self.manager.get_all_categories()
        print(f"\nAll categories ({len(categories)}):")
        for cat in categories:
            tasks = self.manager.filter_tasks(category=cat)
            print(f"  {cat} ({len(tasks)} tasks)")

    def handle_list_tags(self, args):
        """Handle list-tags command."""
        tags = self.manager.get_all_tags()
        print(f"\nAll tags ({len(tags)}):")
        for tag in tags:
            tasks = self.manager.filter_tasks(tag=tag)
            print(f"  {tag} ({len(tasks)} tasks)")

    def handle_make_recurring(self, args):
        """Handle make-recurring command."""
        task = self.manager.make_recurring(args.task_id, args.type, args.interval)
        if task:
            print(f"Task is now recurring: {args.type} (every {args.interval})")
        else:
            print(f"Task not found: {args.task_id}")

    def handle_list_recurring(self, args):
        """Handle list-recurring command."""
        tasks = self.manager.get_recurring_tasks()
        print(f"\nRecurring tasks: {len(tasks)}")
        for task in tasks:
            print(f"  [{task.id[:8]}] {task.title} - {task.recurrence_type}")

    def handle_add_dependency(self, args):
        """Handle add-dependency command."""
        if self.manager.add_dependency(args.task_id, args.depends_on):
            print("Dependency added successfully.")
        else:
            print("Failed to add dependency.")

    def handle_remove_dependency(self, args):
        """Handle remove-dependency command."""
        if self.manager.remove_dependency(args.task_id, args.depends_on):
            print("Dependency removed successfully.")
        else:
            print("Failed to remove dependency.")

    def handle_blocked(self, args):
        """Handle blocked command."""
        tasks = self.manager.get_blocked_tasks()
        print(f"\nBlocked tasks: {len(tasks)}")
        for task in tasks:
            deps = self.manager.get_task_dependencies(task.id)
            print(f"  [{task.id[:8]}] {task.title}")
            for dep in deps:
                print(f"    - Depends on: {dep.title} ({dep.status})")

    def handle_dependencies(self, args):
        """Handle dependencies command."""
        deps = self.manager.get_task_dependencies(args.task_id)
        print(f"\nDependencies: {len(deps)}")
        for dep in deps:
            print(f"  [{dep.id[:8]}] {dep.title} ({dep.status})")

    def handle_start_timer(self, args):
        """Handle start-timer command."""
        entry = self.manager.start_time_tracking(args.task_id, args.notes)
        if entry:
            print(f"Time tracking started.")
            print(f"Entry ID: {entry.id}")
            print(f"Start time: {entry.start_time}")
        else:
            print(f"Task not found: {args.task_id}")

    def handle_stop_timer(self, args):
        """Handle stop-timer command."""
        entry = self.manager.stop_time_tracking(args.task_id, args.entry_id)
        if entry:
            print(f"Time tracking stopped.")
            print(f"Duration: {entry.duration_minutes:.2f} minutes")
        else:
            print("Time entry not found.")

    def handle_show_time(self, args):
        """Handle show-time command."""
        task = self.manager.get_task(args.task_id)
        if not task:
            print(f"Task not found: {args.task_id}")
            return

        print(f"\nTime tracking for: {task.title}")
        print(f"Total time: {task.total_time_spent():.2f} minutes")
        print(f"\nTime entries:")

        for entry_dict in task.time_entries:
            entry = entry_dict
            print(f"  ID: {entry['id'][:8]}")
            print(f"  Start: {entry['start_time']}")
            print(f"  End: {entry.get('end_time', 'In progress')}")
            print(f"  Duration: {entry['duration_minutes']:.2f} minutes")
            if entry.get('notes'):
                print(f"  Notes: {entry['notes']}")
            print()

    def handle_create_template(self, args):
        """Handle create-template command."""
        template = self.manager.create_template(
            name=args.name,
            title=args.title,
            description=args.description,
            priority=args.priority,
            categories=args.categories,
            tags=args.tags
        )
        print(f"Template created: {template.name}")

    def handle_from_template(self, args):
        """Handle from-template command."""
        overrides = {}
        if args.title:
            overrides['title'] = args.title
        if args.description:
            overrides['description'] = args.description
        if args.due:
            overrides['due_date'] = args.due

        task = self.manager.create_task_from_template(args.template_name, **overrides)
        if task:
            print(f"Task created from template: {task.title}")
            print(f"ID: {task.id}")
        else:
            print(f"Template not found: {args.template_name}")

    def handle_list_templates(self, args):
        """Handle list-templates command."""
        templates = self.manager.list_templates()
        print(f"\nTemplates: {len(templates)}")
        for template in templates:
            print(f"  {template.name}: {template.title} ({template.priority})")

    def handle_bulk_update(self, args):
        """Handle bulk-update command."""
        updates = {}
        if args.priority:
            updates['priority'] = args.priority
        if args.status:
            updates['status'] = args.status

        tasks = self.manager.bulk_update(args.task_ids, **updates)
        print(f"Updated {len(tasks)} tasks.")

    def handle_bulk_complete(self, args):
        """Handle bulk-complete command."""
        tasks = self.manager.bulk_complete(args.task_ids)
        print(f"Completed {len(tasks)} tasks.")

    def handle_bulk_delete(self, args):
        """Handle bulk-delete command."""
        count = self.manager.bulk_delete(args.task_ids)
        print(f"Deleted {count} tasks.")

    def handle_bulk_category(self, args):
        """Handle bulk-category command."""
        tasks = self.manager.bulk_set_category(args.task_ids, args.category)
        print(f"Added category '{args.category}' to {len(tasks)} tasks.")

    def handle_bulk_tag(self, args):
        """Handle bulk-tag command."""
        tasks = self.manager.bulk_set_tag(args.task_ids, args.tag)
        print(f"Added tag '{args.tag}' to {len(tasks)} tasks.")

    def handle_search(self, args):
        """Handle search command."""
        tasks = self.manager.search_tasks(args.query, args.fields)
        print(f"\nSearch results: {len(tasks)}")
        for task in tasks:
            print(f"  [{task.id[:8]}] {task.title} ({task.status})")

    def handle_filter(self, args):
        """Handle filter command."""
        tasks = self.manager.filter_tasks(
            status=args.status,
            priority=args.priority,
            category=args.category,
            tag=args.tag
        )
        print(f"\nFiltered tasks: {len(tasks)}")
        for task in tasks:
            print(f"  [{task.id[:8]}] {task.title} - {task.priority} ({task.status})")

    def handle_export_csv(self, args):
        """Handle export-csv command."""
        tasks = None
        if args.status:
            tasks = self.manager.filter_tasks(status=args.status)

        if self.manager.export_to_csv(args.filepath, tasks):
            count = len(tasks) if tasks else len(self.manager.tasks)
            print(f"Exported {count} tasks to {args.filepath}")
        else:
            print("Export failed.")

    def handle_export_json(self, args):
        """Handle export-json command."""
        tasks = None
        if args.status:
            tasks = self.manager.filter_tasks(status=args.status)

        if self.manager.export_to_json(args.filepath, tasks):
            count = len(tasks) if tasks else len(self.manager.tasks)
            print(f"Exported {count} tasks to {args.filepath}")
        else:
            print("Export failed.")

    def handle_stats(self, args):
        """Handle stats command."""
        stats = self.manager.get_statistics()
        print("\n" + "="*50)
        print("TASK STATISTICS")
        print("="*50)
        print(f"Total Tasks: {stats['total_tasks']}")
        print(f"Completed: {stats['completed']}")
        print(f"Pending: {stats['pending']}")
        print(f"Overdue: {stats['overdue']}")
        print(f"\nPriority Breakdown:")
        for priority, count in stats['priority_counts'].items():
            print(f"  {priority.capitalize()}: {count}")
        print(f"\nCategories: {stats['categories']}")
        print(f"Tags: {stats['tags']}")
        print(f"Recurring Tasks: {stats['recurring_tasks']}")
        print(f"\nTotal Time Tracked: {stats['total_time_minutes']:.2f} minutes")
        print(f"                    ({stats['total_time_minutes']/60:.2f} hours)")
        print("="*50 + "\n")


def main():
    """Main entry point."""
    cli = TaskCLI(use_sqlite=False)  # Change to True to use SQLite
    cli.run()


if __name__ == '__main__':
    main()
