"""Read-only conformance checks for remote adapter observations.

A fetch callback must query current provider authority and normalize facts as
specified in REMOTE-WORK.md. This module neither supplies a provider client nor
acquires ownership. Successful inspection is never permission to implement.
"""
from copy import deepcopy


class RemoteError(RuntimeError):
    pass


class RemoteContract:
    def __init__(self, provider, fetch):
        if provider not in {'github', 'gitlab'}:
            raise RemoteError('unsupported remote provider')
        self.provider = provider
        self.fetch = fetch

    def _read(self, ref):
        try:
            record = deepcopy(self.fetch(ref))
            if not isinstance(record, dict):
                raise RemoteError('invalid remote record')
            return record
        except Exception as exc:
            raise RemoteError(f'unavailable remote record: {ref}') from exc

    def inspect(self, target, acquired_basis=None, token=None):
        record = self._read(target)
        if record.get('kind') != 'implementation':
            raise RemoteError('target is not an implementation issue')
        if record.get('effort_state') != 'active' or record.get('state') not in {'open', 'in-progress'}:
            raise RemoteError('inactive effort or issue')
        if record.get('readiness') not in {'ready-for-agent', 'ready-for-human', 'needs-info', 'needs-triage', 'wontfix'}:
            raise RemoteError('missing or unknown readiness')
        if record['readiness'] != 'ready-for-agent':
            raise RemoteError('issue is not ready-for-agent')
        claim = record.get('claim')
        if 'claim' not in record:
            raise RemoteError('unknown remote ownership')
        if claim and (not token or claim.get('token') != token):
            raise RemoteError('conflicting existing claim')
        if token and (not claim or claim.get('token') != token):
            raise RemoteError('ownership token no longer current')
        if record['state'] == 'in-progress' and not claim:
            raise RemoteError('in-progress issue has no current owner')
        basis = record.get('basis')
        if (not isinstance(basis, dict) or not isinstance(basis.get('ref'), str)
                or not basis['ref'].startswith('https://')
                or type(basis.get('revision')) is not int or basis['revision'] < 1):
            raise RemoteError('missing or invalid spec basis')
        spec = self._read(basis.get('ref'))
        if spec.get('kind') != 'spec' or type(spec.get('revision')) is not int:
            raise RemoteError('missing or invalid current spec revision')
        if spec.get('state') != 'current' or basis.get('revision') != spec.get('revision'):
            raise RemoteError('stale spec basis')
        if acquired_basis is not None and acquired_basis != basis:
            raise RemoteError('acquired basis changed; reconcile and acknowledge')
        if record.get('dependencies_complete') is not True or not isinstance(record.get('blocked_by'), list):
            raise RemoteError('incomplete dependency query')
        for ref in record['blocked_by']:
            blocker = self._read(ref)
            if blocker.get('kind') != 'implementation':
                raise RemoteError(f'unknown blocker kind: {ref}')
            outcome = self.outcome(blocker)
            if outcome != 'completed':
                raise RemoteError(f'{outcome} blocker: {ref}')
        return record

    def outcome(self, record):
        state = record.get('native_state')
        if state in {'open', 'opened'}:
            return 'unfinished'
        if state != 'closed':
            return 'unknown'
        if self.provider == 'github':
            return {'completed': 'completed', 'not_planned': 'canceled',
                    'duplicate': 'superseded'}.get(record.get('state_reason'), 'unknown')
        return record.get('completion_outcome') if record.get('completion_outcome') in {
            'completed', 'canceled', 'superseded'} else 'unknown'

    def claim(self, target, owner):
        raise RemoteError(f'{self.provider}: unsupported automatic concurrent claiming; '
                          'native assignment is not exclusive acquisition')
