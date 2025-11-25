"""Storage layer for tasks with JSON and SQLite support."""
import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict
from models import Task, TaskTemplate, TimeEntry
from datetime import datetime


class JSONStorage:
    """JSON-based storage for tasks."""

    def __init__(self, filepath: str = "tasks.json"):
        self.filepath = Path(filepath)
        self.templates_filepath = Path("templates.json")
        self._ensure_files()

    def _ensure_files(self):
        """Ensure storage files exist."""
        if not self.filepath.exists():
            self.filepath.write_text(json.dumps({"tasks": {}}))
        if not self.templates_filepath.exists():
            self.templates_filepath.write_text(json.dumps({"templates": {}}))

    def load_tasks(self) -> Dict[str, Task]:
        """Load all tasks from storage."""
        try:
            data = json.loads(self.filepath.read_text())
            tasks = {}
            for task_id, task_data in data.get("tasks", {}).items():
                tasks[task_id] = Task.from_dict(task_data)
            return tasks
        except Exception as e:
            print(f"Error loading tasks: {e}")
            return {}

    def save_tasks(self, tasks: Dict[str, Task]) -> bool:
        """Save all tasks to storage."""
        try:
            data = {"tasks": {task_id: task.to_dict() for task_id, task in tasks.items()}}
            self.filepath.write_text(json.dumps(data, indent=2))
            return True
        except Exception as e:
            print(f"Error saving tasks: {e}")
            return False

    def load_templates(self) -> Dict[str, TaskTemplate]:
        """Load all templates from storage."""
        try:
            data = json.loads(self.templates_filepath.read_text())
            templates = {}
            for template_id, template_data in data.get("templates", {}).items():
                templates[template_id] = TaskTemplate.from_dict(template_data)
            return templates
        except Exception as e:
            print(f"Error loading templates: {e}")
            return {}

    def save_templates(self, templates: Dict[str, TaskTemplate]) -> bool:
        """Save all templates to storage."""
        try:
            data = {"templates": {t_id: t.to_dict() for t_id, t in templates.items()}}
            self.templates_filepath.write_text(json.dumps(data, indent=2))
            return True
        except Exception as e:
            print(f"Error saving templates: {e}")
            return False


class SQLiteStorage:
    """SQLite-based storage for tasks."""

    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT,
                due_date TEXT,
                completed_at TEXT,
                is_recurring INTEGER,
                recurrence_type TEXT,
                recurrence_interval INTEGER,
                last_recurrence TEXT,
                estimated_minutes INTEGER,
                is_template INTEGER,
                template_name TEXT,
                reminder_before_minutes INTEGER,
                last_reminded TEXT
            )
        """)

        # Categories table (many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_categories (
                task_id TEXT,
                category TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)

        # Tags table (many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_tags (
                task_id TEXT,
                tag TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)

        # Dependencies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_dependencies (
                task_id TEXT,
                depends_on_id TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (depends_on_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)

        # Time entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_entries (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                start_time TEXT,
                end_time TEXT,
                duration_minutes REAL,
                notes TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)

        # Templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                title TEXT,
                description TEXT,
                priority TEXT,
                estimated_minutes INTEGER,
                reminder_before_minutes INTEGER
            )
        """)

        # Template categories
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS template_categories (
                template_id TEXT,
                category TEXT,
                FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE
            )
        """)

        # Template tags
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS template_tags (
                template_id TEXT,
                tag TEXT,
                FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE
            )
        """)

        self.conn.commit()

    def load_tasks(self) -> Dict[str, Task]:
        """Load all tasks from SQLite database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = {}

        for row in cursor.fetchall():
            task_dict = dict(row)
            task_id = task_dict['id']

            # Load categories
            cursor.execute("SELECT category FROM task_categories WHERE task_id = ?", (task_id,))
            task_dict['categories'] = [r['category'] for r in cursor.fetchall()]

            # Load tags
            cursor.execute("SELECT tag FROM task_tags WHERE task_id = ?", (task_id,))
            task_dict['tags'] = [r['tag'] for r in cursor.fetchall()]

            # Load dependencies
            cursor.execute("SELECT depends_on_id FROM task_dependencies WHERE task_id = ?", (task_id,))
            task_dict['depends_on'] = [r['depends_on_id'] for r in cursor.fetchall()]
            task_dict['blocked_by'] = []  # Computed dynamically if needed

            # Load time entries
            cursor.execute("SELECT * FROM time_entries WHERE task_id = ?", (task_id,))
            task_dict['time_entries'] = [dict(r) for r in cursor.fetchall()]

            # Convert integers to booleans
            task_dict['is_recurring'] = bool(task_dict['is_recurring'])
            task_dict['is_template'] = bool(task_dict['is_template'])

            tasks[task_id] = Task.from_dict(task_dict)

        return tasks

    def save_tasks(self, tasks: Dict[str, Task]) -> bool:
        """Save all tasks to SQLite database."""
        try:
            cursor = self.conn.cursor()

            # Clear existing data
            cursor.execute("DELETE FROM tasks")
            cursor.execute("DELETE FROM task_categories")
            cursor.execute("DELETE FROM task_tags")
            cursor.execute("DELETE FROM task_dependencies")
            cursor.execute("DELETE FROM time_entries")

            for task_id, task in tasks.items():
                # Insert task
                cursor.execute("""
                    INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task.id, task.title, task.description, task.priority, task.status,
                    task.created_at, task.updated_at, task.due_date, task.completed_at,
                    int(task.is_recurring), task.recurrence_type, task.recurrence_interval,
                    task.last_recurrence, task.estimated_minutes, int(task.is_template),
                    task.template_name, task.reminder_before_minutes, task.last_reminded
                ))

                # Insert categories
                for category in task.categories:
                    cursor.execute("INSERT INTO task_categories VALUES (?, ?)", (task.id, category))

                # Insert tags
                for tag in task.tags:
                    cursor.execute("INSERT INTO task_tags VALUES (?, ?)", (task.id, tag))

                # Insert dependencies
                for dep_id in task.depends_on:
                    cursor.execute("INSERT INTO task_dependencies VALUES (?, ?)", (task.id, dep_id))

                # Insert time entries
                for entry in task.time_entries:
                    cursor.execute("""
                        INSERT INTO time_entries VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        entry['id'], task.id, entry['start_time'], entry.get('end_time'),
                        entry['duration_minutes'], entry.get('notes', '')
                    ))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving tasks: {e}")
            self.conn.rollback()
            return False

    def load_templates(self) -> Dict[str, TaskTemplate]:
        """Load all templates from database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM templates")
        templates = {}

        for row in cursor.fetchall():
            template_dict = dict(row)
            template_id = template_dict['id']

            # Load categories
            cursor.execute("SELECT category FROM template_categories WHERE template_id = ?", (template_id,))
            template_dict['categories'] = [r['category'] for r in cursor.fetchall()]

            # Load tags
            cursor.execute("SELECT tag FROM template_tags WHERE template_id = ?", (template_id,))
            template_dict['tags'] = [r['tag'] for r in cursor.fetchall()]

            templates[template_id] = TaskTemplate.from_dict(template_dict)

        return templates

    def save_templates(self, templates: Dict[str, TaskTemplate]) -> bool:
        """Save all templates to database."""
        try:
            cursor = self.conn.cursor()

            # Clear existing data
            cursor.execute("DELETE FROM templates")
            cursor.execute("DELETE FROM template_categories")
            cursor.execute("DELETE FROM template_tags")

            for template_id, template in templates.items():
                cursor.execute("""
                    INSERT INTO templates VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    template.id, template.name, template.title, template.description,
                    template.priority, template.estimated_minutes, template.reminder_before_minutes
                ))

                # Insert categories
                for category in template.categories:
                    cursor.execute("INSERT INTO template_categories VALUES (?, ?)", (template.id, category))

                # Insert tags
                for tag in template.tags:
                    cursor.execute("INSERT INTO template_tags VALUES (?, ?)", (template.id, tag))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving templates: {e}")
            self.conn.rollback()
            return False

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
