"""Legacy inputs through the public work-folder handoff boundary."""
import sys
import unittest
import test_work_records as fixtures
sys.path.insert(0, str(fixtures.HELPER.parent))

class LegacyTests(unittest.TestCase):
    setUp = fixtures.HandoffTests.setUp

    def legacy(self, ref='.scratch/old/01.md', extra=''):
        path = self.root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('# Old issue\n\n**Kind:** implementation\n**Status:** ready-for-agent\n**Basis:** null\n**Blocked by:** []\n' + extra + '\n- [ ] Deliver old scope.\n', encoding='utf-8')
        return ref

    def test_explicit_legacy_read_is_nonmutating_and_claimable(self):
        ref = self.legacy()
        before = (self.root / ref).read_bytes()
        self.assertEqual(self.records.select(ref)['target'], ref)
        self.assertEqual(self.records.read(ref)['metadata']['basis'], None)
        self.assertEqual((self.root / ref).read_bytes(), before)
        claim = self.records.claim(ref, 'fresh-session')
        self.assertEqual(claim['target'], ref)
        self.records.release(ref, claim['token'])

    def test_reviewed_migration_preserves_identity_and_alias_claims(self):
        from work_legacy import Legacy
        ref = self.legacy()
        dest = 'work/adopted/tickets/01.md'
        (self.root / 'index.md').write_text('[Old](.scratch/old/01.md)', encoding='utf-8')
        service = Legacy(self.records)
        plan = service.plan({ref: dest})
        self.assertEqual(plan['records'][0]['inbound'], ['index.md'])
        self.assertFalse((self.root / dest).exists())
        service.apply(plan, review=plan['digest'], readers_adopted=True)
        self.assertEqual(self.records.read(dest)['metadata']['id'], ref)
        self.assertEqual(self.records.select(dest)['target'], ref)
        claim = self.records.claim(dest, 'worker')
        with self.assertRaises(fixtures.RecordError):
            self.records.claim(ref, 'other')
        self.assertEqual(self.records.read(ref)['metadata']['state'], 'in-progress')
        self.assertIn('forward', (self.root / ref).read_text(encoding='utf-8').lower())
        self.assertEqual(len(list((self.root / 'work/legacy-history').glob('*.md'))), 1)
        self.records.revalidate(dest, claim['token'])
        self.records.release(dest, claim['token'])
        self.assertEqual(self.records.select(dest)['target'], ref)

    def test_ambiguous_inputs_decisions_and_changed_plans_are_not_executable(self):
        from work_legacy import Legacy
        ref = self.legacy()
        service = Legacy(self.records)
        plan = service.plan({ref: 'work/adopted/tickets/01.md'})
        with self.assertRaisesRegex(fixtures.RecordError, 'reviewed'):
            service.apply(plan, review='not-reviewed', readers_adopted=True)
        (self.root / 'new-inbound.md').write_text('[Old](.scratch/old/01.md)', encoding='utf-8')
        with self.assertRaisesRegex(fixtures.RecordError, 'changed inputs'):
            service.apply(plan, review=plan['digest'], readers_adopted=True)
        original = (self.root / ref).read_text()
        (self.root / ref).write_text(original.replace('**Basis:** null\n', ''), encoding='utf-8')
        with self.assertRaisesRegex(fixtures.RecordError, 'basis'):
            self.records.select(ref)
        report = service.plan({ref: 'work/adopted/tickets/01.md'})
        self.assertEqual(report['records'][0]['kind'], 'ambiguous')
        with self.assertRaisesRegex(fixtures.RecordError, 'ambiguous'):
            service.apply(report, review=report['digest'], readers_adopted=True)
        (self.root / ref).write_text('**Kind:** decision\n**State:** unresolved\n', encoding='utf-8')
        with self.assertRaisesRegex(fixtures.RecordError, 'expected implementation'):
            self.records.select(ref)

    def test_interrupted_apply_blocks_selection_then_resumes_without_duplicate_authority(self):
        from work_legacy import Legacy
        import work_records
        from unittest.mock import patch
        ref = self.legacy()
        dest = 'work/adopted/tickets/01.md'
        service = Legacy(self.records)
        plan = service.plan({ref: dest})
        real_write = work_records.atomic_write
        calls = []
        def interrupt(path, text):
            real_write(path, text)
            calls.append(path)
            if len(calls) == 2:
                raise OSError('fixture interruption after destination write')
        with patch('work_records.atomic_write', side_effect=interrupt):
            with self.assertRaisesRegex(OSError, 'fixture interruption'):
                service.apply(plan, review=plan['digest'], readers_adopted=True)
        with self.assertRaisesRegex(fixtures.RecordError, 'incomplete migration'):
            self.records.select(ref)
        self.assertEqual(service.resume(), plan['digest'])
        self.assertEqual(self.records.select(dest)['target'], ref)
        self.assertEqual(self.records.read(ref), self.records.read(dest))

    def test_dependency_ids_and_relative_links_survive_migration(self):
        from work_legacy import Legacy
        blocker = self.legacy('.scratch/old/blocker.md')
        ref = self.legacy()
        text = (self.root / ref).read_text().replace('**Blocked by:** []', '**Blocked by:** [.scratch/old/blocker.md]')
        (self.root / ref).write_text(text + '\n[Blocker](blocker.md)\n', encoding='utf-8')
        dest = 'work/adopted/tickets/01.md'
        service = Legacy(self.records)
        plan = service.plan({ref: dest, blocker: 'work/adopted/tickets/blocker.md'})
        service.apply(plan, review=plan['digest'], readers_adopted=True)
        self.assertEqual(self.records.read(dest)['metadata']['blocked_by'], [blocker])
        self.assertIn('../../../.scratch/old/blocker.md', self.records.read(dest)['body'])
        with self.assertRaisesRegex(fixtures.RecordError, 'blocked by'):
            self.records.select(dest)
        claim = self.records.claim(blocker, 'worker')
        self.records.complete(blocker, claim['token'], 'Integrated fixture')
        self.assertEqual(self.records.select(dest)['target'], ref)

    def test_old_and_new_references_compete_for_one_claim_in_separate_processes(self):
        from work_legacy import Legacy
        import subprocess
        ref = self.legacy()
        destination = 'work/adopted/tickets/01.md'
        service = Legacy(self.records)
        plan = service.plan({ref: destination})
        service.apply(plan, review=plan['digest'], readers_adopted=True)
        command = [sys.executable, str(fixtures.HELPER), '--repo', str(self.root), 'claim']
        workers = [subprocess.Popen(command + [target, '--owner', owner], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                   for target, owner in [(ref, 'old-reader'), (destination, 'new-reader')]]
        results = [(worker.communicate(timeout=30), worker.returncode) for worker in workers]
        self.assertEqual(sorted(code for _, code in results), [0, 2])
        self.assertIn('already claimed', next(output[1] for output, code in results if code == 2))

    def test_legacy_ownership_requires_recovery_without_source_mutation(self):
        ref = self.legacy(extra='**Owner:** prior-session')
        before = (self.root / ref).read_bytes()
        with self.assertRaisesRegex(fixtures.RecordError, 'ownership requires explicit recovery'):
            self.records.claim(ref, 'new-session')
        self.assertEqual((self.root / ref).read_bytes(), before)

if __name__ == '__main__':
    unittest.main()
