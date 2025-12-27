"""
Habit Tracking Application - Command Line Interface

This is the main entry point for the habit tracker application.
It provides an interactive menu-based interface following the user flow:

START → Main Menu → Submenus → END

Main Menu Options:
1. Check Off Habit - Mark habits as completed
2. View All Habits - Display all habits with streaks
3. Manage Habits - Create or delete habits
4. Analytics - View statistics and analysis
5. Exit - Close the application
"""
import sys
from datetime import datetime
from typing import List

from model.habit import Habit
from database.sqlitedb import (
    get_database_connection,
    initialize_database,
    is_database_initialized,
    save_habit,
    load_all_habits,
    habit_exists,
    save_completion,
    delete_habit,
    get_habit_count
)
from analytics.analytics import (
    get_all_habits,
    get_habits_by_periodicity,
    get_longest_streak_all_habits,
    get_max_streak_per_habit,
    get_not_completed_habits
)
from data.predefined_habits import load_predefined_data


# ============================================================================
# DISPLAY HELPERS
# ============================================================================

def clear_screen():
    """
    Clear the terminal screen.
    """
    print("\n" * 2)


def print_header(title: str):
    """
    Print a formatted header.
    """
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def print_separator():
    """
    Print a visual separator line.
    """
    print("-" * 50)


def print_success(message: str):
    """
    Print a success message.
    """
    print(f"✓ {message}")


def print_error(message: str):
    """
    Print an error message.
    """
    print(f"✗ {message}")


def print_info(message: str):
    """
    Print an info message.
    """
    print(f"ℹ {message}")


def pause():
    """
    Wait for the user to press Enter.
    """
    input("\nPress Enter to continue...")


# ============================================================================
# MAIN MENU (Central hub as shown in user flow)
# ============================================================================

def display_main_menu():
    """
    Display the main menu options.
    """
    print_header("HABIT TRACKER - Main Menu")
    print("\n  1. Check Off Habit")
    print("  2. View All Habits")
    print("  3. Manage Habits")
    print("  4. Analytics")
    print("  5. Exit")
    print_separator()


def main_menu(connection) -> bool:
    """
    Handle main menu interaction.
    
    False if the user chooses to exit, True otherwise
    """
    display_main_menu()
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        check_off_habit_menu(connection)
    elif choice == "2":
        view_all_habits_menu(connection)
    elif choice == "3":
        manage_habits_menu(connection)
    elif choice == "4":
        analytics_menu(connection)
    elif choice == "5":
        return False  # Signal to exit
    else:
        print_error("Invalid choice. Please enter a number 1-5.")
        pause()
    
    return True  # Continue running


# ============================================================================
# OPTION 1: CHECK OFF HABIT
# ============================================================================

def check_off_habit_menu(connection):
    """
    Display and handle the check-off habit menu.
    
    Flow: Display not completed habits → User selects habit →
          Record completion → Update streak → Success message → Return to main
    """
    print_header("Check Off Habit")
    
    # Load habits and filter to not completed
    habits = load_all_habits(connection)
    not_completed = get_not_completed_habits(habits)
    
    if not habits:
        print_info("No habits found. Create some habits first!")
        pause()
        return
    
    if not not_completed:
        print_success("All habits completed for this period! Great job!")
        pause()
        return
    
    # Display not completed habits
    print("\nHabits to complete:")
    print_separator()
    
    for i, habit in enumerate(not_completed, 1):
        status = "OVERDUE" if habit.is_overdue() else "pending"
        print(f"  {i}. {habit.name} ({habit.periodicity}) [{status}]")
        print(f"     Current streak: {habit.current_streak}")
    
    print(f"\n  0. Return to Main Menu")
    print_separator()
    
    # Get user selection
    try:
        choice = input("\nSelect habit to check off (0 to cancel): ").strip()
        
        if choice == "0":
            return
        
        index = int(choice) - 1
        if 0 <= index < len(not_completed):
            selected_habit = not_completed[index]
            
            # Perform check-off
            success = selected_habit.check_off()
            
            if success:
                # Save to database
                save_habit(connection, selected_habit)
                save_completion(connection, selected_habit.name, selected_habit.last_completion_date)
                
                # Success message
                print_success(f"'{selected_habit.name}' checked off!")
                print_success(f"Current streak: {selected_habit.current_streak}")
                
                if selected_habit.current_streak == selected_habit.longest_streak:
                    print_success(f"🎉 New longest streak: {selected_habit.longest_streak}!")
            else:
                print_info("Already completed this period.")
        else:
            print_error("Invalid selection.")
            
    except ValueError:
        print_error("Please enter a valid number.")
    
    pause()


# ============================================================================
# OPTION 2: VIEW ALL HABITS
# ============================================================================

def view_all_habits_menu(connection):
    """
    Display all habits with their current streaks.
    
    Flow: Show all habits with current streaks → Return to main menu
    """
    print_header("View All Habits")
    
    habits = load_all_habits(connection)
    
    if not habits:
        print_info("No habits found. Create some habits first!")
        pause()
        return
    
    print(f"\nTotal habits: {len(habits)}\n")
    print_separator()
    
    for habit in habits:
        # Status indicator
        if habit.is_completed_today():
            status = "✓"
        elif habit.is_overdue():
            status = "⚠"
        else:
            status = "○"
        
        print(f"\n{status} {habit.name}")
        print(f"   Description: {habit.description}")
        print(f"   Periodicity: {habit.periodicity}")
        print(f"   Current streak: {habit.current_streak}")
        print(f"   Longest streak: {habit.longest_streak}")
        
        if habit.due_date:
            print(f"   Due: {habit.due_date.strftime('%Y-%m-%d %H:%M')}")
    
    print_separator()
    print("\nLegend: ✓ = Completed  ○ = Pending  ⚠ = Overdue")
    
    pause()


# ============================================================================
# OPTION 3: MANAGE HABITS
# ============================================================================

def manage_habits_menu(connection):
    """
    Handle the manage habits submenu.
    
    Flow: Show options (Create/Delete) → Execute → Return to main menu
    """
    while True:
        print_header("Manage Habits")
        print("\n  1. Create New Habit")
        print("  2. Delete Habit")
        print("  0. Return to Main Menu")
        print_separator()
        
        choice = input("\nEnter your choice (0-2): ").strip()
        
        if choice == "1":
            create_habit(connection)
        elif choice == "2":
            delete_habit_menu(connection)
        elif choice == "0":
            return
        else:
            print_error("Invalid choice. Please enter 0, 1, or 2.")
            pause()


def create_habit(connection):
    """
    Create a new habit with user input.
    
    Flow: Get name → Get description → Get periodicity → 
          Write to database → Success message → Return
    """
    print_header("Create New Habit")
    
    # Get habit name
    name = input("\nHabit name: ").strip()
    if not name:
        print_error("Habit name cannot be empty.")
        pause()
        return
    
    # Check if habit already exists
    if habit_exists(connection, name):
        print_error(f"A habit named '{name}' already exists.")
        pause()
        return
    
    # Get description
    description = input("Description: ").strip()
    if not description:
        print_error("Description cannot be empty.")
        pause()
        return
    
    # Get periodicity
    print("\nPeriodicity:")
    print("  1. Daily")
    print("  2. Weekly")
    
    period_choice = input("\nSelect periodicity (1 or 2): ").strip()
    
    if period_choice == "1":
        periodicity = "daily"
    elif period_choice == "2":
        periodicity = "weekly"
    else:
        print_error("Invalid periodicity. Please choose 1 or 2.")
        pause()
        return
    
    # Create and save the habit
    try:
        habit = Habit(
            name=name,
            description=description,
            periodicity=periodicity,
            created_date=datetime.now()
        )
        
        save_habit(connection, habit)
        print_success(f"Habit '{name}' created successfully!")
        
    except ValueError as e:
        print_error(f"Error creating habit: {e}")
    
    pause()


def delete_habit_menu(connection):
    """
    Delete an existing habit.
    
    Flow: Show habits → User selects → Confirm → Delete from database →
          Success message → Return
    """
    print_header("Delete Habit")
    
    habits = load_all_habits(connection)
    
    if not habits:
        print_info("No habits to delete.")
        pause()
        return
    
    # Display habits
    print("\nSelect habit to delete:")
    print_separator()
    
    for i, habit in enumerate(habits, 1):
        print(f"  {i}. {habit.name} ({habit.periodicity})")
    
    print(f"\n  0. Cancel")
    print_separator()
    
    try:
        choice = input("\nSelect habit (0 to cancel): ").strip()
        
        if choice == "0":
            return
        
        index = int(choice) - 1
        if 0 <= index < len(habits):
            selected_habit = habits[index]
            
            # Confirm deletion
            confirm = input(f"\nDelete '{selected_habit.name}'? (yes/no): ").strip().lower()
            
            if confirm in ("yes", "y"):
                if delete_habit(connection, selected_habit.name):
                    print_success(f"Habit '{selected_habit.name}' deleted.")
                else:
                    print_error("Failed to delete habit.")
            else:
                print_info("Deletion cancelled.")
        else:
            print_error("Invalid selection.")
            
    except ValueError:
        print_error("Please enter a valid number.")
    
    pause()


# ============================================================================
# OPTION 4: ANALYTICS MENU
# ============================================================================

def analytics_menu(connection):
    """
    Handle the analytics submenu.
    
    Flow: Show analytics options → Query data → Calculate statistics →
          Show results → Return to analytics menu or main menu
    """
    while True:
        print_header("Analytics Menu")
        print("\n  1. All Tracked Habits")
        print("  2. Habits by Periodicity")
        print("  3. Max Streak for Each Habit")
        print("  4. Longest Streak Overall")
        print("  5. Return to Main Menu")
        print_separator()
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        habits = load_all_habits(connection)
        
        if choice == "1":
            show_all_tracked_habits(habits)
        elif choice == "2":
            show_habits_by_periodicity(habits)
        elif choice == "3":
            show_max_streak_each_habit(habits)
        elif choice == "4":
            show_longest_streak_overall(habits)
        elif choice == "5":
            return
        else:
            print_error("Invalid choice. Please enter 1-5.")
            pause()


def show_all_tracked_habits(habits: List[Habit]):
    """
    Display all currently tracked habits.
    """
    print_header("All Tracked Habits")
    
    all_habits = get_all_habits(habits)
    
    if not all_habits:
        print_info("No habits being tracked.")
    else:
        print(f"\nTotal: {len(all_habits)} habits\n")
        
        for habit in all_habits:
            print(f"  • {habit.name}")
            print(f"    {habit.description}")
            print(f"    Periodicity: {habit.periodicity}")
            print()
    
    pause()


def show_habits_by_periodicity(habits: List[Habit]):
    """
    Display habits filtered by periodicity.
    """
    print_header("Habits by Periodicity")
    
    print("\n  1. Daily habits")
    print("  2. Weekly habits")
    
    choice = input("\nSelect periodicity (1 or 2): ").strip()
    
    if choice == "1":
        periodicity = "daily"
    elif choice == "2":
        periodicity = "weekly"
    else:
        print_error("Invalid choice.")
        pause()
        return
    
    filtered = get_habits_by_periodicity(habits, periodicity)
    
    print(f"\n{periodicity.capitalize()} Habits ({len(filtered)}):")
    print_separator()
    
    if not filtered:
        print_info(f"No {periodicity} habits found.")
    else:
        for habit in filtered:
            print(f"  • {habit.name}")
            print(f"    Streak: {habit.current_streak} (best: {habit.longest_streak})")
            print()
    
    pause()


def show_max_streak_each_habit(habits: List[Habit]):
    """
    Display the maximum streak achieved for each habit.
    """
    print_header("Max Streak for Each Habit")
    
    if not habits:
        print_info("No habits found.")
        pause()
        return
    
    streaks = get_max_streak_per_habit(habits)
    
    # Sort by streak descending
    streaks_sorted = sorted(streaks, key=lambda x: x[1], reverse=True)
    
    print("\nHabit                          Longest Streak")
    print_separator()
    
    for name, streak in streaks_sorted:
        print(f"  {name:<28} {streak}")
    
    pause()


def show_longest_streak_overall(habits: List[Habit]):
    """
    Display the habit with the longest streak overall.
    """
    print_header("Longest Streak Overall")
    
    if not habits:
        print_info("No habits found.")
        pause()
        return
    
    habit_name, streak = get_longest_streak_all_habits(habits)
    
    if habit_name:
        print(f"\n🏆 Best Habit: {habit_name}")
        print(f"   Longest Streak: {streak}")
        
        # Find the habit to show more details
        habit = next((h for h in habits if h.name == habit_name), None)
        if habit:
            print(f"   Current Streak: {habit.current_streak}")
            print(f"   Periodicity: {habit.periodicity}")
    else:
        print_info("No streak data available.")
    
    pause()


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

def initialize_app():
    """
    Initialise the application and database.
    """
    print_header("Habit Tracker")
    print("\nInitializing...")
    
    try:
        # Connect to database
        connection = get_database_connection()
        
        # Check if this is first run
        first_run = not is_database_initialized(connection)
        
        # Initialize tables
        initialize_database(connection)
        
        # Load predefined data if first run
        if first_run or get_habit_count(connection) == 0:
            print_info("Loading predefined habits with sample data...")
            load_predefined_data(connection)
            print_success("Predefined habits loaded successfully!")
        
        print_success("Application ready!")
        return connection
        
    except Exception as e:
        print_error(f"Failed to initialize: {e}")
        return None


def run():
    """
    Main application entry point.
    """
    # Initialize
    connection = initialize_app()
    
    if connection is None:
        print_error("Could not start application.")
        sys.exit(1)
    
    pause()
    
    # Main loop - continues until user selects Exit (Option 5)
    try:
        running = True
        while running:
            clear_screen()
            running = main_menu(connection)
        
        # Exit message
        print_header("Goodbye!")
        print("\nKeep building good habits! 🎯\n")
        
    except KeyboardInterrupt:
        print("\n\nExiting...")
    
    finally:
        # Clean up
        if connection:
            connection.close()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    run()
