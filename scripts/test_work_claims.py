"""Ownership continuation and integration tests through the public record seam."""
import test_work_records as handoff
from test_work_records import WorkRecords, RecordError, HELPER
import subprocess
import sys
import json
import unittest

class ClaimTests(unittest.TestCase):
    setUp = handoff.HandoffTests.setUp
    produce = handoff.HandoffTests.produce
    def test_resume_recovery_preserves_work_and_invalidates_old_token(self):
        _, _, issue = self.produce()
        old = self.records.claim(issue, 'stopped-worker', workspace=self.root / 'saved-work')
        with self.assertRaisesRegex(RecordError, 'token'):
            self.records.resume(issue, 'wrong')
        self.assertEqual(self.records.resume(issue, old['token'])['workspace'], old['workspace'])
        with self.assertRaisesRegex(RecordError, 'stopped'):
            self.records.recover(issue, old['token'], 'replacement', stopped_evidence='')
        new = self.records.recover(issue, old['token'], 'replacement', stopped_evidence='Controller confirmed worker process exited.')
        self.assertEqual(new['recovered_from']['workspace'], old['workspace'])
        self.assertNotEqual(new['token'], old['token'])
        with self.assertRaisesRegex(RecordError, 'token'):
            self.records.release(issue, old['token'])
        self.records.resume(issue, new['token'])

    def test_changed_basis_needs_explicit_worker_acknowledgement(self):
        effort, _, issue = self.produce()
        claim = self.records.claim(issue, 'worker')
        self.records.revise_spec(effort, '# New requirement', 1, 'Changed acceptance')
        self.records.reconcile_issue(issue, 'No impact on this slice')
        with self.assertRaisesRegex(RecordError, 'basis changed'):
            self.records.resume(issue, claim['token'])
        self.records.acknowledge_basis(issue, claim['token'], 'Reviewed retained work against revision 2')
        self.assertEqual(self.records.resume(issue, claim['token'])['basis']['revision'], 2)

    def test_completion_waits_for_actual_integration_and_finishes_graph(self):
        effort, spec_ref, issue = self.produce()
        dependent = self.records.publish_issue(effort, 'dependent', '# Uses first', 'Approved', [issue])
        def git(*args):
            return subprocess.check_output(['git', '-C', str(self.root), *args], text=True).strip()
        git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '--allow-empty', '-qm', 'initial')
        git('branch', 'integration')
        git('checkout', '-qb', 'worker')
        git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '--allow-empty', '-qm', 'slice')
        commit = git('rev-parse', 'HEAD')
        claim = self.records.claim(issue, 'worker')
        with self.assertRaisesRegex(RecordError, 'not available'):
            self.records.complete(issue, claim['token'], 'Tests passed', integration_ref='integration', commit=commit)
        with self.assertRaisesRegex(RecordError, 'blocked by'):
            self.records.claim(dependent, 'next')
        git('branch', '-f', 'integration', commit)
        self.records.complete(issue, claim['token'], 'Tests passed', integration_ref='integration', commit=commit)
        with self.assertRaisesRegex(RecordError, 'unfinished'):
            self.records.complete_spec(spec_ref, 1, 'Accepted graph')
        next_claim = self.records.claim(dependent, 'next')
        self.records.complete(dependent, next_claim['token'], 'Dependent verified', integration_ref='integration', commit=commit)
        self.records.complete_spec(spec_ref, 1, 'All acceptance cases pass')
        self.assertEqual(self.records.read(spec_ref)['metadata']['state'], 'completed')
        self.records.complete_effort(effort, 'Requested outcome verified')

    def test_process_exit_retains_claim_and_stale_worktree_cannot_take_it(self):
        _, _, issue = self.produce()
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '--allow-empty', '-qm', 'fixture'], check=True)
        worker = self.root / 'worker-tree'
        subprocess.run(['git', '-C', str(self.root), 'worktree', 'add', '-qb', 'worker', str(worker)], check=True, capture_output=True)
        result = subprocess.run([sys.executable, str(HELPER), '--repo', str(worker), 'claim', issue, '--owner', 'exited-process'], capture_output=True, text=True, check=True)
        claim = json.loads(result.stdout)
        with self.assertRaisesRegex(RecordError, 'already claimed'):
            WorkRecords(worker).claim(issue, 'second-process')
        self.assertEqual(WorkRecords(worker).resume(issue, claim['token'])['token'], claim['token'])
        self.records.release(issue, claim['token'])
        self.assertEqual(WorkRecords(worker).claim(issue, 'replacement')['target'], issue)

    def test_killed_lock_holder_releases_os_lock_without_losing_claim(self):
        _, _, issue = self.produce()
        claim = self.records.claim(issue, 'retained-worker')
        code = "import importlib.util,sys,time; s=importlib.util.spec_from_file_location('w',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); w=m.WorkRecords(sys.argv[2]); lock=w.locked(); lock.__enter__(); print('locked',flush=True); time.sleep(120)"
        child = subprocess.Popen([sys.executable, '-c', code, str(HELPER), str(self.root)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(), 'locked')
        finally:
            child.kill()
            child.communicate(timeout=10)
        self.assertEqual(self.records.resume(issue, claim['token'])['token'], claim['token'])

if __name__ == '__main__':
    unittest.main()
