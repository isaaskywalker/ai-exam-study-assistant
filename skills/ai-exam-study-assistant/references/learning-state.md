# 로컬 학습 상태와 복습 기억

Python 3 표준 라이브러리만 사용한다. `scripts/study-state.py`는 현재 스킬 디렉터리를 기준으로 찾는다. 학생과 함께 안정적인 과목 ID를 정하고, 과목이나 시험이 다르면 디렉터리를 분리한다. 서로 다른 학생이나 과목의 상태를 합치지 않는다. 에이전트가 답안을 채점하고 오답 유형을 판단하며, 도우미는 결과 저장과 복습일 계산만 담당한다.

```bash
python <skill-dir>/scripts/study-state.py --root .study/biology init
python <skill-dir>/scripts/study-state.py --root .study/biology due
python <skill-dir>/scripts/study-state.py --root .study/biology record --event answer.json
```

임시 답안 JSON은 공개 저장소 밖 또는 `.gitignore`에 포함된 `.study/` 폴더에 저장한 뒤 경로를 전달한다.

```json
{"concept":"meiosis","score":0,"question_type":"comparison","error_type":"concept_confusion","confused_with":"mitosis","confidence":0.8,"difficulty":"basic","note":"감수분열과 체세포분열의 염색체 수 변화를 혼동함"}
```

`score`는 0~1이며 부분 점수를 허용한다. `confidence`는 학생이 직접 보고한 값이며 없을 수 있다. 선택적 `at` 값은 시간대를 포함한 ISO datetime이어야 한다. 일반적으로 현재 시각을 사용하고, 과거 기록 이관이나 테스트일 때만 직접 지정한다. 선택적 `event_id`는 재시도 시 중복 저장을 막는다. 오답 판단이 불확실하면 `error_type: unknown`을 사용한다. 상태 파일에 전체 강의자료, 인증정보, 개인식별정보를 저장하지 않는다.

스키마 v1은 concepts, confusion_pairs, question_type_performance, history를 저장한다. 숙련도는 채점 점수 평균 기반의 학습 추정치이지 자격 인증이 아니다. 기본 복습 간격은 점수 0.8 미만이면 1일, 0.8 이상 연속 성공 시 1→3→7→14→30일이다. 실패 또는 부분 회상은 성공 연속 횟수를 초기화한다. 같은 세션 안의 지연 회상은 더 빨리 진행할 수 있다. 이 일정은 단순 휴리스틱이며 검증된 임상 알고리즘이 아니다. 난이도 조절은 스킬 정책에 따라 에이전트가 결정한다.

세션 시작 시 `state.json`을 읽고 과목이 맞는지 확인한 뒤 복습 예정 개념을 보여주고 학습계획에 섞는다. 현재 시험범위와 모드에 맞춰 필터링한다. 범위 밖 기록은 보존하되 문제로 내지 않는다. 복습할 항목이 공부시간보다 많으면 중요하고 약한 주제를 우선하고 미뤄진 항목을 알려준다. 같은 디렉터리에 짧은 세션 인계 정보와 교수 스타일 프로필을 저장할 수 있다. 에이전트가 꺼져 있을 때 푸시 알림이 간다고 말하지 않는다.

도우미는 상태 파일을 원자적으로 교체하고 손상된 파일이나 지원하지 않는 버전을 거부한다. 오류 시 쓰기를 중단하며 조용히 초기화하지 않는다. 과목별로 동시에 하나의 writer만 사용한다. 병렬 세션에서 같은 상태를 동시에 쓰지 않는다. 필요하면 사용자가 승인한 백업으로 복구한다. Python 또는 파일시스템을 사용할 수 없으면 현재 세션에서만 추적하고 휴대 가능한 인계 요약을 제공하되 지속 저장을 했다고 주장하지 않는다. 삭제/초기화는 학생이 명시적으로 요청할 때만 한다.
