---
description: Full pipeline: review staged changes, generate tests, commit, and create PR.
allowed-tools: Bash, Read, Edit, Write
argument-hint: [PR title, or leave blank to auto-generate]
---

Run the full ship pipeline: review, test, commit, PR.

## Step 1: Pre-flight check
Run `git status` and `git diff --staged`. If nothing is staged, say "Nothing staged. Stage your changes with git add first." and stop.

## Step 2: Code Review
Perform the same review as /review:
- Run `git diff --staged`
- Read CLAUDE.md for conventions
- Check module structure, schema correctness, auth decorators, CRUD usage, naming, line length, no secrets
- If any BLOCKING issues are found (wrong structure, missing auth, hardcoded secrets), stop and report them. Do not continue until fixed.
- Minor suggestions are noted but do not block.

## Step 3: Test Generation
Perform the same steps as /test-gen on the staged files:
- Identify changed functions/endpoints
- Generate tests if missing
- Stage the new test files: `git add tests/`
- Run `flask test` to confirm all tests pass
- If tests fail, stop and report. Do not commit broken tests.

## Step 4: Commit
Generate and apply the commit message:
- Analyze the full staged diff (now including any new tests)
- Format as `type(scope): description`
- Run `git commit -m "..."`

## Step 5: Push and create PR
- Run `git push origin HEAD`
- Run `gh pr create` with:
  - Title: $ARGUMENTS if provided, otherwise generate from commit message
  - Body: summary of changes, test results, and what was reviewed
  - Include the checklist from the code review in the PR body

Report the PR URL when done.
