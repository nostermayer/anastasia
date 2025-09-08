#!/usr/bin/env python3
"""
Comprehensive test suite for the Anastasia temporal functionality framework.

This module tests all aspects of the Anastasia mixin class and TemporalAttribute
descriptor, including normal operations, time-travel functionality, error handling,
and edge cases.
"""

import unittest
import datetime
import time
import sys
import os

# Add src directory to path to import anastasia
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from anastasia.anastasia import Anastasia, TemporalAttribute, TemporalValue


class TestTemporalValue(unittest.TestCase):
    """Test cases for the TemporalValue wrapper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock descriptor for testing
        class MockDescriptor:
            def _set_snapshot_for_instance(self, instance, value):
                self.last_snapshot_value = value
                self.last_snapshot_instance = instance
                return f"Snapshot set to {value}"
        
        self.mock_descriptor = MockDescriptor()
        self.mock_instance = object()  # Mock instance
        self.temporal_value = TemporalValue("test_value", self.mock_descriptor, self.mock_instance)
    
    def test_string_representation(self):
        """Test that TemporalValue behaves like its underlying value."""
        self.assertEqual(str(self.temporal_value), "test_value")
        self.assertEqual(repr(self.temporal_value), "'test_value'")
    
    def test_equality_operations(self):
        """Test equality comparisons work correctly."""
        self.assertEqual(self.temporal_value, "test_value")
        self.assertNotEqual(self.temporal_value, "other_value")
    
    def test_comparison_operations(self):
        """Test comparison operations work correctly."""
        numeric_value = TemporalValue(5, self.mock_descriptor, self.mock_instance)
        
        self.assertTrue(numeric_value < 10)
        self.assertTrue(numeric_value <= 5)
        self.assertTrue(numeric_value > 1)
        self.assertTrue(numeric_value >= 5)
    
    def test_arithmetic_operations(self):
        """Test arithmetic operations work correctly."""
        numeric_value = TemporalValue(5, self.mock_descriptor, self.mock_instance)
        
        # Test basic arithmetic
        self.assertEqual(numeric_value + 3, 8)
        self.assertEqual(3 + numeric_value, 8)
        self.assertEqual(numeric_value - 2, 3)
        self.assertEqual(10 - numeric_value, 5)
        self.assertEqual(numeric_value * 3, 15)
        self.assertEqual(3 * numeric_value, 15)
        self.assertEqual(numeric_value / 2, 2.5)
        self.assertEqual(10 / numeric_value, 2.0)
    
    def test_set_snapshot_method(self):
        """Test that set_snapshot method works correctly."""
        result = self.temporal_value.set_snapshot("new_value")
        self.assertEqual(self.mock_descriptor.last_snapshot_value, "new_value")
        self.assertEqual(result, "Snapshot set to new_value")
    
    def test_set_snapshot_with_no_value(self):
        """Test set_snapshot with no explicit value uses current value."""
        result = self.temporal_value.set_snapshot()
        self.assertEqual(self.mock_descriptor.last_snapshot_value, "test_value")


class TestTemporalAttribute(unittest.TestCase):
    """Test cases for the TemporalAttribute descriptor."""
    
    def setUp(self):
        """Set up test fixtures."""
        def initial_value_func(instance):
            return "initial_value"
        
        self.descriptor = TemporalAttribute(initial_value_func)
        self.descriptor.__set_name__(None, "test_attribute")
        
        # Create a mock instance
        class MockInstance:
            pass
        
        self.instance = MockInstance()
    
    def test_descriptor_name_setting(self):
        """Test that __set_name__ correctly sets the descriptor name."""
        self.assertEqual(self.descriptor.name, "test_attribute")
    
    def test_initial_value_lazy_loading(self):
        """Test that initial value is lazy loaded on first access."""
        # Before first access, no instance data should exist
        self.assertEqual(len(self.descriptor._instance_snapshots), 0)
        self.assertEqual(len(self.descriptor._instance_value_set), 0)
        
        # Access the attribute - this should trigger lazy loading
        result = self.descriptor.__get__(self.instance, None)
        
        # Should return TemporalValue wrapper
        self.assertIsInstance(result, TemporalValue)
        self.assertEqual(str(result), "initial_value")
        
        # Current value should now be set for this instance
        self.assertTrue(self.descriptor._instance_value_set[self.instance])
        self.assertEqual(self.descriptor._instance_current_values[self.instance], "initial_value")
        
        # Should have created initial snapshot for this instance
        self.assertEqual(len(self.descriptor._instance_snapshots[self.instance]), 1)
    
    def test_set_method(self):
        """Test the __set__ method for normal assignment."""
        self.descriptor.__set__(self.instance, "new_value")
        
        self.assertTrue(self.descriptor._instance_value_set[self.instance])
        self.assertEqual(self.descriptor._instance_current_values[self.instance], "new_value")
    
    def test_set_snapshot_method(self):
        """Test the set_snapshot method creates snapshots correctly."""
        initial_time = datetime.datetime.now()
        
        self.descriptor.set_snapshot("snapshot_value", self.instance)
        
        self.assertTrue(self.descriptor._instance_value_set[self.instance])
        self.assertEqual(self.descriptor._instance_current_values[self.instance], "snapshot_value")
        self.assertEqual(len(self.descriptor._instance_snapshots[self.instance]), 1)
        
        # Check that snapshot timestamp is reasonable
        snapshot_time = list(self.descriptor._instance_snapshots[self.instance].keys())[0]
        self.assertGreaterEqual(snapshot_time, initial_time)
        self.assertEqual(self.descriptor._instance_snapshots[self.instance][snapshot_time], "snapshot_value")
    
    def test_class_level_access(self):
        """Test that class-level access returns the descriptor itself."""
        result = self.descriptor.__get__(None, None)
        self.assertIs(result, self.descriptor)


class TestAnastasia(unittest.TestCase):
    """Test cases for the Anastasia mixin class."""
    
    def setUp(self):
        """Set up test fixtures."""
        class TestCompany(Anastasia):
            def __init__(self, name):
                self.name = name
            
            @Anastasia.temporal_attribute
            def credit_rating(self):
                return "AAA"
            
            @Anastasia.temporal_attribute
            def employee_count(self):
                return 100
        
        self.TestCompany = TestCompany
        self.company = TestCompany("TestCorp")
    
    def test_class_variable_initialization(self):
        """Test that as_of_timestamp is properly initialized."""
        self.assertIsNone(Anastasia.as_of_timestamp)
    
    def test_temporal_attribute_decorator(self):
        """Test that temporal_attribute decorator creates TemporalAttribute."""
        # Access the descriptor at class level
        descriptor = self.TestCompany.credit_rating
        self.assertIsInstance(descriptor, TemporalAttribute)
    
    def test_basic_attribute_access(self):
        """Test basic attribute access returns TemporalValue."""
        rating = self.company.credit_rating
        self.assertIsInstance(rating, TemporalValue)
        self.assertEqual(str(rating), "AAA")
    
    def test_attribute_assignment(self):
        """Test direct attribute assignment."""
        self.company.credit_rating = "AA+"
        rating = self.company.credit_rating
        self.assertEqual(str(rating), "AA+")
    
    def test_set_snapshot_functionality(self):
        """Test that set_snapshot works through the TemporalValue interface."""
        # Get initial state
        initial_rating = self.company.credit_rating
        self.assertEqual(str(initial_rating), "AAA")
        
        # Wait a moment and create new snapshot
        time.sleep(0.01)
        initial_rating.set_snapshot("AA+")
        
        # Verify value changed
        new_rating = self.company.credit_rating
        self.assertEqual(str(new_rating), "AA+")
    
    def test_multiple_attributes(self):
        """Test that multiple temporal attributes work independently."""
        # Access both attributes
        rating = self.company.credit_rating
        count = self.company.employee_count
        
        self.assertEqual(str(rating), "AAA")
        self.assertEqual(str(count), "100")
        
        # Modify one attribute
        rating.set_snapshot("BB+")
        
        # Verify only the modified attribute changed
        self.assertEqual(str(self.company.credit_rating), "BB+")
        self.assertEqual(str(self.company.employee_count), "100")


class TestContextManager(unittest.TestCase):
    """Test cases for the context manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        class TestCompany(Anastasia):
            @Anastasia.temporal_attribute
            def credit_rating(self):
                return "AAA"
        
        self.TestCompany = TestCompany
        self.company = TestCompany()
        
        # Create some snapshots at different times
        self.timestamps = []
        
        # Initial snapshot (AAA)
        _ = self.company.credit_rating  # Trigger initial snapshot
        self.timestamps.append(datetime.datetime.now())
        
        time.sleep(0.01)
        
        # Second snapshot (AA+)
        self.company.credit_rating.set_snapshot("AA+")
        self.timestamps.append(datetime.datetime.now())
        
        time.sleep(0.01)
        
        # Third snapshot (BB+)
        self.company.credit_rating.set_snapshot("BB+")
        self.timestamps.append(datetime.datetime.now())
    
    def test_context_manager_time_travel(self):
        """Test that context manager enables time travel."""
        # Current state should be BB+
        self.assertEqual(str(self.company.credit_rating), "BB+")
        
        # Travel back to first snapshot
        with self.company.context(self.timestamps[0]):
            self.assertEqual(self.company.credit_rating, "AAA")
        
        # Should be back to current state
        self.assertEqual(str(self.company.credit_rating), "BB+")
    
    def test_context_manager_timestamp_setting(self):
        """Test that context manager properly sets and resets timestamp."""
        # Initially timestamp should be None
        self.assertIsNone(self.TestCompany.as_of_timestamp)
        
        test_time = self.timestamps[1]
        
        with self.company.context(test_time):
            # Inside context, timestamp should be set
            self.assertEqual(self.TestCompany.as_of_timestamp, test_time)
        
        # After context, timestamp should be reset
        self.assertIsNone(self.TestCompany.as_of_timestamp)
    
    def test_context_manager_exception_handling(self):
        """Test that timestamp is reset even when exception occurs."""
        test_time = self.timestamps[1]
        
        try:
            with self.company.context(test_time):
                self.assertEqual(self.TestCompany.as_of_timestamp, test_time)
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Timestamp should still be reset after exception
        self.assertIsNone(self.TestCompany.as_of_timestamp)
    
    def test_nested_context_managers(self):
        """Test that nested context managers work correctly."""
        outer_time = self.timestamps[1]
        inner_time = self.timestamps[0]
        
        with self.company.context(outer_time):
            self.assertEqual(self.TestCompany.as_of_timestamp, outer_time)
            self.assertEqual(self.company.credit_rating, "AA+")
            
            with self.company.context(inner_time):
                self.assertEqual(self.TestCompany.as_of_timestamp, inner_time)
                self.assertEqual(self.company.credit_rating, "AAA")
            
            # Should restore outer timestamp
            self.assertEqual(self.TestCompany.as_of_timestamp, outer_time)
            self.assertEqual(self.company.credit_rating, "AA+")
        
        # Should restore original timestamp (None)
        self.assertIsNone(self.TestCompany.as_of_timestamp)


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        class TestCompany(Anastasia):
            @Anastasia.temporal_attribute
            def credit_rating(self):
                return "AAA"
        
        self.TestCompany = TestCompany
        self.company = TestCompany()
    
    def test_no_snapshot_error(self):
        """Test that ValueError is raised when no snapshot exists for timestamp."""
        # Access attribute to create initial snapshot
        _ = self.company.credit_rating
        
        # Try to access with timestamp before any snapshots
        past_time = datetime.datetime.now() - datetime.timedelta(hours=1)
        
        with self.assertRaises(ValueError) as context:
            with self.company.context(past_time):
                _ = self.company.credit_rating
        
        self.assertIn("No snapshot for 'credit_rating' found", str(context.exception))
    
    def test_snapshot_ordering(self):
        """Test that snapshots are correctly ordered and most recent is used."""
        # Create multiple snapshots
        timestamps = []
        
        # Initial
        _ = self.company.credit_rating
        timestamps.append(datetime.datetime.now())
        time.sleep(0.01)
        
        # Second
        self.company.credit_rating.set_snapshot("AA+")
        timestamps.append(datetime.datetime.now())
        time.sleep(0.01)
        
        # Third
        self.company.credit_rating.set_snapshot("BB")
        timestamps.append(datetime.datetime.now())
        time.sleep(0.01)
        
        # Fourth
        self.company.credit_rating.set_snapshot("AA")
        timestamps.append(datetime.datetime.now())
        
        # Test accessing at different points in time
        # Between first and second - should get first
        between_1_2 = timestamps[0] + datetime.timedelta(milliseconds=5)
        with self.company.context(between_1_2):
            self.assertEqual(self.company.credit_rating, "AAA")
        
        # Between second and third - should get second
        between_2_3 = timestamps[1] + datetime.timedelta(milliseconds=5)
        with self.company.context(between_2_3):
            self.assertEqual(self.company.credit_rating, "AA+")
        
        # After fourth - should get fourth
        after_4 = timestamps[3] + datetime.timedelta(milliseconds=5)
        with self.company.context(after_4):
            self.assertEqual(self.company.credit_rating, "AA")
    
    def test_deep_copy_isolation(self):
        """Test that snapshots are properly isolated via deep copy."""
        class TestContainer(Anastasia):
            @Anastasia.temporal_attribute
            def data(self):
                return {"count": 0, "items": []}
        
        container = TestContainer()
        
        # Get initial data and modify it
        initial_data = container.data
        initial_data._value["count"] = 5
        initial_data._value["items"].append("item1")
        initial_data.set_snapshot()
        
        time.sleep(0.01)
        
        # Modify current data
        current_data = container.data
        current_data._value["count"] = 10
        current_data._value["items"].append("item2")
        current_data.set_snapshot()
        
        # Get timestamps for testing
        descriptor = TestContainer.data
        timestamps = sorted(descriptor._snapshots.keys())
        
        # Check that snapshots are isolated
        with container.context(timestamps[0]):
            snapshot_data = container.data
            self.assertEqual(snapshot_data["count"], 0)
            self.assertEqual(snapshot_data["items"], [])
        
        with container.context(timestamps[1]):
            snapshot_data = container.data
            self.assertEqual(snapshot_data["count"], 5)
            self.assertEqual(snapshot_data["items"], ["item1"])
        
        with container.context(timestamps[2]):
            snapshot_data = container.data
            self.assertEqual(snapshot_data["count"], 10)
            self.assertEqual(snapshot_data["items"], ["item1", "item2"])


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""
    
    def test_complete_workflow(self):
        """Test a complete workflow with multiple attributes and time travel."""
        class Company(Anastasia):
            def __init__(self, name, founded):
                self.name = name
                self.founded = founded
            
            @Anastasia.temporal_attribute
            def credit_rating(self):
                return "AAA"
            
            @Anastasia.temporal_attribute  
            def employee_count(self):
                return 50
            
            @Anastasia.temporal_attribute
            def revenue(self):
                return 1000000
        
        # Create company
        company = Company("TechCorp", 2020)
        
        # Collect timestamps as we go
        timestamps = []
        
        # Initial state
        self.assertEqual(str(company.credit_rating), "AAA")
        self.assertEqual(str(company.employee_count), "50")
        self.assertEqual(str(company.revenue), "1000000")
        timestamps.append(datetime.datetime.now())
        
        time.sleep(0.01)
        
        # Growth phase
        company.credit_rating.set_snapshot("AA+")
        company.employee_count.set_snapshot(75)
        company.revenue.set_snapshot(1500000)
        timestamps.append(datetime.datetime.now())
        
        time.sleep(0.01)
        
        # Expansion phase  
        company.credit_rating.set_snapshot("AA")
        company.employee_count.set_snapshot(120)
        company.revenue.set_snapshot(2500000)
        timestamps.append(datetime.datetime.now())
        
        time.sleep(0.01)
        
        # Difficulty phase
        company.credit_rating.set_snapshot("BBB")
        company.employee_count.set_snapshot(100)  # Layoffs
        company.revenue.set_snapshot(2000000)  # Revenue drop
        timestamps.append(datetime.datetime.now())
        
        # Test time travel to different phases
        # Initial phase
        with company.context(timestamps[0]):
            self.assertEqual(company.credit_rating, "AAA")
            self.assertEqual(company.employee_count, 50)
            self.assertEqual(company.revenue, 1000000)
        
        # Growth phase
        with company.context(timestamps[1]):
            self.assertEqual(company.credit_rating, "AA+")
            self.assertEqual(company.employee_count, 75)
            self.assertEqual(company.revenue, 1500000)
        
        # Expansion phase
        with company.context(timestamps[2]):
            self.assertEqual(company.credit_rating, "AA")
            self.assertEqual(company.employee_count, 120)
            self.assertEqual(company.revenue, 2500000)
        
        # Current state (difficulty phase)
        self.assertEqual(str(company.credit_rating), "BBB")
        self.assertEqual(str(company.employee_count), "100")
        self.assertEqual(str(company.revenue), "2000000")
    
    def test_inheritance_and_multiple_classes(self):
        """Test that the system works with inheritance and multiple classes."""
        class BaseEntity(Anastasia):
            @Anastasia.temporal_attribute
            def status(self):
                return "active"
        
        class Company(BaseEntity):
            @Anastasia.temporal_attribute
            def credit_rating(self):
                return "A"
        
        class Person(BaseEntity):
            @Anastasia.temporal_attribute
            def age(self):
                return 25
        
        # Create instances
        company = Company()
        person = Person()
        
        # Modify each independently
        company.status.set_snapshot("growing")
        company.credit_rating.set_snapshot("AA")
        
        person.status.set_snapshot("employed")
        person.age.set_snapshot(30)
        
        # Verify independence
        self.assertEqual(str(company.status), "growing")
        self.assertEqual(str(company.credit_rating), "AA")
        self.assertEqual(str(person.status), "employed")
        self.assertEqual(str(person.age), "30")
        
        # Verify that as_of_timestamp affects all instances
        company_descriptor = Company.status
        person_descriptor = Person.status
        
        # Get snapshots for each instance
        company_timestamps = sorted(company_descriptor._instance_snapshots[company].keys())
        person_timestamps = sorted(person_descriptor._instance_snapshots[person].keys())
        
        # Time travel should affect both instances
        with company.context(company_timestamps[0]):
            self.assertEqual(company.status, "active")
            # Person should also be affected by the same timestamp
            if person_timestamps[0] <= company_timestamps[0]:
                self.assertEqual(person.status, "active")


if __name__ == '__main__':
    # Create a test suite with all test cases
    test_classes = [
        TestTemporalValue,
        TestTemporalAttribute, 
        TestAnastasia,
        TestContextManager,
        TestErrorHandling,
        TestIntegration
    ]
    
    # Run tests with detailed output
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)