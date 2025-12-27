"""
Unit tests for the Habit Tracking Application.

Run with: pytest tests/ -v
Or: python -m pytest tests/ -v
"""
import pytest
import sqlite3
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.habit import Habit
from database.sqlitedb import (
    get_database_connection,
    initialize_database,
    save_habit,
    load_all_habits,
    load_habit_by_name,
    delete_habit,
    habit_exists,
    save_completion,
    get_completions_for_habit
)
from analytics.analytics import (
    get_all_habits,
    get_habits_by_periodicity,
    get_longest_streak_all_habits,
    get_longest_streak_for_habit,
    get_current_streak_for_habit,
    get_habits_sorted_by_streak,
    get_not_completed_habits,
    get_max_streak_per_habit
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_db():
    """
    Create a test database connection.
    """
    # Use in-memory database for tests
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    initialize_database(connection)
    yield connection
    connection.close()


@pytest.fixture
def sample_daily_habit():
    """
    Create a sample daily habit.
    """
    return Habit(
        name="Test Daily Habit",
        description="A test habit for daily tasks",
        periodicity="daily",
        created_date=datetime.now()
    )


@pytest.fixture
def sample_weekly_habit():
    """
    Create a sample weekly habit.
    """
    return Habit(
        name="Test Weekly Habit",
        description="A test habit for weekly tasks",
        periodicity="weekly",
        created_date=datetime.now()
    )


@pytest.fixture
def sample_habits_list():
    """
    Create a list of sample habits with various states.
    """
    base_date = datetime.now() - timedelta(days=7)
    
    habits = [
        Habit(
            name="Exercise",
            description="Daily exercise",
            periodicity="daily",
            created_date=base_date,
            current_streak=5,
            longest_streak=10
        ),
        Habit(
            name="Read",
            description="Daily reading",
            periodicity="daily",
            created_date=base_date,
            current_streak=3,
            longest_streak=7
        ),
        Habit(
            name="Weekly Review",
            description="Weekly planning",
            periodicity="weekly",
            created_date=base_date,
            current_streak=2,
            longest_streak=4
        ),
        Habit(
            name="Clean",
            description="Weekly cleaning",
            periodicity="weekly",
            created_date=base_date,
            current_streak=1,
            longest_streak=3
        )
    ]
    
    return habits


# ============================================================================
# HABIT MODEL TESTS
# ============================================================================

class TestHabitModel:
    """
    Tests for the Habit class.
    """
    
    def test_create_valid_daily_habit(self):
        """Test creating a valid daily habit."""
        habit = Habit(
            name="Test Habit",
            description="Test description",
            periodicity="daily",
            created_date=datetime.now()
        )
        
        assert habit.name == "Test Habit"
        assert habit.description == "Test description"
        assert habit.periodicity == "daily"
        assert habit.current_streak == 0
        assert habit.longest_streak == 0
    
    def test_create_valid_weekly_habit(self):
        """
        Test creating a valid weekly habit.
        """
        habit = Habit(
            name="Weekly Habit",
            description="Weekly task",
            periodicity="weekly",
            created_date=datetime.now()
        )
        
        assert habit.periodicity == "weekly"
    
    def test_invalid_empty_name(self):
        """
        Test that empty name raises ValueError.
        """
        with pytest.raises(ValueError):
            Habit(
                name="",
                description="Test",
                periodicity="daily",
                created_date=datetime.now()
            )
    
    def test_invalid_empty_description(self):
        """
        Test that empty description raises ValueError.
        """
        with pytest.raises(ValueError):
            Habit(
                name="Test",
                description="",
                periodicity="daily",
                created_date=datetime.now()
            )
    
    def test_invalid_periodicity(self):
        """
        Test that invalid periodicity raises ValueError.
        """
        with pytest.raises(ValueError):
            Habit(
                name="Test",
                description="Test",
                periodicity="monthly",  # Invalid
                created_date=datetime.now()
            )
    
    def test_check_off_increments_streak(self, sample_daily_habit):
        """
        Test that check_off increments the streak.
        """
        initial_streak = sample_daily_habit.current_streak
        
        result = sample_daily_habit.check_off()
        
        assert result is True
        assert sample_daily_habit.current_streak == initial_streak + 1
    
    def test_check_off_updates_longest_streak(self, sample_daily_habit):
        """
        Test that check_off updates longest streak when appropriate.
        """
        sample_daily_habit.check_off()
        
        assert sample_daily_habit.longest_streak >= sample_daily_habit.current_streak
    
    def test_check_off_same_day_returns_false(self, sample_daily_habit):
        """
        Test that checking off twice in same period returns False.
        """
        sample_daily_habit.check_off()
        
        result = sample_daily_habit.check_off()
        
        assert result is False
    
    def test_check_off_sets_due_date(self, sample_daily_habit):
        """
        Test that check_off sets the due date.
        """
        assert sample_daily_habit.due_date is None
        
        sample_daily_habit.check_off()
        
        assert sample_daily_habit.due_date is not None
    
    def test_is_overdue_returns_false_when_no_due_date(self, sample_daily_habit):
        """
        Test is_overdue returns False when no due date is set.
        """
        assert sample_daily_habit.is_overdue() is False
    
    def test_to_dict_conversion(self, sample_daily_habit):
        """
        Test conversion to dictionary.
        """
        habit_dict = sample_daily_habit.to_dict()
        
        assert habit_dict['name'] == sample_daily_habit.name
        assert habit_dict['description'] == sample_daily_habit.description
        assert habit_dict['periodicity'] == sample_daily_habit.periodicity
        assert 'created_date' in habit_dict
    
    def test_from_dict_conversion(self, sample_daily_habit):
        """
        Test creation from a dictionary.
        """
        habit_dict = sample_daily_habit.to_dict()
        
        reconstructed = Habit.from_dict(habit_dict)
        
        assert reconstructed.name == sample_daily_habit.name
        assert reconstructed.description == sample_daily_habit.description
        assert reconstructed.periodicity == sample_daily_habit.periodicity


# ============================================================================
# DATABASE TESTS
# ============================================================================

class TestDatabase:
    """
    Tests for database operations.
    """
    
    def test_save_and_load_habit(self, test_db, sample_daily_habit):
        """
        Test saving and loading a habit.
        """
        save_habit(test_db, sample_daily_habit)
        
        habits = load_all_habits(test_db)
        
        assert len(habits) == 1
        assert habits[0].name == sample_daily_habit.name
    
    def test_load_habit_by_name(self, test_db, sample_daily_habit):
        """
        Test loading a specific habit by name.
        """
        save_habit(test_db, sample_daily_habit)
        
        loaded = load_habit_by_name(test_db, sample_daily_habit.name)
        
        assert loaded is not None
        assert loaded.name == sample_daily_habit.name
    
    def test_load_nonexistent_habit_returns_none(self, test_db):
        """
        Test loading a habit that doesn't exist.
        """
        loaded = load_habit_by_name(test_db, "Nonexistent Habit")
        
        assert loaded is None
    
    def test_habit_exists(self, test_db, sample_daily_habit):
        """
        Test checking if a habit exists.
        """
        assert habit_exists(test_db, sample_daily_habit.name) is False
        
        save_habit(test_db, sample_daily_habit)
        
        assert habit_exists(test_db, sample_daily_habit.name) is True
    
    def test_delete_habit(self, test_db, sample_daily_habit):
        """
        Test deleting a habit.
        """
        save_habit(test_db, sample_daily_habit)
        assert habit_exists(test_db, sample_daily_habit.name) is True
        
        result = delete_habit(test_db, sample_daily_habit.name)
        
        assert result is True
        assert habit_exists(test_db, sample_daily_habit.name) is False
    
    def test_delete_nonexistent_habit_returns_false(self, test_db):
        """
        Test deleting a habit that doesn't exist.
        """
        result = delete_habit(test_db, "Nonexistent")
        
        assert result is False
    
    def test_save_completion(self, test_db, sample_daily_habit):
        """
        Test saving a completion record.
        """
        save_habit(test_db, sample_daily_habit)
        completion_time = datetime.now()
        
        save_completion(test_db, sample_daily_habit.name, completion_time)
        
        completions = get_completions_for_habit(test_db, sample_daily_habit.name)
        assert len(completions) == 1
    
    def test_update_existing_habit(self, test_db, sample_daily_habit):
        """
        Test updating an existing habit.
        """
        save_habit(test_db, sample_daily_habit)
        
        sample_daily_habit.check_off()
        save_habit(test_db, sample_daily_habit)
        
        loaded = load_habit_by_name(test_db, sample_daily_habit.name)
        assert loaded.current_streak == sample_daily_habit.current_streak


# ============================================================================
# ANALYTICS TESTS
# ============================================================================

class TestAnalytics:
    """
    Tests for analytics module (functional programming).
    """
    
    def test_get_all_habits(self, sample_habits_list):
        """
        Test getting all habits.
        """
        result = get_all_habits(sample_habits_list)
        
        assert len(result) == len(sample_habits_list)

    def test_get_not_completed_habits_filters_completed(self):
        """
        Test that completed habits are excluded from the get_not_completed_habits() results.
        """
        completed_habit = Habit(
            name="Done Today",
            description="Already completed",
            periodicity="daily",
            created_date=datetime.now()
        )
        completed_habit.check_off()  # Mark as done
        
        pending_habit = Habit(
            name="Still Pending",
            description="Not done yet",
            periodicity="daily",
            created_date=datetime.now()
        )
        
        habits = [completed_habit, pending_habit]
        not_completed = get_not_completed_habits(habits)
        
        assert len(not_completed) == 1
        assert not_completed[0].name == "Still Pending"    
    
    def test_get_habits_by_periodicity_daily(self, sample_habits_list):
        """
        Test filtering daily habits.
        """
        result = get_habits_by_periodicity(sample_habits_list, "daily")
        
        assert len(result) == 2
        assert all(h.periodicity == "daily" for h in result)
    
    def test_get_habits_by_periodicity_weekly(self, sample_habits_list):
        """
        Test filtering weekly habits.
        """
        result = get_habits_by_periodicity(sample_habits_list, "weekly")
        
        assert len(result) == 2
        assert all(h.periodicity == "weekly" for h in result)
    
    def test_get_longest_streak_all_habits(self, sample_habits_list):
        """
        Test finding the longest streak across all habits.
        """
        habit_name, streak = get_longest_streak_all_habits(sample_habits_list)
        
        assert habit_name == "Exercise"  # Has longest_streak of 10
        assert streak == 10
    
    def test_get_longest_streak_empty_list(self):
        """
        Test the longest streak with an empty list.
        """
        habit_name, streak = get_longest_streak_all_habits([])
        
        assert habit_name is None
        assert streak == 0
    
    def test_get_longest_streak_for_habit(self, sample_habits_list):
        """
        Test getting longest streak for a specific habit.
        """
        habit = sample_habits_list[0]  # Exercise
        
        result = get_longest_streak_for_habit(habit)
        
        assert result == habit.longest_streak
    
    def test_get_current_streak_for_habit(self, sample_habits_list):
        """
        Test getting the current streak for a specific habit.
        """
        habit = sample_habits_list[0]  # Exercise
        
        result = get_current_streak_for_habit(habit)
        
        assert result == habit.current_streak
    
    def test_get_habits_sorted_by_current_streak(self, sample_habits_list):
        """
        Test sorting habits by current streak.
        """
        result = get_habits_sorted_by_streak(sample_habits_list, by_current=True)
        
        # Should be sorted descending by current streak
        for i in range(len(result) - 1):
            assert result[i].current_streak >= result[i + 1].current_streak
    
    def test_get_habits_sorted_by_longest_streak(self, sample_habits_list):
        """
        Test sorting habits by longest streak.
        """
        result = get_habits_sorted_by_streak(sample_habits_list, by_current=False)
        
        # Should be sorted descending by longest streak
        for i in range(len(result) - 1):
            assert result[i].longest_streak >= result[i + 1].longest_streak
    
    def test_get_max_streak_per_habit(self, sample_habits_list):
        """
        Test getting max streak for each habit.
        """
        result = get_max_streak_per_habit(sample_habits_list)
        
        assert len(result) == len(sample_habits_list)
        assert all(isinstance(item, tuple) for item in result)
        assert all(len(item) == 2 for item in result)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """
    Integration tests combining multiple components.
    """
    
    def test_full_habit_lifecycle(self, test_db):
        """
        Test complete habit lifecycle: create, check-off, save, load, delete.
        """
        # Create
        habit = Habit(
            name="Integration Test Habit",
            description="Testing full lifecycle",
            periodicity="daily",
            created_date=datetime.now()
        )
        
        # Save
        save_habit(test_db, habit)
        assert habit_exists(test_db, habit.name)
        
        # Check-off
        habit.check_off()
        save_habit(test_db, habit)
        save_completion(test_db, habit.name, habit.last_completion_date)
        
        # Load and verify
        loaded = load_habit_by_name(test_db, habit.name)
        assert loaded.current_streak == 1
        
        # Delete
        delete_habit(test_db, habit.name)
        assert not habit_exists(test_db, habit.name)
    
    def test_streak_reset_on_missed_period(self, test_db):
        """
        Test that streak resets when a period is missed.
        """
        # Create a habit
        habit = Habit(
            name="Streak Reset Test",
            description="Testing streak reset",
            periodicity="daily",
            created_date=datetime.now() - timedelta(days=5)
        )
        
        # Complete it 3 days ago
        three_days_ago = datetime.now() - timedelta(days=3)
        habit.check_off(three_days_ago)
        assert habit.current_streak == 1
        
        # Now complete it today - should reset because we missed days
        habit.check_off()
        assert habit.current_streak == 1  # Reset, not 2


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
