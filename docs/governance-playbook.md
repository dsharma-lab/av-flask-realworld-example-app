# Governance Playbook: 6-Week Rollout

## Overview

This playbook covers rolling out the AI-augmented development pipeline to a 10-person engineering team safely. The goal is not to flip a switch but to build confidence gradually, catch problems early, and ensure everyone understands both the capabilities and the safety controls before they become dependent on the system.

---

## Week 1: Foundation and Pilot

**Goal:** Two engineers using the pipeline end-to-end on real tasks

**Actions:**
- Copy `.claude/` directory to the team repo (or have engineers pull the branch)
- Install prerequisites on each pilot machine: Claude Code CLI, Python 3, `gh` CLI
- Run `chmod +x .claude/hooks/*.py .claude/hooks/*.sh` on each machine
- Pilot engineers each run `/onboard` to verify it generates useful output
- Pilot engineers each complete one full `/ship` cycle on a real (low-risk) ticket
- Verify `.claude/audit/audit.jsonl` is being written after each session
- Share `docs/workflow-map.md` with the full team for awareness

**What to watch for:**
- Hook false positives (legitimate commands getting blocked)
- Python version issues with hook scripts
- `gh` CLI authentication problems for PR creation

**Success criteria:** Both pilot engineers complete one `/ship` cycle without errors and report the output as useful

---

## Week 2: Hook Tuning

**Goal:** Adjust hook rules based on real usage data

**Actions:**
- Review `audit.jsonl` from week 1. Look for blocked actions (exit_code: 2 entries)
- For each blocked action, determine: was it a real threat or a false positive?
- Update `validate-bash.py` if any project-specific dangerous commands were missed
- Update `scope-guard.sh` if any legitimate directories were blocked (e.g., `static/` or `migrations/`)
- Update `check-secrets.py` exempt paths if test fixtures were triggering false positives
- Document every change to hook rules and the reason for it

**Key question to answer:** What is the false positive rate? If hooks block more than 5% of legitimate operations, engineers will start finding workarounds rather than respecting the controls.

**Success criteria:** False positive rate under 5%, no legitimate workflow operations being blocked

---

## Week 3: Full Team Onboarding

**Goal:** All 10 engineers actively using slash commands

**Actions:**
- 1-hour team workshop: live demo of `/ship` end-to-end (screen share, real ticket)
- Each engineer runs `/onboard` independently on the repo to verify setup
- Walk through what each hook does and why. Engineers need to understand the controls, not just accept them
- Agree on a shared location for audit logs (local per machine, or a shared network path)
- Add `/review` to the team's PR checklist in the GitHub PR template

**What to cover in the workshop:**
- How to use each slash command with real examples from the project
- What gets blocked and why (show a live demo of `validate-bash.py` blocking a dangerous command)
- What audit logs capture and who can see them
- How to report a false positive (update the hook rule, not bypass the hook)

**Success criteria:** 8 out of 10 engineers actively using at least `/commit` and `/review` within the week

---

## Week 4: Measurement Baseline

**Goal:** Capture real before/after numbers to build the ROI case

**Actions:**
- Each engineer tracks time for 3 tasks: one with slash commands, one without (or use memory of recent manual tasks)
- Collect audit log data for the week: total actions, block count, tool distribution
- Compare commit message quality: check `git log` for conventional format compliance rate
- Compare test coverage for PRs opened with `/ship` vs. without
- Identify which commands are used most and least

**What to measure:**
- Average time per feature cycle (ticket to merged PR)
- Convention violation rate in PRs (from `/review` output that found issues)
- Test case count per endpoint (did `/test-gen` increase coverage depth?)

**Success criteria:** Data collected from at least 8 engineers, 3 tasks each, with honest time tracking

---

## Week 5: Process Integration

**Goal:** Make the AI pipeline the default workflow, not optional

**Actions:**
- Document `/review` as a required step before committing (add to CONTRIBUTING.md or team wiki)
- Document `/ship` as the preferred PR creation method
- Configure commitlint in CI to enforce conventional commit format (since `/commit` now generates it)
- Set up centralized audit log aggregation if compliance requires it (options: rsync to shared drive, S3 upload triggered from audit-log.sh, or a log management tool)
- Update CLAUDE.md with any new conventions discovered during weeks 1-4

**CI addition for conventional commits:**
```bash
# Add to .travis.yml or .circleci/config.yml
- pip install commitlint
- commitlint --from HEAD~1
```

**Success criteria:** More than 80% of PRs created via `/ship`, CI enforcing commit format

---

## Week 6: Review and Scale Plan

**Goal:** Document the ROI, identify gaps, plan the next quarter

**Actions:**
- Update `docs/roi-report.md` with real numbers from week 4 measurement
- Present the updated ROI report to the engineering director
- Identify the next 3 automation targets from `docs/leverage-analysis.md`
- Address the scaling questions for if/when the team grows:
  - How will hook updates be distributed to all machines?
  - Who owns the hook code and reviews changes to it?
  - Where do audit logs live and how long are they retained?
  - How is the audit trail identity-verified (beyond `$USER`)?
- Document a maintenance schedule: who reviews audit logs weekly, who updates hook patterns when new threat patterns are discovered

**Success criteria:** ROI report presented, next quarter plan approved, maintenance ownership documented

---

## Common Problems and Fixes

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| scope-guard.sh blocks a legitimate file | Path not in ALLOWED_PREFIXES | Add the path to the allowed list in scope-guard.sh |
| validate-bash.py blocks flask clean | Pattern too broad | Narrow the rm pattern or add flask clean to exempt list |
| audit.jsonl not being written | Missing write permission on .claude/audit/ | `chmod 755 .claude/audit/` |
| Hook not running at all | Python path issue | Use absolute path for python3 in settings.json |
| /ship fails on gh pr create | Not authenticated | Run `gh auth login` |
