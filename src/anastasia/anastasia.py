import datetime
import time
import copy
from contextlib import contextmanager
import sys

class TemporalValue:
    """
    A wrapper class that behaves like the actual value but also provides
    the set_snapshot method.
    """
    def __init__(self, value, descriptor):
        self._value = value
        self._descriptor = descriptor
    
    def set_snapshot(self, value=None):
        """
        Updates the value and explicitly saves a new snapshot at the current time.
        """
        if value is None:
            value = self._value
        return self._descriptor.set_snapshot(value)
    
    def __str__(self):
        return str(self._value)
    
    def __repr__(self):
        return repr(self._value)
    
    def __eq__(self, other):
        return self._value == other
    
    def __ne__(self, other):
        return self._value != other
    
    def __lt__(self, other):
        return self._value < other
    
    def __le__(self, other):
        return self._value <= other
    
    def __gt__(self, other):
        return self._value > other
    
    def __ge__(self, other):
        return self._value >= other
    
    def __add__(self, other):
        return self._value + other
    
    def __radd__(self, other):
        return other + self._value
    
    def __sub__(self, other):
        return self._value - other
    
    def __rsub__(self, other):
        return other - self._value
    
    def __mul__(self, other):
        return self._value * other
    
    def __rmul__(self, other):
        return other * self._value
    
    def __truediv__(self, other):
        return self._value / other
    
    def __rtruediv__(self, other):
        return other / self._value
    
    def __floordiv__(self, other):
        return self._value // other
    
    def __rfloordiv__(self, other):
        return other // self._value
    
    def __mod__(self, other):
        return self._value % other
    
    def __rmod__(self, other):
        return other % self._value
    
    def __pow__(self, other):
        return self._value ** other
    
    def __rpow__(self, other):
        return other ** self._value


class TemporalAttribute:
    """
    A descriptor class that manages the value and snapshot history for a
    single attribute.
    
    This class is instantiated by the Anastasia.temporal_attribute decorator
    and provides the __get__ and __set__ methods to intercept attribute access,
    as well as the set_snapshot() method requested by the user.
    """
    def __init__(self, func):
        self._initial_value_func = func
        self._snapshots = {}
        self._current_value_set = False

    def __set_name__(self, owner, name):
        """
        Called at class creation to set the name of the attribute.
        """
        self.name = name

    def __get__(self, instance, owner):
        """
        Retrieves the value of the attribute.
        
        If a timestamp is set on the Anastasia class, it returns the most
        recent historical value; otherwise, it returns the current value.
        """
        if instance is None:
            # This is a class-level access, so return the descriptor itself.
            return self

        # Store reference to instance for set_snapshot method
        self._instance = instance
        
        # Safely access the global as_of_timestamp without infinite recursion
        timestamp = owner.as_of_timestamp

        if timestamp is not None:
            # Find the correct snapshot based on the timestamp.
            historical_timestamps = [t for t in self._snapshots.keys() if t <= timestamp]
            
            if not historical_timestamps:
                raise ValueError(f"No snapshot for '{self.name}' found at or before {timestamp}")

            latest_snapshot_time = max(historical_timestamps)
            return self._snapshots[latest_snapshot_time]
        else:
            # If the current value has not been set, lazy-load it and take an initial snapshot.
            if not self._current_value_set:
                initial_value = self._initial_value_func(instance)
                self.set_snapshot(initial_value)

            # Return the wrapped value that provides both value access and set_snapshot method
            return TemporalValue(self._current_value, self)

    def __set__(self, instance, value):
        """
        Sets the value of the attribute.
        
        This method is called automatically when you assign a new value, e.g.,
        `instance.attribute = new_value`. It handles both direct assignment
        and the use of the `set_snapshot` method.
        """
        self._current_value = value
        self._current_value_set = True
        
    def set_snapshot(self, value):
        """
        Updates the value and explicitly saves a new snapshot at the current time.

        This method allows you to control exactly when a new version of the
        attribute is saved.
        """
        self._current_value = value
        self._current_value_set = True
        self._snapshots[datetime.datetime.now()] = copy.deepcopy(self._current_value)

class Anastasia:
    """
    A mixin class that provides "time-travel" functionality for objects.

    This version uses a decorator and a descriptor to explicitly define which
    attributes are subject to snapshotting and allows for per-attribute
    snapshot control.
    """

    as_of_timestamp = None

    @staticmethod
    def temporal_attribute(func):
        """
        Decorator to mark an attribute as a temporal attribute.
        
        It replaces the decorated attribute with a TemporalAttribute descriptor,
        which handles all time-travel logic.
        """
        return TemporalAttribute(func)

    @contextmanager
    def context(self, timestamp=None):
        """
        A context manager to set the as_of_timestamp for a block of code.

        The timestamp is automatically reset after the block is exited.
        This is the preferred way to interact with the time-travel view.
        """
        old_timestamp = Anastasia.as_of_timestamp
        Anastasia.as_of_timestamp = timestamp
        try:
            yield self
        finally:
            Anastasia.as_of_timestamp = old_timestamp

# --- Example Usage ---

if __name__ == '__main__':
    print("Initializing a Company object...")
    
    class Company(Anastasia):
        def __init__(self, name, founding_year):
            self.name = name
            self.founding_year = founding_year

        # Use the temporal_attribute decorator with the new syntax.
        @Anastasia.temporal_attribute
        def credit_rating(self):
            return "A"

    # Create a company and access the attribute for the first time
    # This automatically sets the initial value and takes the first snapshot.
    company = Company(name="Globex Corp", founding_year=1999)
    first_snapshot_time = datetime.datetime.now()
    print(f"Current rating (initial access): '{company.credit_rating}'")

    print("\n--- Waiting and creating a second snapshot ---")
    time.sleep(2)  # Simulate time passing
    company.credit_rating.set_snapshot("A-")
    second_snapshot_time = datetime.datetime.now()
    print(f"Current rating after second snapshot: '{company.credit_rating}'")

    print("\n--- Waiting and creating a third snapshot ---")
    time.sleep(2)  # Simulate more time passing
    company.credit_rating.set_snapshot("B+")
    third_snapshot_time = datetime.datetime.now()
    print(f"Current rating after third snapshot: '{company.credit_rating}'")
    print("--- Snapshots captured. Now performing time-travel. ---")

    print("\nAttempting to view the object as it was between snapshot 1 and 2...")
    with company.context(timestamp=second_snapshot_time - datetime.timedelta(seconds=1)):
        print(f"As of {Anastasia.as_of_timestamp.strftime('%H:%M:%S')}: rating = '{company.credit_rating}'")

    print("\nAttempting to view the object as it was after snapshot 2...")
    with company.context(timestamp=third_snapshot_time - datetime.timedelta(seconds=1)):
        print(f"As of {Anastasia.as_of_timestamp.strftime('%H:%M:%S')}: rating = '{company.credit_rating}'")

    print("\nAttempting to view the object before any snapshots were taken...")
    try:
        with company.context(timestamp=first_snapshot_time - datetime.timedelta(seconds=3)):
            print(f"As of {Anastasia.as_of_timestamp.strftime('%H:%M:%S')}: rating = '{company.credit_rating}'")
    except ValueError as e:
        print(f"Caught expected error: {e}")

    print("\nContext manager block finished. The object is back to its current state.")
    print(f"Current rating: '{company.credit_rating}'")
