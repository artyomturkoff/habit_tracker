"""
Habit class for tracking user habits with periodicities and streaks.
"""
from datetime import date, datetime, timedelta


class Habit:
    """
    Represents a single trackable habit with all its state information.
    
    A habit tracks a recurring task that should be completed with a specific
    periodicity (daily or weekly). It maintains streak information and calculates
    when the next completion is due.
    """
    
    # Class constants for valid periodicities
    DAILY = "daily"
    WEEKLY = "weekly"
    VALID_PERIODICITIES = {DAILY, WEEKLY}
    
    def __init__(
        self,
        name: str,
        description: str,
        periodicity: str,
        created_date: datetime,
        last_completion_date: datetime = None,
        due_date: datetime = None,
        current_streak: int = 0,
        longest_streak: int = 0
    ):
        # Validate name
        if not name or not name.strip():
            raise ValueError("Habit name cannot be empty")
        
        # Validate description
        if not description or not description.strip():
            raise ValueError("Habit description cannot be empty")
        
        # Validate periodicity
        if periodicity.lower().strip() not in self.VALID_PERIODICITIES:
            raise ValueError(
                f"Periodicity must be 'daily' or 'weekly', got '{periodicity}'"
            )
        
        # Set attributes
        self.name = name.strip()
        self.description = description.strip()
        self.periodicity = periodicity.lower().strip()
        self.created_date = created_date
        self.last_completion_date = last_completion_date
        self.due_date = due_date
        self.current_streak = current_streak
        self.longest_streak = longest_streak
    
    def check_off(self, completion_time: datetime = None) -> bool:
        """
        Record a completion of the habit for the current period.
        
        Updates the habit's state including streaks, last completion date,
        and next due date. If the habit is overdue, the streak is reset.
        
        Args:
            completion_time: Optional datetime for the completion (defaults to now)
        
        Returns:
            True if check-off was successful, False if already completed this period
        """
        now = completion_time if completion_time else datetime.now()
        
        # Check if already completed in current period
        if self.last_completion_date and self._is_same_period(now, self.last_completion_date):
            return False  # Already completed in this period
        
        # Check if habit was overdue (missed a period)
        if self.is_overdue(now):
            self.current_streak = 1  # Reset streak to 1
        else:
            self.current_streak += 1
        
        # Update longest streak if current is higher
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.last_completion_date = now
        # Calculate next due date
        self.due_date = self._calculate_due_date()
        return True
    
    def is_overdue(self, check_time: datetime = None) -> bool:
        """
        Check if the habit is currently overdue for completion.
        
        Args:
            check_time: Optional datetime to check against (defaults to now)
        """
        if self.due_date is None:
            return False
        check = check_time if check_time else datetime.now()
        return check > self.due_date
    
    def _calculate_due_date(self) -> datetime:
        """
        Calculate the next due date based on periodicity.
        
        For daily habits: due date is the end of the day following completion
        For weekly habits: due date is end of Sunday of the next week after completion
        """
        if self.last_completion_date is None:
            return None
            
        # Daily
        if self.periodicity == self.DAILY:
            return datetime.combine(
                self.last_completion_date.date() + timedelta(days=1), 
                datetime.max.time()
            )
        # Weekly
        else:
            base = self.last_completion_date + timedelta(days=7)
            year, week, _ = base.isocalendar()
            return datetime.combine(
                date.fromisocalendar(year, week, 7), 
                datetime.max.time()
            )
    
    def _is_same_period(self, date1: datetime, date2: datetime) -> bool:
        """
        Check if two dates fall within the same period for this habit's periodicity.
        
        For daily habits: Same calendar day
        For weekly habits: Same calendar week (Monday to Sunday)
        
        Args:
            date1: First date to compare
            date2: Second date to compare
        """
        if self.periodicity == self.DAILY:
            return date1.date() == date2.date()
        else:  # weekly
            year1, week1, _ = date1.isocalendar()
            year2, week2, _ = date2.isocalendar()
            return year1 == year2 and week1 == week2
    
    def is_completed_today(self) -> bool:
        """Check if habit has been completed in the current period."""
        if self.last_completion_date is None:
            return False
        return self._is_same_period(datetime.now(), self.last_completion_date)
    
    def to_dict(self) -> dict:
        """
        Convert the habit to a dictionary representation.
        
        Useful for database storage or JSON export.
        Datetimes are converted to ISO 8601 format strings.
        """
        return {
            'name': self.name,
            'description': self.description,
            'periodicity': self.periodicity,
            'created_date': self.created_date.isoformat(),
            'last_completion_date': (
                self.last_completion_date.isoformat()
                if self.last_completion_date else None
            ),
            'due_date': (
                self.due_date.isoformat()
                if self.due_date else None
            ),
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Habit':
        """
        Create a Habit instance from a dictionary.
        
        Args:
            data: Dictionary containing habit data
            
        Returns:
            New Habit instance
        """
        return cls(
            name=data['name'],
            description=data['description'],
            periodicity=data['periodicity'],
            created_date=datetime.fromisoformat(data['created_date']),
            last_completion_date=(
                datetime.fromisoformat(data['last_completion_date'])
                if data.get('last_completion_date') else None
            ),
            due_date=(
                datetime.fromisoformat(data['due_date'])
                if data.get('due_date') else None
            ),
            current_streak=data.get('current_streak', 0),
            longest_streak=data.get('longest_streak', 0)
        )
    
    def __repr__(self) -> str:
        return f"Habit(name='{self.name}', periodicity='{self.periodicity}', streak={self.current_streak})"
    
    def __str__(self) -> str:
        status = "✓" if self.is_completed_today() else "○"
        return f"{status} {self.name} ({self.periodicity}) - Streak: {self.current_streak}"