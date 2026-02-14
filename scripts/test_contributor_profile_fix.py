#!/usr/bin/env python3
"""
Test script to demonstrate the contributor profile fix (#3694).

Run from repo root: uv run python scripts/test_contributor_profile_fix.py

Shows that without the fix, a GitHub user response with no 'email' key
causes NameError (canonical_email never set). With the fix, we build
the cntrb dict successfully with email/canonical_email as None.
"""
from augur.tasks.util.AugurUUID import GithubUUID

# Minimal mock of a GitHub /users/:username response when email is NOT public
CONTRIBUTOR_NO_EMAIL = {
    "id": 12345,
    "login": "testuser",
    "node_id": "MDQ6VXNlcjEyMzQ1",
    "avatar_url": "https://avatars.githubusercontent.com/u/12345",
    "url": "https://api.github.com/users/testuser",
    "html_url": "https://github.com/testuser",
    "type": "User",
    "site_admin": False,
    "name": "Test User",
    "company": "Acme",
    "location": "Earth",
    "created_at": "2020-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    # NO 'email' key - user keeps email private
}

CONTRIBUTOR_WITH_EMAIL = {**CONTRIBUTOR_NO_EMAIL, "email": "test@example.com"}


def old_logic(contributor):
    """Simulates the old code path: canonical_email only set when 'email' in contributor."""
    company = None
    location = None
    email = None
    if "company" in contributor:
        company = contributor["company"]
    if "location" in contributor:
        location = contributor["location"]
    if "email" in contributor:
        email = contributor["email"]
        canonical_email = contributor["email"]
    # Build cntrb dict - BUG: canonical_email undefined when email missing
    return {
        "cntrb_email": email,
        "cntrb_canonical": canonical_email,  # NameError if email was missing
        "cntrb_company": company,
        "cntrb_location": location,
    }


def new_logic(contributor):
    """Current fix: always set canonical_email from email (both can be None)."""
    email = contributor.get("email")
    canonical_email = email
    company = contributor.get("company")
    location = contributor.get("location")
    full_name = contributor.get("name")
    created_at = contributor.get("created_at")
    updated_at = contributor.get("updated_at")
    return {
        "cntrb_email": email,
        "cntrb_canonical": canonical_email,
        "cntrb_company": company,
        "cntrb_location": location,
        "cntrb_full_name": full_name,
        "cntrb_created_at": created_at,
        "cntrb_last_used": updated_at,
    }


def main():
    print("=== Demonstrating contributor profile fix (#3694) ===\n")

    # 1) Old logic with response that HAS email -> works
    print("1) OLD logic, contributor WITH email:")
    try:
        result = old_logic(CONTRIBUTOR_WITH_EMAIL)
        print(f"   OK: cntrb_canonical = {result['cntrb_canonical']!r}\n")
    except Exception as e:
        print(f"   FAIL: {e}\n")

    # 2) Old logic with response that has NO email -> NameError
    print("2) OLD logic, contributor WITHOUT email (e.g. private):")
    try:
        result = old_logic(CONTRIBUTOR_NO_EMAIL)
        print(f"   OK: cntrb_canonical = {result['cntrb_canonical']!r}\n")
    except NameError as e:
        print(f"   NameError (bug): {e}\n")
    except Exception as e:
        print(f"   FAIL: {type(e).__name__}: {e}\n")

    # 3) New logic with no email -> works
    print("3) NEW logic, contributor WITHOUT email:")
    try:
        result = new_logic(CONTRIBUTOR_NO_EMAIL)
        print(f"   OK: cntrb_email={result['cntrb_email']!r}, cntrb_canonical={result['cntrb_canonical']!r}")
        print(f"       cntrb_full_name={result['cntrb_full_name']!r}, cntrb_company={result['cntrb_company']!r}\n")
    except Exception as e:
        print(f"   FAIL: {e}\n")

    # 4) New logic with email -> still works
    print("4) NEW logic, contributor WITH email:")
    try:
        result = new_logic(CONTRIBUTOR_WITH_EMAIL)
        print(f"   OK: cntrb_canonical = {result['cntrb_canonical']!r}\n")
    except Exception as e:
        print(f"   FAIL: {e}\n")

    print("=== Summary: Without fix, any user with private email causes NameError and failed insert. With fix, all profile fields (including email when present) are stored. ===")


if __name__ == "__main__":
    main()
