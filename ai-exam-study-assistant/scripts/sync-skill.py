from pathlib import Path
import shutil
import filecmp

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "ai-exam-study-assistant"
TARGETS = [
    ROOT / ".agents" / "skills" / "ai-exam-study-assistant",
    ROOT / ".claude" / "skills" / "ai-exam-study-assistant",
]

for target in TARGETS:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(SOURCE, target)

source_text = (SOURCE / "SKILL.md").read_text(encoding="utf-8")
for target in TARGETS:
    assert (target / "SKILL.md").read_text(encoding="utf-8") == source_text

print("Synced canonical skill to Codex and Claude Code directories.")
