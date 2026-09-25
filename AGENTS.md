# AGENTS.md

This file provides guidance for AI coding agents (such as Kiro) contributing to CollectOSS.

## Avoiding Duplicate Work

Before starting on an issue, agents should:

1. **Check the issue thread** on GitHub for existing comments claiming it, or linked PRs.
2. **Search open and closed PRs** for the issue number or related keywords:
   ```
   gh pr list --repo chaoss/CollectOSS --search "<issue-number> OR <key-term>" --state all
   ```
3. **Check `git log` on `main`** for recent commits that may have already resolved it indirectly.

If a claim or existing PR is found, surface this to the user instead of proceeding, and suggest either reviewing/improving the existing PR or picking a different issue.

## Aligning PRs with Contribution Guidelines

Before opening a PR, agents should confirm against [CONTRIBUTING.md](CONTRIBUTING.md):

- Branch is based on and targets `main` (not `release` — that's for tagged versions only)
- PR description clearly references the issue it closes (e.g. `closes chaoss/CollectOSS#<issue-number>`)
- The fork is synced with `main` before opening the PR, to avoid stale-branch conflicts
- Scope stays limited to the linked issue — no unrelated refactors bundled in
- If uncertain about approach or the issue is ambiguous, ask in `#wg-collectoss-8knot` on the CHAOSS Slack rather than guessing

This keeps new contributions easy to review and reduces churn on "good first issue" PRs that skip existing context.
