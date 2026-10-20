"""Planning artifacts and cross-skill handoff through the public producer seam."""
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/engineering/setup-repo/scripts'))
from work_planning import PlanningRecords, RecordError


class PlanningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.records = PlanningRecords(self.root)
        self.records.configure()

    def test_complete_planning_to_fresh_implementation_handoff(self):
        r = self.records
        effort = r.create_effort('notes', 'Find notes', 'Find saved notes', 'A buildable search specification')
        map_ref = r.chart(effort, 'Find notes', 'A buildable search specification', 'Ranking remains unclear.')
        decision = r.add_decision(effort, 'scope', 'Search scope', 'Search titles or full text?', 'grilling')
        r.record_discovery(effort, 'Human requires offline operation. Ranking is still open.')
        claim = r.claim_decision(decision, 'planning-session')
        r.resolve_decision(decision, claim['token'], 'Title search first.', human_answer='Title search first, please.')
        resumed = PlanningRecords(self.root)
        self.assertEqual(resumed.create_effort('unused', '', '', '', effort=effort), effort)
        self.assertEqual(resumed.read(map_ref)['metadata']['state'], 'open')
        self.assertIn('Title search first.', resumed.read(decision)['body'])
        self.assertIn('offline', (self.root / effort / 'discovery.md').read_text())
        spec = resumed.publish_spec(effort, '# Find notes\n\nSearch titles offline.\n\nBasis: [' + decision + '](' + decision + ')')
        self.assertFalse((self.root / effort / 'tickets').exists())
        issue = resumed.publish_issue(effort, 'search', '# Title search\n\n- [ ] Saved title is found offline.', 'Human approved this single slice.')
        consumer = PlanningRecords(self.root)
        self.assertEqual(consumer.read(issue)['metadata']['basis'], {'ref': spec, 'revision': 1})
        self.assertEqual(consumer.claim(issue, 'fresh-worker')['target'], issue)
        with self.assertRaisesRegex(RecordError, 'implementation'):
            consumer.claim(decision, 'wrong-kind')

    def test_supersession_retains_answers_and_requires_dependent_review(self):
        r = self.records
        effort = r.create_effort('search', 'Search', 'Find notes', 'Ready specification')
        map_ref = r.chart(effort, 'Search', 'Ready specification', 'Ranking')
        old = r.add_decision(effort, 'scope', 'Scope', 'Titles or text?', 'grilling')
        claim = r.claim_decision(old, 'human-session')
        with self.assertRaisesRegex(RecordError, 'human answer'):
            r.resolve_decision(old, claim['token'], 'Titles')
        self.assertEqual(r.read(old)['metadata']['state'], 'open')
        r.resolve_decision(old, claim['token'], 'Titles', human_answer='Titles, please.')
        dependent = r.add_decision(effort, 'ranking', 'Ranking', 'How rank?', 'grilling', blocked_by=[old])
        replacement = r.add_decision(effort, 'scope-again', 'Revised scope', 'Full text now?', 'grilling')
        r.supersede_decision(old, replacement, 'New requirement includes body search.')
        self.assertEqual(r.read(old)['metadata']['state'], 'superseded')
        self.assertIn('Titles, please.', r.read(old)['body'])
        self.assertEqual(r.read(dependent)['metadata']['blocked_by'], [replacement])
        self.assertNotIn('readiness', r.read(dependent)['metadata'])
        self.assertIn('superseded', r.read(map_ref)['body'])
        with self.assertRaisesRegex(RecordError, 'review'):
            r.claim_decision(dependent, 'later-session')
        claim = r.claim_decision(replacement, 'human-session')
        r.resolve_decision(replacement, claim['token'], 'Full text', human_answer='Full text.')
        with self.assertRaisesRegex(RecordError, 'review'):
            r.claim_decision(dependent, 'later-session')
        r.review_decision(dependent, 'Ranking question remains valid with full text.')
        claim = r.claim_decision(dependent, 'later-session')
        with self.assertRaisesRegex(RecordError, 'claimed'):
            r.claim_decision(dependent, 'competing-session')
        r.release(dependent, claim['token'])


if __name__ == '__main__':
    unittest.main()
