# Test run: contributor profile fix (#3694)

Script: `scripts/test_contributor_profile_fix.py`  
Run from repo root: `uv run python scripts/test_contributor_profile_fix.py`

## Output (demonstrates bug without fix, and fix)

```
=== Demonstrating contributor profile fix (#3694) ===

1) OLD logic, contributor WITH email:
   OK: cntrb_canonical = 'test@example.com'

2) OLD logic, contributor WITHOUT email (e.g. private):
   NameError (bug): cannot access local variable 'canonical_email' where it is not associated with a value

3) NEW logic, contributor WITHOUT email:
   OK: cntrb_email=None, cntrb_canonical=None
       cntrb_full_name='Test User', cntrb_company='Acme'

4) NEW logic, contributor WITH email:
   OK: cntrb_canonical = 'test@example.com'

=== Summary: Without fix, any user with private email causes NameError and failed insert. With fix, all profile fields (including email when present) are stored. ===
```

So: when the GitHub user API omits `email` (e.g. private), the old code raised `NameError` and the contributor was never inserted. The new code handles it and still stores name, company, location, etc.
