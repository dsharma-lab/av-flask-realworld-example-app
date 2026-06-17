# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask implementation of the RealWorld API spec - a Medium-like blog platform with users, profiles, articles, comments, tags, and favoriting functionality.

## Environment Setup

```bash
# Set required environment variables
export CONDUIT_SECRET='something-really-secret'
export FLASK_APP=/path/to/autoapp.py
export FLASK_DEBUG=1  # For development only

# Install dependencies
pip install -r requirements/dev.txt

# Initialize database
flask db init
flask db migrate
flask db upgrade
```

## Common Commands

```bash
# Run development server
flask run --with-threads

# Run all tests
flask test

# Run specific test file
pytest tests/test_articles.py -v

# Lint code
flask lint
flask lint --fix-imports  # Also fixes import order with isort

# Clean compiled Python files
flask clean

# Open interactive shell (with app and models loaded)
flask shell

# Display all URL routes
flask urls

# Database migrations
flask db migrate  # Generate migration script
flask db upgrade  # Apply migrations
flask db downgrade  # Rollback migrations
```

## Architecture

### Application Factory Pattern
- `conduit/app.py`: Application factory using `create_app(config_object)`
- Configuration classes in `conduit/settings.py`: `DevConfig`, `ProdConfig`, `TestConfig`
- Entry point: `autoapp.py` selects config based on `FLASK_DEBUG` flag

### Module Structure (Blueprint-based)
The app is organized into three main domain modules, each containing models, views, and serializers:

- **user**: User registration, authentication, and profile updates (`/api/users`, `/api/user`)
- **profile**: User profiles and following functionality (`/api/profiles`)
- **articles**: Articles, comments, tags, and favorites (`/api/articles`)

Each module follows the pattern:
- `models.py`: SQLAlchemy model definitions
- `views.py`: Flask Blueprint with route handlers
- `serializers.py`: Marshmallow schemas for request/response serialization

### Database Layer
- **CRUDMixin** (`extensions.py`): Adds `.create()`, `.update()`, `.save()`, `.delete()` to all models
- **SurrogatePK** (`database.py`): Mixin providing `id` primary key and `.get_by_id()` class method
- **reference_col()** (`database.py`): Helper function to create foreign key columns
- Models inherit from both `Model` and `SurrogatePK`

### Authentication
- Flask-JWT-Extended for JWT token management
- `current_user` available in routes decorated with `@jwt_required` or `@jwt_optional`
- Custom JWT identity loaders in `conduit/utils.py`
- Token passed in header: `Authorization: Token <jwt_token>`

### API Serialization Pattern
Marshmallow schemas handle request/response transformation:
- `@pre_load`: Unwraps nested `{"user": {...}}` from request body
- `@post_dump`: Wraps response in `{"user": {...}}` structure
- Use `@use_kwargs(schema)` decorator to deserialize request data
- Use `@marshal_with(schema)` decorator to serialize response data

### Key Model Relationships
- **User** has one **UserProfile** (one-to-one)
- **Article** belongs to **UserProfile** author, has many **Comment**s
- **Article** many-to-many with **Tags** (via `tag_assoc` table)
- **Article** many-to-many with **UserProfile** favoriters (via `favoriter_assoc` table)

### Testing
- Test fixtures in `tests/conftest.py`
- Factory-boy factories in `tests/factories.py`
- Tests use SQLite in-memory database (`sqlite://`)
- Use `testapp` fixture (WebTest) for API testing, `db` fixture for database access

---

## Workflow Rules

### Development Flow
1. Pick up ticket, read CLAUDE.md to orient on architecture
2. Use `/onboard` if unfamiliar with a module (articles, user, profile)
3. Implement changes in the correct module -- follow the models/views/serializers pattern
4. Always update or add tests alongside code changes
5. Run `/review` before committing -- catches convention violations automatically
6. Use `/ship` for the commit + PR step

### Commit Message Format
Use conventional commits: `type(scope): description`
- Types: feat, fix, refactor, test, docs, chore
- Scopes: articles, user, profile, auth, db, api
- Max 72 chars for the first line
- Examples: `feat(articles): add tag filtering`, `fix(auth): return 401 on expired JWT`

### Branch Naming
`type/short-description` -- e.g., `feat/tag-filtering`, `fix/jwt-expiry`

### What Not to Do
- Do not hardcode secrets, API keys, or passwords in any file
- Do not run `flask db downgrade` without manual approval
- Do not push with `--force` or `-f`
- Do not edit files outside `conduit/`, `tests/`, `docs/`, `.claude/`, `migrations/`, `requirements/`

---

## Testing Standards

### Test File Structure
- API endpoint tests: use `testapp` fixture (WebTest), call the full endpoint path
- Model tests: use `db` fixture, interact with models directly
- Always test: happy path + 401 (auth failure) + 400 (invalid input) + 404 (not found)
- Never use a live database -- SQLite in-memory only (`sqlite://` in TestConfig)

### What Must Have Tests
- Every new API endpoint (at minimum: success case + unauthenticated case)
- Every model method that contains business logic
- Every Marshmallow schema with custom `@pre_load` or `@post_dump`

### Running Tests
```bash
flask test                          # all tests
pytest tests/test_articles.py -v   # specific file
pytest tests/ -k "test_name" -v    # specific test by name
```

All tests must pass before merging. No exceptions.

---

## AI Pipeline Usage

### Slash Commands Available
- `/review` -- check staged changes against these conventions before committing
- `/test-gen` -- generate tests for changed files and run them
- `/commit` -- generate a conventional commit message and commit
- `/ship` -- full pipeline (review + test + commit + PR); use this for end-of-feature
- `/onboard` -- generate architecture overview for a module or the full project

### Governance Hooks Active
- `validate-bash.py`: blocks destructive bash commands (rm -rf, git push --force, etc.)
- `check-secrets.py`: blocks hardcoded credentials in file edits
- `scope-guard.sh`: restricts edits to conduit/, tests/, docs/, .claude/, and root config files
- `audit-log.sh`: logs every tool action to .claude/audit/audit.jsonl

All blocked actions are logged with an exit_code of 2 in the audit log. To see recent blocked actions:
```bash
jq 'select(.exit_code == 2)' .claude/audit/audit.jsonl
```

### What AI Can and Cannot Do
**Can:** implement features following the established patterns, write tests, review diffs, generate commit messages, create PRs, explain code and architecture

**Cannot:** push with --force, drop tables, downgrade migrations, edit files outside the allowed scope, bypass hooks
