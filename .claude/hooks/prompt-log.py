#!/usr/bin/env python3
"""UserPromptSubmit hook: logs all user prompts to prompts.jsonl."""

import json
import os
import sys
from datetime import datetime, timezone

PROMPTS_FILE = ".claude/audit/prompts.jsonl"


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    os.makedirs(os.path.dirname(PROMPTS_FILE), exist_ok=True)

    prompt_text = data.get("prompt", "")
    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "operator": os.environ.get("APP_USER") or os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
        "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
        "prompt": prompt_text[:500],
        "prompt_length": len(prompt_text),
    }

    with open(PROMPTS_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
