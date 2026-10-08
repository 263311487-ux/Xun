#!/usr/bin/env python3
"""Masked fixed-denominator scorer for synthetic replay, not confirmatory data.

Baseline conflict cases use mean of their three binary subpoints (one point
per case). This prospective clarification requires review before registration.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

try:
    from . import rrc_act_runner as replay
except ImportError:
    import rrc_act_runner as replay


class ScorerError(ValueError):
    pass


COMPONENTS = ('self_other_attribution', 'goal_consistency', 'contradiction_resolution', 'post_unload_residue')
EXPECTED = {('baseline', c): 4 for c in COMPONENTS[:3]}
EXPECTED.update({('endpoint', c): n for c, n in zip(COMPONENTS, (24, 16, 12, 12))})
CONFLICT_FIELDS = {'conflict_detected', 'preferred_source', 'update_action'}
MASKED_FIELDS = {'agent_id', 'valid_agent', 'technical_reason', 'missing_points', 'dataset_mode',
                 'synthetic', 'baseline_composite', *COMPONENTS}


def require(condition, message):
    if not condition:
        raise ScorerError(message)


def validate_bank(bank, keys):
    require(isinstance(bank, list) and isinstance(keys, dict), 'bank/list and answer-key/object required')
    by_id, counts, strata, attribution = {}, Counter(), Counter(), Counter()
    for item in bank:
        require(isinstance(item, dict), 'invalid bank item')
        iid, component, phase = item.get('item_id'), item.get('component'), item.get('phase')
        fields = {'item_id', 'component', 'phase'} | ({'stratum'} if component == 'post_unload_residue' else set())
        require(set(item) == fields, 'unexpected bank metadata')
        require(isinstance(iid, str) and iid and iid not in by_id, 'invalid/overlapping item ID')
        require(isinstance(phase, str) and isinstance(component, str), 'phase/component must be strings')
        require((phase, component) in EXPECTED and iid in keys, 'unknown item type or missing key')
        answer = keys[iid]
        if component == 'contradiction_resolution':
            require(isinstance(answer, dict) and set(answer) == CONFLICT_FIELDS, 'incomplete conflict key')
            require(answer['conflict_detected'] is True, 'conflict cases require true detection key')
            require(isinstance(answer['preferred_source'], str) and answer['preferred_source'], 'missing source key')
            require(answer['update_action'] in ('revise', 'retain', 'abstain'), 'invalid update key')
        else:
            require(isinstance(answer, str) and answer, 'forced-choice key must be a nonempty string')
            if component == 'self_other_attribution':
                require(answer in ('self', 'other', 'unknown'), 'invalid attribution key')
                if phase == 'endpoint': attribution[answer] += 1
        if component == 'post_unload_residue':
            require(item['stratum'] in ('target', 'control'), 'invalid unload stratum')
            strata[item['stratum']] += 1
        by_id[iid] = item
        counts[(phase, component)] += 1
    require(dict(counts) == EXPECTED, 'bank differs from fixed 12 baseline/64 endpoint response counts')
    require(dict(strata) == {'target': 6, 'control': 6}, 'unload requires six target and six control items')
    require(dict(attribution) == {'self': 8, 'other': 8, 'unknown': 8}, 'attribution requires 8/8/8 strata')
    require(set(keys) == set(by_id), 'unused or missing answer keys')
    try:
        replay.scan(keys); replay.canonical(keys)
    except replay.RunnerError as exc:
        raise ScorerError(str(exc)) from exc
    return by_id


def conflict_points(answer, key):
    if not isinstance(answer, dict):
        return 0
    return sum(type(answer.get(k)) is type(key[k]) and answer.get(k) == key[k] for k in CONFLICT_FIELDS)


def score_replay_agent(agent_id, bank, answer_keys, records, raw_records):
    """Integrity wrapper: verify full history before handing off masked data."""
    try:
        expected_mask = replay.mask_records(raw_records, agent_id)
        require(replay.canonical(records) == replay.canonical(expected_mask),
                'masked responses differ from validated raw attempts')
    except replay.RunnerError as exc:
        raise ScorerError(str(exc)) from exc
    return score_masked_agent(agent_id, bank, answer_keys, records)


def score_masked_agent(agent_id, bank, answer_keys, records):
    """Pure scorer: sees no raw prompts/state, family or treatment key."""
    by_id = validate_bank(bank, answer_keys)
    require(isinstance(records, list), 'records must be a list')
    require(replay.agent_id_ok(agent_id), 'invalid anonymous ID')
    try:
        replay.scan(records)
        replay.canonical(records)
    except replay.RunnerError as exc:
        raise ScorerError(str(exc)) from exc
    for row in records:
        require(isinstance(row, dict) and set(row) == {'mask_schema','dataset_mode','synthetic','agent_id','item_id','session','attempt','status','answer','response_sha256'}, 'scorer accepts masked fields only')
        require(row['mask_schema'] == 'rrc-act-masked-response-v1' and row['dataset_mode'] == 'synthetic-test' and row['synthetic'] is True, 'only explicit masked synthetic responses accepted')
        require(row['agent_id'] == agent_id, 'cross-agent response')
        require(replay.agent_id_ok(row['agent_id']), 'invalid anonymous ID')
        require(type(row['session']) is int and row['session'] >= 0, 'invalid session')
        require(type(row['attempt']) is int and row['attempt'] in (1, 2), 'invalid attempt')
        require(isinstance(row['item_id'], str) and row['item_id'], 'invalid item ID')
        require(row['status'] in ('ok', 'technical_failure', 'missing'), 'invalid response status')
        if row['status'] == 'ok':
            require(row['answer'] is not None, 'successful response cannot be null')
        else:
            require(row['answer'] is None, 'failed/missing response cannot contain answer')
            require(row['attempt'] == (2 if row['status'] == 'technical_failure' else 1), 'incomplete retry history')
        require(isinstance(row['response_sha256'], str) and row['response_sha256'] == replay.digest(row['answer']), 'response/hash mismatch')
    try:
        replay.canonical(records)
    except replay.RunnerError as exc:
        raise ScorerError(str(exc)) from exc
    final = {}
    for row in records:
        require(row['item_id'] in by_id, 'response for unbanked item')
        require(row['item_id'] not in final, 'duplicate masked response item')
        final[row['item_id']] = row
    require(set(final) == set(by_id), 'masked records must cover complete bank including missing markers')
    totals = Counter()
    missing, baseline_observed = 0, 0
    for iid, item in by_id.items():
        phase, component = item['phase'], item['component']
        row = final[iid]
        if row['status'] != 'ok':
            missing += 3 if phase == 'endpoint' and component == 'contradiction_resolution' else 1
            continue
        if phase == 'baseline': baseline_observed += 1
        if component == 'contradiction_resolution':
            value = conflict_points(row['answer'], answer_keys[iid])
            if phase == 'baseline': value /= 3
        else:
            value = int(type(row['answer']) is str and row['answer'] == answer_keys[iid])
        totals[(phase, component)] += value
        if component == 'post_unload_residue': totals[item['stratum']] += value
    return dict(agent_id=agent_id, dataset_mode='synthetic-test', synthetic='1',
                valid_agent='1' if baseline_observed else '0',
                technical_reason='' if baseline_observed else 'failure_before_baseline',
                missing_points=missing,
                baseline_composite=sum(totals[('baseline', c)] for c in COMPONENTS[:3])/12,
                self_other_attribution=totals[('endpoint', COMPONENTS[0])]/24,
                goal_consistency=totals[('endpoint', COMPONENTS[1])]/16,
                contradiction_resolution=totals[('endpoint', COMPONENTS[2])]/36,
                post_unload_residue=.5*(totals['target']/6+totals['control']/6))


def join_assignments(assignments, masked_scores):
    """Join only after scoring; require one score for every assigned agent."""
    require(isinstance(assignments, list) and assignments and isinstance(masked_scores, list), 'invalid join inputs')
    scores = {}
    for row in masked_scores:
        require(isinstance(row, dict) and set(row) == MASKED_FIELDS, 'unexpected score fields')
        require(row['dataset_mode'] == 'synthetic-test' and row['synthetic'] == '1', 'only synthetic scores accepted')
        require(replay.agent_id_ok(row['agent_id']) and row['agent_id'] not in scores, 'duplicate/invalid scored agent')
        require(row['valid_agent'] in ('0', '1'), 'invalid validity flag')
        require((row['valid_agent'] == '1' and row['technical_reason'] == '') or
                (row['valid_agent'] == '0' and row['technical_reason'] == 'failure_before_baseline'),
                'validity and technical reason disagree')
        require(type(row['missing_points']) is int and 0 <= row['missing_points'] <= 100, 'invalid missing-point count')
        for field in ('baseline_composite', *COMPONENTS):
            require(type(row[field]) in (int, float) and math.isfinite(row[field]) and 0 <= row[field] <= 1,
                    'score out of range: '+field)
        scores[row['agent_id']] = row
    seen, joined = set(), []
    cells = {('main', str(a), str(b), str(c)) for a in (0, 1) for b in (0, 1) for c in (0, 1)}
    cells.add(('generic_praise', '2', '1', '0'))
    for assigned in assignments:
        require(isinstance(assigned, dict), 'invalid assignment')
        aid = assigned.get('agent_id')
        require(replay.agent_id_ok(aid) and aid not in seen and aid in scores, 'duplicate/absent assigned agent')
        require(assigned.get('family_id') in ('family_A', 'family_B'), 'unknown family')
        require(tuple(str(assigned.get(k)) for k in ('cohort','A','B','C')) in cells, 'invalid factorial cell')
        seen.add(aid)
        joined.append(dict(scores[aid], **{k: str(assigned[k]) for k in ('cohort','family_id','A','B','C')}))
    require(seen == set(scores), 'extra unassigned score')
    return joined


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent-id', required=True)
    parser.add_argument('--bank', type=Path, required=True)
    parser.add_argument('--keys', type=Path, required=True)
    parser.add_argument('--records', type=Path, required=True)
    parser.add_argument('--raw-records', type=Path, required=True)
    args = parser.parse_args()
    result = score_replay_agent(args.agent_id, json.loads(args.bank.read_text(encoding='utf-8')),
                               json.loads(args.keys.read_text(encoding='utf-8')),
                               [json.loads(line) for line in args.records.read_text(encoding='utf-8').splitlines()],
                               [json.loads(line) for line in args.raw_records.read_text(encoding='utf-8').splitlines()])
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    try:
        main()
    except (ScorerError, OSError, ValueError) as exc:
        print('SCORING_BLOCKED: '+str(exc), file=sys.stderr)
        sys.exit(2)
