# Anastasia

A Python framework for adding temporal functionality to objects, enabling time-travel capabilities for viewing historical states.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

## Overview

Anastasia allows objects to store historical snapshots of their state and view attributes as they were at specific points in time. It uses Python descriptors and context managers to provide a clean, intuitive API for temporal operations.

### Key Features

- 🕰️ **Time Travel**: View object attributes as they were at any point in time
- 📸 **Snapshot Management**: Explicit control over when to save object state
- 🎯 **Selective Temporal Attributes**: Only decorated attributes participate in time travel
- 🔒 **Isolation**: Deep copy ensures historical data cannot be mutated
- 🎨 **Clean API**: Intuitive context manager interface
- ⚡ **Lazy Loading**: Initial values loaded only when needed

## Quick Start

### Basic Usage

```python
from anastasia import Anastasia
import datetime

class Company(Anastasia):
    def __init__(self, name):
        self.name = name
    
    @Anastasia.temporal_attribute
    def credit_rating(self):
        return "AAA"  # Default initial value

# Create and use
company = Company("TechCorp")
print(company.credit_rating)  # "AAA"

# Update the value
company.credit_rating = "AA+"
print(company.credit_rating)  # "AA+"

# Create explicit snapshot
company.credit_rating.set_snapshot("BBB")
print(company.credit_rating)  # "BBB"
```

### Time Travel

```python
import time

# Save current time
snapshot_time = datetime.datetime.now()

# Make changes after some time
time.sleep(0.1)
company.credit_rating.set_snapshot("CCC")

# Travel back in time
with company.context(snapshot_time):
    print(company.credit_rating)  # Shows historical value "BBB"

print(company.credit_rating)  # Back to current value "CCC"
```

### Multiple Attributes

```python
class Company(Anastasia):
    @Anastasia.temporal_attribute
    def credit_rating(self):
        return "AAA"
    
    @Anastasia.temporal_attribute  
    def employee_count(self):
        return 100

company = Company()

# Each attribute maintains independent history
company.credit_rating.set_snapshot("AA+")
company.employee_count.set_snapshot(150)

# Time travel affects all temporal attributes
with company.context(some_timestamp):
    print(f"Rating: {company.credit_rating}")    # Historical rating
    print(f"Employees: {company.employee_count}") # Historical count
```

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/nostermayer/anastasia.git
cd anastasia
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .
```

### For Development

```bash
pip install -r requirements-dev.txt
```

## API Reference

### Anastasia Class

The main mixin class that provides temporal functionality.

#### Class Variables
- `as_of_timestamp`: Current timestamp for time-travel operations (class-level)

#### Methods
- `temporal_attribute(func)`: Decorator to mark attributes as temporal
- `context(timestamp)`: Context manager for time-travel operations

### TemporalAttribute Descriptor

Manages snapshot storage and retrieval for individual attributes.

#### Methods
- `set_snapshot(value)`: Explicitly save current value as snapshot

### TemporalValue Wrapper

Allows temporal attributes to behave like their actual values while providing access to snapshot methods.

## Testing

Run the comprehensive test suite:

```bash
# Basic test run
python run_tests.py

# With verbose output
python run_tests.py -v

# With coverage report
python run_tests.py --coverage

# Using pytest
pytest tests/ -v
```

### Test Coverage

The test suite includes:
- Unit tests for all components
- Integration tests for complete workflows
- Error handling and edge case testing
- Time-travel functionality validation
- Multi-attribute and inheritance testing

## Examples

### Complete Workflow Example

```python
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
timestamps = []

# Initial state
print(f"Initial: {company.credit_rating}, {company.employee_count}, ${company.revenue}")
timestamps.append(datetime.datetime.now())

time.sleep(0.01)

# Growth phase
company.credit_rating.set_snapshot("AA+")
company.employee_count.set_snapshot(75)
company.revenue.set_snapshot(1500000)
timestamps.append(datetime.datetime.now())

# Time travel back to initial state
with company.context(timestamps[0]):
    print(f"Historical: {company.credit_rating}, {company.employee_count}, ${company.revenue}")

print(f"Current: {company.credit_rating}, {company.employee_count}, ${company.revenue}")
```

## Limitations

- **Thread Safety**: Not currently thread-safe due to class-level `as_of_timestamp`
- **Memory Usage**: All snapshots retained in memory with no automatic cleanup
- **Performance**: Deep copying on snapshots may be expensive for large objects
- **Global State**: Time-travel affects all instances of Anastasia-derived classes

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Ensure all tests pass (`python run_tests.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all public APIs
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure backward compatibility

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by temporal database concepts
- Built using Python's descriptor protocol
- Designed for clean, intuitive time-travel operations