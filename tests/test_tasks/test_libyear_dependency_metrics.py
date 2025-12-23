#SPDX-License-Identifier: MIT
"""
Unit tests for libyear dependency metrics parsing.

Tests specifically address issue #3430: Pipfile parsing failures with inline table dependencies.
"""
import pytest
import tempfile
import os
from io import BytesIO
import logging

from augur.tasks.git.dependency_libyear_tasks.libyear_util.pypi_parser import (
    normalize_pipfile_version,
    map_dependencies_pipfile,
    parse_pipfile
)


class TestNormalizePipfileVersion:
    """Test the normalize_pipfile_version function with various Pipfile dependency formats."""
    
    def test_simple_string_version(self):
        """Test that simple string versions are returned as-is."""
        assert normalize_pipfile_version(">=2.0") == ">=2.0"
        assert normalize_pipfile_version("*") == "*"
        assert normalize_pipfile_version("==1.2.3") == "==1.2.3"
        assert normalize_pipfile_version("~=1.4.2") == "~=1.4.2"
    
    def test_dict_with_version_key(self):
        """Test dict format with explicit version key."""
        result = normalize_pipfile_version({"version": ">=2.0"})
        assert result == ">=2.0"
        
        result = normalize_pipfile_version({"version": "*", "markers": "python_version >= '3.6'"})
        assert result == "*"
    
    def test_dict_with_git_dependency(self):
        """Test git dependency format."""
        result = normalize_pipfile_version({
            "git": "https://github.com/user/repo.git",
            "ref": "main"
        })
        assert result == "https://github.com/user/repo.git#main"
        
        # Test without explicit ref
        result = normalize_pipfile_version({
            "git": "https://github.com/user/repo.git"
        })
        assert result == "https://github.com/user/repo.git#HEAD"
    
    def test_dict_with_path_dependency_returns_none(self):
        """Test that path dependencies return None (not suitable for version tracking)."""
        result = normalize_pipfile_version({"path": "./local-package"})
        assert result is None
        
        result = normalize_pipfile_version({"editable": True, "path": "../my-lib"})
        assert result is None
    
    def test_dict_with_only_extras_returns_none(self):
        """Test that dicts with only extras/markers but no version return None."""
        result = normalize_pipfile_version({"extras": ["security"]})
        assert result is None
        
        result = normalize_pipfile_version({
            "extras": ["security", "tests"],
            "markers": "platform_system == 'Linux'"
        })
        assert result is None
    
    def test_dict_with_non_string_version_returns_none(self):
        """Test that non-string version values are handled."""
        result = normalize_pipfile_version({"version": 1.2})
        assert result is None
        
        result = normalize_pipfile_version({"version": [">=2.0"]})
        assert result is None
    
    def test_unexpected_types_return_none(self):
        """Test that unexpected types are handled gracefully."""
        assert normalize_pipfile_version(None) is None
        assert normalize_pipfile_version(123) is None
        assert normalize_pipfile_version([1, 2, 3]) is None
        assert normalize_pipfile_version(True) is None


class TestMapDependenciesPipfile:
    """Test the map_dependencies_pipfile function with various package formats."""
    
    def test_simple_string_dependencies(self):
        """Test that simple string dependencies are processed correctly."""
        packages = {
            "requests": ">=2.0",
            "flask": "==1.1.2",
            "pytest": "*"
        }
        
        result = map_dependencies_pipfile(packages, 'runtime')
        
        assert len(result) == 3
        assert result[0] == {
            'name': 'requests',
            'requirement': '>=2.0',
            'type': 'runtime',
            'package': 'PYPI'
        }
        assert result[1]['name'] == 'flask'
        assert result[2]['name'] == 'pytest'
    
    def test_dict_dependencies_with_version(self):
        """Test dict dependencies with version key."""
        packages = {
            "requests": {"version": ">=2.0", "markers": "python_version >= '3.6'"},
            "flask": {"version": "==1.1.2"}
        }
        
        result = map_dependencies_pipfile(packages, 'develop')
        
        assert len(result) == 2
        assert result[0]['requirement'] == '>=2.0'
        assert result[0]['type'] == 'develop'
        assert result[1]['requirement'] == '==1.1.2'
    
    def test_path_dependencies_are_skipped(self):
        """Test that path dependencies are skipped with debug log."""
        packages = {
            "requests": ">=2.0",
            "local-lib": {"path": "./local-package"},
            "flask": "==1.1.2"
        }
        
        result = map_dependencies_pipfile(packages, 'runtime')
        
        # Only 2 dependencies should be in the result (path dep skipped)
        assert len(result) == 2
        assert result[0]['name'] == 'requests'
        assert result[1]['name'] == 'flask'
    
    def test_mixed_dependency_formats(self):
        """Test a realistic mix of dependency formats."""
        packages = {
            "requests": ">=2.20.0",
            "flask": {"version": "==1.1.2", "markers": "platform_system == 'Linux'"},
            "local-dev-lib": {"path": "../dev-lib"},
            "pytest": "*",
            "django": {"version": ">=3.0", "extras": ["async"]},
            "editable-pkg": {"editable": True, "path": "./src"},
            "git-package": {"git": "https://github.com/user/repo.git", "ref": "v1.0"}
        }
        
        result = map_dependencies_pipfile(packages, 'runtime')
        
        # Should have 5 valid dependencies (2 path deps skipped)
        assert len(result) == 5
        
        # Verify specific dependencies
        names = {dep['name'] for dep in result}
        assert 'requests' in names
        assert 'flask' in names
        assert 'pytest' in names
        assert 'django' in names
        assert 'git-package' in names
        
        # These should NOT be in the result
        assert 'local-dev-lib' not in names
        assert 'editable-pkg' not in names
    
    def test_empty_packages_returns_empty_list(self):
        """Test that empty package dict returns empty list."""
        result = map_dependencies_pipfile({}, 'runtime')
        assert result == []
        
        result = map_dependencies_pipfile(None, 'runtime')
        assert result == []


class TestParsePipfile:
    """Test the complete parse_pipfile function with realistic Pipfile content."""
    
    def test_pipfile_with_inline_table_dependency_does_not_crash(self):
        """
        Test for issue #3430: Pipfile with inline table dependencies should not crash.
        
        This test verifies that Pipfiles with dict-based dependency specifications
        (inline tables) are parsed without throwing "Expecting something like a string" errors.
        """
        pipfile_content = b"""
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
requests = ">=2.20.0"
flask = {version = "==1.1.2", markers = "python_version >= '3.6'"}
django = {version = ">=3.0", extras = ["async"]}
local-package = {path = "./local"}

[dev-packages]
pytest = "*"
black = {version = "==22.3.0"}
mypy = {extras = ["python2"], version = ">=0.950"}

[requires]
python_version = "3.8"
"""
        
        file_handle = BytesIO(pipfile_content)
        
        # This should not raise an exception
        try:
            result = parse_pipfile(file_handle)
            
            # Verify that valid dependencies are processed
            assert isinstance(result, list)
            assert len(result) > 0
            
            # Check that we have both runtime and develop dependencies
            runtime_deps = [d for d in result if d['type'] == 'runtime']
            develop_deps = [d for d in result if d['type'] == 'develop']
            
            assert len(runtime_deps) > 0
            assert len(develop_deps) > 0
            
            # Verify specific dependencies were parsed correctly
            dep_names = {dep['name'] for dep in result}
            assert 'requests' in dep_names
            assert 'flask' in dep_names
            assert 'pytest' in dep_names
            
            # Path dependency should be skipped
            assert 'local-package' not in dep_names
            
            # Verify requirements are strings (not dicts)
            for dep in result:
                assert isinstance(dep['requirement'], str), \
                    f"Dependency {dep['name']} has non-string requirement: {dep['requirement']}"
            
        except Exception as e:
            pytest.fail(f"parse_pipfile raised an unexpected exception: {e}")
    
    def test_pipfile_with_path_and_editable_dependencies(self):
        """Test that path and editable dependencies are gracefully skipped."""
        pipfile_content = b"""
[packages]
requests = ">=2.0"
local-lib = {path = "./local-lib"}
editable-pkg = {editable = true, path = "../editable"}

[dev-packages]
pytest = "*"
"""
        
        file_handle = BytesIO(pipfile_content)
        result = parse_pipfile(file_handle)
        
        # Should only have requests and pytest
        assert len(result) == 2
        dep_names = {dep['name'] for dep in result}
        assert 'requests' in dep_names
        assert 'pytest' in dep_names
        assert 'local-lib' not in dep_names
        assert 'editable-pkg' not in dep_names
    
    def test_pipfile_with_git_dependencies(self):
        """Test that git dependencies are parsed correctly."""
        pipfile_content = b"""
[packages]
requests = ">=2.0"
my-git-package = {git = "https://github.com/user/repo.git", ref = "v1.0.0"}

[dev-packages]
test-git-pkg = {git = "https://github.com/test/repo.git"}
"""
        
        file_handle = BytesIO(pipfile_content)
        result = parse_pipfile(file_handle)
        
        assert len(result) == 3
        
        # Find git dependencies
        git_deps = [d for d in result if '#' in d['requirement']]
        assert len(git_deps) == 2
        
        # Verify git URL format
        for dep in git_deps:
            assert 'https://github.com/' in dep['requirement']
            assert '#' in dep['requirement']
    
    def test_pipfile_edge_cases(self):
        """Test edge cases in Pipfile parsing."""
        # Test with empty packages sections
        pipfile_content = b"""
[packages]

[dev-packages]
pytest = "*"
"""
        
        file_handle = BytesIO(pipfile_content)
        result = parse_pipfile(file_handle)
        
        assert len(result) == 1
        assert result[0]['name'] == 'pytest'
    
    def test_pipfile_without_dev_packages(self):
        """Test Pipfile without dev-packages section (addressing old error handling issue)."""
        pipfile_content = b"""
[packages]
requests = ">=2.0"
flask = "*"
"""
        
        file_handle = BytesIO(pipfile_content)
        
        # Should not crash even without dev-packages section
        try:
            result = parse_pipfile(file_handle)
            assert len(result) == 2
            # All should be runtime type
            assert all(d['type'] == 'runtime' for d in result)
        except KeyError as e:
            pytest.fail(f"parse_pipfile crashed without dev-packages section: {e}")
    
    def test_pipfile_with_only_dev_packages(self):
        """Test Pipfile with only dev-packages section."""
        pipfile_content = b"""
[dev-packages]
pytest = "*"
black = "==22.3.0"
"""
        
        file_handle = BytesIO(pipfile_content)
        result = parse_pipfile(file_handle)
        
        assert len(result) == 2
        # All should be develop type
        assert all(d['type'] == 'develop' for d in result)
    
    def test_invalid_pipfile_returns_empty_list(self):
        """Test that invalid Pipfile content returns empty list with warning."""
        pipfile_content = b"This is not valid TOML content {"
        
        file_handle = BytesIO(pipfile_content)
        result = parse_pipfile(file_handle)
        
        # Should return empty list, not crash
        assert result == []
    
    def test_pipfile_with_complex_version_specs(self):
        """Test Pipfile with complex version specifications."""
        pipfile_content = b"""
[packages]
package1 = ">=1.0,<2.0"
package2 = "~=1.4.2"
package3 = "==1.2.*"
package4 = {version = ">=2.0,!=2.1.0"}
"""
        
        file_handle = BytesIO(pipfile_content)
        result = parse_pipfile(file_handle)
        
        assert len(result) == 4
        
        # Verify all have string requirements
        for dep in result:
            assert isinstance(dep['requirement'], str)
            assert len(dep['requirement']) > 0


class TestPipfileRobustness:
    """Integration tests for overall robustness of Pipfile parsing."""
    
    def test_realistic_pipfile_from_production(self):
        """Test with a realistic Pipfile that might be found in production."""
        pipfile_content = b"""
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[[source]]
url = "https://private-pypi.company.com/simple"
verify_ssl = true
name = "private"

[packages]
# Core dependencies
django = {version = ">=3.2,<4.0"}
djangorestframework = ">=3.12"
celery = {version = ">=5.0", extras = ["redis"]}
requests = ">=2.25.0"

# Database
psycopg2-binary = ">=2.8"

# Local development packages
my-company-lib = {path = "./libs/company-lib"}

# Git dependencies for unreleased features
experimental-feature = {git = "https://github.com/company/experimental.git", ref = "develop"}

# Packages with markers
cryptography = {version = ">=3.0", markers = "platform_system != 'Windows'"}

[dev-packages]
pytest = ">=6.0"
pytest-django = "*"
black = "==22.3.0"
mypy = {version = ">=0.950", extras = ["python2"]}
local-test-utils = {editable = true, path = "../test-utils"}

[requires]
python_version = "3.9"
"""
        
        file_handle = BytesIO(pipfile_content)
        
        # Parse should succeed without exceptions
        result = parse_pipfile(file_handle)
        
        # Verify we got dependencies
        assert len(result) > 0
        
        # Verify no dict requirements made it through
        for dep in result:
            if dep['requirement'] is not None:
                assert isinstance(dep['requirement'], str), \
                    f"Found non-string requirement for {dep['name']}: {dep['requirement']}"
        
        # Verify specific dependencies
        dep_names = {dep['name'] for dep in result}
        assert 'django' in dep_names
        assert 'celery' in dep_names
        assert 'pytest' in dep_names
        
        # Path and editable deps should be skipped
        assert 'my-company-lib' not in dep_names
        assert 'local-test-utils' not in dep_names
        
        # Git dep should be included
        assert 'experimental-feature' in dep_names
        
        # Find the git dependency and verify format
        exp_dep = next(d for d in result if d['name'] == 'experimental-feature')
        assert '#' in exp_dep['requirement']
        assert 'github.com' in exp_dep['requirement']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
