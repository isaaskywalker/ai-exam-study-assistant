import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/ai-exam-study-assistant/scripts/study-state.py'

class StateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'course'
        self.call('init')
    def tearDown(self):
        self.temp.cleanup()
    def call(self, *args, ok=True):
        p = subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root), *args], capture_output=True, text=True)
        self.assertEqual(p.returncode == 0, ok, p.stderr)
        return p.stdout
    def event(self, **values):
        e = dict(concept='recall', score=0, question_type='comparison', error_type='concept_confusion', confused_with='precision', at='2026-10-07T10:00:00+09:00', event_id='a')
        e.update(values)
        path = Path(self.temp.name) / 'event.json'; path.write_text(json.dumps(e))
        return path
    def state(self):
        return json.loads((self.root/'state.json').read_text())
    def test_persistence_confusion_and_due(self):
        self.call('record', '--event', str(self.event()))
        s = self.state()
        self.assertEqual(s['concepts']['recall']['failed_retrievals'], 1)
        self.assertEqual(next(iter(s['confusion_pairs'].values()))['wrong_count'], 1)
        self.assertEqual(json.loads(self.call('due', '--at', '2026-10-08T00:59:59+00:00')), [])
        self.assertEqual(len(json.loads(self.call('due', '--at', '2026-10-08T01:00:00+00:00'))), 1)
        self.call('init'); self.assertEqual(self.state(), s)
    def test_spacing_and_reset(self):
        for i, day in enumerate([7,8,11]):
            self.call('record', '--event', str(self.event(score=1, error_type='unknown', event_id=str(i), at=f'2026-10-{day:02}T00:00:00+00:00')))
        self.assertEqual(self.state()['concepts']['recall']['next_review'], '2026-10-18T00:00:00+00:00')
        self.call('record', '--event', str(self.event(event_id='fail', at='2026-10-12T00:00:00+00:00')))
        self.assertEqual(self.state()['concepts']['recall']['streak'], 0)
        self.assertEqual(self.state()['concepts']['recall']['next_review'], '2026-10-13T00:00:00+00:00')
    def test_duplicate_is_idempotent(self):
        e = str(self.event()); self.call('record', '--event', e); before = self.state()
        self.call('record', '--event', e); self.assertEqual(before, self.state())
    def test_invalid_event_preserves_state(self):
        before = self.state()
        for values in [dict(score=2),dict(score=True),dict(confidence=-1),dict(error_type='typo'),dict(at='2026-10-07')]:
            self.call('record', '--event', str(self.event(**values)), ok=False)
            self.assertEqual(before, self.state())
    def test_corrupt_state_not_reset(self):
        p=self.root/'state.json'; p.write_text('{broken')
        self.call('init', ok=False); self.assertEqual(p.read_text(), '{broken')
    def test_courses_isolated(self):
        self.call('record','--event',str(self.event()))
        other=self.root; self.root=Path(self.temp.name)/'another'; self.call('init')
        self.assertEqual(self.state()['concepts'], {})
        self.assertTrue((other/'state.json').exists())

if __name__ == '__main__':
    unittest.main()
