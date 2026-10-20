"""Durable local planning records using the shared work-record authority.

CLI: work_planning.py --repo CHECKOUT OPERATION --request-file JSON
The request is an object of keyword arguments to the named public operation.
Human evidence is supplied by the caller; this helper cannot authenticate a conversation.
"""
from datetime import datetime, timezone
import argparse
import json
import re
from pathlib import Path
import sys
import uuid

from work_records import WorkRecords, RecordError, atomic_write


class PlanningRecords(WorkRecords):
    def _overview(self, effort):
        record = self._read(effort + '/README.md')
        if record['metadata'].get('kind') != 'effort' or record['metadata'].get('state') != 'active':
            raise RecordError('planning requires an active effort')
        return record

    def _decision(self, target):
        record = self._read(target)
        if record['metadata']['kind'] != 'decision':
            raise RecordError('expected decision kind')
        self._overview(record['metadata']['effort'])
        return record

    def chart(self, effort, title, destination, fog, notes=''):
        if not destination.strip():
            raise RecordError('destination is required')
        with self.locked():
            self._authority()
            overview = self._overview(effort)
            ref = effort + '/map.md'
            if overview['metadata'].get('current_map') or self._path(ref).exists():
                raise RecordError('map already exists; resume its identity')
            meta = dict(schema=1, kind='map', id=ref, effort=effort, state='open')
            body = f'# {title}\n\n## Destination\n\n{destination}\n\n## Notes\n\n{notes}\n\n## Decisions so far\n\n## Not yet specified\n\n{fog}\n\n## Out of scope\n'
            self._write(ref, meta, body)
            overview['metadata'].update(current_map=ref, stage='decisions', next_action='Continue the next named decision with Wayfinder.')
            overview['body'] += '\n[Planning map](map.md) indexes the authoritative decisions.\n'
            self._write(effort + '/README.md', **overview)
            return ref

    def record_discovery(self, effort, finding):
        if not finding.strip():
            raise RecordError('finding is required')
        with self.locked():
            self._authority()
            overview = self._overview(effort)
            ref = effort + '/discovery.md'
            path = self._path(ref)
            body = path.read_text(encoding='utf-8') if path.exists() else '# Discovery\n'
            atomic_write(path, body.rstrip() + '\n\n' + finding.strip() + '\n')
            if not overview['metadata'].get('current_map') and not overview['metadata'].get('current_spec'):
                overview['metadata'].update(stage='discovery', next_action='Continue the recorded open questions or synthesize the agreed specification.')
            if '[Discovery](discovery.md)' not in overview['body']:
                overview['body'] += '\n[Discovery](discovery.md) holds ordinary requirements and open questions.\n'
            self._write(effort + '/README.md', **overview)
            return ref

    def add_decision(self, effort, slug, title, question, decision_type, blocked_by=()):
        if decision_type not in {'grilling', 'prototype', 'research', 'task'} or not question.strip():
            raise RecordError('decision type and question are required')
        with self.locked():
            self._authority()
            overview = self._overview(effort)
            map_ref = overview['metadata'].get('current_map')
            if not map_ref or self._read(map_ref)['metadata'].get('state') != 'open':
                raise RecordError('an open current map is required')
            children = list(self._path(effort + '/decisions').glob('*.md'))
            orders = [self._read(p.relative_to(self.authority).as_posix())['metadata'].get('order') for p in children]
            if any(type(n) is not int or n < 1 for n in orders) or len(set(orders)) != len(orders):
                raise RecordError('invalid or duplicate decision order')
            order = max(orders, default=0) + 1
            ref = f'{effort}/decisions/{order:02d}-{self._slug(slug)}.md'
            blockers = list(blocked_by)
            if len(set(blockers)) != len(blockers):
                raise RecordError('duplicate decision blockers')
            for blocker in blockers:
                if self._decision(blocker)['metadata'].get('map') != map_ref:
                    raise RecordError('decision blocker must belong to this map')
            meta = dict(schema=1, kind='decision', id=ref, effort=effort, map=map_ref, order=order, type=decision_type, state='open', blocked_by=blockers)
            self._write(ref, meta, f'# {title}\n\n## Question\n\n{question}\n')
            if order == 1:
                overview['metadata']['next_action'] = f'Continue {title} with Wayfinder: {ref}'
                self._write(effort + '/README.md', **overview)
            return ref

    def _ready_decision(self, target):
        record = self._decision(target)
        meta = record['metadata']
        overview = self._overview(meta['effort'])
        if overview['metadata'].get('current_map') != meta.get('map') or self._read(meta['map'])['metadata'].get('state') != 'open':
            raise RecordError('decision must belong to the current open map')
        if meta.get('state') != 'open' or meta.get('review_required'):
            raise RecordError('decision is not open or requires dependent review')
        for blocker in meta.get('blocked_by', []):
            prior = self._decision(blocker)
            if prior['metadata'].get('state') != 'resolved' or prior['metadata'].get('review_required'):
                raise RecordError(f'decision blocked by {blocker}')
        return record

    def claim_decision(self, target, owner):
        if not owner:
            raise RecordError('owner is required')
        with self.locked():
            self._authority()
            self._ready_decision(target)
            claims = self._json('claims.json', {})
            if target in claims:
                raise RecordError('decision already claimed')
            claim = dict(target=target, token=uuid.uuid4().hex, owner=owner, workspace=str(self.checkout), acquired_at=datetime.now(timezone.utc).isoformat())
            claims[target] = claim
            self._save_json('claims.json', claims)
            return claim

    def resolve_decision(self, target, token, answer, human_answer=None):
        if not answer.strip():
            raise RecordError('answer is required')
        with self.locked():
            self._authority()
            record = self._ready_decision(target)
            claims = self._json('claims.json', {})
            if claims.get(target, {}).get('token') != token:
                raise RecordError('decision claim token does not match')
            if record['metadata']['type'] in {'grilling', 'prototype'} and not (human_answer or '').strip():
                raise RecordError('human answer is required; leave this decision open')
            record['metadata']['state'] = 'resolved'
            record['body'] += '\n## Resolution\n\n' + answer.strip() + '\n'
            if human_answer:
                record['body'] += '\n## Human answer evidence\n\n' + human_answer.strip() + '\n'
            self._write(target, **record)
            map_ref = record['metadata']['map']
            map_record = self._read(map_ref)
            title = record['body'].lstrip().splitlines()[0].lstrip('# ').strip()
            relative = Path(target).relative_to(Path(map_ref).parent).as_posix()
            entry = f'- [{title}]({relative}): resolved; read the recorded answer.'
            pattern = re.compile(r'^- \[[^\n]*?\]\(' + re.escape(relative) + r'(?:#[^)]*)?\):[^\n]*$', re.M)
            match = pattern.search(map_record['body'])
            if match:
                history = match.group().partition('; [prior answer]')[2]
                if history:
                    entry += '; [prior answer]' + history
                map_record['body'] = pattern.sub(lambda _: entry, map_record['body'], count=1)
            else:
                map_record['body'] = map_record['body'].replace('## Decisions so far\n', '## Decisions so far\n\n' + entry + '\n', 1)
            self._write(map_ref, **map_record)
            del claims[target]
            self._save_json('claims.json', claims)
            return target

    def supersede_decision(self, target, replacement, reason):
        if not reason.strip() or target == replacement:
            raise RecordError('distinct replacement and supersession reason are required')
        with self.locked():
            self._authority()
            prior = self._decision(target)
            successor = self._decision(replacement)
            if prior['metadata'].get('state') not in {'open', 'resolved'}:
                raise RecordError('only open or resolved decisions can be superseded')
            if successor['metadata'].get('state') != 'open' or successor['metadata'].get('map') != prior['metadata'].get('map'):
                raise RecordError('replacement must be an open decision in the same map')
            if target in self._json('claims.json', {}):
                raise RecordError('release the prior decision claim before supersession')
            effort = prior['metadata']['effort']
            records = {p.relative_to(self.authority).as_posix(): self._read(p.relative_to(self.authority).as_posix())
                       for p in self._path(effort + '/decisions').glob('*.md')}
            affected = {target}
            while True:
                expanded = affected | {ref for ref, record in records.items()
                                       if set(record['metadata'].get('blocked_by', [])) & affected}
                if expanded == affected:
                    break
                affected = expanded
            if replacement in affected:
                raise RecordError('replacement cannot depend on the invalidated decision')
            # Gate dependents first so interrupted publication cannot authorize them.
            for ref in sorted(affected - {target}):
                record = records[ref]
                if record['metadata'].get('state') in {'canceled', 'superseded'}:
                    continue
                reviews = record['metadata'].setdefault('review_required', [])
                if target not in reviews:
                    reviews.append(target)
                record['metadata']['blocked_by'] = list(dict.fromkeys(
                    replacement if blocker == target else blocker for blocker in record['metadata']['blocked_by']))
                record['body'] += f'\n## Dependent review required\n\n[{target}]({Path(target).name}) was superseded by [{replacement}]({Path(replacement).name}): {reason}\n'
                self._write(ref, **record)
            prior['metadata'].update(state='superseded', superseded_by=replacement)
            prior['body'] += f'\n## Superseded\n\nReplacement: [{replacement}]({Path(replacement).name}). {reason}\n'
            self._write(target, **prior)
            map_ref = prior['metadata']['map']
            map_record = self._read(map_ref)
            old_link = Path(target).relative_to(Path(map_ref).parent).as_posix()
            new_link = Path(replacement).relative_to(Path(map_ref).parent).as_posix()
            title = successor['body'].lstrip().splitlines()[0].lstrip('# ').strip()
            lines = map_record['body'].splitlines()
            pattern = re.compile(r'^- \[[^\n]*?\]\((' + re.escape(old_link) + r'(?:#[^)]*)?)\):')
            updated = []
            for line in lines:
                match = pattern.match(line)
                updated.append(f'- [{title}]({new_link}): unresolved replacement; [prior answer]({match.group(1)}) superseded.' if match else line)
            lines = updated
            map_record['body'] = '\n'.join(lines) + '\n'
            self._write(map_ref, **map_record)
            return sorted(affected - {target})

    def review_decision(self, target, rationale):
        if not rationale.strip():
            raise RecordError('dependent review rationale is required')
        with self.locked():
            self._authority()
            record = self._decision(target)
            if record['metadata'].get('state') not in {'open', 'resolved'}:
                raise RecordError('only current decisions can be reviewed')
            record['metadata'].pop('review_required', None)
            record['body'] += '\n## Dependent review\n\n' + rationale.strip() + '\n'
            self._write(target, **record)
            return target


OPERATIONS = ('chart', 'record-discovery', 'add-decision', 'claim-decision', 'resolve-decision', 'supersede-decision', 'review-decision')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True)
    parser.add_argument('operation', choices=OPERATIONS)
    parser.add_argument('--request-file', required=True)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(Path(args.request_file).read_text(encoding='utf-8-sig'))
        if not isinstance(payload, dict):
            raise RecordError('request must be a JSON object')
        result = getattr(PlanningRecords(args.repo), args.operation.replace('-', '_'))(**payload)
        print(json.dumps(result, indent=2))
        return 0
    except (RecordError, OSError, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
