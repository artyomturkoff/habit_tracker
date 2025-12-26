"""
Analytics module for habit tracking application.

This module implements analytics functionality using the functional programming
paradigm, as required by the project specifications.
"""
from typing import List, Tuple, Optional
from functools import reduce

from model.habit import Habit


def get_all_habits(habits: List[Habit]) -> List[Habit]:
    """
    Return all currently tracked habits.
    
    Args:
        habits: List of Habit objects
        
    Returns:
        List of all habits (pass-through for API consistency)
    """
    return list(habits)


def get_habits_by_periodicity(habits: List[Habit], periodicity: str) -> List[Habit]:
    """
    Return habits matching specified periodicity.
    
    Uses functional filter() to select habits.
    
    Args:
        habits: List of Habit objects
        periodicity: Either 'daily' or 'weekly'
        
    Returns:
        Filtered list of habits with matching periodicity
    """
    return list(filter(lambda h: h.periodicity == periodicity.lower(), habits))


def get_longest_streak_all_habits(habits: List[Habit]) -> Tuple[Optional[str], int]:
    """
    Find the habit with the longest streak among all habits.
    
    Uses functional max() with key function.
    
    Args:
        habits: List of Habit objects
        
    Returns:
        Tuple of (habit_name, streak_length). Returns (None, 0) if no habits exist.
    """
    if not habits:
        return None, 0
    
    longest_habit = max(habits, key=lambda h: h.longest_streak)
    return longest_habit.name, longest_habit.longest_streak


def get_longest_streak_for_habit(habit: Habit) -> int:
    """
    Return the longest streak for a specific habit.
    
    Args:
        habit: Habit object
        
    Returns:
        Longest streak achieved by this habit
    """
    return habit.longest_streak


def get_current_streak_for_habit(habit: Habit) -> int:
    """
    Return the current streak for a specific habit.
    
    Args:
        habit: Habit object
        
    Returns:
        Current active streak for this habit
    """
    return habit.current_streak


def get_habits_sorted_by_streak(habits: List[Habit], 
                                by_current: bool = True) -> List[Habit]:
    """
    Return habits sorted by streak length (descending).
    
    Uses functional sorted() with key function.
    
    Args:
        habits: List of Habit objects
        by_current: If True, sort by current_streak; if False, sort by longest_streak
        
    Returns:
        Sorted list of habits (new list, original unchanged)
    """
    key_func = (lambda h: h.current_streak) if by_current else (lambda h: h.longest_streak)
    return sorted(habits, key=key_func, reverse=True)


def get_not_completed_habits(habits: List[Habit]) -> List[Habit]:
    """
    Return all habits not yet completed in the current period.
    
    Uses functional filter() to select incomplete habits.
    
    Args:
        habits: List of Habit objects
        
    Returns:
        List of habits not completed today/this week
    """
    return list(filter(lambda h: not h.is_completed_today(), habits))


def get_max_streak_per_habit(habits: List[Habit]) -> List[Tuple[str, int]]:
    """
    Get the maximum streak for each habit.
    
    Uses functional map().
    
    Args:
        habits: List of Habit objects
        
    Returns:
        List of tuples (habit_name, longest_streak)
    """
    return list(map(lambda h: (h.name, h.longest_streak), habits))