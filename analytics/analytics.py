"""
This module implements analytics functionality.
"""
from typing import List, Tuple, Optional
from model.habit import Habit


def get_all_habits(habits: List[Habit]) -> List[Habit]:
    """
    Return all currently tracked habits.
    """
    return list(habits)


def get_habits_by_periodicity(habits: List[Habit], periodicity: str) -> List[Habit]:
    """
    Return habits matching the specified periodicity.
    """
    return list(filter(lambda h: h.periodicity == periodicity.lower(), habits))


def get_longest_streak_all_habits(habits: List[Habit]) -> Tuple[Optional[str], int]:
    """
    Return the habit with the longest streak among all habits.
    """
    if not habits:
        return None, 0
    
    longest_habit = max(habits, key=lambda h: h.longest_streak)
    return longest_habit.name, longest_habit.longest_streak


def get_longest_streak_for_habit(habit: Habit) -> int:
    """
    Return the longest streak for a specific habit.
    """
    return habit.longest_streak


def get_current_streak_for_habit(habit: Habit) -> int:
    """
    Return the current streak for a specific habit.
    """
    return habit.current_streak


def get_habits_sorted_by_streak(habits: List[Habit], by_current: bool = True) -> List[Habit]:
    """
    Return habits sorted by streak length (descending).
    """
    key_func = (lambda h: h.current_streak) if by_current else (lambda h: h.longest_streak)
    return sorted(habits, key=key_func, reverse=True)


def get_not_completed_habits(habits: List[Habit]) -> List[Habit]:
    """
    Return all habits not yet completed in the current period.
    """
    return list(filter(lambda h: not h.is_completed_today(), habits))


def get_max_streak_per_habit(habits: List[Habit]) -> List[Tuple[str, int]]:
    """
    Return the maximum streak for each habit.
    """
    return list(map(lambda h: (h.name, h.longest_streak), habits))
