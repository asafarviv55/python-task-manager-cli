"""Business logic for task management operations."""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from models import Task, TaskTemplate, TimeEntry, Priority, RecurrenceType
import csv
import json


class TaskManager:
    """Core business logic for managing tasks."""

    def __init__(self, storage):
        self.storage = storage
        self.tasks = {}
        self.templates = {}
        self.load()

    def load(self):
        """Load tasks and templates from storage."""
        self.tasks = self.storage.load_tasks()
        self.templates = self.storage.load_templates()

    def save(self):
        """Save tasks and templates to storage."""
        self.storage.save_tasks(self.tasks)
        self.storage.save_templates(self.templates)

    # Task CRUD operations
    def create_task(self, title: str, description: str = "", priority: str = Priority.MEDIUM.value,
                    due_date: Optional[str] = None, categories: List[str] = None,
                    tags: List[str] = None) -> Task:
        """Create a new task."""
        task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            categories=categories or [],
            tags=tags or []
        )
        self.tasks[task.id] = task
        self.save()
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        """Update task properties."""
        task = self.tasks.get(task_id)
        if not task:
            return None

        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)

        task.update_timestamp()
        self.save()
        return task

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.save()
            return True
        return False

    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task as completed and handle recurrence."""
        task = self.tasks.get(task_id)
        if not task:
            return None

        task.complete()

        # Generate next recurring instance if applicable
        if task.is_recurring:
            next_task = task.generate_next_recurrence()
            if next_task:
                self.tasks[next_task.id] = next_task

        self.save()
        return task

    # Priority management
    def set_priority(self, task_id: str, priority: str) -> Optional[Task]:
        """Set task priority."""
        return self.update_task(task_id, priority=priority)

    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """Get all tasks with specific priority."""
        return [task for task in self.tasks.values() if task.priority == priority]

    # Due dates and reminders
    def set_due_date(self, task_id: str, due_date: str, reminder_minutes: Optional[int] = None) -> Optional[Task]:
        """Set task due date and optional reminder."""
        return self.update_task(task_id, due_date=due_date, reminder_before_minutes=reminder_minutes)

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        return [task for task in self.tasks.values() if task.is_overdue()]

    def get_tasks_due_soon(self, hours: int = 24) -> List[Task]:
        """Get tasks due within specified hours."""
        now = datetime.now()
        threshold = now + timedelta(hours=hours)
        due_soon = []

        for task in self.tasks.values():
            if task.due_date and task.status != "completed":
                due = datetime.fromisoformat(task.due_date)
                if now <= due <= threshold:
                    due_soon.append(task)

        return due_soon

    def check_reminders(self) -> List[Task]:
        """Check for tasks that need reminders."""
        tasks_to_remind = []
        for task in self.tasks.values():
            if task.needs_reminder():
                task.last_reminded = datetime.now().isoformat()
                tasks_to_remind.append(task)

        if tasks_to_remind:
            self.save()

        return tasks_to_remind

    # Categories and tags
    def add_category(self, task_id: str, category: str) -> Optional[Task]:
        """Add a category to a task."""
        task = self.tasks.get(task_id)
        if task and category not in task.categories:
            task.categories.append(category)
            task.update_timestamp()
            self.save()
        return task

    def remove_category(self, task_id: str, category: str) -> Optional[Task]:
        """Remove a category from a task."""
        task = self.tasks.get(task_id)
        if task and category in task.categories:
            task.categories.remove(category)
            task.update_timestamp()
            self.save()
        return task

    def add_tag(self, task_id: str, tag: str) -> Optional[Task]:
        """Add a tag to a task."""
        task = self.tasks.get(task_id)
        if task and tag not in task.tags:
            task.tags.append(tag)
            task.update_timestamp()
            self.save()
        return task

    def remove_tag(self, task_id: str, tag: str) -> Optional[Task]:
        """Remove a tag from a task."""
        task = self.tasks.get(task_id)
        if task and tag in task.tags:
            task.tags.remove(tag)
            task.update_timestamp()
            self.save()
        return task

    def get_all_categories(self) -> List[str]:
        """Get all unique categories."""
        categories = set()
        for task in self.tasks.values():
            categories.update(task.categories)
        return sorted(list(categories))

    def get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        tags = set()
        for task in self.tasks.values():
            tags.update(task.tags)
        return sorted(list(tags))

    # Recurring tasks
    def make_recurring(self, task_id: str, recurrence_type: str, interval: int = 1) -> Optional[Task]:
        """Make a task recurring."""
        return self.update_task(task_id, is_recurring=True, recurrence_type=recurrence_type,
                               recurrence_interval=interval)

    def get_recurring_tasks(self) -> List[Task]:
        """Get all recurring tasks."""
        return [task for task in self.tasks.values() if task.is_recurring]

    # Dependencies
    def add_dependency(self, task_id: str, depends_on_id: str) -> bool:
        """Add a dependency between tasks."""
        task = self.tasks.get(task_id)
        dep_task = self.tasks.get(depends_on_id)

        if not task or not dep_task:
            return False

        if depends_on_id not in task.depends_on:
            task.depends_on.append(depends_on_id)
            task.update_timestamp()
            self.save()

        return True

    def remove_dependency(self, task_id: str, depends_on_id: str) -> bool:
        """Remove a dependency."""
        task = self.tasks.get(task_id)
        if task and depends_on_id in task.depends_on:
            task.depends_on.remove(depends_on_id)
            task.update_timestamp()
            self.save()
            return True
        return False

    def get_blocked_tasks(self) -> List[Task]:
        """Get tasks that are blocked by dependencies."""
        blocked = []
        for task in self.tasks.values():
            if task.depends_on and not task.can_start(self.tasks):
                blocked.append(task)
        return blocked

    def get_task_dependencies(self, task_id: str) -> List[Task]:
        """Get all tasks that this task depends on."""
        task = self.tasks.get(task_id)
        if not task:
            return []
        return [self.tasks[dep_id] for dep_id in task.depends_on if dep_id in self.tasks]

    # Time tracking
    def start_time_tracking(self, task_id: str, notes: str = "") -> Optional[TimeEntry]:
        """Start tracking time for a task."""
        task = self.tasks.get(task_id)
        if not task:
            return None

        entry = TimeEntry(notes=notes)
        task.time_entries.append(entry.to_dict())
        task.update_timestamp()
        self.save()
        return entry

    def stop_time_tracking(self, task_id: str, entry_id: str) -> Optional[TimeEntry]:
        """Stop tracking time for a task."""
        task = self.tasks.get(task_id)
        if not task:
            return None

        for entry_dict in task.time_entries:
            if entry_dict['id'] == entry_id:
                entry = TimeEntry.from_dict(entry_dict)
                entry.end_time = datetime.now().isoformat()

                # Calculate duration
                start = datetime.fromisoformat(entry.start_time)
                end = datetime.fromisoformat(entry.end_time)
                entry.duration_minutes = (end - start).total_seconds() / 60

                # Update in task
                for i, e in enumerate(task.time_entries):
                    if e['id'] == entry_id:
                        task.time_entries[i] = entry.to_dict()
                        break

                task.update_timestamp()
                self.save()
                return entry

        return None

    def get_active_time_entries(self, task_id: str) -> List[TimeEntry]:
        """Get active time tracking entries."""
        task = self.tasks.get(task_id)
        if not task:
            return []

        active = []
        for entry_dict in task.time_entries:
            if not entry_dict.get('end_time'):
                active.append(TimeEntry.from_dict(entry_dict))

        return active

    # Templates
    def create_template(self, name: str, title: str, description: str = "",
                       priority: str = Priority.MEDIUM.value, categories: List[str] = None,
                       tags: List[str] = None) -> TaskTemplate:
        """Create a task template."""
        template = TaskTemplate(
            name=name,
            title=title,
            description=description,
            priority=priority,
            categories=categories or [],
            tags=tags or []
        )
        self.templates[template.id] = template
        self.save()
        return template

    def create_task_from_template(self, template_name: str, **overrides) -> Optional[Task]:
        """Create a task from a template."""
        template = None
        for t in self.templates.values():
            if t.name == template_name:
                template = t
                break

        if not template:
            return None

        task = template.create_task()

        # Apply overrides
        for key, value in overrides.items():
            if hasattr(task, key):
                setattr(task, key, value)

        self.tasks[task.id] = task
        self.save()
        return task

    def get_template(self, template_name: str) -> Optional[TaskTemplate]:
        """Get a template by name."""
        for template in self.templates.values():
            if template.name == template_name:
                return template
        return None

    def list_templates(self) -> List[TaskTemplate]:
        """List all templates."""
        return list(self.templates.values())

    # Bulk operations
    def bulk_update(self, task_ids: List[str], **kwargs) -> List[Task]:
        """Update multiple tasks at once."""
        updated = []
        for task_id in task_ids:
            task = self.update_task(task_id, **kwargs)
            if task:
                updated.append(task)
        return updated

    def bulk_complete(self, task_ids: List[str]) -> List[Task]:
        """Complete multiple tasks at once."""
        completed = []
        for task_id in task_ids:
            task = self.complete_task(task_id)
            if task:
                completed.append(task)
        return completed

    def bulk_delete(self, task_ids: List[str]) -> int:
        """Delete multiple tasks at once."""
        count = 0
        for task_id in task_ids:
            if self.delete_task(task_id):
                count += 1
        return count

    def bulk_set_category(self, task_ids: List[str], category: str) -> List[Task]:
        """Add a category to multiple tasks."""
        updated = []
        for task_id in task_ids:
            task = self.add_category(task_id, category)
            if task:
                updated.append(task)
        return updated

    def bulk_set_tag(self, task_ids: List[str], tag: str) -> List[Task]:
        """Add a tag to multiple tasks."""
        updated = []
        for task_id in task_ids:
            task = self.add_tag(task_id, tag)
            if task:
                updated.append(task)
        return updated

    # Search and filtering
    def search_tasks(self, query: str, search_fields: List[str] = None) -> List[Task]:
        """Search tasks by query string."""
        if not search_fields:
            search_fields = ['title', 'description']

        query = query.lower()
        results = []

        for task in self.tasks.values():
            for field in search_fields:
                value = getattr(task, field, '')
                if value and query in str(value).lower():
                    results.append(task)
                    break

        return results

    def filter_tasks(self, status: Optional[str] = None, priority: Optional[str] = None,
                    category: Optional[str] = None, tag: Optional[str] = None,
                    has_due_date: Optional[bool] = None) -> List[Task]:
        """Filter tasks by various criteria."""
        results = list(self.tasks.values())

        if status:
            results = [t for t in results if t.status == status]

        if priority:
            results = [t for t in results if t.priority == priority]

        if category:
            results = [t for t in results if category in t.categories]

        if tag:
            results = [t for t in results if tag in t.tags]

        if has_due_date is not None:
            if has_due_date:
                results = [t for t in results if t.due_date]
            else:
                results = [t for t in results if not t.due_date]

        return results

    # Export functionality
    def export_to_csv(self, filepath: str, tasks: List[Task] = None) -> bool:
        """Export tasks to CSV file."""
        if tasks is None:
            tasks = list(self.tasks.values())

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if not tasks:
                    return True

                fieldnames = ['id', 'title', 'description', 'priority', 'status', 'created_at',
                            'updated_at', 'due_date', 'completed_at', 'categories', 'tags',
                            'is_recurring', 'recurrence_type', 'total_time_minutes']

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for task in tasks:
                    row = {
                        'id': task.id,
                        'title': task.title,
                        'description': task.description,
                        'priority': task.priority,
                        'status': task.status,
                        'created_at': task.created_at,
                        'updated_at': task.updated_at,
                        'due_date': task.due_date or '',
                        'completed_at': task.completed_at or '',
                        'categories': ','.join(task.categories),
                        'tags': ','.join(task.tags),
                        'is_recurring': task.is_recurring,
                        'recurrence_type': task.recurrence_type or '',
                        'total_time_minutes': task.total_time_spent()
                    }
                    writer.writerow(row)

            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def export_to_json(self, filepath: str, tasks: List[Task] = None) -> bool:
        """Export tasks to JSON file."""
        if tasks is None:
            tasks = list(self.tasks.values())

        try:
            data = {
                'exported_at': datetime.now().isoformat(),
                'task_count': len(tasks),
                'tasks': [task.to_dict() for task in tasks]
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False

    # Statistics and reporting
    def get_statistics(self) -> Dict:
        """Get task statistics."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == "completed")
        pending = sum(1 for t in self.tasks.values() if t.status == "pending")
        overdue = len(self.get_overdue_tasks())

        priority_counts = {}
        for p in Priority:
            priority_counts[p.value] = len(self.get_tasks_by_priority(p.value))

        total_time = sum(t.total_time_spent() for t in self.tasks.values())

        return {
            'total_tasks': total,
            'completed': completed,
            'pending': pending,
            'overdue': overdue,
            'priority_counts': priority_counts,
            'total_time_minutes': total_time,
            'categories': len(self.get_all_categories()),
            'tags': len(self.get_all_tags()),
            'recurring_tasks': len(self.get_recurring_tasks())
        }
