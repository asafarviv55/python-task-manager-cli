"""Example usage of the Task Manager."""
from datetime import datetime, timedelta
from storage import JSONStorage
from business_logic import TaskManager
from models import Priority, RecurrenceType


def main():
    """Demonstrate all features of the task manager."""

    # Initialize the task manager
    storage = JSONStorage("example_tasks.json")
    manager = TaskManager(storage)

    print("=" * 60)
    print("TASK MANAGER DEMO - ALL FEATURES")
    print("=" * 60)

    # Feature 1: Task Priorities
    print("\n1. TASK PRIORITIES")
    print("-" * 60)
    task1 = manager.create_task(
        "Fix critical security bug",
        "Patch vulnerability in authentication system",
        priority=Priority.URGENT.value
    )
    task2 = manager.create_task(
        "Update documentation",
        "Add API documentation",
        priority=Priority.LOW.value
    )
    task3 = manager.create_task(
        "Implement new feature",
        "Add user profile page",
        priority=Priority.HIGH.value
    )
    print(f"Created 3 tasks with different priorities")
    print(f"  - {task1.title}: {task1.priority}")
    print(f"  - {task2.title}: {task2.priority}")
    print(f"  - {task3.title}: {task3.priority}")

    # Feature 2: Due Dates with Reminders
    print("\n2. DUE DATES WITH REMINDERS")
    print("-" * 60)
    tomorrow = (datetime.now() + timedelta(days=1)).isoformat()
    next_week = (datetime.now() + timedelta(days=7)).isoformat()
    manager.set_due_date(task1.id, tomorrow, reminder_minutes=60)
    manager.set_due_date(task3.id, next_week, reminder_minutes=1440)
    print(f"Set due dates:")
    print(f"  - {task1.title}: {tomorrow} (reminder: 60 min before)")
    print(f"  - {task3.title}: {next_week} (reminder: 24 hours before)")

    overdue = manager.get_overdue_tasks()
    due_soon = manager.get_tasks_due_soon(hours=48)
    print(f"\nOverdue tasks: {len(overdue)}")
    print(f"Due within 48 hours: {len(due_soon)}")

    # Feature 3: Categories and Tags
    print("\n3. CATEGORIES AND TAGS")
    print("-" * 60)
    manager.add_category(task1.id, "Security")
    manager.add_category(task1.id, "Backend")
    manager.add_tag(task1.id, "critical")
    manager.add_tag(task1.id, "bug-fix")

    manager.add_category(task2.id, "Documentation")
    manager.add_tag(task2.id, "api")

    manager.add_category(task3.id, "Frontend")
    manager.add_category(task3.id, "Backend")
    manager.add_tag(task3.id, "feature")
    manager.add_tag(task3.id, "user-facing")

    print(f"Added categories and tags to tasks")
    categories = manager.get_all_categories()
    tags = manager.get_all_tags()
    print(f"  Total categories: {len(categories)} - {', '.join(categories)}")
    print(f"  Total tags: {len(tags)} - {', '.join(tags)}")

    # Feature 4: Recurring Tasks
    print("\n4. RECURRING TASKS")
    print("-" * 60)
    task4 = manager.create_task(
        "Daily standup meeting",
        "Team sync meeting",
        priority=Priority.MEDIUM.value
    )
    manager.make_recurring(task4.id, RecurrenceType.DAILY.value, interval=1)

    task5 = manager.create_task(
        "Weekly report",
        "Submit weekly progress report",
        priority=Priority.MEDIUM.value
    )
    manager.make_recurring(task5.id, RecurrenceType.WEEKLY.value, interval=1)

    print(f"Created recurring tasks:")
    print(f"  - {task4.title}: {RecurrenceType.DAILY.value}")
    print(f"  - {task5.title}: {RecurrenceType.WEEKLY.value}")

    # Feature 5: Task Dependencies
    print("\n5. TASK DEPENDENCIES")
    print("-" * 60)
    task6 = manager.create_task(
        "Write unit tests",
        "Test the new feature"
    )
    manager.add_dependency(task6.id, task3.id)

    task7 = manager.create_task(
        "Deploy to production",
        "Deploy after testing"
    )
    manager.add_dependency(task7.id, task6.id)

    print(f"Created dependency chain:")
    print(f"  {task3.title}")
    print(f"    -> {task6.title}")
    print(f"       -> {task7.title}")

    blocked = manager.get_blocked_tasks()
    print(f"\nBlocked tasks: {len(blocked)}")
    for task in blocked:
        print(f"  - {task.title}")

    # Feature 6: Time Tracking
    print("\n6. TIME TRACKING")
    print("-" * 60)
    entry1 = manager.start_time_tracking(task1.id, "Investigating the bug")
    print(f"Started time tracking for: {task1.title}")
    print(f"  Entry ID: {entry1.id[:8]}...")

    # Simulate some work
    import time
    time.sleep(2)

    stopped_entry = manager.stop_time_tracking(task1.id, entry1.id)
    print(f"Stopped time tracking")
    print(f"  Duration: {stopped_entry.duration_minutes:.2f} minutes")

    # Feature 7: Task Templates
    print("\n7. TASK TEMPLATES")
    print("-" * 60)
    template1 = manager.create_template(
        name="bug-fix-template",
        title="Fix bug in module",
        description="Standard bug fix workflow",
        priority=Priority.HIGH.value,
        categories=["Development", "Bug-Fix"],
        tags=["bug"]
    )

    template2 = manager.create_template(
        name="feature-template",
        title="Implement new feature",
        description="Standard feature development workflow",
        priority=Priority.MEDIUM.value,
        categories=["Development", "Feature"],
        tags=["feature", "enhancement"]
    )

    print(f"Created templates:")
    print(f"  - {template1.name}: {template1.title}")
    print(f"  - {template2.name}: {template2.title}")

    task_from_template = manager.create_task_from_template(
        "bug-fix-template",
        title="Fix login validation bug"
    )
    print(f"\nCreated task from template: {task_from_template.title}")
    print(f"  Categories: {', '.join(task_from_template.categories)}")
    print(f"  Tags: {', '.join(task_from_template.tags)}")

    # Feature 8: Bulk Operations
    print("\n8. BULK OPERATIONS")
    print("-" * 60)
    bulk_task1 = manager.create_task("Bulk task 1", priority=Priority.LOW.value)
    bulk_task2 = manager.create_task("Bulk task 2", priority=Priority.LOW.value)
    bulk_task3 = manager.create_task("Bulk task 3", priority=Priority.LOW.value)

    task_ids = [bulk_task1.id, bulk_task2.id, bulk_task3.id]

    # Bulk update priority
    updated = manager.bulk_update(task_ids, priority=Priority.HIGH.value)
    print(f"Bulk updated {len(updated)} tasks to HIGH priority")

    # Bulk add category
    categorized = manager.bulk_set_category(task_ids, "Sprint-1")
    print(f"Bulk added 'Sprint-1' category to {len(categorized)} tasks")

    # Bulk add tag
    tagged = manager.bulk_set_tag(task_ids, "ready-for-review")
    print(f"Bulk added 'ready-for-review' tag to {len(tagged)} tasks")

    # Feature 9: Search and Filters
    print("\n9. SEARCH AND FILTERS")
    print("-" * 60)
    search_results = manager.search_tasks("bug")
    print(f"Search for 'bug': {len(search_results)} results")
    for task in search_results[:3]:
        print(f"  - {task.title}")

    filtered = manager.filter_tasks(priority=Priority.HIGH.value, category="Development")
    print(f"\nFilter (HIGH priority + Development category): {len(filtered)} results")
    for task in filtered[:3]:
        print(f"  - {task.title}")

    # Feature 10: Export to CSV/JSON
    print("\n10. EXPORT FUNCTIONALITY")
    print("-" * 60)

    # Export all tasks to CSV
    csv_success = manager.export_to_csv("example_export.csv")
    print(f"Export to CSV: {'Success' if csv_success else 'Failed'}")

    # Export all tasks to JSON
    json_success = manager.export_to_json("example_export.json")
    print(f"Export to JSON: {'Success' if json_success else 'Failed'}")

    # Export only completed tasks
    manager.complete_task(bulk_task1.id)
    manager.complete_task(bulk_task2.id)
    completed_tasks = manager.filter_tasks(status="completed")
    completed_export = manager.export_to_csv("completed_tasks.csv", completed_tasks)
    print(f"Export {len(completed_tasks)} completed tasks: {'Success' if completed_export else 'Failed'}")

    # Statistics
    print("\n" + "=" * 60)
    print("FINAL STATISTICS")
    print("=" * 60)
    stats = manager.get_statistics()
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
    print(f"Total Time Tracked: {stats['total_time_minutes']:.2f} minutes")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE!")
    print("=" * 60)
    print("\nAll 10 features have been demonstrated successfully.")
    print("Data saved to: example_tasks.json")
    print("Exports saved to: example_export.csv, example_export.json")


if __name__ == "__main__":
    main()
