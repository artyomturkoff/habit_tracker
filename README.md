# Habit Tracker Application

A command-line habit tracking application built in Python that helps users build and maintain good habits through daily/weekly tracking, streak monitoring, and analytics.

---

## Table of Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Running the Application](#running-the-application)
5. [How to Use](#how-to-use)
   - [Main Menu](#main-menu)
   - [Checking Off Habits](#1-check-off-habit)
   - [Viewing Habits](#2-view-all-habits)
   - [Managing Habits](#3-manage-habits)
   - [Analytics](#4-analytics)
6. [Predefined Habits](#predefined-habits)
7. [Understanding Streaks](#understanding-streaks)
8. [Project Structure](#project-structure)
9. [Running Tests](#running-tests)
10. [Technical Documentation](#technical-documentation)

---

## Overview

This habit tracker allows you to:

- **Create habits** with daily or weekly periodicity
- **Check off habits** when completed to build streaks
- **Track progress** with current and longest streak statistics
- **Analyse habits** using various filters and reports
- **Persist data** automatically using SQLite database

The application comes pre-loaded with 5 sample habits and 4 weeks of tracking data for demonstration purposes.

---

## Requirements

- **Python 3.7** or later
- **pytest** (optional, for running unit tests)

No additional external libraries are required - the application uses only Python standard library modules (`sqlite3`, `datetime`, `os`, `sys`, `typing`).

---

## Installation

### Step 1: Download the Project

Download or clone the project files to your computer. The project should have this structure:

```
habit_tracker/
├── main.py
├── README.md
├── model/
│   └── habit.py
├── database/
│   └── sqlitedb.py
├── analytics/
│   └── analytics.py
├── data/
│   └── predefined_habits.py
└── tests/
    └── test_habit_tracker.py
```

### Step 2: Navigate to Project Directory

Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and navigate to the project folder:

```bash
cd path/to/habit_tracker
```

### Step 3: Verify Python Installation

Ensure Python 3.7+ is installed:

```bash
python --version
```

or on some systems:

```bash
python3 --version
```

You should see output like `Python 3.9.7` (version 3.7 or higher).

### Step 4: (Optional) Install pytest for Testing

If you want to run the unit tests:

```bash
pip install pytest
```

or:

```bash
pip3 install pytest
```

---

## Running the Application

### Starting the Habit Tracker

From the project directory, run:

```bash
python main.py
```

or on some systems:

```bash
python3 main.py
```

### What Happens on First Run

When you start the application for the first time:

1. The database file (`data/habits.db`) is created automatically
2. Database tables are initialized
3. Five predefined habits with 4 weeks of sample data are loaded
4. The main menu is displayed

```
==================================================
  Habit Tracker
==================================================

Initializing...
ℹ Loading predefined habits with sample data...
✓ Predefined habits loaded successfully!
✓ Application ready!

Press Enter to continue...
```

### Subsequent Runs

On subsequent runs, your existing data is loaded automatically from the database:

```
==================================================
  Habit Tracker
==================================================

Initializing...
✓ Application ready!

Press Enter to continue...
```

---

## How to Use

### Main Menu

After initialization, you'll see the main menu:

```
==================================================
  HABIT TRACKER - Main Menu
==================================================

  1. Check Off Habit
  2. View All Habits
  3. Manage Habits
  4. Analytics
  5. Exit
--------------------------------------------------

Enter your choice (1-5):
```

Enter a number (1-5) and press Enter to select an option.

---

### 1. Check Off Habit

**Purpose:** Mark a habit as completed for the current period.

**How it works:**
- Displays only habits that haven't been completed yet today (for daily habits) or this week (for weekly habits)
- Select a habit by entering its number
- The system records the completion, updates your streak, and saves to the database

**Example:**
```
==================================================
  Check Off Habit
==================================================

Habits to complete:
--------------------------------------------------
  1. Morning Exercise (daily) [pending]
     Current streak: 5
  2. Read Book (daily) [OVERDUE]
     Current streak: 0

  0. Return to Main Menu
--------------------------------------------------

Select habit to check off (0 to cancel): 1

✓ 'Morning Exercise' checked off!
✓ Current streak: 6
✓ 🎉 New longest streak: 6!

Press Enter to continue...
```

---

### 2. View All Habits

**Purpose:** Display all your habits with their current status and streaks.

**Status indicators:**
- `✓` = Completed for this period
- `○` = Pending (not yet completed)
- `⚠` = Overdue (missed the deadline)

**Example:**
```
==================================================
  View All Habits
==================================================

Total habits: 5

--------------------------------------------------

✓ Morning Exercise
   Description: 30 minutes of exercise every morning
   Periodicity: daily
   Current streak: 6
   Longest streak: 6
   Due: 2024-01-16 23:59

○ Read Book
   Description: Read at least 20 pages of a book
   Periodicity: daily
   Current streak: 3
   Longest streak: 7
   Due: 2024-01-15 23:59

...

--------------------------------------------------

Legend: ✓ = Completed  ○ = Pending  ⚠ = Overdue

Press Enter to continue...
```

---

### 3. Manage Habits

**Purpose:** Create new habits or delete existing ones.

```
==================================================
  Manage Habits
==================================================

  1. Create New Habit
  2. Delete Habit
  0. Return to Main Menu
--------------------------------------------------

Enter your choice (0-2):
```

#### Creating a New Habit

1. Select option `1`
2. Enter a name for your habit
3. Enter a description
4. Choose periodicity: `1` for Daily or `2` for Weekly

**Example:**
```
==================================================
  Create New Habit
==================================================

Habit name: Meditate
Description: 10 minutes of morning meditation
Periodicity:
  1. Daily
  2. Weekly

Select periodicity (1 or 2): 1

✓ Habit 'Meditate' created successfully!

Press Enter to continue...
```

#### Deleting a Habit

1. Select option `2`
2. Choose the habit to delete by number
3. Confirm deletion by typing `yes`

**Example:**
```
==================================================
  Delete Habit
==================================================

Select habit to delete:
--------------------------------------------------
  1. Morning Exercise (daily)
  2. Read Book (daily)
  3. Meditate (daily)

  0. Cancel
--------------------------------------------------

Select habit (0 to cancel): 3

Delete 'Meditate'? (yes/no): yes

✓ Habit 'Meditate' deleted.

Press Enter to continue...
```

---

### 4. Analytics

**Purpose:** View statistics and analysis of your habits.

```
==================================================
  Analytics Menu
==================================================

  1. All Tracked Habits
  2. Habits by Periodicity
  3. Max Streak for Each Habit
  4. Longest Streak Overall
  5. Return to Main Menu
--------------------------------------------------

Enter your choice (1-5):
```

#### Option 1: All Tracked Habits

Lists all habits you're currently tracking with their descriptions.

#### Option 2: Habits by Periodicity

Filter habits by daily or weekly:
```
  1. Daily habits
  2. Weekly habits

Select periodicity (1 or 2): 1

Daily Habits (3):
--------------------------------------------------
  • Morning Exercise
    Streak: 6 (best: 6)

  • Read Book
    Streak: 3 (best: 7)

  • Drink Water
    Streak: 14 (best: 14)
```

#### Option 3: Max Streak for Each Habit

Shows the longest streak achieved for every habit:
```
==================================================
  Max Streak for Each Habit
==================================================

Habit                          Longest Streak
--------------------------------------------------
  Drink Water                    14
  Read Book                      7
  Morning Exercise               6
  Clean Room                     4
  Weekly Review                  2
```

#### Option 4: Longest Streak Overall

Shows which habit has the best streak:
```
==================================================
  Longest Streak Overall
==================================================

🏆 Best Habit: Drink Water
   Longest Streak: 14
   Current Streak: 14
   Periodicity: daily
```

---

## Predefined Habits

The application comes with 5 predefined habits loaded with 4 weeks of sample tracking data:

| Habit | Periodicity | Description |
|-------|-------------|-------------|
| Morning Exercise | Daily | 30 minutes of exercise every morning |
| Read Book | Daily | Read at least 20 pages of a book |
| Drink Water | Daily | Drink at least 8 glasses of water |
| Weekly Review | Weekly | Review goals and plan for the upcoming week |
| Clean Room | Weekly | Deep clean and organize living space |

This sample data demonstrates various streak patterns and helps you understand how the tracking works.

---

## Understanding Streaks

### What is a Streak?

A streak counts how many consecutive periods you've completed a habit without missing.

### How Streaks Work

**Daily Habits:**
- Must be completed once per calendar day
- Missing a day resets your current streak to 0
- Example: Complete exercise Mon, Tue, Wed = 3-day streak

**Weekly Habits:**
- Must be completed once per calendar week (Monday to Sunday)
- Missing a week resets your current streak to 0
- Example: Complete review Week 1, Week 2, Week 3 = 3-week streak

### Current vs Longest Streak

- **Current Streak:** Your active consecutive completions
- **Longest Streak:** The best streak you've ever achieved (never resets)

### Due Dates

- **Daily habits:** Due by end of the next day after last completion
- **Weekly habits:** Due by end of Sunday of the following week

---

## Project Structure

```
habit_tracker/
│
├── main.py                      # CLI application entry point and user flow
│
├── model/
│   └── habit.py                 # Defines the Habit class with all habit logic (OOP implementation)
│
├── database/
│   └── sqlitedb.py              # Handles all database operations
│
├── analytics/
│   └── analytics.py             # Provides habits analytics
│
├── data/
│   ├── habits.db                # SQLite database (created on first run)
│   └── predefined_habits.py     # Sample habits and test data
│
├── tests/
│   └── test_habit_tracker.py    # Unit tests
│
└── README.md                    # This file
```

---

## Running Tests

The project includes 34 unit tests covering:

- Habit model creation and validation
- Streak calculations
- Database CRUD operations
- Analytics functions
- Integration scenarios

### Running All Tests

```bash
# Using pytest (recommended)
pytest tests/ -v

# Or using Python's pytest module
python -m pytest tests/ -v
```

### Expected Output

```
============================= test session starts ==============================
collected 34 items

tests/test_habit_tracker.py::TestHabitModel::test_create_valid_daily_habit PASSED
tests/test_habit_tracker.py::TestHabitModel::test_create_valid_weekly_habit PASSED
tests/test_habit_tracker.py::TestHabitModel::test_invalid_empty_name PASSED
...
tests/test_habit_tracker.py::TestIntegration::test_full_habit_lifecycle PASSED
tests/test_habit_tracker.py::TestIntegration::test_streak_reset_on_missed_period PASSED

============================== 34 passed in 0.04s ==============================
```

---

## Technical Documentation

### Habit Class Usage

```python
from model.habit import Habit
from datetime import datetime

# Create a new habit
habit = Habit(
    name="Exercise",
    description="Daily workout routine",
    periodicity="daily",  # or "weekly"
    created_date=datetime.now()
)

# Check off the habit
success = habit.check_off()  # Returns True if successful

# Access habit properties
print(habit.current_streak)   # Current consecutive completions
print(habit.longest_streak)   # Best streak ever
print(habit.is_overdue())     # Whether habit is past due
print(habit.is_completed_today())  # Completed in current period
```

### Database Operations

```python
from database.sqlitedb import (
    get_database_connection,
    initialize_database,
    save_habit,
    load_all_habits,
    load_habit_by_name,
    delete_habit
)

# Connect and initialize
conn = get_database_connection()
initialize_database(conn)

# Save a habit
save_habit(conn, habit)

# Load habits
all_habits = load_all_habits(conn)
single_habit = load_habit_by_name(conn, "Exercise")

# Delete a habit
delete_habit(conn, "Exercise")

# Close connection when done
conn.close()
```

### Analytics Functions

```python
from analytics.analytics import (
    get_all_habits,
    get_habits_by_periodicity,
    get_longest_streak_all_habits,
    get_longest_streak_for_habit,
    get_max_streak_per_habit
)

# Get all habits
habits = get_all_habits(habit_list)

# Filter by periodicity
daily_habits = get_habits_by_periodicity(habit_list, "daily")
weekly_habits = get_habits_by_periodicity(habit_list, "weekly")

# Find best overall streak
habit_name, streak = get_longest_streak_all_habits(habit_list)

# Get streak for specific habit
streak = get_longest_streak_for_habit(habit)

# Get all max streaks
streaks = get_max_streak_per_habit(habit_list)  # [(name, streak), ...]
```

---

## Troubleshooting

### "Module not found" Error

Ensure you're running the application from the `habit_tracker` directory:

```bash
cd habit_tracker
python main.py
```

### Database Issues

To reset the application and start fresh, delete the database file:

```bash
rm data/habits.db
```

The next run will recreate it with predefined data.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/artyomturkoff/habit_tracker/blob/main/LICENSE) file for details.

