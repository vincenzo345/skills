"""Public work-record handoff tests; synthetic requirements are supplied, not inferred."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HELPER = Path(__file__).resolve().parents[1] / 'skills/engineering/setup-repo/scripts/work_records.py'
spec = importlib.util.spec_from_file_location('work_records', HELPER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
WorkRecords, RecordError = module.WorkRecords, module.RecordError

class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.records = WorkRecords(self.root)
        self.records.configure()

    def produce(self):
        effort = self.records.create_effort('search', 'Search', 'Find saved notes', 'Find one saved note')
        spec_ref = self.records.publish_spec(effort, '# Search\n\n## Acceptance criteria\n\n- Find a saved note.\n')
        issue = self.records.publish_issue(effort, 'find-note', '# Find note\n\n- [ ] Find the saved note by title.\n', 'User approved one slice in fixture conversation.')
        return effort, spec_ref, issue

    def test_produced_issue_is_claimable_in_a_fresh_session(self):
        effort, spec_ref, issue = self.produce()
        resumed = WorkRecords(self.root)
        self.assertEqual(resumed.create_effort('ignored', 'Search', 'ignored', 'ignored', effort=effort), effort)
        self.assertEqual(resumed.read(effort + '/README.md')['metadata']['current_spec'], {'ref': spec_ref, 'revision': 1})
        self.assertEqual(resumed.read(issue)['metadata']['basis'], {'ref': spec_ref, 'revision': 1})
        self.assertIn('User approved one slice', resumed.read(issue)['body'])
        self.assertFalse((self.root / effort / 'map.md').exists())
        claim = resumed.claim(issue, 'fresh-session')
        self.assertEqual(claim['target'], issue)
        self.assertEqual(resumed.read(issue)['metadata']['state'], 'in-progress')
        resumed.release(issue, claim['token'])
        self.assertEqual(resumed.read(issue)['metadata']['state'], 'open')

    def test_completion_requires_ownership_and_revalidates_basis(self):
        effort, spec_ref, issue = self.produce()
        claim = self.records.claim(issue, 'worker')
        with self.assertRaisesRegex(RecordError, 'token'):
            self.records.complete(issue, 'wrong-token', 'Tests pass and merged into integration')
        self.records.complete(issue, claim['token'], 'Tests pass and merged into integration')
        self.assertEqual(self.records.read(issue)['metadata']['state'], 'completed')
        self.assertIn('merged into integration', self.records.read(issue)['body'])

    def test_two_processes_cannot_claim_the_same_issue(self):
        _, _, issue = self.produce()
        command = [sys.executable, str(HELPER), '--repo', str(self.root), 'claim', issue, '--owner']
        workers = [subprocess.Popen(command + [owner], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for owner in ('one', 'two')]
        results = [(worker.communicate(timeout=30), worker.returncode) for worker in workers]
        self.assertEqual(sorted(code for _, code in results), [0, 2])
        self.assertIn('already claimed', next(output[1] for output, code in results if code == 2))

    def test_blocked_and_stale_work_cannot_start(self):
        effort, spec_ref, issue = self.produce()
        dependent = self.records.publish_issue(effort, 'dependent', '# Dependent\n- [ ] Uses first slice.', 'User approved dependent slice.', blocked_by=[issue])
        with self.assertRaisesRegex(RecordError, 'blocked by'):
            self.records.claim(dependent, 'worker')
        path = self.root / spec_ref
        path.write_text(path.read_text(encoding='utf-8').replace('revision: 1', 'revision: 2'), encoding='utf-8')
        with self.assertRaisesRegex(RecordError, 'stale spec'):
            self.records.claim(issue, 'worker')

    def test_similar_titles_remain_distinct_and_spec_does_not_create_children(self):
        first = self.records.create_effort('search', 'Search', 'first', 'first outcome')
        second = self.records.create_effort('search', 'Search', 'second', 'second outcome')
        self.assertEqual((first, second), ('work/search', 'work/search-2'))
        self.records.publish_spec(first, '# Spec\n- Find a note.')
        self.assertFalse((self.root / first / 'tickets').exists())
        with self.assertRaisesRegex(RecordError, 'approval'):
            self.records.publish_issue(first, 'unapproved', '# Not approved', '')

    def test_worktree_uses_declared_authority_and_rejects_foreign_authority(self):
        _, _, issue = self.produce()
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '--allow-empty', '-qm', 'fixture'], check=True)
        worker = self.root / 'worker-tree'
        subprocess.run(['git', '-C', str(self.root), 'worktree', 'add', '-qb', 'worker', str(worker)], check=True, capture_output=True)
        consumer = WorkRecords(worker)
        self.assertFalse((worker / issue).exists())
        self.assertEqual(consumer.claim(issue, 'worktree-worker')['target'], issue)
        unrelated = self.root / 'unrelated'
        subprocess.run(['git', 'init', '-q', str(unrelated)], check=True)
        with self.assertRaisesRegex(RecordError, 'common directory'):
            consumer.configure(unrelated)

if __name__ == '__main__':
    unittest.main()
