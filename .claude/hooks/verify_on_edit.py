"""PostToolUse hook: after editing claims.json or the manuscript, re-run the claim gate.

Reads the hook JSON from stdin. Exit 2 (stderr shown to Claude) if any claim is
unverified, so an unverified number cannot silently stay in the workflow.
"""
import json
import subprocess
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

path = (payload.get("tool_input") or {}).get("file_path", "").replace("\\", "/")
if not (path.endswith("data/claims.json") or path.endswith("paper/main.md")):
    sys.exit(0)

r = subprocess.run(["uv", "run", "python", "-m", "src.agent.cli", "verify"], capture_output=True, text=True, encoding="utf-8")
bad = [ln for ln in r.stdout.splitlines() if "unverified-in-abstract" in ln]
if bad:
    print("Claim gate: unverified claims (open full text or mark as assumption †):\n" + "\n".join(bad), file=sys.stderr)
    sys.exit(2)
