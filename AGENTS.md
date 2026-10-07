# 저장소 작업 지침

이 저장소는 한국인 대학생용 AI 시험공부 어시스턴트 스킬을 패키징합니다.

## 구조

- `.agents/skills/ai-exam-study-assistant/`: Codex용 로컬 스킬
- `.claude/skills/ai-exam-study-assistant/`: Claude Code용 로컬 스킬
- `skills/ai-exam-study-assistant/`: canonical source
- `scripts/sync-skill.py`: canonical source를 두 로컬 스킬 경로로 동기화

## 유지보수

스킬을 수정할 때:
1. `skills/ai-exam-study-assistant/`를 수정합니다.
2. `python scripts/sync-skill.py`를 실행합니다.
3. 세 경로의 `SKILL.md`와 부속 파일이 동일한지 확인합니다.

학생에게 보여주는 기본 출력 언어는 한국어입니다. 영어 강의자료도 기본 설명은 한국어로 하며, 핵심 전공 용어는 필요 시 원문을 병기합니다.

API 키, 개인 강의자료, 학생 개인정보를 저장소에 추가하지 마세요.
