# SPDX-License-Identifier: MIT
"""
CSV processing utilities for Augur CLI
"""
import csv
import logging
import os
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


class CSVProcessingError(Exception):
    """Raised when CSV processing fails."""

    pass


def check_file_size(filename: str) -> None:
    """Validate file size is under limit"""
    size = os.path.getsize(filename)
    if size > MAX_FILE_SIZE_BYTES:
        size_mb = size / (1024 * 1024)
        raise CSVProcessingError(
            f"File size ({size_mb:.1f}MB) exceeds {MAX_FILE_SIZE_MB}MB limit. "
            f"Consider splitting into smaller batches."
        )


def detect_headers(first_row: List[str], expected_columns: set) -> bool:
    """Detect if first row contains column headers"""
    normalized = {col.strip().lower() for col in first_row}
    return expected_columns.issubset(normalized)


def detect_column_mapping_repos(rows: List[List[str]]) -> Dict[str, int]:
    """Detect which column contains URLs vs IDs for headerless repo CSVs"""
    from augur.application.db.models import Repo

    if not rows or len(rows[0]) != 2:
        raise CSVProcessingError(
            "Expected 2 columns (repo_url, repo_group_id). "
            f"Found {len(rows[0]) if rows else 0} columns."
        )

    # Sample first 10 rows to determine column types
    sample_size = min(10, len(rows))
    sample_rows = rows[:sample_size]

    # Test each column to see if it contains URLs
    for col_idx in [0, 1]:
        col_values = [row[col_idx] for row in sample_rows]

        # Count how many values in this column parse as valid git URLs
        url_matches = 0
        for value in col_values:
            value = value.strip()
            github_parse = Repo.parse_github_repo_url(value)
            gitlab_parse = Repo.parse_gitlab_repo_url(value)

            if github_parse != (None, None) or gitlab_parse != (None, None):
                url_matches += 1

        # If >80% of values are valid URLs, this is the URL column
        match_rate = url_matches / len(col_values)
        if match_rate >= 0.8:
            url_col = col_idx
            id_col = 1 - col_idx  # The other column
            return {"repo_url": url_col, "repo_group_id": id_col}

    raise CSVProcessingError(
        "Could not detect column types. Ensure CSV contains valid git repository URLs. "
        "Or add headers: repo_url,repo_group_id"
    )


def detect_column_mapping_repo_groups(rows: List[List[str]]) -> Dict[str, int]:
    """Detect which column contains IDs vs names for headerless repo group CSVs"""
    if not rows or len(rows[0]) != 2:
        raise CSVProcessingError(
            "Expected 2 columns (repo_group_id, repo_group_name). "
            f"Found {len(rows[0]) if rows else 0} columns."
        )

    # Sample first 10 rows
    sample_size = min(10, len(rows))
    sample_rows = rows[:sample_size]

    # Test each column to see if it contains integers
    for col_idx in [0, 1]:
        col_values = [row[col_idx] for row in sample_rows]

        # Count how many values are positive integers
        int_matches = 0
        for value in col_values:
            try:
                if int(value.strip()) > 0:
                    int_matches += 1
            except (ValueError, AttributeError):
                pass

        # If >80% of values are integers, this is the ID column
        match_rate = int_matches / len(col_values)
        if match_rate >= 0.8:
            id_col = col_idx
            name_col = 1 - col_idx  # The other column
            return {"repo_group_id": id_col, "repo_group_name": name_col}

    raise CSVProcessingError(
        "Could not detect column types. Ensure CSV has valid format. "
        "Or add headers: repo_group_id,repo_group_name"
    )


def process_repo_csv(filename: str) -> List[Dict[str, str]]:
    """Process repository CSV file with intelligent header detection"""
    check_file_size(filename)

    rows = []

    with open(filename, "r", newline="") as f:
        # Read first line to detect headers
        first_line = f.readline()
        f.seek(0)

        first_row = next(csv.reader([first_line]))
        has_headers = detect_headers(first_row, {"repo_url", "repo_group_id"})

        if has_headers:
            logger.info("CSV has headers, using DictReader")
            reader = csv.DictReader(f)

            # Normalize fieldnames
            reader.fieldnames = [fn.strip().lower() for fn in reader.fieldnames]

            # Validate required columns present
            required = {"repo_url", "repo_group_id"}
            if not required.issubset(set(reader.fieldnames)):
                missing = required - set(reader.fieldnames)
                raise CSVProcessingError(
                    f"Missing required columns: {missing}. "
                    f"Expected: repo_url, repo_group_id"
                )

            for line_num, row in enumerate(reader, start=2):
                row_normalized = {k.strip().lower(): v.strip() for k, v in row.items()}
                rows.append(row_normalized)

        else:
            logger.info("CSV has no headers, using intelligent column detection")
            # Read all rows
            all_rows = list(csv.reader(f))

            if not all_rows:
                raise CSVProcessingError("CSV file is empty")

            # Detect which column is which
            col_mapping = detect_column_mapping_repos(all_rows)

            # Convert to dicts
            for line_num, row in enumerate(all_rows, start=1):
                if len(row) != 2:
                    logger.warning(
                        f"Line {line_num}: Expected 2 columns, got {len(row)}, skipping"
                    )
                    continue

                row_dict = {
                    "repo_url": row[col_mapping["repo_url"]].strip(),
                    "repo_group_id": row[col_mapping["repo_group_id"]].strip(),
                }
                rows.append(row_dict)

    logger.info(f"Parsed {len(rows)} rows from CSV")
    return rows


def process_repo_group_csv(filename: str) -> List[Dict[str, str]]:
    """Process repository group CSV file with intelligent header detection"""
    check_file_size(filename)

    rows = []

    with open(filename, "r", newline="") as f:
        # Read first line to detect headers
        first_line = f.readline()
        f.seek(0)

        first_row = next(csv.reader([first_line]))
        has_headers = detect_headers(first_row, {"repo_group_id", "repo_group_name"})

        if has_headers:
            logger.info("CSV has headers, using DictReader")
            reader = csv.DictReader(f)

            # Normalize fieldnames
            reader.fieldnames = [fn.strip().lower() for fn in reader.fieldnames]

            # Validate required columns present
            required = {"repo_group_id", "repo_group_name"}
            if not required.issubset(set(reader.fieldnames)):
                missing = required - set(reader.fieldnames)
                raise CSVProcessingError(
                    f"Missing required columns: {missing}. "
                    f"Expected: repo_group_id, repo_group_name"
                )

            for line_num, row in enumerate(reader, start=2):
                row_normalized = {k.strip().lower(): v.strip() for k, v in row.items()}

                # Skip empty rows
                if not row_normalized.get("repo_group_id") or not row_normalized.get(
                    "repo_group_name"
                ):
                    continue

                rows.append(row_normalized)

        else:
            logger.info("CSV has no headers, using intelligent column detection")
            # Read all rows
            all_rows = list(csv.reader(f))

            if not all_rows:
                raise CSVProcessingError("CSV file is empty")

            # Detect which column is which
            col_mapping = detect_column_mapping_repo_groups(all_rows)

            # Convert to dicts
            for line_num, row in enumerate(all_rows, start=1):
                if len(row) != 2:
                    logger.warning(
                        f"Line {line_num}: Expected 2 columns, got {len(row)}, skipping"
                    )
                    continue

                # Skip empty rows
                if not row[0].strip() or not row[1].strip():
                    continue

                row_dict = {
                    "repo_group_id": row[col_mapping["repo_group_id"]].strip(),
                    "repo_group_name": row[col_mapping["repo_group_name"]].strip(),
                }
                rows.append(row_dict)

    logger.info(f"Parsed {len(rows)} rows from CSV")
    return rows


def write_rejection_file(filename: str, rejections: List[Tuple[Dict, str]]) -> str:
    """Write rejected rows to a .rejected.csv file"""
    if not rejections:
        return None

    rejection_file = f"{filename}.rejected.csv"

    with open(rejection_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["original_data", "rejection_reason"])

        for row_dict, reason in rejections:
            original_data = ",".join(str(v) for v in row_dict.values())
            writer.writerow([original_data, reason])

    logger.info(f"Wrote {len(rejections)} rejections to {rejection_file}")
    return rejection_file
