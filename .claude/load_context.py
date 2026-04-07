"""SessionStart hook: inject CLAUDE.md and docs/architecture.md into model context."""
import json
import pathlib

root = pathlib.Path(__file__).parent.parent  # project root

candidates = [
    (root / "CLAUDE.md", "CLAUDE.md"),
    (root / "agent.md", "agent.md  [rename to CLAUDE.md so it auto-loads]"),
]
arch = root / "docs" / "architecture.md"

parts = []
for path, label in candidates:
    if path.exists():
        parts.append(f"=== {label} ===\n{path.read_text('utf-8', errors='replace')}")
        break  # only load one (prefer CLAUDE.md)

if arch.exists():
    parts.append(f"=== docs/architecture.md ===\n{arch.read_text('utf-8', errors='replace')}")

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "\n\n".join(parts),
    }
}))
