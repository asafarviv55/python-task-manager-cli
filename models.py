"""Data models for task management."""
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
import uuid


class Priority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecurrenceType(Enum):
    """Recurrence patterns for tasks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class TimeEntry:
    """Time tracking entry for a task."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    duration_minutes: float = 0.0
    notes: str = ""

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class Task:
    """Main task model with all features."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    priority: str = Priority.MEDIUM.value
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    due_date: Optional[str] = None
    completed_at: Optional[str] = None

    # Categories and tags
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # Recurrence
    is_recurring: bool = False
    recurrence_type: Optional[str] = None
    recurrence_interval: int = 1
    last_recurrence: Optional[str] = None

    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    blocked_by: List[str] = field(default_factory=list)

    # Time tracking
    time_entries: List[dict] = field(default_factory=list)
    estimated_minutes: Optional[int] = None

    # Template
    is_template: bool = False
    template_name: Optional[str] = None

    # Reminders
    reminder_before_minutes: Optional[int] = None
    last_reminded: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def update_timestamp(self):
        """Update the modified timestamp."""
        self.updated_at = datetime.now().isoformat()

    def complete(self):
        """Mark task as completed."""
        self.status = "completed"
        self.completed_at = datetime.now().isoformat()
        self.update_timestamp()

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date or self.status == "completed":
            return False
        return datetime.fromisoformat(self.due_date) < datetime.now()

    def needs_reminder(self) -> bool:
        """Check if task needs a reminder."""
        if not self.due_date or not self.reminder_before_minutes:
            return False
        if self.status == "completed":
            return False

        due = datetime.fromisoformat(self.due_date)
        remind_time = due - timedelta(minutes=self.reminder_before_minutes)

        if datetime.now() >= remind_time:
            # Check if already reminded recently
            if self.last_reminded:
                last = datetime.fromisoformat(self.last_reminded)
                # Don't remind more than once per hour
                if datetime.now() - last < timedelta(hours=1):
                    return False
            return True
        return False

    def can_start(self, all_tasks: dict) -> bool:
        """Check if all dependencies are met."""
        if not self.depends_on:
            return True

        for dep_id in self.depends_on:
            dep_task = all_tasks.get(dep_id)
            if not dep_task or dep_task.status != "completed":
                return False
        return True

    def total_time_spent(self) -> float:
        """Calculate total time spent on task in minutes."""
        total = 0.0
        for entry_dict in self.time_entries:
            total += entry_dict.get('duration_minutes', 0.0)
        return total

    def generate_next_recurrence(self) -> Optional['Task']:
        """Generate the next recurring task instance."""
        if not self.is_recurring or not self.recurrence_type:
            return None

        next_task = Task.from_dict(self.to_dict())
        next_task.id = str(uuid.uuid4())
        next_task.status = "pending"
        next_task.completed_at = None
        next_task.created_at = datetime.now().isoformat()
        next_task.updated_at = datetime.now().isoformat()
        next_task.time_entries = []

        # Update due date based on recurrence
        if self.due_date:
            current_due = datetime.fromisoformat(self.due_date)
            interval = self.recurrence_interval

            if self.recurrence_type == RecurrenceType.DAILY.value:
                new_due = current_due + timedelta(days=interval)
            elif self.recurrence_type == RecurrenceType.WEEKLY.value:
                new_due = current_due + timedelta(weeks=interval)
            elif self.recurrence_type == RecurrenceType.MONTHLY.value:
                # Approximate month as 30 days
                new_due = current_due + timedelta(days=30 * interval)
            elif self.recurrence_type == RecurrenceType.YEARLY.value:
                # Approximate year as 365 days
                new_due = current_due + timedelta(days=365 * interval)
            else:
                new_due = current_due

            next_task.due_date = new_due.isoformat()

        next_task.last_recurrence = datetime.now().isoformat()
        return next_task


@dataclass
class TaskTemplate:
    """Template for creating tasks quickly."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    title: str = ""
    description: str = ""
    priority: str = Priority.MEDIUM.value
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    estimated_minutes: Optional[int] = None
    reminder_before_minutes: Optional[int] = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def create_task(self) -> Task:
        """Create a new task from this template."""
        return Task(
            title=self.title,
            description=self.description,
            priority=self.priority,
            categories=self.categories.copy(),
            tags=self.tags.copy(),
            estimated_minutes=self.estimated_minutes,
            reminder_before_minutes=self.reminder_before_minutes
        )
