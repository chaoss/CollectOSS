# Issue #3430 Reproduction Guide

## Overview
This guide helps you reproduce and verify the fix for **Augur Issue #3430**: Pipfile parsing failures when encountering inline table (dict) dependencies.

## The Bug
The original code in `process_libyear_dependency_metrics` assumed all Pipfile dependency values were strings. However, Pipfile format allows dependencies to be specified as inline tables (dicts):

```toml
[packages]
# String format - works ✓
requests = ">=2.0"

# Inline table format - CRASHES ✗
django = {version = ">=3.0", extras = ["async"]}
pytest-cov = {extras = ["toml"]}
local-lib = {path = "./local"}
```

This caused crashes with errors like:
- `AttributeError: 'dict' object has no attribute 'split'`
- `TypeError: expected string or bytes-like object`

## Files Created

### 1. Test Pipfile
**Location**: `tests/test_data/issue_3430_test_Pipfile`

Contains various Pipfile dependency formats that trigger the bug:
- String versions (baseline)
- Inline tables with version + extras
- Inline tables with only extras/markers
- Path dependencies
- Editable dependencies
- Git dependencies

### 2. Reproduction Script
**Location**: `scripts/reproduce_issue_3430.py`

Python script that:
- Tests the `normalize_pipfile_version()` function
- Parses the problematic Pipfile
- Verifies downstream functions handle the normalized data
- Shows clear PASS/FAIL results

### 3. Unit Tests
**Location**: `tests/test_tasks/test_libyear_dependency_metrics.py`

Comprehensive test suite with 26 test methods covering:
- All Pipfile dependency formats
- Edge cases and error handling
- Integration with downstream functions

## Reproduction Steps

### Option 1: Run the Reproduction Script (Recommended)

```powershell
# From the Augur root directory
cd E:\zeba\augur

# Run the reproduction script
python scripts/reproduce_issue_3430.py
```

**Expected Output (After Fix):**
```
======================================================================
  Augur Issue #3430 Reproduction Script
======================================================================

✓ Successfully imported parsing functions

----------------------------------------------------------------------
TEST 1: Testing normalize_pipfile_version() function
----------------------------------------------------------------------
  ✓ String version: >=2.0 → >=2.0
  ✓ Dict with version: {'version': '>=2.0'} → >=2.0
  ✓ Dict with extras only: {'extras': ['security']} → None
  ✓ Dict with path: {'path': './local'} → None
  ...

----------------------------------------------------------------------
TEST 2: Parsing test Pipfile with inline table dependencies
----------------------------------------------------------------------
  ✓ SUCCESS! Parsed N dependencies
  ✓ All requirements are strings

----------------------------------------------------------------------
TEST 3: Testing downstream functions with parsed dependencies
----------------------------------------------------------------------
  ✓ sort_dependency_requirement() works
  ✓ sort_dependency_requirement() handles None

======================================================================
  ✅ ALL TESTS PASSED - Fix is working correctly!
======================================================================
```

### Option 2: Run the Unit Tests

```powershell
# Run all libyear tests
pytest tests/test_tasks/test_libyear_dependency_metrics.py -v

# Run just the main issue test
pytest tests/test_tasks/test_libyear_dependency_metrics.py::TestParsePipfile::test_pipfile_with_inline_table_dependency_does_not_crash -v

# Run with coverage
pytest tests/test_tasks/test_libyear_dependency_metrics.py --cov=augur.tasks.git.dependency_libyear_tasks
```

### Option 3: Manual Testing with Python REPL

```python
# Start Python from Augur root
cd E:\zeba\augur
python

# Import and test
from augur.tasks.git.dependency_libyear_tasks.libyear_util.pypi_parser import (
    normalize_pipfile_version,
    parse_pipfile
)

# Test with dict
result = normalize_pipfile_version({"version": ">=2.0"})
print(result)  # Should print: >=2.0

# Test with path (should return None)
result = normalize_pipfile_version({"path": "./local"})
print(result)  # Should print: None

# Parse test Pipfile
with open('tests/test_data/issue_3430_test_Pipfile', 'rb') as f:
    deps = parse_pipfile(f)
    print(f"Parsed {len(deps)} dependencies")
    for d in deps:
        print(f"  {d['name']}: {d['requirement']}")
```

## What to Look For

### ✅ Success Indicators (Fix Working)
- No AttributeError or TypeError exceptions
- All parsed dependencies have string requirements
- Path/editable dependencies are skipped with debug logs
- Downstream functions don't crash

### ❌ Failure Indicators (Bug Present)
- `AttributeError: 'dict' object has no attribute 'split'`
- `TypeError: expected string or bytes-like object`
- Crash in `handle_upper_limit_dependency()`
- Crash in `sort_dependency_requirement()`

## Testing Without Fix (Reverting Changes)

To verify the bug exists before the fix:

```powershell
# Backup current files
copy augur\tasks\git\dependency_libyear_tasks\libyear_util\pypi_parser.py pypi_parser.py.fixed
copy augur\tasks\git\dependency_libyear_tasks\libyear_util\pypi_libyear_util.py pypi_libyear_util.py.fixed

# Revert to see original bug (use git)
git checkout HEAD~1 augur/tasks/git/dependency_libyear_tasks/libyear_util/pypi_parser.py
git checkout HEAD~1 augur/tasks/git/dependency_libyear_tasks/libyear_util/pypi_libyear_util.py

# Run reproduction script - should FAIL
python scripts/reproduce_issue_3430.py

# Restore fixed versions
copy pypi_parser.py.fixed augur\tasks\git\dependency_libyear_tasks\libyear_util\pypi_parser.py
copy pypi_libyear_util.py.fixed augur\tasks\git\dependency_libyear_tasks\libyear_util\pypi_libyear_util.py

# Run again - should PASS
python scripts/reproduce_issue_3430.py
```

## Files Modified by Fix

1. **`augur/tasks/git/dependency_libyear_tasks/libyear_util/pypi_parser.py`**
   - Added: `normalize_pipfile_version()` function (lines 74-150)
   - Modified: `map_dependencies()` to delegate to normalization (lines 152-159)
   - Modified: `map_dependencies_pipfile()` to skip None values (lines 162-193)

2. **`augur/tasks/git/dependency_libyear_tasks/libyear_util/pypi_libyear_util.py`**
   - Modified: `clean_version()` - added type check (lines 19-31)
   - Modified: `handle_upper_limit_dependency()` - added type check (lines 50-68)
   - Modified: `sort_dependency_requirement()` - added type check (lines 96-119)

3. **`augur/tasks/git/dependency_libyear_tasks/libyear_util/util.py`**
   - Modified: Reordered `file_list` to prefer Pipfile.lock (lines 8-22)
   - Modified: `get_parsed_deps()` - added Pipfile.lock preference logic (lines 30-71)

## PR Checklist

Before submitting the PR, verify:

- [ ] Reproduction script passes: `python scripts/reproduce_issue_3430.py`
- [ ] Unit tests pass: `pytest tests/test_tasks/test_libyear_dependency_metrics.py`
- [ ] No existing tests broken: `pytest tests/test_tasks/`
- [ ] Manual testing with real Pipfiles works
- [ ] Debug logs appear when dependencies are skipped
- [ ] Pipfile.lock is preferred over Pipfile when both exist

## Additional Notes

### Why Pipfile.lock is Preferred
The fix also adds logic to prefer `Pipfile.lock` over `Pipfile`:
- Pipfile.lock uses JSON format (more reliable to parse)
- Has exact pinned versions (deterministic)
- Avoids the inline table issues entirely

### Supported Dependency Formats

| Format | Example | Handled |
|--------|---------|---------|
| String | `">=2.0"` | ✅ Parsed |
| Dict w/ version | `{version = ">=2.0"}` | ✅ Extracted |
| Git | `{git = "url", ref = "main"}` | ✅ Converted |
| Path | `{path = "./local"}` | ⚠️ Skipped |
| Editable | `{editable = true}` | ⚠️ Skipped |
| Extras only | `{extras = ["security"]}` | ⚠️ Skipped |

## Troubleshooting

### Import Errors
```
ModuleNotFoundError: No module named 'augur'
```
**Solution**: Make sure you're in the Augur root directory and Augur is installed:
```powershell
cd E:\zeba\augur
pip install -e .
```

### Test File Not Found
```
Test Pipfile not found at: tests/test_data/issue_3430_test_Pipfile
```
**Solution**: The script will create an in-memory test Pipfile, or you can ensure the file exists.

### Python Not Found
```powershell
python : The term 'python' is not recognized
```
**Solution**: Try `python3` or `py -3` instead.

## Contact

For questions about this fix, refer to:
- **Issue**: #3430
- **Files**: See "Files Modified by Fix" section above
- **Tests**: `tests/test_tasks/test_libyear_dependency_metrics.py`
