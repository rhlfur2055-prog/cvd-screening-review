"""PreToolUse hook: results/*.md|json and figures/ are generated. Block hand edits."""
import json
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

path = (payload.get("tool_input") or {}).get("file_path", "").replace("\\", "/")
generated = ("results/screening_grid.", "results/claim_verification.md", "figures/")
if any(g in path for g in generated):
    print("Generated file — edit src/ and re-run instead (quality rule: no hand-edited numbers).", file=sys.stderr)
    sys.exit(2)
