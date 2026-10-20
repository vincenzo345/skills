"""Remote contract fixtures, not authenticated provider or exclusivity proof."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/engineering/setup-repo/scripts'))
from work_remote import RemoteContract, RemoteError


class RemoteHandoffTests(unittest.TestCase):
    def setUp(self):
        self.spec = 'https://github.com/example/issues/issues/10'
        self.issue = 'https://github.com/example/issues/issues/11'
        self.data = {
            self.spec: {'kind': 'spec', 'state': 'current', 'revision': 2},
            self.issue: {'kind': 'implementation', 'state': 'open', 'readiness': 'ready-for-agent',
                         'basis': {'ref': self.spec, 'revision': 2}, 'blocked_by': [],
                         'dependencies_complete': True, 'claim': None, 'order': 1,
                         'assets': ['work/search/design.md'], 'effort_state': 'active'},
        }
        self.reads = []
        def fetch(ref):
            self.reads.append(ref)
            return deepcopy(self.data[ref])
        self.remote = RemoteContract('github', fetch)

    def test_remote_handoff_uses_current_spec_and_preserves_asset_links(self):
        selected = self.remote.inspect(self.issue)
        self.assertEqual(selected['assets'], ['work/search/design.md'])
        self.assertEqual(self.reads, [self.issue, self.spec])
        self.data[self.spec]['revision'] = 3
        with self.assertRaisesRegex(RemoteError, 'stale spec basis'):
            self.remote.inspect(self.issue, acquired_basis=selected['basis'])
        self.assertEqual(self.reads[-2:], [self.issue, self.spec])

class RemoteFailureTests(unittest.TestCase):
    setUp = RemoteHandoffTests.setUp
    def test_incomplete_dependencies_and_canceled_blocker_are_not_satisfied(self):
        blocker = 'https://github.com/example/issues/issues/9'
        self.data[self.issue]['blocked_by'] = [blocker]
        self.data[self.issue]['dependencies_complete'] = False
        with self.assertRaisesRegex(RemoteError, 'incomplete dependency query'):
            self.remote.inspect(self.issue)
        self.data[self.issue]['dependencies_complete'] = True
        self.data[blocker] = {'kind': 'implementation', 'native_state': 'closed', 'state_reason': 'not_planned'}
        with self.assertRaisesRegex(RemoteError, 'canceled blocker'):
            self.remote.inspect(self.issue)
        self.data[blocker]['state_reason'] = 'completed'
        self.assertEqual(self.remote.inspect(self.issue)['basis']['revision'], 2)
        self.data.pop(blocker)
        with self.assertRaisesRegex(RemoteError, 'unavailable remote record'):
            self.remote.inspect(self.issue)

class RemoteOwnershipTests(unittest.TestCase):
    setUp = RemoteHandoffTests.setUp

    def test_conflicting_claim_and_reconciled_basis_stop_completion(self):
        self.data[self.issue]['claim'] = {'token': 'held', 'owner': 'another worker'}
        with self.assertRaisesRegex(RemoteError, 'conflicting existing claim'):
            self.remote.inspect(self.issue)
        self.data[self.issue]['state'] = 'in-progress'
        self.assertEqual(self.remote.inspect(self.issue, token='held')['claim']['owner'], 'another worker')
        self.data[self.issue]['basis']['revision'] = 3
        self.data[self.spec]['revision'] = 3
        with self.assertRaisesRegex(RemoteError, 'acquired basis changed'):
            self.remote.inspect(self.issue, token='held', acquired_basis={'ref': self.spec, 'revision': 2})

    def test_two_contenders_both_fail_closed_without_verified_claim_capability(self):
        from concurrent.futures import ThreadPoolExecutor
        for provider in ('github', 'gitlab'):
            remote = RemoteContract(provider, lambda ref: self.data[ref])
            def attempt(owner):
                try:
                    remote.claim(self.issue, owner)
                except RemoteError as exc:
                    return str(exc)
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(attempt, ['one', 'two']))
            self.assertTrue(all('unsupported automatic concurrent claiming' in r for r in results))
            self.assertIsNone(self.data[self.issue]['claim'])

    def test_unknown_basis_and_unowned_in_progress_are_indeterminate(self):
        self.data[self.issue]['basis'] = {'ref': self.spec}
        self.data[self.spec].pop('revision')
        with self.assertRaisesRegex(RemoteError, 'missing or invalid spec basis'):
            self.remote.inspect(self.issue)
        self.data[self.issue]['basis']['revision'] = 2
        self.data[self.spec]['revision'] = 2
        self.data[self.issue]['state'] = 'in-progress'
        with self.assertRaisesRegex(RemoteError, 'in-progress issue has no current owner'):
            self.remote.inspect(self.issue)

    def test_gitlab_closed_without_recorded_outcome_and_missing_readiness_fail(self):
        remote = RemoteContract('gitlab', lambda ref: self.data[ref])
        self.assertEqual(remote.outcome({'native_state': 'closed'}), 'unknown')
        self.assertEqual(remote.outcome({'native_state': 'closed', 'completion_outcome': 'canceled'}), 'canceled')
        self.assertEqual(remote.outcome({'native_state': 'closed', 'completion_outcome': 'completed'}), 'completed')
        self.data[self.issue].pop('readiness')
        with self.assertRaisesRegex(RemoteError, 'missing or unknown readiness'):
            remote.inspect(self.issue)


if __name__ == '__main__':
    unittest.main()
