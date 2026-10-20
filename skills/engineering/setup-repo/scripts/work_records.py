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


class RecordError(ValueError):
    """A record is ineligible or its authority is indeterminate."""


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

    def _path(self, ref):
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
        path = self._path(ref)
        try:
            text = path.read_text(encoding='utf-8-sig')
        except OSError as exc:
            raise RecordError(f'{ref}: unavailable record: {exc}') from exc
        match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)(.*)\Z', text, re.S)
        if not match:
            raise RecordError(f'{ref}: missing typed metadata; normalize the explicit legacy input first')
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

    def publish_spec(self, effort, body, readiness='ready-for-agent'):
        with self.locked():
            self._authority()
            overview = self._read(effort + '/README.md')
            if overview['metadata'].get('state') != 'active':
                raise RecordError('effort is not active')
            ref = effort + '/spec.md'
            if overview['metadata'].get('current_spec') or self._path(ref).exists():
                raise RecordError('spec already exists; publish a retained revision rather than overwrite')
            meta = dict(schema=1, kind='spec', id=ref, effort=effort, revision=1, state='current', readiness=readiness)
            self._write(ref, meta, body)
            overview['metadata'].update(current_spec={'ref': ref, 'revision': 1}, stage='specification', next_action='Review and approve implementation slices.')
            self._write(effort + '/README.md', **overview)
            return ref

    def publish_issue(self, effort, slug, body, approval, blocked_by=(), readiness='ready-for-agent'):
        if not isinstance(approval, str) or not approval.strip():
            raise RecordError('breakdown approval or explicit task authority is required')
        with self.locked():
            self._authority()
            overview = self._read(effort + '/README.md')
            if overview['metadata'].get('state') != 'active':
                raise RecordError('effort is not active')
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

    def _eligible(self, target, allow_in_progress=False):
        if 'history' in Path(target).parts:
            raise RecordError(f'{target}: historical records cannot be executed; use the current record')
        record = self._read(target)
        meta = record['metadata']
        if meta['kind'] != 'implementation':
            raise RecordError(f'{target}: expected implementation kind')
        if meta.get('state') not in ({'open', 'in-progress'} if allow_in_progress else {'open'}):
            raise RecordError(f'{target}: lifecycle is not open ({meta.get("state")})')
        if meta.get('readiness') != 'ready-for-agent':
            raise RecordError(f'{target}: readiness is not ready-for-agent ({meta.get("readiness")})')
        effort = meta.get('effort')
        overview = None
        if effort:
            overview = self._read(effort + '/README.md')['metadata']
            if overview.get('state') != 'active':
                raise RecordError(f'{target}: effort is not active')
            if type(meta.get('order')) is not int or meta['order'] < 1:
                raise RecordError(f'{target}: missing or invalid order')
        if 'basis' not in meta:
            raise RecordError(f'{target}: missing basis; use explicit null for self-contained work')
        basis = meta['basis']
        if basis is not None:
            if not isinstance(basis, dict) or not isinstance(basis.get('ref'), str) or type(basis.get('revision')) is not int or basis['revision'] < 1:
                raise RecordError(f'{target}: invalid spec basis')
            spec = self._read(basis['ref'])['metadata']
            if spec['kind'] != 'spec' or spec.get('state') != 'current' or spec.get('readiness') != 'ready-for-agent':
                raise RecordError(f'{target}: basis is not a current ready spec')
            if spec.get('revision') != basis['revision'] or (overview and overview.get('current_spec') != basis):
                raise RecordError(f'{target}: stale spec basis or inconsistent current pointer')
            if effort and spec.get('effort') != effort:
                raise RecordError(f'{target}: spec effort mismatch')
        for blocker in self._dependencies(target):
            if self._read(blocker)['metadata'].get('state') != 'completed':
                raise RecordError(f'{target}: blocked by {blocker} (not completed)')
        return record

    def claim(self, target, owner, workspace=None):
        if not owner:
            raise RecordError('claim owner is required')
        with self.locked():
            self._authority()
            claims = self._json('claims.json', {})
            if target in claims:
                raise RecordError(f'{target}: already claimed by {claims[target].get("owner")}')
            record = self._eligible(target)
            claim = dict(target=target, token=uuid.uuid4().hex, owner=owner, workspace=str(Path(workspace or self.checkout).resolve()), acquired_at=datetime.now(timezone.utc).isoformat())
            claims[target] = claim
            self._save_json('claims.json', claims)
            record['metadata']['state'] = 'in-progress'
            self._write(target, **record)
            return claim

    def complete(self, target, token, evidence):
        """Close only after caller verifies acceptance and integration availability."""
        if not isinstance(evidence, str) or not evidence.strip():
            raise RecordError('completion evidence is required')
        with self.locked():
            self._authority()
            claims = self._json('claims.json', {})
            if target not in claims or claims[target].get('token') != token:
                raise RecordError(f'{target}: claim token does not match')
            record = self._eligible(target, allow_in_progress=True)
            record['metadata']['state'] = 'completed'
            record['body'] = record['body'].rstrip() + '\n\n## Completion evidence\n\n' + evidence.strip() + '\n'
            self._write(target, **record)
            del claims[target]
            self._save_json('claims.json', claims)

    def release(self, target, token):
        with self.locked():
            self._authority()
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
    spec = sub.add_parser('publish-spec')
    spec.add_argument('--effort', required=True)
    spec.add_argument('--body-file', required=True)
    issue = sub.add_parser('publish-issue')
    for name in ('effort', 'slug', 'body-file', 'approval'):
        issue.add_argument('--' + name, required=True)
    issue.add_argument('--blocked-by', action='append', default=[])
    claim = sub.add_parser('claim')
    claim.add_argument('target')
    claim.add_argument('--owner', required=True)
    claim.add_argument('--workspace')
    complete = sub.add_parser('complete')
    complete.add_argument('target')
    complete.add_argument('--token', required=True)
    complete.add_argument('--evidence', required=True)
    release = sub.add_parser('release')
    release.add_argument('target')
    release.add_argument('--token', required=True)
    args = vars(parser.parse_args(argv))
    command = args.pop('command').replace('-', '_')
    try:
        records = WorkRecords(args.pop('repo'))
        if 'body_file' in args:
            args['body'] = Path(args.pop('body_file')).read_text(encoding='utf-8-sig')
        result = getattr(records, command)(**args)
        print(json.dumps(result, indent=2))
        return 0
    except (RecordError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
