#!/usr/bin/env bash
# PostToolUse hook: append every tool action to audit.jsonl.
# Never exits non-zero — logging failures should not block work.

set -uo pipefail

AUDIT_FILE=".claude/audit/audit.jsonl"
mkdir -p "$(dirname "$AUDIT_FILE")"

INPUT=$(cat)

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TOOL=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name','unknown'))" 2>/dev/null || echo "unknown")
OPERATOR="${APP_USER:-${USER:-${USERNAME:-unknown}}}"

# Extract the relevant identifier (file path or command)
DETAIL=$(echo "$INPUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
inp = d.get('tool_input', {})
detail = inp.get('file_path') or inp.get('command') or inp.get('url') or ''
print(str(detail)[:200])
" 2>/dev/null || echo "")

# Outcome: check tool_response for failure indicators
EXIT_CODE=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_response',{}).get('exit_code', 0))" 2>/dev/null || echo "0")
OUTCOME="success"
if [[ "$EXIT_CODE" != "0" ]]; then
    OUTCOME="failed"
fi

ENTRY=$(python3 -c "
import json, sys
detail = sys.argv[1]
entry = {
    'timestamp': '$TIMESTAMP',
    'operator': '$OPERATOR',
    'tool': '$TOOL',
    'detail': detail,
    'outcome': '$OUTCOME',
    'exit_code': int('$EXIT_CODE') if '$EXIT_CODE'.isdigit() else 0
}
print(json.dumps(entry))
" "$DETAIL" 2>/dev/null || echo "{\"timestamp\":\"$TIMESTAMP\",\"tool\":\"$TOOL\",\"outcome\":\"$OUTCOME\",\"detail\":\"\"}")

echo "$ENTRY" >> "$AUDIT_FILE"
exit 0
