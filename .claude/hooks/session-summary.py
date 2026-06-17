#!/usr/bin/env python3
"""Stop hook: generates a session summary report."""

import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

AUDIT_FILE = ".claude/audit/audit.jsonl"
SUMMARY_DIR = ".claude/audit"


def main():
    os.makedirs(SUMMARY_DIR, exist_ok=True)

    entries = []
    if os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

    if not entries:
        sys.exit(0)

    session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")
    tool_counts = Counter(e["tool"] for e in entries)
    outcomes = Counter(e.get("outcome", "success") for e in entries)

    # Derive operator from audit entries (most common), fallback to $USER
    operators = Counter(e.get("operator", "") for e in entries if e.get("operator"))
    operator = operators.most_common(1)[0][0] if operators else os.environ.get("USER", "unknown")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report_path = os.path.join(SUMMARY_DIR, f"session-{timestamp[:10]}.txt")

    lines = [
        f"Session Summary: {timestamp}",
        f"Session ID: {session_id}",
        f"Operator: {operator}",
        "",
        f"Total actions: {len(entries)}",
        f"Successes: {outcomes.get('success', 0)}",
        f"Failures: {outcomes.get('failed', 0)}",
        "",
        "Actions by tool:",
    ]
    for tool, count in tool_counts.most_common():
        lines.append(f"  {tool}: {count}")

    with open(report_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
