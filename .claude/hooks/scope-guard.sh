#!/usr/bin/env bash
# PreToolUse hook: enforces file scope for edits.
# Only conduit/, tests/, docs/, .claude/, migrations/, requirements/ and known root files are editable.

set -uo pipefail

# Read JSON from stdin
INPUT=$(cat)

TOOL=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")

if [[ "$TOOL" != "Edit" && "$TOOL" != "Write" ]]; then
    exit 0
fi

FILE_PATH=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

# Allowed prefixes (relative to project root)
ALLOWED_PREFIXES=(
    "conduit/"
    "tests/"
    "docs/"
    ".claude/"
    "migrations/"
    "requirements/"
)

# Allowed root-level files
ALLOWED_ROOT_FILES=(
    "CLAUDE.md"
    "REPORT.md"
    "autoapp.py"
    "setup.cfg"
    ".flake8"
    "Pipfile"
    "Makefile"
)

# Strip leading ./
NORMALIZED="${FILE_PATH#./}"
# If absolute path, strip the project root prefix
PROJECT_ROOT="$(pwd)/"
NORMALIZED="${NORMALIZED#$PROJECT_ROOT}"

for prefix in "${ALLOWED_PREFIXES[@]}"; do
    if [[ "$NORMALIZED" == "$prefix"* ]]; then
        exit 0
    fi
done

for allowed in "${ALLOWED_ROOT_FILES[@]}"; do
    if [[ "$NORMALIZED" == "$allowed" ]]; then
        exit 0
    fi
done

echo "BLOCKED: Edit outside allowed scope." >&2
echo "File: $FILE_PATH" >&2
echo "Allowed: conduit/, tests/, docs/, .claude/, migrations/, requirements/, and root config files." >&2
exit 2
