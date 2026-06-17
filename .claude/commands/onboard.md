---
description: Generate an architecture summary and key file map for new team members.
allowed-tools: Bash, Read
---

Generate an onboarding guide for a new team member joining this project.

Steps:
1. Read `CLAUDE.md` for project overview and conventions.
2. Run `flask urls` to list all API endpoints.
3. Read the following files to understand the architecture:
   - `conduit/app.py` — application factory
   - `conduit/settings.py` — config classes
   - `conduit/extensions.py` — CRUDMixin
   - `conduit/database.py` — SurrogatePK, reference_col
   - `conduit/user/models.py` — User model
   - `conduit/articles/models.py` — Article model
   - `tests/conftest.py` — test fixtures
4. Run `git log --oneline -10` to show recent activity.
5. Generate the onboarding guide:

```
# Project Onboarding Guide

## What This Project Does
[1-2 sentences from CLAUDE.md overview]

## Getting Started
[Environment setup commands from CLAUDE.md]

## Architecture at a Glance
[Module map: user, profile, articles — each with models/views/serializers]

## Key Files
| File | Purpose |
|------|---------|
| conduit/app.py | App factory — start here |
| conduit/settings.py | Config for dev/prod/test |
| conduit/extensions.py | CRUDMixin — how all models save/delete |
| autoapp.py | Entry point |
| tests/conftest.py | Test fixtures |

## All API Endpoints
[Output of flask urls]

## How to Run Things
[Commands for server, tests, lint, migrations]

## Team Conventions
[From CLAUDE.md: naming, structure, auth patterns]

## Recent Activity
[git log output]
```
