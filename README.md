# Python Task Manager CLI

A comprehensive command-line task management application with advanced features for organizing, tracking, and managing tasks efficiently.

## Features

### 1. Task Priorities
- Four priority levels: Low, Medium, High, Urgent
- Quick filtering and sorting by priority
- Visual priority indicators in task lists

### 2. Due Dates with Reminders
- Set due dates for tasks
- Automatic reminder notifications before due dates
- Track overdue tasks
- List tasks due within specific timeframes

### 3. Categories and Tags
- Organize tasks with multiple categories
- Add flexible tags for enhanced filtering
- View all tasks by category or tag
- Bulk categorization and tagging

### 4. Recurring Tasks
- Create daily, weekly, monthly, or yearly recurring tasks
- Automatic generation of next instances upon completion
- Customizable recurrence intervals

### 5. Task Dependencies
- Define task dependencies
- Track blocked tasks
- Ensure proper task ordering
- View dependency chains

### 6. Time Tracking
- Start and stop time tracking sessions
- Track multiple time entries per task
- View total time spent on tasks
- Add notes to time tracking sessions

### 7. Task Templates
- Create reusable task templates
- Quick task creation from templates
- Template-based workflow optimization

### 8. Bulk Operations
- Update multiple tasks simultaneously
- Bulk complete tasks
- Bulk delete operations
- Mass categorization and tagging

### 9. Search and Filters
- Full-text search across task fields
- Advanced filtering by status, priority, category, tag
- Combine multiple filter criteria
- Quick access to relevant tasks

### 10. Export Functionality
- Export tasks to CSV format
- Export tasks to JSON format
- Filter before export
- Complete task data preservation

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/python-task-manager-cli.git
cd python-task-manager-cli

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Task Management

```bash
# Create a task
python cli.py create "Complete project documentation" -d "Write comprehensive docs" -p high

# List all tasks
python cli.py list

# Show task details
python cli.py show <task_id>

# Update a task
python cli.py update <task_id> -t "New title" -p urgent

# Complete a task
python cli.py complete <task_id>

# Delete a task
python cli.py delete <task_id>
```

### Priority Management

```bash
# Set task priority
python cli.py priority <task_id> urgent

# List tasks by priority
python cli.py list-priority high
```

### Due Dates and Reminders

```bash
# Set due date with reminder
python cli.py set-due <task_id> "2025-12-31" -r 60

# View overdue tasks
python cli.py overdue

# View tasks due soon (next 24 hours by default)
python cli.py due-soon -h 48

# Check reminders
python cli.py reminders
```

### Categories and Tags

```bash
# Add category to task
python cli.py add-category <task_id> "Development"

# Add tag to task
python cli.py add-tag <task_id> "frontend"

# Remove category
python cli.py remove-category <task_id> "Development"

# List all categories
python cli.py list-categories

# List all tags
python cli.py list-tags
```

### Recurring Tasks

```bash
# Make task recurring
python cli.py make-recurring <task_id> weekly -i 2

# List recurring tasks
python cli.py list-recurring
```

### Task Dependencies

```bash
# Add dependency
python cli.py add-dependency <task_id> <depends_on_task_id>

# Remove dependency
python cli.py remove-dependency <task_id> <depends_on_task_id>

# View blocked tasks
python cli.py blocked

# View task dependencies
python cli.py dependencies <task_id>
```

### Time Tracking

```bash
# Start time tracking
python cli.py start-timer <task_id> -n "Working on implementation"

# Stop time tracking
python cli.py stop-timer <task_id> <entry_id>

# View time tracking
python cli.py show-time <task_id>
```

### Templates

```bash
# Create template
python cli.py create-template "bug-fix" "Fix bug in module" -p high -c "Development" -t "bug"

# Create task from template
python cli.py from-template "bug-fix" --due "2025-12-15"

# List templates
python cli.py list-templates
```

### Bulk Operations

```bash
# Bulk update
python cli.py bulk-update <id1> <id2> <id3> -p high -s in-progress

# Bulk complete
python cli.py bulk-complete <id1> <id2> <id3>

# Bulk delete
python cli.py bulk-delete <id1> <id2> <id3>

# Bulk add category
python cli.py bulk-category "Sprint-1" <id1> <id2> <id3>

# Bulk add tag
python cli.py bulk-tag "urgent" <id1> <id2> <id3>
```

### Search and Filter

```bash
# Search tasks
python cli.py search "documentation" -f title description

# Filter tasks
python cli.py filter -s pending -p high -c "Development"
```

### Export

```bash
# Export to CSV
python cli.py export-csv tasks.csv

# Export to JSON
python cli.py export-json tasks.json

# Export with filter
python cli.py export-csv completed_tasks.csv -s completed
```

### Statistics

```bash
# View task statistics
python cli.py stats
```

## Storage Options

The application supports two storage backends:

- **JSON Storage** (default): Simple file-based storage
- **SQLite Storage**: Relational database storage

To use SQLite, modify `cli.py`:
```python
cli = TaskCLI(use_sqlite=True)
```

## Data Models

### Task
- ID, title, description
- Priority (low, medium, high, urgent)
- Status (pending, in-progress, completed)
- Created/updated timestamps
- Due date and completion date
- Categories and tags
- Recurrence settings
- Dependencies
- Time tracking entries
- Reminder settings

### TaskTemplate
- Template name
- Default title and description
- Default priority
- Default categories and tags
- Default time estimates

### TimeEntry
- Entry ID
- Start/end timestamps
- Duration in minutes
- Session notes

## Architecture

```
python-task-manager-cli/
├── models.py           # Data models (Task, TaskTemplate, TimeEntry)
├── storage.py          # Storage layer (JSON and SQLite)
├── business_logic.py   # Core business logic (TaskManager)
├── cli.py             # Command-line interface
├── requirements.txt    # Python dependencies
└── README.md          # Documentation
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

MIT License
