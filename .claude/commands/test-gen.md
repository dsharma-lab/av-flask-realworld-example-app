---
description: Generate tests for recently changed files, run them, and report coverage.
allowed-tools: Bash, Read, Edit, Write
argument-hint: [file path, or leave blank for auto-detect from git diff]
---

Generate tests for recently changed files, run them, and report results.

Steps:
1. Find changed files:
   - If $ARGUMENTS is provided, use that file path.
   - Otherwise run `git diff --name-only HEAD` to find changed Python files in conduit/.
2. For each changed file, read it and identify:
   - New functions or methods added
   - Changed logic in existing functions
   - New API endpoints (routes)
3. Read `tests/conftest.py` and `tests/factories.py` to understand available fixtures and factories.
4. Read an existing test file (e.g., `tests/test_articles.py`) to understand test patterns used in this project.
5. Generate tests following the project's pattern:
   - Use `testapp` fixture for API endpoint tests
   - Use `db` fixture for model tests
   - Use factory-boy factories for test data
   - Test happy path AND error cases (400, 401, 404 responses)
   - For auth-protected routes, test both authenticated and unauthenticated requests
6. Write generated tests to the appropriate test file in `tests/`.
7. Run the tests: `flask test` or `pytest tests/ -v`
8. Report:

```
## Test Generation Report

### Files Changed
- conduit/articles/views.py

### Tests Generated
- tests/test_articles.py: 3 new tests

### Test Results
[paste pytest output]

### Coverage
[any coverage notes]
```
