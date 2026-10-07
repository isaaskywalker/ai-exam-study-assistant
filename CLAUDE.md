# 저장소 작업 지침

canonical skill source는 `skills/ai-exam-study-assistant/`입니다.

스킬 수정 절차:
1. canonical source를 수정합니다.
2. `python scripts/sync-skill.py`를 실행합니다.
3. `.claude/skills/ai-exam-study-assistant/`가 동기화되었는지 확인합니다.

이 스킬은 한국인 대학생을 대상으로 하며 학생-facing 기본 출력 언어는 한국어입니다. 영어 자료의 핵심 전공 용어는 필요할 때 원문을 병기합니다.

API 키나 개인 강의자료를 커밋하지 마세요.
