#!/usr/bin/env python3
"""PreToolUse hook: scans file edits for leaked secrets."""

import json
import re
import sys

SECRET_PATTERNS = [
    (r'sk-[a-zA-Z0-9]{20,}', "OpenAI/Anthropic API key pattern detected"),
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID detected"),
    (r'[0-9a-zA-Z/+]{40}', "Possible AWS Secret Access Key (40-char base64)"),
    (r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----', "Private key detected"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token detected"),
    (r'ghs_[a-zA-Z0-9]{36}', "GitHub App token detected"),
    (r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{4,}["\']', "Hardcoded password detected"),
    (r'(?i)(secret|api_key|apikey|access_token|auth_token)\s*=\s*["\'][^"\']{4,}["\']', "Hardcoded secret detected"),
    (r'(?i)CONDUIT_SECRET\s*=\s*["\'][^"\']{4,}["\']', "Flask secret key hardcoded"),
    (r'postgresql://[^:]+:[^@]+@', "Database URL with credentials detected"),
    (r'mysql://[^:]+:[^@]+@', "MySQL URL with credentials detected"),
]

# Files where some patterns are expected (test fixtures with fake data)
EXEMPT_PATHS = [
    "tests/",
    ".env.example",
    "requirements/",
    ".claude/hooks/",
]


def is_exempt(file_path):
    return any(file_path.startswith(p) or f"/{p}" in file_path for p in EXEMPT_PATHS)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    # Edit uses new_string, Write uses content
    content = tool_input.get("new_string", "") or tool_input.get("content", "")

    if is_exempt(file_path):
        sys.exit(0)

    for pattern, reason in SECRET_PATTERNS:
        if re.search(pattern, content):
            print(f"BLOCKED: {reason}", file=sys.stderr)
            print(f"File: {file_path}", file=sys.stderr)
            print("Move secrets to environment variables or .env files (not committed).", file=sys.stderr)
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
