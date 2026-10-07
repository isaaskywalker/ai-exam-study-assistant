# Local state and review memory

Use Python 3 (standard library only). Resolve `scripts/study-state.py` relative to this skill's directory. Choose a stable course ID with the student; use separate directories for different courses or exams. Never merge unrelated students or courses. The agent grades answers and diagnoses errors; the helper stores results and schedules reviews.

```bash
python <skill-dir>/scripts/study-state.py --root .study/biology init
python <skill-dir>/scripts/study-state.py --root .study/biology due
python <skill-dir>/scripts/study-state.py --root .study/biology record --event answer.json
```

Write a temporary answer JSON outside the public repository or in the ignored `.study/` directory, then pass its path:

```json
{"concept":"meiosis","score":0,"question_type":"comparison","error_type":"concept_confusion","confused_with":"mitosis","confidence":0.8,"difficulty":"basic","note":"Confused chromosome count with mitosis"}
```

Score is 0–1 (partial credit allowed); confidence is nullable and student-reported. Optional `at` must be an ISO datetime with timezone. Use the current time normally; override only for imported historical events or tests. Optional stable `event_id` prevents retry duplication. Use `error_type: unknown` for uncertain diagnoses. Do not store full lecture files, credentials or personal identifiers in state.

Schema version 1 stores concepts (mastery as mean graded score, attempts, successes/failures, streak, difficulty, last_seen, next_review, confidence), confusion_pairs, question_type_performance, and history. Mastery is a performance estimate, not certification. Helper review intervals: score below 0.8 → 1 day; consecutive scores at least 0.8 → 1, 3, 7, 14, then 30 days. Failed/partial retrieval resets the success streak. In-session delayed recall can happen earlier; stored scheduling is a simple heuristic, not a clinically validated algorithm. Difficulty changes remain an agent decision governed by the skill.

At start, load `state.json`, verify course context, present due concepts and mix them into the plan. Filter by confirmed scope and mode; out-of-scope records stay stored but are not quizzed. If due exceeds the time budget, prioritize important weak topics and disclose deferred reviews. Save a concise session handoff and professor profile in the same directory. Never claim reminders are pushed while the agent is closed.

The helper atomically replaces state and rejects corrupt files or unsupported versions. Stop writes on errors; do not silently reset progress. Use one writer per course; parallel sessions must not write the same state. Restore from a user-approved backup if needed. If Python/filesystem is unavailable, maintain session state and offer a portable handoff without claiming persistence. Delete/reset only at the student's explicit request.
