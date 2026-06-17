---
description: Generate a smart commit message from staged diff and commit.
allowed-tools: Bash
---

Generate a conventional commit message from the staged diff and commit it.

Steps:
1. Run `git diff --staged` to see what's staged. If nothing is staged, say "Nothing staged. Run git add first." and stop.
2. Run `git status` to confirm which files are staged.
3. Analyze the diff:
   - What type of change is it? (feat, fix, refactor, test, docs, chore)
   - What module/area does it affect? (articles, user, profile, auth, etc.)
   - What is the core change in one sentence?
4. Format the commit message:
   - First line: `type(scope): short description` (max 72 chars)
   - Body (optional): what changed and why, if non-obvious
   - No "Co-authored-by" lines unless the user asks
5. Run the commit:
   ```
   git commit -m "type(scope): description"
   ```
6. Confirm success with `git log --oneline -1`.

Examples of good commit messages:
- `feat(articles): add tag filtering to article list endpoint`
- `fix(auth): return 401 instead of 500 on expired JWT`
- `test(profile): add tests for follow/unfollow API`
- `refactor(models): move CRUDMixin save() to use db.session.merge`
