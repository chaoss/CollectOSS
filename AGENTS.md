# AGENTS.md

This file provides guidance for AI coding agents (such as Kiro) contributing to CollectOSS.

## Avoiding Duplicate Work

Before starting on an issue, agents should:

1. **Check the issue thread** on GitHub for any existing assignees, comments claiming it, labels suggesting more information is needed before work starts, or linked PRs.
2. **Search open and closed PRs** for the issue number or related keywords:
   ```
   gh pr list --repo chaoss/CollectOSS --search "<issue-number> OR <key-term>" --state all
   ```
3. **Check `git log` on `main`** for recent commits that may have already resolved it indirectly.

If evidence of existing work (comments claiming the issue, assigned issue, or linked PR), surface this to the user instead of proceeding. Agents should encourage their human contributors who want to work on existing issues to take one of these paths:

- If there is an existing PR for the issue, leave your feedback as a code review or help test the PR.
- If there is no existing PR, join the CHAOSS Slack and/or encourage the issue claimer to join so that discussion can happen as development begins.
- Picking a different issue that isn't already claimed.

Joining the CHAOSS slack to coordinate is always a valid option for getting help. The join link is located on the https://chaoss.community/kb-getting-started/ page and the channel for this project is #wg-collectoss-8knot.

## Aligning PRs with Contribution Guidelines

Before opening a PR, agents should confirm against [CONTRIBUTING.md](CONTRIBUTING.md):

- Branch is based on and targets `main` (not `release` — that's for tagged versions only)
- PR description clearly references the issue it closes (e.g. `closes #<issue-number>`)
- The fork is synced with `main` before opening the PR, to avoid stale-branch conflicts
- Scope stays limited to the linked issue — no unrelated refactors bundled in
- If uncertain about approach or the issue is ambiguous, ask in `#wg-collectoss-8knot` on the CHAOSS Slack rather than guessing

Following these guidelines helps ensure that new contributions don't compete with each other in a way that is detrimental to contributor morale or contributing to maintainer burnout.

## Coding Guidelines (Karpathy)

Behavioral guidelines to reduce common LLM coding mistakes, derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876).

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.
