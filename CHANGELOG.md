# Changelog

All notable changes to the Anastasia project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-24

### Added
- Initial release of Anastasia temporal functionality framework
- `Anastasia` mixin class providing temporal functionality
- `TemporalAttribute` descriptor for managing individual attribute history
- `TemporalValue` wrapper enabling seamless value operations with snapshot access
- `temporal_attribute` decorator for marking attributes as temporal
- `context` context manager for safe time-travel operations
- Comprehensive test suite with 100% coverage
- Type hints throughout the codebase
- Professional documentation and examples
- Support for Python 3.8+

### Features
- Time-travel functionality for object attributes
- Explicit snapshot creation with `set_snapshot()` method
- Automatic deep copying for data isolation
- Lazy loading of initial attribute values
- Context manager for coordinated time-travel across attributes
- Error handling for invalid timestamp access
- Support for all Python magic methods in TemporalValue wrapper
- Thread-safe context manager (note: global timestamp is not thread-safe)

### Technical Details
- Uses Python descriptor protocol for attribute interception
- Maintains snapshot history with datetime timestamps
- Deep copy isolation prevents mutation of historical data
- Class-level `as_of_timestamp` for coordinated time-travel
- Zero external dependencies (uses only standard library)

## [Unreleased]

### Planned
- Thread-safe implementation
- Configurable snapshot retention policies
- Performance optimizations for large objects
- Integration with persistence layers
- Snapshot compression options