#!/usr/bin/env python3
"""
Test runner script for the Anastasia project.

This script provides an easy way to run the test suite with various options.
"""

import sys
import os
import unittest
import argparse


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run Anastasia test suite')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Run tests with verbose output')
    parser.add_argument('-f', '--failfast', action='store_true', 
                       help='Stop on first failure')
    parser.add_argument('-b', '--buffer', action='store_true',
                       help='Buffer stdout/stderr during tests')
    parser.add_argument('-p', '--pattern', default='test_*.py',
                       help='Pattern to match test files')
    parser.add_argument('--coverage', action='store_true',
                       help='Run with coverage reporting (requires coverage.py)')
    
    args = parser.parse_args()
    
    # Set up test discovery
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    if args.coverage:
        try:
            import coverage
            cov = coverage.Coverage(source=['src/anastasia'])
            cov.start()
        except ImportError:
            print("Coverage.py not installed. Install with: pip install coverage")
            sys.exit(1)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = test_dir
    suite = loader.discover(start_dir, pattern=args.pattern)
    
    # Configure test runner
    verbosity = 2 if args.verbose else 1
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=args.failfast,
        buffer=args.buffer
    )
    
    # Run tests
    result = runner.run(suite)
    
    if args.coverage:
        cov.stop()
        cov.save()
        
        print("\n" + "="*60)
        print("COVERAGE REPORT")
        print("="*60)
        cov.report()
        
        # Generate HTML coverage report
        try:
            cov.html_report(directory='htmlcov')
            print(f"\nHTML coverage report generated in 'htmlcov' directory")
        except Exception as e:
            print(f"Could not generate HTML report: {e}")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)


if __name__ == '__main__':
    main()