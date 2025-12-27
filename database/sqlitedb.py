"""
Database module for habit tracking application.
Handles all SQLite operations for persistent storage.
"""
import sqlite3
from datetime import datetime
from typing import List, Optional
import os

from model.habit import Habit


def get_database_connection(db_path: str = "data/habits.db") -> sqlite3.Connection:
    """
    Create and return a connection to the SQLite database.
    
    The database file will be created automatically if it doesn't exist.
    """
    # Create directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    
    # Connect to database (creates file if doesn't exist)
    connection = sqlite3.connect(db_path)
    
    # Enable foreign key support
    connection.execute("PRAGMA foreign_keys = ON")
    
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    """
    Create the database tables if they don't exist.
    
    This should be called when the app starts to ensure
    the database schema is set up properly.

    """
    # Create habits table (IF NOT EXISTS to prevent errors on restart)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            name TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            periodicity TEXT NOT NULL CHECK(periodicity IN ('daily', 'weekly')),
            created_date TEXT NOT NULL,
            last_completion_date TEXT,
            due_date TEXT,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0
        )
    """)
    
    # Create completions table for tracking history
    connection.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_name TEXT NOT NULL,
            completion_date TEXT NOT NULL,
            FOREIGN KEY (habit_name) REFERENCES habits(name) ON DELETE CASCADE,
            UNIQUE(habit_name, completion_date)
        )
    """)
    
    connection.commit()


def is_database_initialized(connection: sqlite3.Connection) -> bool:
    """
    Check if the database tables exist.
    """
    cursor = connection.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='habits'
    """)
    return cursor.fetchone() is not None


def save_habit(connection: sqlite3.Connection, habit: Habit) -> None:
    """
    Save or update a habit in the database.
    
    If the habit already exists (same name), it will be updated.
    If it's new, it will be inserted.
    """
    connection.execute("""
        INSERT OR REPLACE INTO habits 
        (name, description, periodicity, created_date, 
         last_completion_date, due_date, current_streak, longest_streak)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        habit.name,
        habit.description,
        habit.periodicity,
        habit.created_date.isoformat(),
        habit.last_completion_date.isoformat() if habit.last_completion_date else None,
        habit.due_date.isoformat() if habit.due_date else None,
        habit.current_streak,
        habit.longest_streak
    ))
    
    connection.commit()


def load_all_habits(connection: sqlite3.Connection) -> List[Habit]:
    """
    Load all habits from the database.
    """
    cursor = connection.execute("""
        SELECT name, description, periodicity, created_date,
               last_completion_date, due_date, current_streak, longest_streak
        FROM habits
        ORDER BY name
    """)
    
    habits = []
    for row in cursor.fetchall():
        habit = Habit(
            name=row[0],
            description=row[1],
            periodicity=row[2],
            created_date=datetime.fromisoformat(row[3]),
            last_completion_date=datetime.fromisoformat(row[4]) if row[4] else None,
            due_date=datetime.fromisoformat(row[5]) if row[5] else None,
            current_streak=row[6],
            longest_streak=row[7]
        )
        habits.append(habit)
    
    return habits


def load_habit_by_name(connection: sqlite3.Connection, habit_name: str) -> Optional[Habit]:
    """
    Load a specific habit from the database by name.
    """
    cursor = connection.execute("""
        SELECT name, description, periodicity, created_date,
               last_completion_date, due_date, current_streak, longest_streak
        FROM habits
        WHERE name = ?
    """, (habit_name,))
    
    row = cursor.fetchone()
    if row is None:
        return None
    
    return Habit(
        name=row[0],
        description=row[1],
        periodicity=row[2],
        created_date=datetime.fromisoformat(row[3]),
        last_completion_date=datetime.fromisoformat(row[4]) if row[4] else None,
        due_date=datetime.fromisoformat(row[5]) if row[5] else None,
        current_streak=row[6],
        longest_streak=row[7]
    )


def habit_exists(connection: sqlite3.Connection, habit_name: str) -> bool:
    """
    Check if a habit with the given name exists.
    """
    cursor = connection.execute(
        "SELECT 1 FROM habits WHERE name = ?",
        (habit_name,)
    )
    return cursor.fetchone() is not None


def save_completion(connection: sqlite3.Connection, habit_name: str, 
                   completion_date: datetime) -> None:
    """
    Log a habit completion to the database.
    """
    try:
        connection.execute("""
            INSERT INTO completions (habit_name, completion_date)
            VALUES (?, ?)
        """, (
            habit_name,
            completion_date.isoformat()
        ))
        connection.commit()
    except sqlite3.IntegrityError:
        # Completion already exists for this habit and date - ignore
        pass


def get_completions_for_habit(connection: sqlite3.Connection, habit_name: str) -> List[datetime]:
    """
    Get all completion dates sorted chronologically for a specific habit.
    """
    cursor = connection.execute("""
        SELECT completion_date FROM completions
        WHERE habit_name = ?
        ORDER BY completion_date
    """, (habit_name,))
    
    return [datetime.fromisoformat(row[0]) for row in cursor.fetchall()]


def delete_habit(connection: sqlite3.Connection, habit_name: str) -> bool:
    """
    Delete a habit and all its completions from the database.
    """
    cursor = connection.execute(
        "DELETE FROM habits WHERE name = ?",
        (habit_name,)
    )
    
    connection.commit()
    
    return cursor.rowcount > 0


def get_habit_count(connection: sqlite3.Connection) -> int:
    """
    Get the total number of habits in the database.
    """
    cursor = connection.execute("SELECT COUNT(*) FROM habits")
    return cursor.fetchone()[0]
