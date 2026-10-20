"""Explicit legacy normalization and reviewed, resumable local adoption.

No scan or read moves records. Migration requires a saved plan and its review digest.

Internal boundary: Legacy is the storage migration component of WorkRecords, not
an independent tracker client. Its public plan/apply/resume operations acquire
records.locked() and validate _authority() before using the coordinator's internal
storage interface: _read/_record_text and path/identity resolution, plus
_json/_save_json for claims, publication checks, and the recovery journal.
Callers supply the same
WorkRecords instance so migrations and ordinary operations share one authority,
lock, resolver, and error type. Keep these accesses within this component rather
than exposing unlocked storage operations to skill consumers.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import yaml


def normalize(text, ref, error):
    fields = {}
    for name, value in re.findall(r'^\*\*([^*]+):\*\*\s*(.*?)\s*$', text, re.M):
        key = name.lower().replace(' ', '_')
        if key in fields:
            raise error(f'{ref}: ambiguous duplicate legacy field {key}')
        try:
            fields[key] = yaml.safe_load(value)
        except yaml.YAMLError as exc:
            raise error(f'{ref}: malformed legacy {key}') from exc
    if 'id' in fields and fields['id'] != ref:
        raise error(f'{ref}: legacy ID differs from path; reconcile identity explicitly before adoption')
    ownership = {'claim', 'claimed_by', 'claim_token', 'owner', 'workspace', 'assignee'}
    if any(fields.get(key) not in (None, '', False) for key in ownership) or fields.get('status') in {'claimed', 'in-progress'} or fields.get('state') == 'in-progress':
        raise error(f'{ref}: legacy ownership requires explicit recovery; confirm the prior worker stopped before adoption')
    kind = fields.get('kind')
    if kind not in {'implementation', 'decision', 'map', 'spec'}:
        raise error(f'{ref}: missing or ambiguous legacy kind; supply explicit Kind')
    meta = dict(schema=1, kind=kind, id=ref)
    for key in ('effort', 'parent', 'order', 'basis', 'blocked_by', 'revision', 'state', 'readiness'):
        if key in fields:
            meta[key] = fields[key]
    if kind == 'implementation':
        status = fields.get('status')
        if status in {'ready-for-agent', 'needs-info', 'needs-triage', 'ready-for-human', 'wontfix'}:
            meta.setdefault('readiness', status)
            meta.setdefault('state', 'canceled' if status == 'wontfix' else 'open')
        elif status in {'open', 'in-progress', 'waiting', 'completed', 'canceled', 'superseded'}:
            meta.setdefault('state', status)
        if 'readiness' in fields and status in {'ready-for-agent', 'needs-info', 'needs-triage', 'ready-for-human', 'wontfix'} and fields['readiness'] != status:
            raise error(f'{ref}: conflicting legacy status and readiness')
        for key in ('state', 'readiness', 'basis', 'blocked_by'):
            if key not in meta:
                raise error(f'{ref}: missing legacy {key}; explicit information required')
        if not isinstance(meta['blocked_by'], list) or any(not isinstance(v, str) for v in meta['blocked_by']):
            raise error(f'{ref}: ambiguous legacy blocked_by; use a list of repository-relative IDs')
        basis = meta['basis']
        if basis is not None and (not isinstance(basis, dict) or not isinstance(basis.get('ref'), str) or type(basis.get('revision')) is not int):
            raise error(f'{ref}: ambiguous legacy basis; supply ref and revision or explicit null')
    return {'metadata': meta, 'body': text}

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


class Legacy:
    """A migration is a bounded mapping, reviewed before any relocation."""
    def __init__(self, records):
        self.records = records
        # Reuse the caller's exception identity, including imported fixture modules.
        self.error = records.error_type

    def _inventory(self):
        root = self.records.authority
        return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob('*.md') if '.git' not in p.relative_to(root).parts}

    def _plan(self, mappings):
        r = self.records
        if not isinstance(mappings, dict) or not mappings:
            raise self.error('supply a nonempty source-to-destination mapping')
        inventory = self._inventory()
        rows, problems = [], []
        existing = r._legacy_mapping()
        for source, destination in mappings.items():
            src, dst = r._raw_path(source), r._raw_path(destination)
            problems_here = []
            if source in existing or source in existing.values():
                problems_here.append('already migrated identity')
            if dst.exists() or destination in mappings or list(mappings.values()).count(destination) > 1:
                problems_here.append('destination collision')
            if not destination.startswith('work/') or not destination.endswith('.md') or source == destination or {'history', 'legacy-history'} & set(Path(destination).parts):
                problems_here.append('destination must be a new work/ Markdown location')
            try:
                record = r._read(source)
                if record['metadata']['kind'] == 'effort':
                    raise self.error('effort relocation is unsupported; map individual records')
                meta = record['metadata']
                states = {'implementation': {'open', 'in-progress', 'waiting', 'completed', 'canceled', 'superseded'},
                          'decision': {'open', 'resolved', 'superseded', 'canceled'},
                          'map': {'open', 'completed', 'superseded', 'canceled'},
                          'spec': {'current', 'completed', 'superseded', 'canceled'}}
                if meta.get('state') not in states[meta['kind']]:
                    raise self.error('missing or ambiguous lifecycle state')
                if meta['kind'] in {'implementation', 'spec'} and meta.get('readiness') not in {'ready-for-agent', 'needs-info', 'needs-triage', 'ready-for-human', 'wontfix'}:
                    raise self.error('missing or ambiguous readiness')
                if meta['kind'] == 'implementation' and ('basis' not in meta or not isinstance(meta.get('blocked_by'), list)):
                    raise self.error('missing basis or dependency information')
                # Verify dependency identities exist without requiring them to be complete.
                for dep in record['metadata'].get('blocked_by', []):
                    expected = 'decision' if meta['kind'] == 'decision' else 'implementation'
                    if r._read(dep)['metadata']['kind'] != expected:
                        raise self.error(f'{dep}: blocker is not {expected}')
                basis = record['metadata'].get('basis')
                if basis is not None:
                    if not isinstance(basis, dict) or not isinstance(basis.get('ref'), str) or type(basis.get('revision')) is not int:
                        raise self.error('ambiguous legacy basis')
                    r.read_revision_unlocked_for_migration(basis['ref'], basis['revision'])
                kind = record['metadata']['kind']
            except (self.error, OSError, TypeError) as exc:
                problems_here.append(str(exc))
                record, kind = None, 'ambiguous'
            inbound = []
            for ref in inventory:
                text = r._raw_path(ref).read_text(encoding='utf-8-sig')
                links = re.findall(r'\]\(([^)]+)\)', text)
                if source in text or any((r._raw_path(ref).parent / link.split('#')[0]).resolve() == src for link in links if '://' not in link):
                    inbound.append(ref)
            rows.append(dict(source=source, destination=destination, kind=kind, record=record,
                             inbound=inbound, problems=problems_here))
            problems.extend(f'{source}: {p}' for p in problems_here)
        plan = dict(schema=1, mappings=mappings, records=rows, fingerprints=inventory,
                    mapping_before=existing, problems=problems)
        plan['digest'] = digest(plan)
        return plan

    def plan(self, mappings):
        with self.records.locked():
            self.records._authority()
            return self._plan(mappings)

    def apply(self, plan, review, readers_adopted=False):
        r = self.records
        with r.locked():
            r._authority()
            unsigned = {k: v for k, v in plan.items() if k != 'digest'}
            if not readers_adopted or review != plan.get('digest') or digest(unsigned) != review:
                raise self.error('reviewed plan digest and participating-reader adoption are required')
            if plan.get('problems'):
                raise self.error('ambiguous or colliding migration plan: ' + '; '.join(plan['problems']))
            current = self._plan(plan['mappings'])
            if current != plan:
                raise self.error('changed inputs or references; regenerate and review the migration plan')
            if r._json('claims.json', {}):
                raise self.error('release outstanding claims before migration')
            if r._json('publications.json', {}):
                raise self.error('finish pending publications before migration')
            writes = {}
            mapping = dict(plan['mapping_before'])
            for row in plan['records']:
                source, destination = row['source'], row['destination']
                original = r._raw_path(source).read_text(encoding='utf-8-sig')
                snapshot = 'work/legacy-history/' + hashlib.sha256(source.encode()).hexdigest() + '.md'
                if r._raw_path(snapshot).exists():
                    raise self.error('retained snapshot collision')
                writes[snapshot] = original
                record = row['record']
                body = record['body']
                def relink(match):
                    import os
                    link = match.group(1)
                    if '://' in link or link.startswith(('#', 'mailto:')):
                        return match.group(0)
                    path, separator, anchor = link.partition('#')
                    resolved = (r._raw_path(source).parent / path).resolve()
                    if not resolved.is_relative_to(r.authority) or not resolved.exists():
                        raise self.error(f'{source}: unresolved outbound link {link}')
                    adjusted = os.path.relpath(resolved, r._raw_path(destination).parent).replace('\\', '/')
                    return '](' + adjusted + (separator + anchor if separator else '') + ')'
                record = dict(record, body=re.sub(r'\]\(([^)]+)\)', relink, body))
                writes[destination] = r._record_text(record)
                import os
                forward = os.path.relpath(r._raw_path(destination), r._raw_path(source).parent).replace('\\', '/')
                writes[source] = '# Forwarding reference\n\nThis is read-only. Use the shared work-record resolver.\n\n[Authoritative record](' + forward + ')\n\nStable ID: `' + source + '`\n'
                mapping[source] = destination
            writes['work/legacy-map.json'] = json.dumps({'schema': 1, 'mappings': mapping}, indent=2) + '\n'
            before = {ref: r._raw_path(ref).read_text(encoding='utf-8-sig') if r._raw_path(ref).exists() else None for ref in writes}
            r._save_json('migration.json', {'digest': review, 'writes': writes, 'before': before})
            return self._resume()

    def _resume(self):
        r = self.records
        transaction = r._json('migration.json')
        # Check the entire transaction before writing, so recovery never overwrites edits.
        for ref, text in transaction['writes'].items():
            path = r._raw_path(ref)
            current = path.read_text(encoding='utf-8-sig') if path.exists() else None
            if current not in (transaction['before'][ref], text):
                raise self.error(f'{ref}: changed during migration; explicit recovery required')
        from work_records import atomic_write
        for ref, text in transaction['writes'].items():
            atomic_write(r._raw_path(ref), text)
        (r.control / 'migration.json').unlink()
        return transaction['digest']

    def resume(self):
        with self.records.locked():
            self.records._authority()
            return self._resume()


def main(argv=None):
    import argparse
    from work_records import WorkRecords, RecordError
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='.')
    commands = parser.add_subparsers(dest='command', required=True)
    normal = commands.add_parser('normalize')
    normal.add_argument('ref')
    planning = commands.add_parser('plan')
    planning.add_argument('--mapping', required=True, help='JSON source-to-destination object')
    applying = commands.add_parser('apply')
    applying.add_argument('--plan', required=True, help='Saved JSON plan printed by plan')
    applying.add_argument('--review', required=True, help='Digest explicitly reviewed by user')
    applying.add_argument('--readers-adopted', action='store_true')
    commands.add_parser('resume')
    args = parser.parse_args(argv)
    records = WorkRecords(args.repo)
    service = Legacy(records)
    try:
        if args.command == 'normalize':
            result = records.read(args.ref)
        elif args.command == 'plan':
            result = service.plan(json.loads(Path(args.mapping).read_text(encoding='utf-8-sig')))
        elif args.command == 'apply':
            result = service.apply(json.loads(Path(args.plan).read_text(encoding='utf-8-sig')), args.review, args.readers_adopted)
        else:
            result = service.resume()
        print(json.dumps(result, indent=2))
        return 0
    except (RecordError, OSError, ValueError) as exc:
        import sys
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
