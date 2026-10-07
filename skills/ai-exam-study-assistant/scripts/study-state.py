#!/usr/bin/env python3
"""Store graded retrievals locally; show reviews on return, never push reminders."""
import argparse
import json
import math
import os
from pathlib import Path
import tempfile
import uuid
from datetime import datetime, timedelta, timezone

ERRORS = {'knowledge_gap', 'concept_confusion', 'retrieval_failure', 'application_failure', 'procedure_error', 'misread_question', 'overconfidence_guess', 'unknown'}

def stamp(value=None):
    result = datetime.fromisoformat(value) if value else datetime.now(timezone.utc)
    if result.tzinfo is None:
        raise ValueError('Datetime must include timezone')
    return result.astimezone(timezone.utc)

def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError('Score/confidence must be a finite number from 0 to 1')
    return value

def load(path):
    if not path.exists():
        raise ValueError('Initialize this course first')
    state = json.loads(path.read_text())
    if state.get('schema_version') != 1:
        raise ValueError('Unsupported schema version; do not overwrite')
    for key, kind in [('concepts', dict), ('confusion_pairs', dict), ('question_type_performance', dict), ('history', list)]:
        if not isinstance(state.get(key), kind):
            raise ValueError('Invalid state: ' + key)
    return state

def save(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp = tempfile.mkstemp(dir=path.parent, prefix='.state-')
    try:
        with os.fdopen(handle, 'w') as out:
            json.dump(state, out, ensure_ascii=False, indent=2, allow_nan=False)
            out.write('\n')
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def record(state, event):
    concept = event.get('concept')
    qtype = event.get('question_type')
    if not isinstance(concept, str) or not concept.strip() or not isinstance(qtype, str) or not qtype.strip():
        raise ValueError('concept and question_type are required nonempty strings')
    score = number(event['score'])
    confidence = event.get('confidence')
    if confidence is not None:
        number(confidence)
    error = event.get('error_type', 'unknown')
    if error not in ERRORS:
        raise ValueError('Unknown error type')
    difficulty = event.get('difficulty', 'basic')
    if difficulty not in {'basic', 'intermediate', 'advanced'}:
        raise ValueError('Unknown difficulty')
    other = event.get('confused_with')
    if other is not None and (not isinstance(other, str) or not other.strip() or other == concept):
        raise ValueError('confused_with must identify a different concept')
    event_id = event.get('event_id') or str(uuid.uuid4())
    if not isinstance(event_id, str):
        raise ValueError('event_id must be a string')
    if any(e['event_id'] == event_id for e in state['history']):
        return
    at = stamp(event.get('at'))
    c = state['concepts'].setdefault(concept, {'attempts': 0, 'total_score': 0, 'successful_retrievals': 0, 'failed_retrievals': 0, 'streak': 0})
    if c.get('last_seen') and at < stamp(c['last_seen']):
        raise ValueError('Out-of-order event; import chronologically')
    success = score >= .8
    c['attempts'] += 1
    c['total_score'] += score
    c['mastery'] = c['total_score'] / c['attempts']
    c['successful_retrievals' if success else 'failed_retrievals'] += 1
    c['streak'] = c['streak'] + 1 if success else 0
    interval = [1, 3, 7, 14, 30][min(max(c['streak'] - 1, 0), 4)] if success else 1
    c.update(last_seen=at.isoformat(), next_review=(at + timedelta(days=interval)).isoformat(), confidence=confidence, difficulty=difficulty)
    perf = state['question_type_performance'].setdefault(qtype, {'attempts': 0, 'total_score': 0})
    perf['attempts'] += 1
    perf['total_score'] += score
    perf['accuracy'] = perf['total_score'] / perf['attempts']
    if other and not success and error == 'concept_confusion':
        key = json.dumps(sorted([concept, other]), ensure_ascii=False)
        pair = state['confusion_pairs'].setdefault(key, {'concepts': sorted([concept, other]), 'status': 'observed', 'wrong_count': 0})
        pair['wrong_count'] += 1
        pair['last_wrong'] = at.isoformat()
    state['history'].append(dict(event, event_id=event_id, at=at.isoformat(), score=score, error_type=error))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    subs = p.add_subparsers(dest='command', required=True)
    subs.add_parser('init')
    due = subs.add_parser('due'); due.add_argument('--at')
    rec = subs.add_parser('record'); rec.add_argument('--event', type=Path, required=True)
    args = p.parse_args(); path = args.root / 'state.json'
    try:
        if args.command == 'init':
            if path.exists():
                state = load(path)
            else:
                state = dict(schema_version=1, course_id=args.root.name, concepts={}, confusion_pairs={}, question_type_performance={}, history=[])
                save(path, state)
            print(json.dumps({'course_id': state['course_id'], 'state': str(path)}))
        elif args.command == 'due':
            state = load(path); at = stamp(args.at)
            print(json.dumps([dict(concept=k, **v) for k, v in state['concepts'].items() if stamp(v['next_review']) <= at], ensure_ascii=False, indent=2))
        else:
            state = load(path); record(state, json.loads(args.event.read_text())); save(path, state)
            print('Learning state saved.')
    except (ValueError, OSError, KeyError, TypeError) as error:
        p.exit(1, 'State error: ' + str(error) + '\n')

if __name__ == '__main__':
    main()
