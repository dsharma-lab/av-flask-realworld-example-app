# Automation Leverage Analysis

## Scoring Framework

Each workflow step is scored on four dimensions:
- **Frequency**: daily / weekly / monthly
- **Time per occurrence**: minutes spent on this step
- **AI Capability**: how well AI can handle this (low / medium / high / very high)
- **ROI Score**: 1-10 composite score (frequency * time * AI capability, normalized)

## Scored Workflow Steps

| Step | Frequency | Time (min) | AI Capability | ROI Score |
|------|-----------|-----------|---------------|-----------|
| Ticket Pickup | Daily | 10 | Low | 2 |
| Codebase Understanding | Daily | 20 | Very High | 9 |
| Implementation | Daily | 45 | High | 7 |
| Testing | Daily | 25 | High | 8 |
| Code Review | Daily | 15 | Very High | 9 |
| Commit | Daily | 5 | High | 7 |
| Push and PR | Daily | 10 | High | 8 |
| CI/CD Wait | Daily | 8 | Low | 1 |
| Merge and Deploy | Weekly | 7 | Low | 2 |

## Top 3 Automation Targets

### 1. Code Review (ROI: 9/10)

**Why this target:** Code review happens multiple times every day and is the main bottleneck before a commit goes in. Manual review takes 15 minutes and is inconsistent -- different reviewers catch different things, and even the same person misses stuff when tired. AI can check every single convention from CLAUDE.md in under a minute, every time, with no variation.

The cost of a bad review is also high: convention violations that slip through create technical debt that takes much longer to fix later. Automating this step has both a speed benefit and a quality benefit.

**Automated by:** `/review` command

**Expected time reduction:** 15 min -> 1 min per review cycle (15x speedup)

---

### 2. Codebase Understanding (ROI: 9/10)

**Why this target:** Every ticket requires 20 minutes of exploration before any code gets written -- reading model files to understand relationships, grepping for route definitions, checking what fixtures are available in tests/conftest.py. This work is pure pattern recognition that AI does well.

For new team members this is even worse: they spend days building a mental model that an experienced developer has internalized. A single `/onboard` run can surface all of that structure in 2-3 minutes.

**Automated by:** `/onboard` command + Claude's contextual navigation during any session

**Expected time reduction:** 20 min -> 3 min (7x speedup)

---

### 3. Test Writing + PR Creation (Combined ROI: 9/10)

**Why this target:** Test writing follows a highly repetitive pattern in this codebase. Every endpoint test uses the same `testapp` fixture, the same factory-boy data setup, and the same assertion structure. Once you've written ten of them, you're not learning anything new -- you're just executing a template. AI can do that instantly and more thoroughly (covering more error cases).

PR creation is similar: writing a PR description means explaining your own diff to a reviewer, which is exactly what AI can do from the git diff. Combining `/test-gen` + `/commit` + PR creation into `/ship` eliminates the most tedious 30-40 minutes at the end of every feature.

**Automated by:** `/test-gen` and `/ship` commands

**Expected time reduction:** 40 min -> 7 min (6x speedup)

---

## What Was NOT Targeted

- **Ticket Pickup** (ROI: 2/10): Understanding requirements from a ticket requires human judgment about business context. AI can help summarize a ticket but cannot determine priority or feasibility.
- **CI/CD Wait** (ROI: 1/10): This is pure infrastructure latency. No amount of AI helps while GitHub Actions is running.
- **Merge and Deploy** (ROI: 2/10): These steps are already fast and have human approval checkpoints that should stay human.
