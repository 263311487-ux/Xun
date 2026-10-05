#!/usr/bin/env python3
"""RRC-ACT v1.2 preparation/integrity gates; no provider calls or registry claims."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path


class GateError(ValueError):
    pass


SPEC = 'papers/registration_execution/execution_spec_v1.2.json'
FAMILIES = ('family_A', 'family_B')
MODEL_FIELDS = ('provider', 'model_id', 'snapshot_or_digest', 'tokenizer_id', 'runtime_version', 'api_endpoint_label')
REQUIRED_ROLES = (
    'protocol', 'execution_amendment', 'scoring_spec', 'model_manifest', 'item_bank_manifest',
    'system_prompt', 'training_templates', 'baseline_bank', 'endpoint_bank', 'answer_keys',
    'tool_contract', 'memory_schema', 'runtime_code', 'scoring_code', 'analysis_code',
    'preflight_code', 'environment_lock',
)
RESPONSE_HASH_FIELDS = ('freeze_lock_sha256', 'model_manifest_sha256', 'prompt_hash',
                        'response_hash', 'state_before_hash', 'state_after_hash')
FIELDS = ('agent_id', 'cohort', 'family_id', 'A', 'B', 'C', 'condition_label', 'run_order', 'seed_sha256')
HEX64 = re.compile(r'^[0-9a-f]{64}$')


def require(condition, message):
    if not condition:
        raise GateError(message)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise GateError(f'missing or invalid manifest/artifact {path}: {type(exc).__name__}') from exc


def require_hash(value, label):
    require(isinstance(value, str) and bool(HEX64.fullmatch(value)), f'{label}: missing/invalid SHA-256')


def resolve_artifact(root, relative):
    require(isinstance(relative, str) and relative and not Path(relative).is_absolute(), 'artifact path must be relative')
    path = (root / relative).resolve()
    require(root.resolve() in path.parents, 'artifact path escapes repository')
    require(path.is_file(), f'missing artifact: {relative}')
    return path


def validate_package(repo):
    """Check concrete inputs. Registry receipt and assignment are downstream, never inputs."""
    root = Path(repo).resolve()
    spec = read_json(root / SPEC)
    require(spec.get('schema_version') == '1.2', 'execution manifest must use schema 1.2')
    artifacts = spec.get('artifacts', {})
    require(isinstance(artifacts, dict), 'artifacts must be an object')
    errors, files = [], {}
    for role in REQUIRED_ROLES:
        try:
            entry = artifacts.get(role, {})
            require(isinstance(entry, dict), f'{role}: artifact entry must be an object')
            require_hash(entry.get('sha256'), role)
            path = resolve_artifact(root, entry.get('path'))
            require(sha256_file(path) == entry['sha256'], f'{role}: artifact hash mismatch')
            files[role] = {'path': entry['path'], 'sha256': entry['sha256']}
        except GateError as exc:
            errors.append(str(exc))
    require(not errors, '\n'.join(errors))
    model = read_json(root / files['model_manifest']['path'])
    require(model.get('status') == 'concrete', 'model manifest is still a template')
    families = model.get('model_families', [])
    require(len(families) == 2 and {x.get('family_id') for x in families} == set(FAMILIES),
            'model manifest requires exactly family_A and family_B')
    for family in families:
        for field in MODEL_FIELDS:
            value = family.get(field)
            require(isinstance(value, str) and value.strip() and value.lower() not in {'todo','null','unknown','latest'},
                    f'{family["family_id"]}.{field} is missing or mutable')
    require(len({(x['provider'], x['model_id']) for x in families}) == 2, 'two distinct model identities required')
    decoding = model.get('decoding', {})
    require(type(decoding.get('max_output_tokens')) is int and decoding['max_output_tokens'] > 0, 'max_output_tokens is missing')
    require(decoding.get('temperature') == .2 and decoding.get('top_p') == 1.0, 'decoding differs from protocol')
    requirements = model.get('runtime_requirements', {})
    require(requirements.get('common_external_runtime') is True and requirements.get('durable_policy_checkpoint') is True,
            'runtime must expose common durable-policy state')
    # This binds *all bytes* of every upstream artifact, including prompts, code,
    # banks and model snapshots. No exclusion/projection can hide a changed input.
    input_root = sha256_bytes(canonical_json(files).encode('utf-8'))
    spec_hash = sha256_file(root / SPEC)
    seed = sha256_bytes(('rrc-act-allocation-v1.2\n' + input_root + '\n' + spec_hash).encode('ascii'))
    return {'schema_version': '1.2', 'spec_sha256': spec_hash, 'artifacts': files,
            'input_root_sha256': input_root, 'assignment_seed_sha256': seed}


def digest(seed, label):
    return sha256_bytes((seed + ':' + label).encode('ascii'))


def build_assignment_rows(seed_sha256):
    require_hash(seed_sha256, 'assignment seed')
    # IDs are opaque with respect to condition. Families receive permuted pools;
    # A/B/C and run order are randomized by separate domain-separated rankings.
    ids = sorted((f'AM{i:05d}' for i in range(1, 577)), key=lambda a: digest(seed_sha256, 'id:' + a))
    rows, cursor = [], 0
    for family in FAMILIES:
        cells = [('main', str(a), str(b), str(c)) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
        cells.append(('generic_praise', '2', '1', '0'))
        for cohort, a, b, c in cells:
            label = 'generic_praise_B1_C0' if cohort == 'generic_praise' else f'A{a}_B{b}_C{c}'
            for aid in ids[cursor:cursor + 32]:
                rows.append(dict(agent_id=aid, cohort=cohort, family_id=family, A=a, B=b, C=c,
                                 condition_label=label, run_order='',
                                 seed_sha256=digest(seed_sha256, 'agent:' + aid)))
            cursor += 32
    rows.sort(key=lambda r: digest(seed_sha256, 'run:' + r['agent_id']))
    for i, row in enumerate(rows, 1):
        row['run_order'] = str(i)
    return rows


def assignment_bytes(rows):
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=FIELDS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode('utf-8')


def freeze_package(repo, destination):
    """Create a NEW local candidate bundle. Never overwrite a registered/used bundle."""
    data = validate_package(repo)
    destination = Path(destination)
    require(not destination.exists(), 'freeze destination already exists; never overwrite an existing lock or assignment')
    destination.mkdir(parents=True, exist_ok=False)
    table = assignment_bytes(build_assignment_rows(data['assignment_seed_sha256']))
    bundle_artifacts = {}
    for role, entry in data['artifacts'].items():
        source = Path(repo) / entry['path']
        bundle_path = Path('inputs') / role / Path(entry['path']).name
        target = destination / bundle_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        require(sha256_file(target) == entry['sha256'], f'copied bundle artifact hash mismatch: {role}')
        bundle_artifacts[role] = {'bundle_path': str(bundle_path), 'sha256': entry['sha256']}
    data.update(created_at_utc=datetime.now(timezone.utc).isoformat(),
                assignment_sha256=sha256_bytes(table), bundle_artifacts=bundle_artifacts,
                status='local_candidate_not_registered')
    (destination / 'assignment.csv').write_bytes(table)
    (destination / 'freeze.lock.json').write_text(canonical_json(data) + '\n', encoding='utf-8')
    return data


def verify_freeze(repo, bundle, expected_lock_sha256):
    """expected_lock_sha256 must come from the independent deposited record.

    This verifies integrity relative to that anchor, not its authenticity or time.
    Never derive the expected anchor from the potentially modified local lock.
    """
    require_hash(expected_lock_sha256, 'external lock anchor')
    bundle = Path(bundle)
    lock_path = bundle / 'freeze.lock.json'
    require(lock_path.is_file(), 'missing freeze lock')
    require(sha256_file(lock_path) == expected_lock_sha256, 'freeze lock differs from external anchor')
    lock = read_json(lock_path)
    current = validate_package(repo)
    require(all(lock.get(k) == v for k, v in current.items()), 'input manifest/seed changed after freeze')
    bundle_artifacts = lock.get('bundle_artifacts')
    require(isinstance(bundle_artifacts, dict) and set(bundle_artifacts) == set(REQUIRED_ROLES),
            'freeze lock is missing one or more copied bundle artifacts')
    for role, entry in bundle_artifacts.items():
        copied = bundle / entry.get('bundle_path', '')
        require(copied.is_file() and sha256_file(copied) == entry.get('sha256'),
                f'bundle artifact hash mismatch: {role}')
    table = bundle / 'assignment.csv'
    require(table.is_file(), 'missing assignment table')
    expected = assignment_bytes(build_assignment_rows(current['assignment_seed_sha256']))
    require(table.read_bytes() == expected and sha256_file(table) == lock.get('assignment_sha256'),
            'assignment table differs from frozen deterministic allocation')
    return {'status': 'integrity_verified_against_supplied_anchor', 'registration_verified': False,
            'lock_sha256': expected_lock_sha256}


def validate_response_record(record):
    require(record.get('schema_version') == 'rrc-act-response-v1.2', 'wrong response schema')
    require(record.get('dataset_mode') == 'confirmatory' and record.get('synthetic') is False,
            'only explicitly real confirmatory records allowed')
    require(isinstance(record.get('agent_id'), str) and re.fullmatch(r'AM\d{5}', record['agent_id']), 'invalid agent_id')
    require(type(record.get('session')) is int and record['session'] >= 0 and record.get('item_id'), 'missing session/item')
    for field in RESPONSE_HASH_FIELDS:
        require_hash(record.get(field), field)
    forbidden = {'api_key', 'access_token', 'refresh_token', 'password', 'authorization', 'credential', 'secret', 'self_report_score'}
    def inspect(value):
        if isinstance(value, dict):
            require(not any(str(k).lower() in forbidden for k in value), 'credential/self-report field forbidden')
            for v in value.values(): inspect(v)
        elif isinstance(value, list):
            for v in value: inspect(v)
    inspect(record)
    for field in ('input_tokens', 'output_tokens'):
        require(type(record.get(field)) is int and record[field] >= 0, f'invalid {field}')
    latency = record.get('latency_ms')
    require(type(latency) in (int, float) and 0 <= latency < float('inf'), 'invalid latency_ms')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'freeze', 'verify'])
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--expected-lock-sha256')
    args = parser.parse_args()
    if args.action == 'prepare':
        result = validate_package(args.repo)
    else:
        require(args.bundle is not None, '--bundle is required')
        result = freeze_package(args.repo, args.bundle) if args.action == 'freeze' else verify_freeze(args.repo, args.bundle, args.expected_lock_sha256)
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__':
    try:
        main()
    except (GateError, OSError, TypeError, KeyError) as exc:
        print('PREFLIGHT_BLOCKED: ' + str(exc), file=sys.stderr)
        sys.exit(2)
