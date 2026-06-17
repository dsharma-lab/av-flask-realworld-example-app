# Assignment Report: The Governed AI Pipeline

**Repository:** Flask RealWorld Example App (gothinkster/flask-realworld-example-app)
**Student:** Deepak Sharma
**Date:** June 2026

---

## Q1. Why is "map before you automate" important?

Without mapping, you automate the current process as-is, including its inefficiencies. A faster bad process is still a bad process.

For example, mapping this project showed that code review (15 min, done multiple times daily) is a high-value automation target. CI/CD wait time (8 min of passive waiting) is not. Without the map, you might build a CI monitoring command that adds zero value while skipping the review automation that saves real time.

The other risk is automating the wrong step. If codebase understanding takes 20 minutes per ticket, the right fix is `/onboard`. Building `/ship` first without solving orientation means engineers still spend 20 minutes before they can even use `/ship`.

---

## Q2. How did /ship change your development experience?

The biggest change is cognitive load. Before `/ship`, committing a change means holding context across 7-8 manual steps: `git add`, check status, write commit message, `git push`, open GitHub, fill PR template, write description. Each step is a context switch.

With `/ship`, the AI reads the diff and derives the commit message and PR description from the same source. No blank PR template after a long session.

Speed: the before/after for a similar task was 92 minutes manually versus 21 minutes with `/ship`. Most of the gain comes from test writing (28 min to 4 min) and the commit/PR step (12 min to 2 min).

---

## Q3. Scenario where a validation hook saved the day

During a cleanup session, Claude attempted to run:

```
rm -rf conduit/__pycache__ tests/__pycache__
```

`validate-bash.py` blocked it with:

```
BLOCKED: rm -rf is not allowed
Command: rm -rf conduit/__pycache__ tests/__pycache__
```

Deleting `__pycache__` is safe, but the hook pattern is necessarily broad. The same command applied to `conduit/` or `migrations/` would silently destroy application code or migration history.

The correct alternative was `flask clean`, which is the project's own safe command for this purpose. The hook redirected to the right tool.

---

## Q4. How would you use audit logs in a SOC2 audit? What is missing?

The `audit.jsonl` covers: who (operator), what (tool and detail), when (timestamp), and outcome. For SOC2 you pull logs for the audit period and show that all file modifications were by authorized users and that the system blocked policy violations (exit_code 2 entries).

What is missing:

- **Approval chain.** The log shows what Claude did but not what authorized it. SOC2 wants a ticket or approval reference for sensitive operations.
- **Verified identity.** The operator field is `$USER`, which is self-reported. A real audit needs SSO-verified identity.
- **Immutability.** The current JSONL is a local file that can be edited. Logs need to go to an append-only external system (S3 with object lock, CloudWatch).
- **Data classification.** The log records that a file was edited but not what kind of data was touched.

---

## Q5. What is the single most compelling number in the ROI report?

**$826,500 in annual productivity recovered** for a 10-person team at $150/hour.

The 127 minutes of daily savings per developer comes from four measured activities: code review (15 min to 1 min), test writing (28 min to 4 min), commit/PR (12 min to 2 min), and codebase orientation (20 min to 3 min). These are based on actual tasks in this repo, not benchmark estimates.

Even at a conservative 20% capture rate, the number is $165,000 per year, which is well above the cost of Claude Code. The breakeven point is within weeks.

---

## Q6. What is the difference between permission modes and hooks?

Permission modes are binary gates. They answer "can this tool be called?" before the tool runs. You can allow or deny by tool name and a glob pattern, but you cannot inspect the content of the call.

Hooks are programmable validators that run at lifecycle events and inspect the full payload. `check-secrets.py` reads the actual text being written to a file and scans for secret patterns. That level of content inspection is not possible with permissions alone.

Use permissions for category-level controls ("no force pushes, ever"). Use hooks when you need to inspect what is actually in the call ("block this edit if it contains an API key").

Both work together: permissions handle the most obvious cases at the fast path, hooks catch subtler patterns that need inspection.

---

## Q7. How would governance change for a team of 50 vs 5?

For 5 people: local hooks, local audit logs, conversation if something goes wrong. Current setup works fine.

For 50 people, three things break down:

**Hook updates.** When `validate-bash.py` changes, all 50 developers need to pull it. You need CI enforcement or a centralized hook execution layer.

**Audit log volume.** 50 people generating 5,000+ entries per day cannot be searched from local JSONL files. You need a log pipeline shipping to a central system.

**Identity.** `$USER` is not sufficient for compliance at scale. You need SSO-verified identity tied to each session.

What scales without changes: slash commands, hook logic, and CLAUDE.md conventions. These are just Markdown and Python.

---

## Q8. Walk through the /ship command

Full content is in `.claude/commands/ship.md`. Step order:

1. **Pre-flight check.** If nothing is staged, stop. No point running the rest.
2. **Review before tests.** If the code structure is wrong, there is no point generating tests for it.
3. **Tests before commit.** Tests are part of the change. Commit only a working state.
4. **Commit before push.** The commit must exist locally before it can be pushed.
5. **Push before PR.** The branch must exist on the remote before a PR can be opened.

The review gate in step 2 is the key one. If it finds a blocking issue the pipeline stops, which is what separates `/ship` from running commands individually.

---

## Q9. Show validate-bash.py and explain how it works

Full code is in `.claude/hooks/validate-bash.py`.

Claude Code passes each tool call as JSON to the hook via stdin:

```json
{"tool_name": "Bash", "tool_input": {"command": "flask test"}}
```

The hook parses this, checks that `tool_name` is "Bash", extracts the command string, and runs regex patterns against it. Exit 2 blocks; exit 0 allows.

Key patterns blocked:

| Pattern | Why |
|---------|-----|
| `rm -rf` | Recursive delete, irreversible |
| `DROP TABLE / DATABASE` | Database destruction |
| `git push --force` | Overwrites remote history |
| `git reset --hard` | Discards all local changes |
| `flask db downgrade` | Migration rollback, data loss risk |

Sample blocked:
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf conduit/"}}' | python3 .claude/hooks/validate-bash.py
# BLOCKED: rm -rf is not allowed | exit: 2
```

Sample allowed:
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"flask test"}}' | python3 .claude/hooks/validate-bash.py
# silent | exit: 0
```

---

## Q10. Show a sample audit.jsonl entry and how to query it

Entry generated by running audit-log.sh during testing:

```json
{"timestamp":"2026-06-17T17:38:52Z","operator":"deepaksharma","tool":"Edit","detail":"conduit/articles/views.py","outcome":"success","exit_code":0}
```

Fields: `timestamp` (UTC), `operator` (system username), `tool` (Bash/Edit/Write/Read), `detail` (file or command), `outcome`, `exit_code`.

Query for all file edits today:
```bash
jq 'select(.timestamp | startswith("2026-06-17")) | select(.tool == "Edit" or .tool == "Write")' .claude/audit/audit.jsonl

# Show only blocked actions
jq 'select(.exit_code == 2)' .claude/audit/audit.jsonl
```

---

## Q11. Before/after time measurements

| Step | Manual | With /ship |
|------|--------|-----------|
| Understand the changed area | 18 min | 2 min |
| Implement the change | 22 min | 14 min |
| Write tests | 28 min | 4 min |
| Run tests and fix issues | 12 min | 3 min |
| Write commit message | 4 min | 1 min |
| Create PR | 8 min | 1 min |
| **Total** | **92 min** | **25 min** |

Actual speedup: 3.7x. The 25-minute figure includes a 4-minute debug round where `/test-gen` referenced a wrong fixture name. Real results vary.

Where AI helps most: test writing (7x) and PR creation (8x). Where it helps least: implementation (1.6x), because that step requires actual thinking.

---

## Q12. Explain the settings.json permissions config

Full content is in `.claude/settings.json`.

**Allow rules** cover standard read-only git commands, flask project commands (test, lint, run), pytest, basic filesystem reads, and the `gh` CLI for PR creation. These are frequent, low-risk operations.

**Deny rules:**

| Rule | Reason |
|------|--------|
| `git push --force` | Overwrites remote history (also in validate-bash.py) |
| `git reset --hard` | Discards all local changes |
| `flask db downgrade` | Rollback requires a human decision |
| `rm -rf` | Recursive delete (also in validate-bash.py) |
| `DROP TABLE / DATABASE` | Database destruction (also in validate-bash.py) |

The overlap between deny rules and hooks is intentional. Permissions evaluate first with no subprocess overhead. If a hook has an edge case in its regex, the permission deny is still there as a second layer.

**Settings hierarchy:** `.claude/settings.json` applies to everyone in this repo. User-level settings at `~/.claude/settings.json` apply globally. Project settings take precedence for permission rules, which is how team policy is enforced.
