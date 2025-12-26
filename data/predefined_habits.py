"""
Predefined habits with 4 weeks of example tracking data.

This module provides test fixtures with realistic habit data for testing
and demonstration purposes as required by the project specification.
"""
from datetime import datetime, timedelta
from typing import List

from model.habit import Habit


def get_predefined_habits() -> List[Habit]:
    """
    Create and return 5 predefined habits with initial state.
    
    Returns:
        List of 5 Habit objects (3 daily, 2 weekly)
    """
    base_date = datetime.now() - timedelta(days=28)  # 4 weeks ago
    
    habits = [
        Habit(
            name="Morning Exercise",
            description="30 minutes of exercise every morning",
            periodicity="daily",
            created_date=base_date
        ),
        Habit(
            name="Read Book",
            description="Read at least 20 pages of a book",
            periodicity="daily",
            created_date=base_date
        ),
        Habit(
            name="Drink Water",
            description="Drink at least 8 glasses of water",
            periodicity="daily",
            created_date=base_date
        ),
        Habit(
            name="Weekly Review",
            description="Review goals and plan for the upcoming week",
            periodicity="weekly",
            created_date=base_date
        ),
        Habit(
            name="Clean Room",
            description="Deep clean and organize living space",
            periodicity="weekly",
            created_date=base_date
        )
    ]
    
    return habits


def get_sample_completion_dates() -> dict:
    """
    Generate 4 weeks of realistic completion data for each predefined habit.
    
    Returns:
        Dictionary mapping habit names to lists of completion datetimes
    """
    today = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    
    completions = {}
    
    # Morning Exercise - Good consistency, 22 out of 28 days (missed 6 days)
    # Simulates someone who exercises most days but sometimes skips
    exercise_dates = []
    for i in range(28, 0, -1):
        day = today - timedelta(days=i)
        # Skip some days to simulate realistic behavior
        if i not in [3, 8, 12, 15, 21, 25]:  # Missed days
            exercise_dates.append(day)
    completions["Morning Exercise"] = exercise_dates
    
    # Read Book - Very consistent, 26 out of 28 days
    # Simulates a dedicated reader who rarely misses
    reading_dates = []
    for i in range(28, 0, -1):
        day = today - timedelta(days=i)
        if i not in [14, 20]:  # Only missed 2 days
            reading_dates.append(day)
    completions["Read Book"] = reading_dates
    
    # Drink Water - Perfect streak for last 14 days, some misses before
    # Simulates someone who improved their habit halfway through
    water_dates = []
    for i in range(28, 0, -1):
        day = today - timedelta(days=i)
        if i <= 14 or i in [16, 18, 22, 24, 26, 28]:  # Perfect last 2 weeks
            water_dates.append(day)
    completions["Drink Water"] = water_dates
    
    # Weekly Review - Done 3 out of 4 weeks
    # Week numbers calculated from start date
    weekly_review_dates = []
    for week in range(4):
        if week != 2:  # Missed week 3
            # Complete on Sunday of each week
            completion_day = today - timedelta(days=28) + timedelta(days=week*7 + 6)
            weekly_review_dates.append(completion_day)
    completions["Weekly Review"] = weekly_review_dates
    
    # Clean Room - Done all 4 weeks (perfect weekly habit)
    clean_room_dates = []
    for week in range(4):
        # Complete on Saturday of each week
        completion_day = today - timedelta(days=28) + timedelta(days=week*7 + 5)
        clean_room_dates.append(completion_day)
    completions["Clean Room"] = clean_room_dates
    
    return completions


def load_predefined_data(connection) -> List[Habit]:
    """
    Load predefined habits with their completion history into the database.
    
    This applies the 4 weeks of sample data to create realistic habit states
    with proper streak calculations.
    
    Args:
        connection: Active SQLite database connection
        
    Returns:
        List of Habit objects with applied completion data
    """
    from database.sqlitedb import save_habit, save_completion
    
    habits = get_predefined_habits()
    completions = get_sample_completion_dates()
    
    # Apply completions to habits and save
    for habit in habits:
        habit_completions = completions.get(habit.name, [])
        
        # Sort completions chronologically and apply each one
        for completion_date in sorted(habit_completions):
            habit.check_off(completion_date)
            save_completion(connection, habit.name, completion_date)
        
        # Save the habit with updated streak info
        save_habit(connection, habit)
    
    return habits