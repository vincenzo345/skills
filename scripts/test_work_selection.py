"""Queue and explicit selection at the shared work-folder handoff seam."""
import test_work_records as fixtures
module = fixtures.module
import unittest

class SelectionTests(unittest.TestCase):
    setUp = fixtures.HandoffTests.setUp
    produce = fixtures.HandoffTests.produce

    def edit(self, ref, **updates):
        import yaml
        record = self.records.read(ref)
        record["metadata"].update(updates)
        (self.root / ref).write_text("---\n" + yaml.safe_dump(record["metadata"]) + "---\n" + record["body"], encoding="utf-8")

    def queue(self, *efforts):
        (self.root / 'work/queue.md').write_text('# Queue\n\n' + ''.join(f'1. [Effort]({e.removeprefix("work/")}/README.md)\n' for e in efforts), encoding='utf-8')

    def test_queue_skips_blocked_and_claimed_work_but_respects_explicit_scope(self):
        effort, spec, first = self.produce()
        second = self.records.publish_issue(effort, 'blocked', '- [ ] Dependent', 'Approved', blocked_by=[first])
        third = self.records.publish_issue(effort, 'independent', '- [ ] Independent', 'Approved')
        other = self.records.create_effort('other', 'Other', 'Other', 'Other')
        other_issue = self.records.publish_issue(other, 'other', '- [ ] Other', 'Approved')
        self.queue(effort, other)
        self.records.claim(first, 'occupied')
        self.assertEqual(self.records.select()['target'], third)
        self.assertEqual(self.records.select(other)['target'], other_issue)
        self.assertEqual(self.records.select(spec)['target'], third)
        with self.assertRaisesRegex(module.RecordError, 'blocked by'):
            self.records.select(second)
        self.assertEqual(self.records.select_and_claim('worker')['target'], third)
        self.assertEqual(self.records.select()['target'], other_issue)

    def test_missing_readiness_and_unknown_blockers_stop_before_lower_effort(self):
        effort, _, issue = self.produce()
        other = self.records.create_effort('other', 'Other', 'Other', 'Other')
        ready = self.records.publish_issue(other, 'other', '- [ ] Other', 'Approved')
        self.queue(effort, other)
        self.edit(issue, readiness=None)
        with self.assertRaisesRegex(module.RecordError, 'missing or unknown readiness'):
            self.records.select()
        self.assertEqual(self.records.select(other)['target'], ready)
        self.edit(issue, readiness='needs-info')
        self.assertEqual(self.records.select()['target'], ready)
        self.edit(issue, readiness='ready-for-agent', blocked_by=['missing.md'])
        with self.assertRaisesRegex(module.RecordError, 'unavailable record'):
            self.records.select()

    def test_direct_spec_completion_and_effort_completion_preserve_paths(self):
        effort = self.records.create_effort('direct', 'Direct', 'Direct', 'Direct')
        spec = self.records.publish_spec(effort, '# Spec\n- [ ] Deliver scope')
        self.queue(effort)
        with self.assertRaisesRegex(module.Ineligible, 'no implementation issues'):
            self.records.select()
        claim = self.records.claim(spec, 'direct-worker')
        self.records.complete(spec, claim['token'], 'Acceptance passed and integrated.')
        with self.assertRaisesRegex(module.Ineligible, 'completed'):
            self.records.select(spec)
        self.records.complete_effort(effort, 'Requested outcome delivered.')
        self.assertEqual(self.records.read(effort + '/README.md')['metadata']['state'], 'completed')
        self.assertTrue((self.root / spec).exists())
        self.assertNotIn('direct/README.md', (self.root / 'work/queue.md').read_text())

    def test_spec_claim_conflicts_with_later_child_and_issue_claim_conflicts_with_spec(self):
        effort = self.records.create_effort('direct', 'Direct', 'Direct', 'Direct')
        spec = self.records.publish_spec(effort, '# Spec\n- [ ] Deliver scope')
        claim = self.records.claim(spec, 'direct-worker')
        child = self.records.publish_issue(effort, 'child', '- [ ] Child', 'Approved')
        with self.assertRaisesRegex(module.Ineligible, 'scope conflicts'):
            self.records.claim(child, 'child-worker')
        self.records.release(spec, claim['token'])
        child_claim = self.records.claim(child, 'child-worker')
        with self.assertRaises(module.Ineligible):
            self.records.claim(spec, 'second-worker')
        self.records.release(child, child_claim['token'])
        self.assertEqual(self.records.claim(spec, 'graph-worker')['target'], child)

    def test_order_and_history_are_not_implicit_priority(self):
        effort, spec, first = self.produce()
        second = self.records.publish_issue(effort, 'second', '- [ ] Second', 'Approved')
        self.queue(effort)
        self.edit(second, order=1)
        with self.assertRaisesRegex(module.RecordError, 'duplicate issue order'):
            self.records.select()
        self.assertEqual(self.records.select(first)['target'], first)
        self.edit(second, order=2)
        historical = self.root / effort / 'history/spec-r1.md'
        historical.parent.mkdir()
        historical.write_text((self.root / spec).read_text(), encoding='utf-8')
        with self.assertRaisesRegex(module.Ineligible, 'historical'):
            self.records.select(historical.relative_to(self.root).as_posix())
        self.edit(effort + '/README.md', state='waiting')
        with self.assertRaisesRegex(module.Ineligible, 'waiting'):
            self.records.select()

    def test_stale_basis_and_canceled_blockers_are_known_ineligible(self):
        effort, spec, first = self.produce()
        second = self.records.publish_issue(effort, 'second', '- [ ] Second', 'Approved', blocked_by=[first])
        third = self.records.publish_issue(effort, 'third', '- [ ] Third', 'Approved')
        self.queue(effort)
        self.edit(first, state='canceled')
        self.assertEqual(self.records.select()['target'], third)
        with self.assertRaisesRegex(module.Ineligible, 'blocked by'):
            self.records.select(second)
        self.edit(third, basis={'ref':spec, 'revision':2})
        with self.assertRaisesRegex(module.Ineligible, 'stale spec basis'):
            self.records.select()

    def test_missing_queue_is_unavailable_information(self):
        self.produce()
        with self.assertRaisesRegex(module.RecordError, 'queue authority unavailable'):
            self.records.select()

    def test_explicit_standalone_issue_needs_no_effort_or_spec(self):
        import yaml
        ref = 'small-fix.md'
        meta = dict(schema=1, kind='implementation', id=ref, state='open',
                    readiness='ready-for-agent', basis=None, blocked_by=[])
        (self.root / ref).write_text('---\n' + yaml.safe_dump(meta) + '---\n# Small fix\n\n- [ ] Fix supplied typo.\n\nApproved by fixture user.', encoding='utf-8')
        claim = self.records.claim(ref, 'standalone')
        self.assertEqual(claim['target'], ref)
        self.assertIsNone(claim['basis'])
        self.records.complete(ref, claim['token'], 'Typo fixed and verified on integration.')
        with self.assertRaisesRegex(module.Ineligible, 'completed'):
            self.records.select(ref)

if __name__ == '__main__':
    unittest.main()
