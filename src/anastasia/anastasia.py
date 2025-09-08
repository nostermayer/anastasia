#!/usr/bin/env python3
"""
Anastasia: A framework for adding temporal functionality to objects.

This module provides a comprehensive system for enabling time-travel capabilities
in Python objects through the use of descriptors, context managers, and decorators.
Objects can store historical snapshots of their state and view attributes as they 
were at specific points in time.

The framework consists of three main components:
- Anastasia: The main mixin class providing temporal functionality
- TemporalAttribute: A descriptor managing individual attribute history
- TemporalValue: A wrapper enabling seamless value operations with snapshot access

Example:
    >>> from anastasia import Anastasia
    >>> import datetime
    >>> 
    >>> class Company(Anastasia):
    ...     @Anastasia.temporal_attribute
    ...     def credit_rating(self):
    ...         return "AAA"
    ...
    >>> company = Company()
    >>> company.credit_rating.set_snapshot("BB+")
    >>> timestamp = datetime.datetime.now()
    >>> company.credit_rating.set_snapshot("CCC")
    >>> with company.context(timestamp):
    ...     print(company.credit_rating)  # "BB+"

Author: Nick Ostermayer
License: MIT
"""

from __future__ import annotations

import datetime
import time
import copy
from contextlib import contextmanager
from weakref import WeakKeyDictionary
from typing import (
    Any, 
    Callable, 
    Dict, 
    Generator, 
    Optional, 
    Type, 
    TypeVar, 
    Union,
    cast
)

__version__ = "1.0.0"
__author__ = "Nick Ostermayer"
__email__ = "nick@nickostermayer.com"
__all__ = ["Anastasia", "TemporalAttribute", "TemporalValue"]

# Type variables for better type safety
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


class TemporalValue:
    """
    A wrapper class that behaves like the actual value while providing snapshot functionality.
    
    This class acts as a transparent proxy for the underlying value, implementing
    magic methods to ensure seamless integration with Python's built-in operations
    while providing access to the set_snapshot method for explicit snapshot creation.
    
    Attributes:
        _value: The actual wrapped value
        _descriptor: Reference to the TemporalAttribute descriptor
    
    Example:
        >>> value = TemporalValue("AAA", descriptor)
        >>> print(value)  # "AAA"
        >>> value.set_snapshot("BBB")
        >>> print(value == "BBB")  # True
    """
    
    def __init__(self, value: Any, descriptor: TemporalAttribute, instance: Any) -> None:
        """
        Initialize the temporal value wrapper.
        
        Args:
            value: The actual value to wrap
            descriptor: The TemporalAttribute descriptor that manages this value
            instance: The instance that this value belongs to
        """
        self._value = value
        self._descriptor = descriptor
        self._instance = instance
    
    def set_snapshot(self, value: Optional[Any] = None) -> Any:
        """
        Create a new snapshot with the specified or current value.
        
        Args:
            value: Value to snapshot. If None, uses current value.
            
        Returns:
            Any value returned by the descriptor's set_snapshot method
            
        Example:
            >>> temporal_value.set_snapshot("new_value")
            >>> temporal_value.set_snapshot()  # Uses current value
        """
        snapshot_value = value if value is not None else self._value
        return self._descriptor._set_snapshot_for_instance(self._instance, snapshot_value)
    
    # String representation methods
    def __str__(self) -> str:
        """Return string representation of the wrapped value."""
        return str(self._value)
    
    def __repr__(self) -> str:
        """Return detailed string representation of the wrapped value."""
        return repr(self._value)
    
    def __format__(self, format_spec: str) -> str:
        """Format the wrapped value using the given format specification."""
        return format(self._value, format_spec)
    
    # Equality and comparison operators
    def __eq__(self, other: Any) -> bool:
        """Test equality with another value."""
        return self._value == other
    
    def __ne__(self, other: Any) -> bool:
        """Test inequality with another value."""
        return self._value != other
    
    def __lt__(self, other: Any) -> bool:
        """Test if less than another value."""
        return self._value < other
    
    def __le__(self, other: Any) -> bool:
        """Test if less than or equal to another value."""
        return self._value <= other
    
    def __gt__(self, other: Any) -> bool:
        """Test if greater than another value."""
        return self._value > other
    
    def __ge__(self, other: Any) -> bool:
        """Test if greater than or equal to another value."""
        return self._value >= other
    
    # Arithmetic operators
    def __add__(self, other: Any) -> Any:
        """Add to the wrapped value."""
        return self._value + other
    
    def __radd__(self, other: Any) -> Any:
        """Right-side addition to the wrapped value."""
        return other + self._value
    
    def __sub__(self, other: Any) -> Any:
        """Subtract from the wrapped value."""
        return self._value - other
    
    def __rsub__(self, other: Any) -> Any:
        """Right-side subtraction from the wrapped value."""
        return other - self._value
    
    def __mul__(self, other: Any) -> Any:
        """Multiply the wrapped value."""
        return self._value * other
    
    def __rmul__(self, other: Any) -> Any:
        """Right-side multiplication of the wrapped value."""
        return other * self._value
    
    def __truediv__(self, other: Any) -> Any:
        """True division of the wrapped value."""
        return self._value / other
    
    def __rtruediv__(self, other: Any) -> Any:
        """Right-side true division of the wrapped value."""
        return other / self._value
    
    def __floordiv__(self, other: Any) -> Any:
        """Floor division of the wrapped value."""
        return self._value // other
    
    def __rfloordiv__(self, other: Any) -> Any:
        """Right-side floor division of the wrapped value."""
        return other // self._value
    
    def __mod__(self, other: Any) -> Any:
        """Modulo operation on the wrapped value."""
        return self._value % other
    
    def __rmod__(self, other: Any) -> Any:
        """Right-side modulo operation on the wrapped value."""
        return other % self._value
    
    def __pow__(self, other: Any) -> Any:
        """Exponentiation of the wrapped value."""
        return self._value ** other
    
    def __rpow__(self, other: Any) -> Any:
        """Right-side exponentiation of the wrapped value."""
        return other ** self._value
    
    # Container operations (if applicable)
    def __len__(self) -> int:
        """Return length of the wrapped value if it supports len()."""
        return len(self._value)
    
    def __getitem__(self, key: Any) -> Any:
        """Get item from the wrapped value if it supports indexing."""
        return self._value[key]
    
    def __contains__(self, item: Any) -> bool:
        """Test membership in the wrapped value if it supports 'in'."""
        return item in self._value


class TemporalAttribute:
    """
    A descriptor class that manages temporal functionality for individual attributes.
    
    This descriptor intercepts attribute access and provides time-travel capabilities
    by maintaining a history of snapshots with timestamp keys. It handles lazy loading
    of initial values, snapshot creation, and historical value retrieval.
    
    Attributes:
        _initial_value_func: Function that provides the initial value
        _snapshots: Dictionary mapping timestamps to historical values
        _current_value_set: Flag indicating if current value has been set
        _current_value: The current value of the attribute
        name: Name of the attribute (set by __set_name__)
    
    Example:
        >>> @Anastasia.temporal_attribute
        ... def credit_rating(self):
        ...     return "AAA"
    """
    
    def __init__(self, func: Callable[[Any], T]) -> None:
        """
        Initialize the temporal attribute descriptor.
        
        Args:
            func: Function that returns the initial value for this attribute
        """
        self._initial_value_func: Callable[[Any], T] = func
        # Use WeakKeyDictionary to store per-instance data
        self._instance_snapshots: WeakKeyDictionary = WeakKeyDictionary()
        self._instance_current_values: WeakKeyDictionary = WeakKeyDictionary()
        self._instance_value_set: WeakKeyDictionary = WeakKeyDictionary()
        self.name: str = ""
    
    def __set_name__(self, owner: Type[Any], name: str) -> None:
        """
        Called when the descriptor is assigned to a class attribute.
        
        Args:
            owner: The class that owns this descriptor
            name: The name of the attribute
        """
        self.name = name
    
    def __get__(self, instance: Optional[Any], owner: Optional[Type[Any]] = None) -> Union[TemporalAttribute, T, TemporalValue]:
        """
        Handle attribute access for temporal functionality.
        
        This method implements the core time-travel logic:
        - Returns the descriptor itself for class-level access
        - Returns historical values when as_of_timestamp is set
        - Returns wrapped current values for normal access
        - Performs lazy loading of initial values
        
        Args:
            instance: The instance accessing the attribute (None for class access)
            owner: The class that owns this descriptor
            
        Returns:
            Historical value, current TemporalValue wrapper, or descriptor itself
            
        Raises:
            ValueError: When no snapshot exists for the requested timestamp
        """
        if instance is None:
            # Class-level access returns the descriptor itself
            return self
        
        if owner is None:
            owner = type(instance)
        
        # Get per-instance data
        if instance not in self._instance_snapshots:
            self._instance_snapshots[instance] = {}
        if instance not in self._instance_current_values:
            self._instance_current_values[instance] = cast(T, None)
        if instance not in self._instance_value_set:
            self._instance_value_set[instance] = False

        # Check if we're in time-travel mode
        timestamp: Optional[datetime.datetime] = getattr(owner, 'as_of_timestamp', None)
        
        if timestamp is not None:
            # Time-travel mode: find historical value
            instance_snapshots = self._instance_snapshots[instance]
            valid_snapshots = {
                ts: snapshot for ts, snapshot in instance_snapshots.items()
                if ts <= timestamp
            }
            
            if not valid_snapshots:
                raise ValueError(
                    f"No snapshot for '{self.name}' found at or before {timestamp}"
                )
            
            # Return the most recent valid snapshot
            most_recent_timestamp = max(valid_snapshots.keys())
            return valid_snapshots[most_recent_timestamp]
        
        else:
            # Normal mode: return current value
            if not self._instance_value_set[instance]:
                # Lazy loading: initialize with default value and create first snapshot
                initial_value = self._initial_value_func(instance)
                self._set_snapshot_for_instance(instance, initial_value)
            
            # Return wrapped value that provides both value access and set_snapshot method
            return TemporalValue(self._instance_current_values[instance], self, instance)
    
    def __set__(self, instance: Any, value: T) -> None:
        """
        Handle attribute assignment.
        
        This method updates the current value without creating a snapshot,
        allowing for normal assignment operations while preserving explicit
        snapshot control through the set_snapshot method.
        
        Args:
            instance: The instance being assigned to
            value: The new value to assign
        """
        # Initialize per-instance data if needed
        if instance not in self._instance_current_values:
            self._instance_current_values[instance] = cast(T, None)
        if instance not in self._instance_value_set:
            self._instance_value_set[instance] = False
        if instance not in self._instance_snapshots:
            self._instance_snapshots[instance] = {}
            
        self._instance_current_values[instance] = value
        self._instance_value_set[instance] = True
    
    def _set_snapshot_for_instance(self, instance: Any, value: T) -> Any:
        """
        Helper method to create a snapshot for a specific instance.
        
        Args:
            instance: The instance to create a snapshot for
            value: The value to snapshot
            
        Returns:
            Any value returned by set_snapshot (for backward compatibility)
        """
        # Initialize per-instance data if needed
        if instance not in self._instance_snapshots:
            self._instance_snapshots[instance] = {}
        if instance not in self._instance_current_values:
            self._instance_current_values[instance] = cast(T, None)
        if instance not in self._instance_value_set:
            self._instance_value_set[instance] = False
            
        self._instance_current_values[instance] = value
        self._instance_value_set[instance] = True
        
        # Create deep copy to prevent mutation of historical data
        try:
            snapshot_value = copy.deepcopy(value)
        except (TypeError, AttributeError):
            # Fallback for objects that can't be deep copied
            snapshot_value = copy.copy(value) if hasattr(value, '__copy__') else value
        
        self._instance_snapshots[instance][datetime.datetime.now()] = snapshot_value
        
    def set_snapshot(self, value: T, instance: Optional[Any] = None) -> Any:
        """
        Explicitly create a new snapshot with the given value.
        
        Args:
            value: The value to snapshot
            instance: The instance to create snapshot for (required for new API)
            
        Example:
            >>> descriptor.set_snapshot("new_value", instance)
        """
        if instance is None:
            raise RuntimeError(
                "set_snapshot() requires an instance parameter. "
                "Use instance.attribute.set_snapshot(value) instead."
            )
        return self._set_snapshot_for_instance(instance, value)
    
    @property
    def _snapshots(self) -> Dict[datetime.datetime, T]:
        """
        Backward compatibility property for accessing snapshots.
        
        Note: This only works when there's a single instance using this descriptor.
        For multiple instances, this will raise an error.
        """
        if len(self._instance_snapshots) == 0:
            return {}
        elif len(self._instance_snapshots) == 1:
            # Return snapshots for the single instance
            instance = next(iter(self._instance_snapshots.keys()))
            return self._instance_snapshots[instance]
        else:
            raise RuntimeError(
                "Cannot access _snapshots property when multiple instances exist. "
                "Use per-instance access methods instead."
            )


class Anastasia:
    """
    A mixin class that provides temporal functionality to objects.
    
    This class enables time-travel capabilities for objects by providing:
    - A class-level timestamp for coordinated time-travel across attributes
    - A context manager for safe time-travel operations
    - A decorator for marking attributes as temporal
    
    The class uses a descriptor-based approach where only explicitly marked
    attributes participate in time-travel functionality, providing fine-grained
    control over which object state is tracked historically.
    
    Attributes:
        as_of_timestamp: Class-level timestamp for time-travel operations
    
    Example:
        >>> class Company(Anastasia):
        ...     @Anastasia.temporal_attribute
        ...     def credit_rating(self):
        ...         return "AAA"
        ...
        >>> company = Company()
        >>> with company.context(some_timestamp):
        ...     print(company.credit_rating)  # Historical value
    """
    
    # Class variable for coordinating time-travel across all instances
    as_of_timestamp: Optional[datetime.datetime] = None
    
    @staticmethod
    def temporal_attribute(func: F) -> TemporalAttribute:
        """
        Decorator to mark an attribute as temporal.
        
        This decorator replaces the decorated method with a TemporalAttribute
        descriptor that handles all time-travel logic. The original method
        serves as the initial value factory for the attribute.
        
        Args:
            func: Method that returns the initial value for this attribute
            
        Returns:
            TemporalAttribute descriptor instance
            
        Example:
            >>> @Anastasia.temporal_attribute
            ... def credit_rating(self):
            ...     return "AAA"
        """
        return TemporalAttribute(func)
    
    @classmethod
    @contextmanager
    def context(
        cls, 
        timestamp: Optional[datetime.datetime]
    ) -> Generator[None, None, None]:
        """
        Context manager for safe time-travel operations.
        
        This context manager temporarily sets the as_of_timestamp class variable
        to enable time-travel functionality, ensuring that the timestamp is
        properly restored even if an exception occurs within the context.
        
        Args:
            timestamp: The timestamp to travel to, or None for current time
            
        Yields:
            None
            
        Example:
            >>> with company.context(historical_timestamp):
            ...     print(company.credit_rating)  # Historical value
            >>> print(company.credit_rating)  # Current value
        """
        original_timestamp = cls.as_of_timestamp
        
        try:
            cls.as_of_timestamp = timestamp
            yield
        finally:
            # Always restore original timestamp, even if exception occurs
            cls.as_of_timestamp = original_timestamp


# Example usage and demonstration
if __name__ == '__main__':
    """
    Comprehensive demonstration of Anastasia temporal functionality.
    
    This example shows all major features of the framework including:
    - Basic attribute access and modification
    - Explicit snapshot creation
    - Time-travel using context managers
    - Multiple temporal attributes
    - Error handling for invalid timestamps
    """
    
    print("Anastasia Temporal Functionality Demo")
    print("=" * 40)
    
    # Define a sample Company class that uses Anastasia
    class Company(Anastasia):
        """A sample company class demonstrating temporal functionality."""
        
        def __init__(self, name: str, founded: int) -> None:
            """
            Initialize a company instance.
            
            Args:
                name: Company name
                founded: Year the company was founded
            """
            self.name = name
            self.founded = founded
        
        @Anastasia.temporal_attribute
        def credit_rating(self) -> str:
            """Initial credit rating of the company."""
            return "A"
        
        @Anastasia.temporal_attribute
        def employee_count(self) -> int:
            """Initial number of employees."""
            return 50
        
        @Anastasia.temporal_attribute
        def revenue(self) -> int:
            """Initial annual revenue in dollars."""
            return 1000000
    
    # Create a company instance and demonstrate functionality
    print("Creating company with initial data...")
    company = Company("TechCorp", 1999)
    
    # Access initial values (triggers lazy loading and first snapshots)
    print(f"Initial state:")
    print(f"  Credit Rating: {company.credit_rating}")
    print(f"  Employees: {company.employee_count}")
    print(f"  Revenue: ${company.revenue:,}")
    
    # Store timestamps for time-travel demonstration
    timestamps = []
    timestamps.append(datetime.datetime.now())
    
    # Wait and make changes to simulate time passing
    print("\n--- Company Growth Phase ---")
    time.sleep(0.01)  # Small delay to ensure different timestamps
    
    company.credit_rating.set_snapshot("A+")
    company.employee_count.set_snapshot(75)
    company.revenue.set_snapshot(1500000)
    timestamps.append(datetime.datetime.now())
    
    print(f"After growth:")
    print(f"  Credit Rating: {company.credit_rating}")
    print(f"  Employees: {company.employee_count}")
    print(f"  Revenue: ${company.revenue:,}")
    
    # Another phase of changes
    print("\n--- Company Expansion Phase ---")
    time.sleep(0.01)
    
    company.credit_rating.set_snapshot("AA-")
    company.employee_count.set_snapshot(120)
    company.revenue.set_snapshot(2500000)
    timestamps.append(datetime.datetime.now())
    
    print(f"After expansion:")
    print(f"  Credit Rating: {company.credit_rating}")
    print(f"  Employees: {company.employee_count}")
    print(f"  Revenue: ${company.revenue:,}")
    
    # Demonstrate time-travel functionality
    print("\n" + "=" * 40)
    print("TIME TRAVEL DEMONSTRATION")
    print("=" * 40)
    
    print(f"\nCurrent state:")
    print(f"  Credit Rating: {company.credit_rating}")
    print(f"  Employees: {company.employee_count}")
    print(f"  Revenue: ${company.revenue:,}")
    
    # Travel back to initial state
    print(f"\nTraveling to initial state ({timestamps[0]}):")
    with company.context(timestamps[0]):
        print(f"  Credit Rating: {company.credit_rating}")
        print(f"  Employees: {company.employee_count}")
        print(f"  Revenue: ${company.revenue:,}")
    
    # Travel to growth phase
    print(f"\nTraveling to growth phase ({timestamps[1]}):")
    with company.context(timestamps[1]):
        print(f"  Credit Rating: {company.credit_rating}")
        print(f"  Employees: {company.employee_count}")
        print(f"  Revenue: ${company.revenue:,}")
    
    print(f"\nBack to current state:")
    print(f"  Credit Rating: {company.credit_rating}")
    print(f"  Employees: {company.employee_count}")
    print(f"  Revenue: ${company.revenue:,}")
    
    # Demonstrate error handling
    print("\n" + "=" * 40)
    print("ERROR HANDLING DEMONSTRATION")
    print("=" * 40)
    
    print(f"\nAttempting to access state before any snapshots...")
    try:
        past_timestamp = timestamps[0] - datetime.timedelta(hours=1)
        with company.context(past_timestamp):
            print(f"Credit Rating: {company.credit_rating}")
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Show snapshot summary
    print("\n" + "=" * 40)
    print("SNAPSHOT SUMMARY")
    print("=" * 40)
    
    # Access descriptors to show snapshot counts
    credit_descriptor = Company.credit_rating
    employee_descriptor = Company.employee_count
    revenue_descriptor = Company.revenue
    
    print(f"\nCredit Rating snapshots: {len(credit_descriptor._snapshots)}")
    print(f"Employee Count snapshots: {len(employee_descriptor._snapshots)}")
    print(f"Revenue snapshots: {len(revenue_descriptor._snapshots)}")
    
    print(f"\nDemo completed successfully! 🎉")