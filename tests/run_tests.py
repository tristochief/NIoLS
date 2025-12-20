#!/usr/bin/env python3
"""
Test runner for all unit and integration tests.
"""

import unittest
import sys
from pathlib import Path

# Add software directory to path
software_dir = Path(__file__).parent.parent / "software"
sys.path.insert(0, str(software_dir))

def run_unit_tests():
    """Run all unit tests."""
    print("=" * 70)
    print("Running Unit Tests")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Discover and add unit tests
    unit_test_dir = Path(__file__).parent / "unit"
    unit_tests = loader.discover(str(unit_test_dir), pattern='test_*.py')
    suite.addTests(unit_tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_integration_tests():
    """Run all integration tests."""
    print("\n" + "=" * 70)
    print("Running Integration Tests")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Discover and add integration tests
    integration_test_dir = Path(__file__).parent / "integration"
    integration_tests = loader.discover(str(integration_test_dir), pattern='test_*.py')
    suite.addTests(integration_tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("EUV Detection & Laser Communication Device - Test Suite")
    print("=" * 70 + "\n")
    
    unit_success = run_unit_tests()
    integration_success = run_integration_tests()
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Unit Tests: {'PASSED' if unit_success else 'FAILED'}")
    print(f"Integration Tests: {'PASSED' if integration_success else 'FAILED'}")
    
    if unit_success and integration_success:
        print("\nAll tests PASSED!")
        return 0
    else:
        print("\nSome tests FAILED!")
        return 1


if __name__ == '__main__':
    sys.exit(main())

