#!/usr/bin/env python3
"""
Test runner for Trivia.NET

Runs all Python unit, integration, and system tests.
"""

import unittest
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))


def run_tests():
    """Discover and run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code based on results
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
