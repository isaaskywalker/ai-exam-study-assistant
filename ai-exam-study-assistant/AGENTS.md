# Repository Instructions

This repository packages the AI Exam Study Assistant skill.

## Structure

- `.agents/skills/ai-exam-study-assistant/` is the Codex-local skill.
- `.claude/skills/ai-exam-study-assistant/` is the Claude Code-local skill.
- `skills/ai-exam-study-assistant/` is the canonical source.
- `scripts/sync-skill.py` mirrors the canonical source to both local skill directories.

## Maintenance

When changing the skill:
1. Edit `skills/ai-exam-study-assistant/`.
2. Run `python scripts/sync-skill.py`.
3. Verify the mirrored SKILL.md files are identical.

Do not add API keys, personal lecture materials, or private student data to the repository.
