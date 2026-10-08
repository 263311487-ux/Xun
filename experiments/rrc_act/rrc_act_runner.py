#!/usr/bin/env python3
"""Offline synthetic replay recorder. NOT a real RRC-ACT experiment runner.

No provider adapters, credentials, network access, or confirmatory switch exist.
Payload hashes detect inconsistent edits; they do not authenticate provenance.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path


class RunnerError(ValueError):
    pass


SCHEMA = 'rrc-act-synthetic-replay-v1'
PAYLOADS = ('prompt', 'answer', 'state_before', 'state_after')
ROW_FIELDS = {'schema_version', 'dataset_mode', 'synthetic', 'agent_id', 'item_id',
              'session', 'attempt', 'status', 'input_tokens', 'output_tokens',
              'provider_latency_ms', 'prev_record_sha256', 'record_sha256',
              *PAYLOADS, *(x+'_sha256' for x in PAYLOADS)}


def require(condition, message):
    if not condition:
        raise RunnerError(message)


def canonical(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise RunnerError('payload must be finite JSON') from exc


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def record_digest(row):
    # Exclude the digest field itself to avoid a self-referential hash.
    return digest({k: v for k, v in row.items() if k != 'record_sha256'})


def scan(value):
    if isinstance(value, dict):
        require(all(isinstance(k, str) for k in value), 'JSON object keys must be strings')
        normalized = {re.sub(r'[^a-z0-9]', '', k.lower()) for k in value}
        require(not any(any(mark in key for mark in ('apikey', 'accesstoken', 'refreshtoken',
                                                     'password', 'authorization', 'credential', 'secret',
                                                     'selfreportscore')) for key in normalized),
                'credential/self-report field forbidden')
        for item in value.values():
            scan(item)
    elif isinstance(value, list):
        for item in value:
            scan(item)


def agent_id_ok(value):
    return isinstance(value, str) and re.fullmatch(r'AM[0-9]{5}', value) is not None


def validate_records(records, agent_id):
    """Check replay order, retries, state continuity, and payload hashes."""
    require(agent_id_ok(agent_id), 'invalid opaque agent ID')
    require(isinstance(records, list), 'records must be a list')
    previous, closed, state, last_session = None, set(), {}, 0
    previous_digest = '0' * 64
    for row in records:
        require(isinstance(row, dict) and set(row) == ROW_FIELDS, 'invalid/unmasked record fields')
        scan(row)
        require(row['schema_version'] == SCHEMA and row['dataset_mode'] == 'synthetic-test'
                and row['synthetic'] is True, 'only synthetic replay records accepted')
        require(row['agent_id'] == agent_id, 'cross-agent record')
        require(type(row['session']) is int and row['session'] >= last_session and row['session'] >= 0, 'invalid session order')
        last_session = row['session']
        require(isinstance(row['item_id'], str) and row['item_id'], 'missing item ID')
        require(type(row['attempt']) is int and row['attempt'] in (1, 2), 'invalid attempt')
        require(row['status'] in ('ok', 'technical_failure', 'missing'), 'unknown replay status')
        require(all(row[k] is None for k in ('input_tokens', 'output_tokens', 'provider_latency_ms')),
                'replay has no measured provider usage or latency')
        require(isinstance(row['prompt'], dict) and row['prompt'], 'missing prompt')
        require(isinstance(row['state_before'], dict) and isinstance(row['state_after'], dict), 'invalid state')
        for field in PAYLOADS:
            require(row[field+'_sha256'] == digest(row[field]), 'payload hash mismatch: '+field)
        require(row['prev_record_sha256'] == previous_digest, 'record chain mismatch')
        require(row['record_sha256'] == record_digest(row), 'record metadata/payload hash mismatch')
        require(row['state_before_sha256'] == digest(state), 'state chain mismatch')
        if previous is not None and row['item_id'] == previous['item_id']:
            require(previous['attempt'] == 1 and previous['status'] == 'technical_failure'
                    and row['attempt'] == 2, 'retry only once after technical failure')
            require(all(row[k] == previous[k] for k in ('session', 'prompt_sha256', 'state_before_sha256')),
                    'retry must preserve session, prompt and state')
        else:
            require(row['item_id'] not in closed and row['attempt'] == 1, 'duplicate/reordered item')
            if previous is not None:
                require(previous['status'] != 'technical_failure' or previous['attempt'] == 2,
                        'technical failure must include the one retry')
                closed.add(previous['item_id'])
        if row['status'] != 'ok':
            require(row['answer'] is None and row['state_after_sha256'] == digest(state), 'failed turn changed answer/state')
        else:
            require(row['answer'] is not None, 'successful response cannot be null')
        if row['status'] == 'missing':
            require(row['attempt'] == 1, 'absent fixture cannot be a retry')
        state, previous, previous_digest = row['state_after'], row, row['record_sha256']
    if previous:
        require(previous['status'] != 'technical_failure' or previous['attempt'] == 2,
                'technical failure must include the one retry')


def mask_records(records, agent_id):
    """Verify raw records, then expose only anonymous response data for scoring."""
    validate_records(records, agent_id)
    final = {row['item_id']: row for row in records}
    return [dict(mask_schema='rrc-act-masked-response-v1', dataset_mode='synthetic-test',
                 synthetic=True, agent_id=row['agent_id'], item_id=row['item_id'],
                 session=row['session'], attempt=row['attempt'], status=row['status'],
                 answer=copy.deepcopy(row['answer']), response_sha256=row['answer_sha256'])
            for row in final.values()]


def replay_agent(*, agent_id, requests, replies, output_dir, expected_item_ids=None, dataset_mode='synthetic-test'):
    """Replay supplied fixtures, preserving attempts; never invoke a provider.

    Absent replies are explicit missing-fixture records. A supplied technical
    failure needs its second attempt, even when that second attempt also fails.
    All validation precedes creation; an existing output directory is refused.
    """
    require(dataset_mode == 'synthetic-test', 'confirmatory execution is not implemented')
    require(agent_id_ok(agent_id), 'invalid opaque agent ID')
    require(isinstance(requests, list) and requests and isinstance(replies, dict), 'invalid replay inputs')
    require(len(requests) == 76, 'complete 76-item protocol request list required')
    require(isinstance(expected_item_ids, list) and len(expected_item_ids) == 76
            and all(isinstance(i, str) and i for i in expected_item_ids)
            and len(set(expected_item_ids)) == 76, 'complete 76-item bank ID list required')
    scan(requests); scan(replies)
    canonical(requests); canonical(replies)
    rows, state, seen = [], {}, set()
    for request in requests:
        require(isinstance(request, dict) and set(request) == {'item_id', 'session', 'prompt'}, 'invalid request fields')
        iid = request['item_id']
        require(isinstance(iid, str) and iid and iid not in seen, 'duplicate/invalid item ID')
        require(type(request['session']) is int and request['session'] >= 0, 'session must be a nonnegative integer')
        require(isinstance(request['prompt'], dict) and request['prompt'], 'prompt must be a nonempty object')
        seen.add(iid)
        attempts = replies.get(iid, [dict(status='missing')])
        require(isinstance(attempts, list) and 1 <= len(attempts) <= 2, 'one or two attempts required')
        for number, attempt in enumerate(attempts, 1):
            require(isinstance(attempt, dict) and attempt.get('status') in ('ok', 'technical_failure', 'missing'), 'bad attempt')
            success = attempt['status'] == 'ok'
            require(set(attempt) == ({'status', 'answer', 'state_after'} if success else {'status'}), 'invalid attempt fields')
            row = dict(schema_version=SCHEMA, dataset_mode='synthetic-test', synthetic=True,
                       agent_id=agent_id, item_id=iid, session=request['session'], attempt=number,
                       status=attempt['status'], input_tokens=None, output_tokens=None, provider_latency_ms=None,
                       prompt=copy.deepcopy(request['prompt']), answer=copy.deepcopy(attempt.get('answer')),
                       state_before=copy.deepcopy(state), state_after=copy.deepcopy(attempt['state_after'] if success else state))
            row.update({field+'_sha256': digest(row[field]) for field in PAYLOADS})
            row['prev_record_sha256'] = rows[-1]['record_sha256'] if rows else '0' * 64
            row['record_sha256'] = record_digest(row)
            rows.append(row)
            state = row['state_after']
    require(set(replies) <= seen, 'reply for unrequested item')
    require(seen == set(expected_item_ids), 'requests must match complete frozen bank IDs')
    validate_records(rows, agent_id)
    destination = Path(output_dir).absolute()
    require(not destination.exists(), 'output already exists; never overwrite a replay')
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.'+destination.name+'.incomplete-', dir=destination.parent))
    try:
        with (staging/'responses.jsonl').open('x', encoding='utf-8') as handle:
            for row in rows: handle.write(canonical(row)+'\n')
        with (staging/'masked_responses.jsonl').open('x', encoding='utf-8') as handle:
            for row in mask_records(rows, agent_id): handle.write(canonical(row)+'\n')
        for name, value in (('requests.json', requests), ('replies.json', replies),
                            ('expected_item_ids.json', expected_item_ids)):
            with (staging/name).open('x', encoding='utf-8') as handle: handle.write(canonical(value)+'\n')
        manifest = dict(evidence_status='synthetic_test_only', agent_id=agent_id,
                        attempts=len(rows), item_count=len(seen),
                        files={name: hashlib.sha256((staging/name).read_bytes()).hexdigest()
                               for name in ('responses.jsonl', 'masked_responses.jsonl',
                                            'requests.json', 'replies.json', 'expected_item_ids.json')})
        with (staging/'COMPLETE.json').open('x', encoding='utf-8') as handle:
            handle.write(canonical(manifest)+'\n')
        # Exclusive mkdir reserves the destination, including against races.
        # Move the completion marker last; interruption leaves an explicit
        # incomplete export, never silently replaces another directory.
        destination.mkdir(exist_ok=False)
        for name in ('responses.jsonl', 'masked_responses.jsonl', 'requests.json',
                     'replies.json', 'expected_item_ids.json', 'COMPLETE.json'):
            (staging/name).rename(destination/name)
        staging.rmdir()
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent-id', required=True)
    parser.add_argument('--requests', type=Path, required=True)
    parser.add_argument('--replies', type=Path, required=True)
    parser.add_argument('--expected-item-ids', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--dataset-mode', default='synthetic-test')
    args = parser.parse_args()
    rows = replay_agent(agent_id=args.agent_id, requests=json.loads(args.requests.read_text(encoding='utf-8')),
                        replies=json.loads(args.replies.read_text(encoding='utf-8')), output_dir=args.output,
                        expected_item_ids=json.loads(args.expected_item_ids.read_text(encoding='utf-8')), dataset_mode=args.dataset_mode)
    print(canonical(dict(evidence_status='synthetic_test_only', attempts=len(rows))))


if __name__ == '__main__':
    try:
        main()
    except (RunnerError, OSError, ValueError) as exc:
        print('REPLAY_BLOCKED: '+str(exc), file=sys.stderr)
        sys.exit(2)
