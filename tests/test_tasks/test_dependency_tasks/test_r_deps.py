#!/usr/bin/env python3
"""
Simple test script to verify that our R dependency parser is working correctly.
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add project root to path so we can import augur modules
# This assumes the file is at tests/test_tasks/test_dependency_tasks/test_r_deps.py
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from augur.tasks.git.dependency_tasks.dependency_util import r_deps


def test_description_file():
    print("Checking DESCRIPTION file parsing...")
    
    # A standard looking DESCRIPTION file with various edge cases to test our parser
    description_content = """Package: mypackage
Type: Package
Title: My Test Package
Version: 0.1.0
Author: Test Author
Maintainer: Test Author <test@example.com>
Description: A test package.
License: GPL-3
Encoding: UTF-8
LazyData: true
Depends:
    R (>= 3.5.0),
    dplyr (>= 1.0.0)
Imports:
    ggplot2,
    tidyr (>= 1.1.0),
    stringr
Suggests:
    testthat (>= 3.0.0),
    knitr,
    rmarkdown
LinkingTo:
    Rcpp (>= 1.0.0)
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = os.path.join(tmpdir, 'DESCRIPTION')
        with open(temp_file, 'w') as f:
            f.write(description_content)
    
        deps = r_deps.get_deps_for_file(temp_file)
        
        # Verify we found exactly what we expected
        expected_deps = {'dplyr', 'ggplot2', 'tidyr', 'stringr', 'testthat', 
                        'knitr', 'rmarkdown', 'Rcpp'}
        missing = expected_deps - set(deps)
        extra = set(deps) - expected_deps
        
        if not missing and not extra:
            print("Looks good! All dependencies found.")
            return True
        else:
            print(f"Something's off. Missing: {missing}, Extra: {extra}")
            return False


def test_renv_lock_file():
    print("\nChecking renv.lock parsing...")
    
    # A basic renv.lock json structure
    renv_lock_content = {
        "R": {"Version": "4.3.0", "Repositories": [{"Name": "CRAN", "URL": "https://cran.rstudio.com"}]},
        "Packages": {
            "ggplot2": {"Package": "ggplot2", "Version": "3.4.0", "Source": "Repository", "Repository": "CRAN"},
            "dplyr": {"Package": "dplyr", "Version": "1.1.0", "Source": "Repository", "Repository": "CRAN"},
            "tidyr": {"Package": "tidyr", "Version": "1.3.0", "Source": "Repository", "Repository": "CRAN"},
            "rmarkdown": {"Package": "rmarkdown", "Version": "2.20", "Source": "Repository", "Repository": "CRAN"}
        }
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = os.path.join(tmpdir, 'renv.lock')
        with open(temp_file, 'w') as f:
            json.dump(renv_lock_content, f)
    
        deps = r_deps.get_deps_for_file(temp_file)
        
        expected_deps = {'ggplot2', 'dplyr', 'tidyr', 'rmarkdown'}
        missing = expected_deps - set(deps)
        extra = set(deps) - expected_deps
        
        if not missing and not extra:
            print("renv.lock parsed successfully.")
            return True
        else:
            print(f"renv.lock parsing failed. Missing: {missing}, Extra: {extra}")
            return False


def test_get_files():
    print("\nChecking file discovery...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # We set up a fake directory structure with some hidden files to find
        (Path(tmpdir) / 'DESCRIPTION').touch()
        (Path(tmpdir) / 'renv.lock').touch()
        (Path(tmpdir) / 'subdir').mkdir()
        (Path(tmpdir) / 'subdir' / 'DESCRIPTION').touch()
        (Path(tmpdir) / 'another' / 'nested').mkdir(parents=True)
        (Path(tmpdir) / 'another' / 'nested' / 'renv.lock').touch()
        
        files = r_deps.get_files(tmpdir)
        file_names = [f.name for f in files]
        
        desc_count = file_names.count('DESCRIPTION')
        lock_count = file_names.count('renv.lock')
        
        # We hid 2 DESCRIPTIONs and 2 lockfiles, let's make sure we found them all
        if desc_count == 2 and lock_count == 2:
            print("Found all the files we hid.")
            return True
        else:
            print(f"File discovery missed something. Found {desc_count} DESCRIPTIONs and {lock_count} lockfiles.")
            return False


def main():
    print("Starting tests...\n")
    
    results = [
        test_description_file(),
        test_renv_lock_file(),
        test_get_files()
    ]
    
    if all(results):
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
