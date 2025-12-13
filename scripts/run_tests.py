"""
WorkFlowX Test Suite Runner

Runs all unit and integration tests for CA-2 submission.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py models       # Run only model tests
    python run_tests.py utils        # Run only utils tests
    python run_tests.py repository   # Run only repository tests
    python run_tests.py integration  # Run only integration tests

Test with unittest framework
Comprehensive testing strategy
"""

import sys
import os
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import test modules
from tests import test_models, test_utils, test_repository, test_integration


def run_all_tests():
    """
    Run complete test suite.
    
    Returns:
        bool: True if all tests passed, False otherwise
    """
    print("=" * 70)
    print("WORKFLOWX EMPLOYEE MANAGEMENT SYSTEM - TEST SUITE")
    print("CA-2 Advanced Programming Techniques")
    print("Team: Samuel Ogunlusi (20086108) & George M. Sherman (20079442)")
    print("=" * 70)
    print()
    
    # Create master test suite
    master_suite = unittest.TestSuite()
    
    # Add all test modules
    print("📦 Loading test modules...")
    loader = unittest.TestLoader()
    
    # Model tests
    master_suite.addTests(loader.loadTestsFromModule(test_models))
    print("   ✓ Model tests loaded")
    
    # Utils tests
    master_suite.addTests(loader.loadTestsFromModule(test_utils))
    print("   ✓ Utils tests loaded")
    
    # Repository tests
    master_suite.addTests(loader.loadTestsFromModule(test_repository))
    print("   ✓ Repository tests loaded")
    
    # Integration tests
    master_suite.addTests(loader.loadTestsFromModule(test_integration))
    print("   ✓ Integration tests loaded")
    
    print()
    print("🧪 Running tests...")
    print("=" * 70)
    print()
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(master_suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print("=" * 70)
    
    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED! 🎉")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        return False


def run_specific_tests(test_module):
    """
    Run tests from specific module.
    
    Args:
        test_module: Name of test module to run
    """
    print(f"Running {test_module} tests...")
    print("=" * 70)
    
    if test_module == 'models':
        success = test_models.run_model_tests()
    elif test_module == 'utils':
        success = test_utils.run_utils_tests()
    elif test_module == 'repository':
        success = test_repository.run_repository_tests()
    elif test_module == 'integration':
        success = test_integration.run_integration_tests()
    else:
        print(f"Unknown test module: {test_module}")
        print("Available modules: models, utils, repository, integration")
        return False
    
    return success


def main():
    """Main test runner entry point."""
    if len(sys.argv) > 1:
        # Run specific test module
        test_module = sys.argv[1].lower()
        success = run_specific_tests(test_module)
    else:
        # Run all tests
        success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
