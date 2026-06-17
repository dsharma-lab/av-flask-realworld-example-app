---
description: AI code review of staged changes against CLAUDE.md conventions. Run before committing.
allowed-tools: Bash, Read
---

Run an AI-first code review of staged changes against the project's conventions.

Steps:
1. Run `git diff --staged` to get all staged changes. If nothing is staged, run `git diff HEAD` to show unstaged changes.
2. Read `CLAUDE.md` to understand the project's conventions and architecture rules.
3. Review the diff against these criteria:
   - Blueprint/module structure: do new files follow the models/views/serializers pattern?
   - Marshmallow schema correctness: are pre_load/post_dump decorators used correctly?
   - JWT authentication: are protected routes using @jwt_required or @jwt_optional?
   - CRUDMixin usage: are create/update/delete operations going through the mixin?
   - Test coverage: does changed code have corresponding test changes?
   - Naming conventions: snake_case for functions/variables, PascalCase for classes
   - Line length: max 120 chars (from setup.cfg)
   - No hardcoded secrets or credentials
4. Output a structured review:

```
## Code Review

### Conventions Check
- [ ] Module structure correct
- [ ] Marshmallow schemas correct
- [ ] Auth decorators present where needed
- [ ] CRUDMixin used for DB ops
- [ ] Tests updated
- [ ] Naming conventions followed
- [ ] Line length <= 120 chars
- [ ] No secrets in code

### Issues Found
[List any issues with file:line references]

### Suggestions
[Optional improvements]

### Verdict
APPROVED / NEEDS CHANGES
```
