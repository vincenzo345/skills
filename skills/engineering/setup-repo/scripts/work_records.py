"""Local work-record producer and consumer shared by the engineering skills.

Requires Python 3.10+ and PyYAML. All live reads use the declared authority;
OS locks coordinate processes in worktrees sharing one Git common directory.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid

import yaml

# The helper is shipped beside this script in installed skill bundles.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from work_legacy import normalize


class RecordError(ValueError):
    """A record is ineligible or its authority is indeterminate."""


class Ineligible(RecordError):
    """Known work that cannot currently start; queue traversal may continue."""


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise RecordError(f'duplicate metadata field: {key}')
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def git(checkout, *args):
    result = subprocess.run(['git', '-C', str(checkout), *args], text=True, capture_output=True)
    if result.returncode:
        raise RecordError(f'Git authority unavailable: {result.stderr.strip()}')
    return result.stdout.strip()


class WorkRecords:
    error_type = RecordError
    def __init__(self, checkout):
        self.checkout = Path(git(checkout, 'rev-parse', '--show-toplevel')).resolve()
        self.common = Path(git(self.checkout, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve()
        self.control = self.common / 'work-records'
        self.control.mkdir(exist_ok=True)
        self.authority = None

    @contextmanager
    def locked(self):
        """Short process-safe lock; never hold it while implementing work."""
        with (self.control / 'coordinator.lock').open('a+b') as lock:
            lock.seek(0, os.SEEK_END)
            if lock.tell() == 0:
                lock.write(b'0')
                lock.flush()
            lock.seek(0)
            try:
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
                elif os.name == 'posix':
                    import fcntl
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                else:
                    raise RecordError('unsupported local locking platform')
            except OSError as exc:
                raise RecordError(f'coordinator unavailable: {exc}') from exc
            try:
                yield
            finally:
                lock.seek(0)
                if os.name == 'nt':
                    msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                elif os.name == 'posix':
                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def _json(self, name, default=None):
        path = self.control / name
        if not path.exists() and default is not None:
            return default
        try:
            result = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(result, dict):
                raise ValueError('expected object')
            return result
        except (OSError, ValueError) as exc:
            raise RecordError(f'{name}: authority unavailable: {exc}') from exc

    def _save_json(self, name, value):
        atomic_write(self.control / name, json.dumps(value, indent=2) + '\n')

    def configure(self, authority=None):
        """Declare once; another worktree cannot silently change authority."""
        root = Path(authority or self.checkout).resolve()
        with self.locked():
            if Path(git(root, 'rev-parse', '--show-toplevel')).resolve() != root:
                raise RecordError('authority must be the checkout root')
            common = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve()
            if common != self.common:
                raise RecordError('authority must share this Git common directory')
            existing = self._json('authority.json', {})
            if existing and existing.get('root') != str(root):
                raise RecordError('authority already declared; reconcile it explicitly before changing')
            self._save_json('authority.json', {'root': str(root)})
            self.authority = root
        return str(root)

    def _authority(self):
        config = self._json('authority.json')
        if not isinstance(config.get('root'), str):
            raise RecordError('missing authority root; configure the coordinator first')
        root = Path(config['root']).resolve()
        if Path(git(root, 'rev-parse', '--show-toplevel')).resolve() != root:
            raise RecordError('declared authority is not a checkout root')
        if Path(git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve() != self.common:
            raise RecordError('declared authority no longer shares the Git coordinator')
        self.authority = root
        return root

    def _legacy_mapping(self):
        if (self.control / 'migration.json').exists():
            raise RecordError('incomplete migration; resume migration before accessing records')
        path = self._raw_path('work/legacy-map.json')
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            mappings = data['mappings']
            if data['schema'] != 1 or not isinstance(mappings, dict):
                raise ValueError('unsupported mapping schema')
            for old, new in mappings.items():
                self._raw_path(old)
                self._raw_path(new)
            if len(set(mappings.values())) != len(mappings) or set(mappings) & set(mappings.values()):
                raise ValueError('ambiguous identity mapping')
            return mappings
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise RecordError(f'legacy mapping unavailable: {exc}') from exc

    def _canonical(self, ref):
        mappings = self._legacy_mapping()
        return next((old for old, new in mappings.items() if new == ref), ref)

    def _path(self, ref):
        mappings = self._legacy_mapping()
        return self._raw_path(mappings.get(ref, ref))

    def _raw_path(self, ref):
        if not isinstance(ref, str) or not ref or '\\' in ref:
            raise RecordError(f'invalid repository-relative reference: {ref!r}')
        path = Path(ref)
        if path.is_absolute() or '..' in path.parts or ':' in ref:
            raise RecordError(f'invalid repository-relative reference: {ref}')
        root = self.authority or self._authority()
        resolved = (root / path).resolve()
        if not resolved.is_relative_to(root):
            raise RecordError(f'reference escapes authority: {ref}')
        return resolved

    def _read(self, ref):
        ref = self._canonical(ref)
        path = self._path(ref)
        try:
            text = path.read_text(encoding='utf-8-sig')
        except OSError as exc:
            raise RecordError(f'{ref}: unavailable record: {exc}') from exc
        match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)(.*)\Z', text, re.S)
        if not match:
            return normalize(text, ref, RecordError)
        try:
            meta = yaml.load(match[1], Loader=UniqueLoader)
        except (yaml.YAMLError, TypeError, ValueError) as exc:
            raise RecordError(f'{ref}: invalid metadata: {exc}') from exc
        if not isinstance(meta, dict):
            raise RecordError(f'{ref}: metadata must be a mapping')
        if type(meta.get('schema')) is not int or meta['schema'] != 1:
            raise RecordError(f'{ref}: unsupported schema {meta.get("schema")!r}')
        if meta.get('kind') not in {'effort', 'spec', 'implementation', 'map', 'decision'}:
            raise RecordError(f'{ref}: missing or unknown kind')
        identity = str(Path(ref).parent).replace('\\', '/') if meta['kind'] == 'effort' else ref
        if meta.get('id') != identity:
            raise RecordError(f'{ref}: identity mismatch (expected {identity})')
        return {'metadata': meta, 'body': match[2]}

    def read(self, ref):
        with self.locked():
            self._authority()
            return self._read(ref)

    def _write(self, ref, metadata, body):
        atomic_write(self._path(ref), '---\n' + yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True) + '---\n\n' + body.lstrip())

    @staticmethod
    def _slug(slug):
        if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
            raise RecordError('slug must use lowercase letters, digits, and single hyphens')
        return slug

    def create_effort(self, slug, title, request, outcome, effort=None):
        with self.locked():
            self._authority()
            if effort:
                record = self._read(effort + '/README.md')
                if record['metadata']['kind'] != 'effort':
                    raise RecordError('explicit effort reference is not an effort')
                return effort
            base = 'work/' + self._slug(slug)
            effort = base
            suffix = 2
            while self._path(effort).exists():
                effort = f'{base}-{suffix}'
                suffix += 1
            meta = dict(schema=1, kind='effort', id=effort, state='active', stage='specification', current_spec=None, current_map=None, next_action='Publish the agreed specification.')
            body = f'# {title}\n\n## Original request\n\n{request}\n\n## Desired outcome\n\n{outcome}\n'
            self._write(effort + '/README.md', meta, body)
            return effort

    def _assert_no_pending_publication(self, effort):
        pending = self._json('publications.json', {})
        if effort in pending:
            raise RecordError(f'{effort}: incomplete spec publication; resume publication before selecting work')

    def _apply_publication(self, effort, transaction):
        # A durable journal survives interruption between the two atomic writes.
        history = transaction.get('history')
        if history:
            path = self._path(history['ref'])
            if path.exists():
                if path.read_text(encoding='utf-8') != history['text']:
                    raise RecordError('retained history differs; reconcile publication without overwriting history')
            else:
                atomic_write(path, history['text'])
        for ref, text in transaction['writes'].items():
            path = self._path(ref)
            current = path.read_text(encoding='utf-8') if path.exists() else None
            if current not in (transaction['before'][ref], text):
                raise RecordError(f'{ref}: changed during interrupted publication; reconcile explicitly')
            atomic_write(path, text)
        pending = self._json('publications.json', {})
        pending.pop(effort)
        self._save_json('publications.json', pending)
        return effort + '/spec.md'

    @staticmethod
    def _record_text(record):
        return '---\n' + yaml.safe_dump(record['metadata'], sort_keys=False, allow_unicode=True) + '---\n\n' + record['body'].lstrip()

    def _publish_revision(self, effort, body, expected_revision, readiness, rationale, material):
        self._assert_no_pending_publication(effort)
        overview_ref = effort + '/README.md'
        overview = self._read(overview_ref)
        if overview['metadata'].get('state') != 'active':
            raise RecordError('effort is not active')
        ref = effort + '/spec.md'
        previous = None
        history = None
        if expected_revision == 0:
            if overview['metadata'].get('current_spec') or self._path(ref).exists():
                raise RecordError('spec already exists; publish a retained revision rather than overwrite')
            metadata = dict(schema=1, kind='spec', id=ref, effort=effort, revision=1, state='current', readiness=readiness)
        else:
            spec = self._read(ref)
            metadata = spec['metadata']
            if metadata.get('kind') != 'spec' or metadata.get('state') != 'current' or metadata.get('revision') != expected_revision or overview['metadata'].get('current_spec') != {'ref': ref, 'revision': expected_revision}:
                raise RecordError('stale spec revision or inconsistent current pointer')
            previous = self._path(ref).read_text(encoding='utf-8')
            if material:
                history = {'ref': effort + f'/history/spec-r{expected_revision}.md', 'text': previous}
                metadata['revision'] += 1
            metadata['readiness'] = readiness
            body = body.rstrip() + '\n\n## Revision note\n\n' + rationale.strip() + '\n'
        overview['metadata'].update(current_spec={'ref': ref, 'revision': metadata['revision']}, next_action='Review implementation issues against the current specification.' if previous else 'Review and approve implementation slices.')
        transaction = {'history': history, 'before': {ref: previous, overview_ref: self._path(overview_ref).read_text(encoding='utf-8')}, 'writes': {ref: self._record_text({'metadata': metadata, 'body': body}), overview_ref: self._record_text(overview)}}
        pending = self._json('publications.json', {})
        pending[effort] = transaction
        self._save_json('publications.json', pending)
        return self._apply_publication(effort, transaction)

    def publish_spec(self, effort, body, readiness='ready-for-agent'):
        with self.locked():
            self._authority()
            return self._publish_revision(effort, body, 0, readiness, '', True)

    def revise_spec(self, effort, body, expected_revision, rationale, material=True, readiness='ready-for-agent'):
        if type(expected_revision) is not int or expected_revision < 1:
            raise RecordError('expected_revision must identify a positive published revision')
        if not isinstance(rationale, str) or not rationale.strip():
            raise RecordError('revision rationale is required')
        with self.locked():
            self._authority()
            return self._publish_revision(effort, body, expected_revision, readiness, rationale, material)

    def resume_publication(self, effort):
        with self.locked():
            self._authority()
            pending = self._json('publications.json', {})
            if effort not in pending:
                raise RecordError('no incomplete publication for this effort')
            return self._apply_publication(effort, pending[effort])

    def read_revision_unlocked_for_migration(self, spec_ref, revision):
        spec = self._read(spec_ref)['metadata']
        if spec.get('kind') != 'spec' or type(revision) is not int or revision < 1:
            raise RecordError('invalid legacy basis')
        if revision == spec.get('revision'):
            return
        effort = spec.get('effort')
        if not effort or revision > spec.get('revision', 0) or not self._path(effort + f'/history/spec-r{revision}.md').exists():
            raise RecordError('legacy historical basis unavailable')

    def read_revision(self, spec_ref, revision):
        with self.locked():
            self._authority()
            spec = self._read(spec_ref)['metadata']
            if spec['kind'] != 'spec' or type(revision) is not int or revision < 1:
                raise RecordError('expected spec identity and positive revision')
            effort = spec.get('effort')
            self._assert_no_pending_publication(effort)
            if spec.get('revision') == revision:
                return self._path(spec_ref).read_text(encoding='utf-8')
            if not effort or revision > spec.get('revision', 0):
                raise RecordError('requested revision is unavailable')
            path = self._path(effort + f'/history/spec-r{revision}.md')
            if not path.exists():
                raise RecordError('requested historical revision is unavailable')
            return path.read_text(encoding='utf-8')

    def reconcile_issue(self, target, rationale, affected=False, body=None, readiness=None, approval=None):
        if not isinstance(rationale, str) or not rationale.strip():
            raise RecordError('explicit reconciliation rationale is required')
        with self.locked():
            self._authority()
            target = self._canonical(target)
            issue = self._read(target)
            meta = issue['metadata']
            if meta['kind'] != 'implementation' or meta.get('state') not in {'open', 'in-progress', 'waiting'}:
                raise RecordError('reconciliation requires an unfinished issue; terminal evidence is immutable')
            effort = meta.get('effort')
            if not isinstance(effort, str) or not effort:
                raise RecordError('reconciliation requires a managed effort')
            self._assert_no_pending_publication(effort)
            overview = self._read(effort + '/README.md')['metadata']
            basis = overview.get('current_spec')
            if not isinstance(basis, dict) or not isinstance(meta.get('basis'), dict) or not basis.get('ref') or basis['ref'] != meta['basis'].get('ref'):
                raise RecordError('reconciliation requires the same specification identity')
            if overview.get('state') != 'active':
                raise RecordError('effort is not active')
            old_revision = meta['basis'].get('revision')
            if type(old_revision) is not int or old_revision < 1 or old_revision > basis['revision']:
                raise RecordError('invalid original basis revision')
            spec = self._read(basis['ref'])['metadata']
            if spec.get('kind') != 'spec' or spec.get('revision') != basis['revision'] or spec.get('state') != 'current':
                raise RecordError('inconsistent current spec pointer')
            if affected:
                if not body or not readiness:
                    raise RecordError('affected issues require updated scope and readiness')
                if readiness == 'ready-for-agent' and not (isinstance(approval, str) and approval.strip()):
                    raise RecordError('changed-slice approval is required before affected work is ready')
                issue['body'] = body
                meta['readiness'] = readiness
            elif body is not None or readiness is not None:
                raise RecordError('scope or readiness changes require affected reconciliation')
            previous = meta['basis']['revision']
            meta['basis'] = dict(basis)
            issue['body'] = issue['body'].rstrip() + f'\n\n## Reconciliation r{previous} to r{basis["revision"]}\n\n' + ('Affected: ' if affected else 'No impact: ') + rationale.strip() + ('\n\nApproval: ' + approval.strip() if approval else '') + '\n'
            self._write(target, **issue)
            return target

    @staticmethod
    def _validate_claim_basis(target, record, claim):
        meta = record['metadata']
        live_basis = {'ref': target, 'revision': meta.get('revision')} if meta['kind'] == 'spec' else meta.get('basis')
        if 'basis' not in claim or claim['basis'] != live_basis:
            raise RecordError(f'{target}: acquired basis changed; retain work and explicitly reconcile the active claim')

    def revalidate(self, target, token):
        """Call immediately before publishing results as well as at completion."""
        with self.locked():
            self._authority()
            target = self._canonical(target)
            claim = self._json('claims.json', {}).get(target)
            if not claim or claim.get('token') != token:
                raise RecordError('claim token does not match')
            record = self._eligible(target, allow_in_progress=True)
            self._validate_claim_basis(target, record, claim)
            return {'target': target, 'basis': claim['basis'], 'token': token}

    def resume(self, target, token):
        """Resume only the same ownership after validating live eligibility."""
        with self.locked():
            self._authority()
            target = self._canonical(target)
            claim = self._json('claims.json', {}).get(target)
            if not claim or claim.get('token') != token:
                raise RecordError('claim token does not match')
            record = self._eligible(target, allow_in_progress=True)
            self._validate_claim_basis(target, record, claim)
            return claim

    def recover(self, target, expected_token, owner, stopped_evidence, workspace=None):
        """Controller attests worker stoppage; compare-and-replace prevents takeover races."""
        if not owner or not isinstance(stopped_evidence, str) or not stopped_evidence.strip():
            raise RecordError('owner and evidence that the previous worker stopped are required')
        with self.locked():
            self._authority()
            target = self._canonical(target)
            claims = self._json('claims.json', {})
            old = claims.get(target)
            if not old or old.get('token') != expected_token:
                raise RecordError('claim token does not match')
            record = self._eligible(target, allow_in_progress=True)
            self._validate_claim_basis(target, record, old)
            claim = dict(old, token=uuid.uuid4().hex, owner=owner,
                         workspace=str(Path(workspace or self.checkout).resolve()),
                         acquired_at=datetime.now(timezone.utc).isoformat(),
                         recovered_from=old, stopped_evidence=stopped_evidence.strip())
            claims[target] = claim
            self._save_json('claims.json', claims)
            return claim

    def acknowledge_basis(self, target, token, evidence):
        """Retain ownership after the issue is reconciled and its worker reviews the change."""
        if not isinstance(evidence, str) or not evidence.strip():
            raise RecordError('worker reconciliation evidence is required')
        with self.locked():
            self._authority()
            target = self._canonical(target)
            claims = self._json('claims.json', {})
            claim = claims.get(target)
            if not claim or claim.get('token') != token:
                raise RecordError('claim token does not match')
            record = self._eligible(target, allow_in_progress=True)
            meta = record['metadata']
            basis = {'ref': target, 'revision': meta['revision']} if meta['kind'] == 'spec' else meta['basis']
            claim.setdefault('basis_reviews', []).append({'previous': claim['basis'], 'current': basis, 'evidence': evidence.strip()})
            claim['basis'] = basis
            self._save_json('claims.json', claims)
            return claim

    def publish_issue(self, effort, slug, body, approval, blocked_by=(), readiness='ready-for-agent'):
        if not isinstance(approval, str) or not approval.strip():
            raise RecordError('breakdown approval or explicit task authority is required')
        with self.locked():
            self._authority()
            overview = self._read(effort + '/README.md')
            if overview['metadata'].get('state') != 'active':
                raise RecordError('effort is not active')
            self._assert_no_pending_publication(effort)
            basis = overview['metadata'].get('current_spec')
            if basis:
                spec = self._read(basis['ref'])['metadata']
                if spec.get('kind') != 'spec' or spec.get('revision') != basis.get('revision') or spec.get('state') != 'current':
                    raise RecordError('current spec pointer does not match the live spec')
            children = list(self._path(effort + '/tickets').glob('*.md'))
            orders = [self._read(p.relative_to(self.authority).as_posix())['metadata'].get('order') for p in children]
            if any(type(n) is not int or n < 1 for n in orders) or len(set(orders)) != len(orders):
                raise RecordError('invalid or duplicate issue order')
            order = max(orders, default=0) + 1
            ref = f'{effort}/tickets/{order:02d}-{self._slug(slug)}.md'
            blockers = list(blocked_by)
            if len(set(blockers)) != len(blockers):
                raise RecordError('duplicate blockers')
            for blocker in blockers:
                if self._read(blocker)['metadata']['kind'] != 'implementation':
                    raise RecordError(f'{blocker}: blocker is not an implementation issue')
            meta = dict(schema=1, kind='implementation', id=ref, effort=effort, order=order, state='open', readiness=readiness, basis=basis, blocked_by=blockers)
            self._write(ref, meta, body.rstrip() + '\n\n## Approval\n\n' + approval.strip() + '\n')
            overview['metadata'].update(stage='implementation', next_action='Implement an eligible approved issue when requested.')
            self._write(effort + '/README.md', **overview)
            return ref

    def _dependencies(self, target, visiting=None):
        target = self._canonical(target)
        visiting = set() if visiting is None else visiting
        if target in visiting:
            raise RecordError(f'{target}: dependency cycle')
        visiting.add(target)
        meta = self._read(target)['metadata']
        if meta['kind'] != 'implementation':
            raise RecordError(f'{target}: blocker is not an implementation issue')
        blockers = meta.get('blocked_by')
        if not isinstance(blockers, list) or any(not isinstance(ref, str) for ref in blockers):
            raise RecordError(f'{target}: missing or invalid blocked_by')
        if len(set(blockers)) != len(blockers):
            raise RecordError(f'{target}: duplicate blockers')
        for blocker in blockers:
            self._dependencies(blocker, visiting)
        visiting.remove(target)
        return blockers

    @staticmethod
    def _state(meta, allowed, known, target):
        state = meta.get('state')
        if state not in known:
            raise RecordError(f'{target}: missing or unknown lifecycle {state!r}')
        if state not in allowed:
            raise Ineligible(f'{target}: lifecycle is not eligible ({state})')

    @staticmethod
    def _ready(meta, target):
        value = meta.get('readiness')
        if value not in {'needs-triage', 'needs-info', 'ready-for-agent', 'ready-for-human', 'wontfix'}:
            raise RecordError(f'{target}: missing or unknown readiness {value!r}')
        if value != 'ready-for-agent':
            raise Ineligible(f'{target}: readiness is not ready-for-agent ({value})')

    def _effort(self, effort):
        record = self._read(effort + '/README.md')
        meta = record['metadata']
        if meta['kind'] != 'effort':
            raise RecordError(f'{effort}: expected effort kind')
        self._state(meta, {'active'}, {'active', 'waiting', 'completed', 'canceled', 'superseded'}, effort)
        self._assert_no_pending_publication(effort)
        return record

    def _spec_eligible(self, target):
        record = self._read(target)
        meta = record['metadata']
        if meta['kind'] != 'spec':
            raise RecordError(f'{target}: expected spec kind')
        self._state(meta, {'current'}, {'current', 'completed', 'superseded', 'canceled'}, target)
        self._ready(meta, target)
        if type(meta.get('revision')) is not int or meta['revision'] < 1:
            raise RecordError(f'{target}: invalid spec revision')
        if meta.get('effort'):
            overview = self._effort(meta['effort'])['metadata']
            if overview.get('current_spec') != {'ref': target, 'revision': meta['revision']}:
                raise RecordError(f'{target}: stale spec pointer or inconsistent current pointer')
        return record

    def _eligible(self, target, allow_in_progress=False):
        if {'history', 'legacy-history'} & set(Path(target).parts):
            raise Ineligible(f'{target}: historical records cannot be executed; use the current record')
        record = self._read(target)
        meta = record['metadata']
        if meta['kind'] == 'spec':
            record = self._spec_eligible(target)
            children = self._issues(meta['effort']) if meta.get('effort') else []
            if any((child.get('basis') or {}).get('ref') == target for _, child in children):
                raise Ineligible(f'{target}: spec scope is decomposed; release the direct claim and use the issue graph')
            return record
        if meta['kind'] != 'implementation':
            raise Ineligible(f'{target}: expected implementation kind')
        self._state(meta, {'open', 'in-progress'} if allow_in_progress else {'open'},
                    {'open', 'in-progress', 'waiting', 'completed', 'canceled', 'superseded'}, target)
        self._ready(meta, target)
        effort = meta.get('effort')
        if effort:
            self._effort(effort)
            if type(meta.get('order')) is not int or meta['order'] < 1:
                raise RecordError(f'{target}: missing or invalid order')
        if 'basis' not in meta:
            raise RecordError(f'{target}: missing basis; use explicit null for self-contained work')
        basis = meta['basis']
        if basis is not None:
            if not isinstance(basis, dict) or not isinstance(basis.get('ref'), str) or type(basis.get('revision')) is not int or basis['revision'] < 1:
                raise RecordError(f'{target}: invalid spec basis')
            spec = self._spec_eligible(basis['ref'])['metadata']
            if spec['revision'] != basis['revision']:
                raise Ineligible(f'{target}: stale spec basis')
            if effort and spec.get('effort') != effort:
                raise RecordError(f'{target}: spec effort mismatch')
        for blocker in self._dependencies(target):
            state = self._read(blocker)['metadata'].get('state')
            if state not in {'open', 'in-progress', 'waiting', 'completed', 'canceled', 'superseded'}:
                raise RecordError(f'{blocker}: unknown dependency outcome')
            if state != 'completed':
                raise Ineligible(f'{target}: blocked by {blocker} (not completed)')
        return record

    def _issues(self, effort):
        self._effort(effort)
        records = []
        for path in self._path(effort + '/tickets').glob('*.md'):
            ref = self._canonical(path.relative_to(self.authority).as_posix())
            meta = self._read(ref)['metadata']
            if meta['kind'] != 'implementation':
                continue
            if meta.get('effort') != effort:
                raise RecordError(f'{ref}: effort membership mismatch')
            records.append((ref, meta))
        orders = [meta.get('order') for _, meta in records]
        if any(type(n) is not int or n < 1 for n in orders) or len(set(orders)) != len(orders):
            raise RecordError(f'{effort}: missing, invalid or duplicate issue order')
        return sorted(records, key=lambda item: item[1]['order'])

    def _queue(self):
        try:
            text = self._path('work/queue.md').read_text(encoding='utf-8')
        except OSError as exc:
            raise RecordError(f'queue authority unavailable: {exc}') from exc
        efforts = []
        for line in text.splitlines():
            if not re.match(r'^\s*(?:[0-9]+[.)]|[-*])\s+', line):
                continue
            match = re.search(r'\[[^]]+\]\(([^)]+)\)', line)
            if not match:
                raise RecordError('queue entry must link an effort overview')
            ref = match[1]
            if not ref.endswith('/README.md'):
                raise RecordError(f'invalid queue effort reference: {ref}')
            effort = 'work/' + ref.removesuffix('/README.md')
            self._path(effort)
            if effort in efforts:
                raise RecordError(f'duplicate queue effort: {effort}')
            efforts.append(effort)
        return efforts

    def _conflict(self, target, record, claims):
        if target in claims:
            raise Ineligible(f'{target}: already claimed by {claims[target].get("owner")}')
        meta = record['metadata']
        spec = target if meta['kind'] == 'spec' else (meta.get('basis') or {}).get('ref')
        if spec:
            for ref in claims:
                other = self._read(ref)['metadata']
                other_spec = ref if other['kind'] == 'spec' else (other.get('basis') or {}).get('ref')
                if spec == other_spec and (meta['kind'] == 'spec' or other['kind'] == 'spec'):
                    raise Ineligible(f'{target}: scope conflicts with claim on {ref}')

    def _select(self, target, claims):
        reasons = []
        if target:
            target = self._canonical(target)
            if {'history', 'legacy-history'} & set(Path(target).parts):
                raise Ineligible(f'{target}: historical records cannot be executed; use the current record')
            if self._path(target).is_dir():
                target = target.rstrip('/') + '/README.md'
            record = self._read(target)
            meta = record['metadata']
            if meta['kind'] == 'implementation':
                candidates = [(target, meta)]
            elif meta['kind'] == 'effort':
                candidates = self._issues(meta['id'])
            elif meta['kind'] == 'spec':
                self._spec_eligible(target)
                children = self._issues(meta['effort']) if meta.get('effort') else []
                candidates = [(ref, child) for ref, child in children if (child.get('basis') or {}).get('ref') == target]
                if not candidates:
                    candidates = [(target, meta)]
            else:
                raise Ineligible(f'{target}: expected implementation, spec, or effort kind')
            scopes = [candidates]
        else:
            scopes = None
        def candidates_by_scope():
            if scopes is not None:
                yield from scopes
            else:
                for effort in self._queue():
                    try:
                        yield self._issues(effort)
                    except Ineligible as exc:
                        reasons.append(str(exc))
        for candidates in candidates_by_scope():
            for ref, _ in candidates:
                try:
                    record = self._read(ref)
                    self._conflict(ref, record, claims)
                    record = self._eligible(ref)
                    return {'target': ref, 'record': record, 'authority': str(self.authority), 'skipped': reasons}
                except Ineligible as exc:
                    reasons.append(str(exc))
        raise Ineligible('No eligible work: ' + ('; '.join(reasons) or 'no implementation issues in the requested scope'))

    def select(self, target=None):
        """Read-only preview. Execution must use select_and_claim to recheck atomically."""
        with self.locked():
            self._authority()
            return self._select(target, self._json('claims.json', {}))

    def select_and_claim(self, owner, target=None, workspace=None):
        if not owner:
            raise RecordError('claim owner is required')
        with self.locked():
            self._authority()
            claims = self._json('claims.json', {})
            selected = self._select(target, claims)
            target, record = selected['target'], selected['record']
            claim = dict(target=target, token=uuid.uuid4().hex, owner=owner, workspace=str(Path(workspace or self.checkout).resolve()), acquired_at=datetime.now(timezone.utc).isoformat())
            meta = record['metadata']
            claim['basis'] = {'ref': target, 'revision': meta['revision']} if meta['kind'] == 'spec' else meta['basis']
            claims[target] = claim
            self._save_json('claims.json', claims)
            if record['metadata']['kind'] == 'implementation':
                record['metadata']['state'] = 'in-progress'
                self._write(target, **record)
            return claim

    def claim(self, target, owner, workspace=None):
        return self.select_and_claim(owner, target, workspace)

    def complete_effort(self, effort, evidence):
        """Record a verified overall outcome while preserving stable artifact paths."""
        if not isinstance(evidence, str) or not evidence.strip():
            raise RecordError('completion evidence is required')
        with self.locked():
            self._authority()
            record = self._effort(effort)
            for ref, meta in self._issues(effort):
                if meta.get('state') not in {'completed', 'canceled', 'superseded'}:
                    raise Ineligible(f'{effort}: unfinished issue {ref}')
            if any(self._read(ref)['metadata'].get('effort') == effort for ref in self._json('claims.json', {})):
                raise Ineligible(f'{effort}: outstanding claims')
            for pointer in ('current_spec', 'current_map'):
                ref = record['metadata'].get(pointer)
                if ref:
                    ref = ref['ref'] if isinstance(ref, dict) else ref
                    if self._read(ref)['metadata'].get('state') != 'completed':
                        raise Ineligible(f'{effort}: unfinished {pointer}')
            queue_path = self._path('work/queue.md')
            queue = queue_path.read_text(encoding='utf-8') if queue_path.exists() else None
            if queue is not None:
                link = effort.removeprefix('work/') + '/README.md'
                queue = ''.join(line for line in queue.splitlines(keepends=True) if f']({link})' not in line)
            record['metadata']['state'] = 'completed'
            record['metadata']['next_action'] = 'Completed; see recorded outcome.'
            record['body'] += '\n## Completion evidence\n\n' + evidence.strip() + '\n'
            self._write(effort + '/README.md', **record)
            if queue is not None:
                atomic_write(queue_path, queue)

    def complete_spec(self, target, expected_revision, evidence):
        """Finalize a decomposed specification after every child was integrated."""
        if not isinstance(evidence, str) or not evidence.strip():
            raise RecordError('spec acceptance evidence is required')
        with self.locked():
            self._authority()
            target = self._canonical(target)
            record = self._spec_eligible(target)
            meta = record['metadata']
            if meta['revision'] != expected_revision:
                raise RecordError('stale spec revision')
            children = [(ref, child) for ref, child in self._issues(meta['effort'])
                        if (child.get('basis') or {}).get('ref') == target]
            if not children:
                raise RecordError('no issue graph; complete the direct spec claim instead')
            for ref, child in children:
                if child.get('state') != 'completed':
                    raise Ineligible(f'{target}: unfinished issue {ref}')
                receipt = child.get('integration')
                if not isinstance(receipt, dict):
                    raise RecordError(f'{ref}: missing integration receipt')
                self._integration_receipt(receipt.get('ref'), receipt.get('commit'))
            self._conflict(target, record, self._json('claims.json', {}))
            record['metadata']['state'] = 'completed'
            record['body'] = record['body'].rstrip() + '\n\n## Completion evidence\n\n' + evidence.strip() + '\n'
            self._write(target, **record)

    def _integration_receipt(self, integration_ref, commit):
        if not integration_ref or not commit:
            raise RecordError('both integration_ref and commit are required')
        integrated = git(self.authority, 'rev-parse', '--verify', integration_ref + '^{commit}')
        accepted = git(self.authority, 'rev-parse', '--verify', commit + '^{commit}')
        result = subprocess.run(['git', '-C', str(self.authority), 'merge-base', '--is-ancestor', accepted, integrated], text=True, capture_output=True)
        if result.returncode == 1:
            raise RecordError('accepted commit is not available on the integration ref')
        if result.returncode:
            raise RecordError(f'Git integration unavailable: {result.stderr.strip()}')
        return {'ref': integration_ref, 'commit': accepted, 'verified_tip': integrated}

    def complete(self, target, token, evidence, integration_ref=None, commit=None):
        """Close only after caller verifies acceptance and integration availability."""
        if not isinstance(evidence, str) or not evidence.strip():
            raise RecordError('completion evidence is required')
        with self.locked():
            self._authority()
            target = self._canonical(target)
            claims = self._json('claims.json', {})
            if target not in claims or claims[target].get('token') != token:
                raise RecordError(f'{target}: claim token does not match')
            record = self._eligible(target, allow_in_progress=True)
            self._validate_claim_basis(target, record, claims[target])
            if integration_ref is not None or commit is not None:
                record['metadata']['integration'] = self._integration_receipt(integration_ref, commit)
            record['metadata']['state'] = 'completed'
            record['body'] = record['body'].rstrip() + '\n\n## Completion evidence\n\n' + evidence.strip() + '\n'
            self._write(target, **record)
            del claims[target]
            self._save_json('claims.json', claims)

    def release(self, target, token):
        with self.locked():
            self._authority()
            target = self._canonical(target)
            claims = self._json('claims.json', {})
            if target not in claims or claims[target].get('token') != token:
                raise RecordError(f'{target}: claim token does not match')
            record = self._read(target)
            if record['metadata'].get('state') == 'in-progress':
                record['metadata']['state'] = 'open'
                self._write(target, **record)
            del claims[target]
            self._save_json('claims.json', claims)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, help='Target checkout, never inferred from helper installation')
    sub = parser.add_subparsers(dest='command', required=True)
    configure = sub.add_parser('configure')
    configure.add_argument('--authority')
    read = sub.add_parser('read')
    read.add_argument('ref')
    create = sub.add_parser('create-effort')
    for name in ('slug', 'title', 'request', 'outcome'):
        create.add_argument('--' + name, required=True)
    create.add_argument('--effort')
    revision = sub.add_parser('revise-spec')
    revision.add_argument('--effort', required=True)
    revision.add_argument('--body-file', required=True)
    revision.add_argument('--expected-revision', required=True, type=int)
    revision.add_argument('--rationale', required=True)
    revision.add_argument('--editorial', dest='material', action='store_false')
    revision.add_argument('--readiness', default='ready-for-agent')
    resume = sub.add_parser('resume-publication')
    resume.add_argument('--effort', required=True)
    history = sub.add_parser('read-revision')
    history.add_argument('spec_ref')
    history.add_argument('revision', type=int)
    reconcile = sub.add_parser('reconcile-issue')
    reconcile.add_argument('target')
    reconcile.add_argument('--rationale', required=True)
    reconcile.add_argument('--affected', action='store_true')
    reconcile.add_argument('--body-file')
    reconcile.add_argument('--readiness')
    reconcile.add_argument('--approval')
    validate = sub.add_parser('revalidate')
    validate.add_argument('target')
    validate.add_argument('--token', required=True)
    spec = sub.add_parser('publish-spec')
    spec.add_argument('--effort', required=True)
    spec.add_argument('--body-file', required=True)
    issue = sub.add_parser('publish-issue')
    for name in ('effort', 'slug', 'body-file', 'approval'):
        issue.add_argument('--' + name, required=True)
    issue.add_argument('--blocked-by', action='append', default=[])
    selection = sub.add_parser('select')
    selection.add_argument('target', nargs='?')
    acquire = sub.add_parser('select-and-claim')
    acquire.add_argument('target', nargs='?')
    acquire.add_argument('--owner', required=True)
    acquire.add_argument('--workspace')
    finish_effort = sub.add_parser('complete-effort')
    finish_effort.add_argument('effort')
    finish_effort.add_argument('--evidence', required=True)
    claim = sub.add_parser('claim')
    claim.add_argument('target')
    claim.add_argument('--owner', required=True)
    claim.add_argument('--workspace')
    complete = sub.add_parser('complete')
    complete.add_argument('target')
    complete.add_argument('--token', required=True)
    complete.add_argument('--evidence', required=True)
    complete.add_argument('--integration-ref')
    complete.add_argument('--commit')
    finish_spec = sub.add_parser('complete-spec')
    finish_spec.add_argument('target')
    finish_spec.add_argument('--expected-revision', required=True, type=int)
    finish_spec.add_argument('--evidence', required=True)
    continuation = sub.add_parser('resume')
    continuation.add_argument('target')
    continuation.add_argument('--token', required=True)
    recovery = sub.add_parser('recover')
    recovery.add_argument('target')
    recovery.add_argument('--expected-token', required=True)
    recovery.add_argument('--owner', required=True)
    recovery.add_argument('--stopped-evidence', required=True)
    recovery.add_argument('--workspace')
    acknowledge = sub.add_parser('acknowledge-basis')
    acknowledge.add_argument('target')
    acknowledge.add_argument('--token', required=True)
    acknowledge.add_argument('--evidence', required=True)
    release = sub.add_parser('release')
    release.add_argument('target')
    release.add_argument('--token', required=True)
    args = vars(parser.parse_args(argv))
    command = args.pop('command').replace('-', '_')
    try:
        records = WorkRecords(args.pop('repo'))
        if 'body_file' in args:
            body_file = args.pop('body_file')
            if body_file:
                args['body'] = Path(body_file).read_text(encoding='utf-8-sig')
        result = getattr(records, command)(**args)
        print(json.dumps(result, indent=2))
        return 0
    except (RecordError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
