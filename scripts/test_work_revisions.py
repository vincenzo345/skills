"""Revision publication and reconciliation at the shared work-record handoff seam."""
import unittest
from unittest.mock import patch
import test_work_records as handoff
RecordError, WorkRecords = handoff.RecordError, handoff.WorkRecords


class RevisionTests(unittest.TestCase):
    setUp = handoff.HandoffTests.setUp
    produce = handoff.HandoffTests.produce

    def test_revision_retains_basis_and_requires_individual_reconciliation(self):
        effort, spec, issue = self.produce()
        sibling = self.records.publish_issue(effort, 'other', '# Other', 'Approved')
        finished = self.records.publish_issue(effort, 'done', '# Done', 'Approved')
        claim = self.records.claim(finished, 'worker')
        self.records.complete(finished, claim['token'], 'Integrated and tested')
        original = (self.root / spec).read_text(encoding='utf-8')
        self.records.revise_spec(effort, '# Revised search', 1, rationale='Add filters')
        self.assertEqual(self.records.read_revision(spec, 1), original)
        self.assertEqual(self.records.read(effort + '/README.md')['metadata']['current_spec']['revision'], 2)
        for target in (issue, sibling):
            with self.assertRaisesRegex(RecordError, 'stale'):
                self.records.claim(target, 'worker')
        self.records.reconcile_issue(issue, 'Title search is unchanged')
        self.assertEqual(self.records.claim(issue, 'worker')['target'], issue)
        with self.assertRaisesRegex(RecordError, 'approval'):
            self.records.reconcile_issue(sibling, 'Scope changed', affected=True, body='# Filters', readiness='ready-for-agent')
        self.records.reconcile_issue(sibling, 'Scope changed', affected=True, body='# Filters', readiness='ready-for-agent', approval='User approved changed slice')
        self.assertEqual(self.records.claim(sibling, 'worker')['target'], sibling)
        self.assertEqual(self.records.read(finished)['metadata']['basis']['revision'], 1)
        with self.assertRaisesRegex(RecordError, 'terminal'):
            self.records.reconcile_issue(finished, 'Never rewrite completed evidence')

    def test_interrupted_publication_blocks_claim_and_retry_preserves_history(self):
        effort, spec, issue = self.produce()
        original = self.records.read_revision(spec, 1)
        real_replace = handoff.module.os.replace
        def interrupt_overview(source, destination):
            if str(destination).replace('\\', '/').endswith(effort + '/README.md'):
                raise OSError('simulated power loss after spec replacement')
            return real_replace(source, destination)
        with patch.object(handoff.module.os, 'replace', side_effect=interrupt_overview):
            with self.assertRaisesRegex(OSError, 'power loss'):
                self.records.revise_spec(effort, '# New scope', 1, rationale='Add filters')
        fresh = WorkRecords(self.root)
        with self.assertRaisesRegex(RecordError, 'incomplete spec publication'):
            fresh.claim(issue, 'worker')
        with self.assertRaisesRegex(RecordError, 'incomplete spec publication'):
            fresh.publish_issue(effort, 'new', '# New', 'Approved')
        fresh.resume_publication(effort)
        self.assertEqual(fresh.read_revision(spec, 1), original)
        self.assertEqual(fresh.read(effort + '/README.md')['metadata']['current_spec']['revision'], 2)
        with self.assertRaisesRegex(RecordError, 'stale'):
            fresh.claim(issue, 'worker')

    def test_active_worker_pauses_without_losing_claim_or_work(self):
        effort, spec, issue = self.produce()
        claim = self.records.claim(issue, 'worker')
        self.records.revalidate(issue, claim['token'])
        self.records.revise_spec(effort, '# New scope', 1, rationale='Change acceptance')
        for operation in (lambda: self.records.revalidate(issue, claim['token']),
                          lambda: self.records.complete(issue, claim['token'], 'Old scope implemented')):
            with self.assertRaisesRegex(RecordError, 'stale'):
                operation()
        self.assertEqual(self.records.read(issue)['metadata']['state'], 'in-progress')
        self.assertIn('Find note', self.records.read(issue)['body'])
        with self.assertRaisesRegex(RecordError, 'already claimed'):
            self.records.claim(issue, 'thief')
        self.records.reconcile_issue(issue, 'Existing title search remains valid')
        with self.assertRaisesRegex(RecordError, 'acquired basis'):
            self.records.revalidate(issue, claim['token'])
        with self.assertRaisesRegex(RecordError, 'acquired basis'):
            self.records.complete(issue, claim['token'], 'Old scope implemented')
        self.records.release(issue, claim['token'])

    def test_editorial_correction_keeps_revision_and_stale_writer_cannot_overwrite(self):
        effort, spec, issue = self.produce()
        self.records.revise_spec(effort, '# Corrected spelling', 1, rationale='Typographical correction only', material=False)
        self.assertEqual(self.records.read(spec)['metadata']['revision'], 1)
        self.assertIn('Typographical correction only', self.records.read(spec)['body'])
        claim = self.records.claim(issue, 'worker')
        self.records.release(issue, claim['token'])
        self.records.revise_spec(effort, '# Changed scope', 1, rationale='Add filters')
        with self.assertRaisesRegex(RecordError, 'stale'):
            self.records.revise_spec(effort, '# Lost update', 1, rationale='Another change')
        self.assertIn('Corrected spelling', self.records.read_revision(spec, 1))

    def test_publication_and_acquisition_share_one_coordination_boundary(self):
        import json
        import subprocess
        import sys
        effort, spec, issue = self.produce()
        revised = self.root / 'revised.md'
        revised.write_text('# New scope', encoding='utf-8')
        base = [sys.executable, str(handoff.HELPER), '--repo', str(self.root)]
        publisher = subprocess.Popen(base + ['revise-spec', '--effort', effort, '--body-file', str(revised), '--expected-revision', '1', '--rationale', 'Change acceptance'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        consumer = subprocess.Popen(base + ['claim', issue, '--owner', 'concurrent-worker'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = publisher.communicate(timeout=30)
        self.assertEqual(publisher.returncode, 0, error)
        claim_output, claim_error = consumer.communicate(timeout=30)
        if consumer.returncode == 0:
            token = json.loads(claim_output)['token']
            with self.assertRaisesRegex(RecordError, 'stale'):
                self.records.revalidate(issue, token)
            self.records.release(issue, token)
        else:
            self.assertEqual(consumer.returncode, 2)
            self.assertIn('stale', claim_error)
        self.assertEqual(self.records.read(spec)['metadata']['revision'], 2)
        self.assertEqual(self.records.read(effort + '/README.md')['metadata']['current_spec']['revision'], 2)
        self.assertIn('saved note', self.records.read_revision(spec, 1))

    def test_conflicting_retained_history_is_never_overwritten(self):
        effort, spec, issue = self.produce()
        history = self.root / effort / 'history/spec-r1.md'
        history.parent.mkdir()
        history.write_text('Preexisting different history', encoding='utf-8')
        with self.assertRaisesRegex(RecordError, 'retained history differs'):
            self.records.revise_spec(effort, '# Revised', 1, rationale='New scope')
        self.assertEqual(history.read_text(encoding='utf-8'), 'Preexisting different history')
        with self.assertRaisesRegex(RecordError, 'incomplete spec publication'):
            self.records.claim(issue, 'worker')

    def test_initial_publication_is_recoverable_after_interruption(self):
        effort = self.records.create_effort('new', 'New', 'Request', 'Outcome')
        real_replace = handoff.module.os.replace
        def interrupt_overview(source, destination):
            if str(destination).replace('\\', '/').endswith(effort + '/README.md'):
                raise OSError('simulated interruption')
            return real_replace(source, destination)
        with patch.object(handoff.module.os, 'replace', side_effect=interrupt_overview):
            with self.assertRaises(OSError):
                self.records.publish_spec(effort, '# Initial')
        fresh = WorkRecords(self.root)
        fresh.resume_publication(effort)
        issue = fresh.publish_issue(effort, 'first', '# Implement', 'Approved')
        self.assertEqual(fresh.claim(issue, 'worker')['target'], issue)
