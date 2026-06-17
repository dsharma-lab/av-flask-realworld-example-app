#!/usr/bin/env python3
"""PreToolUse hook: blocks dangerous bash commands."""

import json
import re
import sys

BLOCKED_PATTERNS = [
    (r'\brm\s+-rf\b', "rm -rf is not allowed"),
    (r'\brm\s+-fr\b', "rm -rf is not allowed"),
    (r'\bDROP\s+TABLE\b', "DROP TABLE is not allowed"),
    (r'\bDROP\s+DATABASE\b', "DROP DATABASE is not allowed"),
    (r'\bTRUNCATE\s+TABLE\b', "TRUNCATE TABLE is not allowed"),
    (r'git\s+push\s+--force', "git push --force is not allowed"),
    (r'git\s+push\s+-f\b', "git push -f is not allowed"),
    (r'git\s+reset\s+--hard', "git reset --hard is not allowed without confirmation"),
    (r'git\s+checkout\s+--\s+\.', "git checkout -- . discards all changes; not allowed"),
    (r'\bchmod\s+777\b', "chmod 777 is not allowed"),
    (r'\bkill\s+-9\b', "kill -9 is not allowed"),
    (r'>\s*/dev/sd[a-z]', "writing to block devices is not allowed"),
    (r'\bdd\s+if=', "dd commands are not allowed"),
    (r'flask\s+db\s+downgrade', "flask db downgrade requires manual approval"),
]


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")

    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print(f"BLOCKED: {reason}", file=sys.stderr)
            print(f"Command: {command[:200]}", file=sys.stderr)
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
