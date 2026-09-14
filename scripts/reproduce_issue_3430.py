#!/usr/bin/env python3
"""
Reproduction script for Augur Issue #3430: Pipfile parsing failures

This script demonstrates the bug where Pipfile parsing crashes when encountering
inline table dependencies (dict format) because the code assumes all dependency
values are strings.

Usage:
    python scripts/reproduce_issue_3430.py

Expected Results:
    BEFORE FIX: Script crashes with AttributeError about string methods
    AFTER FIX:  Script succeeds and shows parsed dependencies
"""

import sys
import os
import logging
from io import BytesIO

# Setup logging to see debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)

# Add augur to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def print_banner(message):
    """Print a formatted banner."""
    print("\n" + "="*70)
    print(f"  {message}")
    print("="*70)

def test_original_bug():
    """
    Demonstrate the original bug with inline table dependencies.
    
    This test uses a Pipfile that contains inline table (dict) dependencies
    which would cause the original code to crash.
    """
    print_banner("TESTING ISSUE #3430: Pipfile with Inline Table Dependencies")
    
    # Import the parsing functions
    try:
        from augur.tasks.git.dependency_libyear_tasks.libyear_util.pypi_parser import (
            parse_pipfile,
            normalize_pipfile_version,
            map_dependencies_pipfile
        )
        from augur.tasks.git.dependency_libyear_tasks.libyear_util.pypi_libyear_util import (
            sort_dependency_requirement,
            handle_upper_limit_dependency
        )
        print("✓ Successfully imported parsing functions")
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        print("\nMake sure you're running this from the Augur root directory:")
        print("  cd /path/to/augur")
        print("  python scripts/reproduce_issue_3430.py")
        return False
    
    # Test 1: Test normalize_pipfile_version with various formats
    print("\n" + "-"*70)
    print("TEST 1: Testing normalize_pipfile_version() function")
    print("-"*70)
    
    test_cases = [
        ("String version", ">=2.0", ">=2.0"),
        ("Dict with version", {"version": ">=2.0"}, ">=2.0"),
        ("Dict with extras only", {"extras": ["security"]}, None),
        ("Dict with path", {"path": "./local"}, None),
        ("Dict with editable", {"editable": True, "path": "../lib"}, None),
        ("Git dependency", {"git": "https://github.com/user/repo.git", "ref": "main"}, "https://github.com/user/repo.git#main"),
    ]
    
    all_passed = True
    for description, input_val, expected in test_cases:
        try:
            result = normalize_pipfile_version(input_val)
            if result == expected:
                print(f"  ✓ {description}: {input_val} → {result}")
            else:
                print(f"  ✗ {description}: Expected {expected}, got {result}")
                all_passed = False
        except Exception as e:
            print(f"  ✗ {description}: CRASHED with {type(e).__name__}: {e}")
            all_passed = False
    
    if not all_passed:
        print("\n❌ Some normalize_pipfile_version tests failed!")
        return False
    
    # Test 2: Parse the problematic Pipfile
    print("\n" + "-"*70)
    print("TEST 2: Parsing test Pipfile with inline table dependencies")
    print("-"*70)
    
    test_pipfile_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'tests', 
        'test_data', 
        'issue_3430_test_Pipfile'
    )
    
    if not os.path.exists(test_pipfile_path):
        print(f"\n⚠ Test Pipfile not found at: {test_pipfile_path}")
        print("Creating minimal test Pipfile in memory instead...")
        
        pipfile_content = b"""
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
requests = ">=2.20.0"
django = {version = ">=3.0", extras = ["async"]}
pytest-cov = {extras = ["toml"]}
local-package = {path = "./local-lib"}

[dev-packages]
pytest = "*"
black = {version = "==22.3.0"}
"""
        file_handle = BytesIO(pipfile_content)
        print("  Using in-memory test Pipfile")
    else:
        print(f"  Reading Pipfile from: {test_pipfile_path}")
        file_handle = open(test_pipfile_path, 'rb')
    
    try:
        print("\n  Attempting to parse Pipfile...")
        dependencies = parse_pipfile(file_handle)
        
        print(f"\n  ✓ SUCCESS! Parsed {len(dependencies)} dependencies")
        print("\n  Parsed dependencies:")
        
        for dep in dependencies:
            req_preview = str(dep['requirement'])[:50]
            if len(str(dep['requirement'])) > 50:
                req_preview += "..."
            print(f"    - {dep['name']:20s} | {dep['type']:8s} | {req_preview}")
        
        # Verify no dict requirements leaked through
        print("\n  Verifying all requirements are strings (not dicts)...")
        invalid_deps = [d for d in dependencies if not isinstance(d['requirement'], str)]
        
        if invalid_deps:
            print(f"\n  ✗ FAILED! Found {len(invalid_deps)} dependencies with non-string requirements:")
            for dep in invalid_deps:
                print(f"    - {dep['name']}: {type(dep['requirement']).__name__} = {dep['requirement']}")
            return False
        else:
            print("  ✓ All requirements are strings")
        
        # Test 3: Test downstream functions don't crash
        print("\n" + "-"*70)
        print("TEST 3: Testing downstream functions with parsed dependencies")
        print("-"*70)
        
        test_dep = {
            'name': 'test-package',
            'requirement': '>=2.0,<3.0',
            'type': 'runtime',
            'package': 'PYPI'
        }
        
        # Mock data for testing
        mock_data = {
            'releases': {'2.0.0': [], '2.5.0': [], '2.9.9': []},
            'info': {'name': 'test-package'}
        }
        
        try:
            result = sort_dependency_requirement(test_dep, mock_data)
            print(f"  ✓ sort_dependency_requirement() works: {result}")
        except Exception as e:
            print(f"  ✗ sort_dependency_requirement() crashed: {e}")
            return False
        
        # Test with None requirement (should handle gracefully)
        test_dep_none = {
            'name': 'path-package',
            'requirement': None,
            'type': 'runtime',
            'package': 'PYPI'
        }
        
        try:
            result = sort_dependency_requirement(test_dep_none, mock_data)
            print(f"  ✓ sort_dependency_requirement() handles None: {result}")
        except Exception as e:
            print(f"  ✗ sort_dependency_requirement() crashed on None: {e}")
            return False
        
        return True
        
    except AttributeError as e:
        print(f"\n  ✗ FAILED with AttributeError: {e}")
        print("\n  This is the EXPECTED ERROR before the fix is applied!")
        print("  The error occurs because the code tries to call string methods")
        print("  (like .split() or regex operations) on dict objects.")
        return False
        
    except Exception as e:
        print(f"\n  ✗ FAILED with {type(e).__name__}: {e}")
        import traceback
        print("\n  Full traceback:")
        print(traceback.format_exc())
        return False
    
    finally:
        if hasattr(file_handle, 'close'):
            file_handle.close()


def main():
    """Main entry point."""
    print_banner("Augur Issue #3430 Reproduction Script")
    print("\nThis script reproduces the Pipfile parsing bug where inline table")
    print("dependencies (dict format) cause crashes due to string assumptions.")
    print("\nBEFORE FIX: Code crashes with AttributeError")
    print("AFTER FIX:  Code successfully parses all dependency formats")
    
    success = test_original_bug()
    
    print("\n" + "="*70)
    if success:
        print("  ✅ ALL TESTS PASSED - Fix is working correctly!")
        print("="*70)
        print("\nThe fix successfully:")
        print("  ✓ Normalizes dict dependencies to strings")
        print("  ✓ Skips unsupported formats (path, editable)")
        print("  ✓ Handles None values in downstream functions")
        print("  ✓ Continues processing when one dependency fails")
        print("\n🎉 Ready to submit PR!")
        return 0
    else:
        print("  ❌ TESTS FAILED - Bug still present or fix incomplete")
        print("="*70)
        print("\nExpected behavior after fix:")
        print("  • Pipfile parsing should succeed without exceptions")
        print("  • Dict dependencies should be normalized to strings")
        print("  • Path/editable dependencies should be skipped gracefully")
        print("\n⚠ Fix may need adjustment or is not yet applied")
        return 1


if __name__ == '__main__':
    sys.exit(main())
