#!/usr/bin/env python3
"""Primary ANCOVA scaffold. Only synthetic-test input is enabled in v1.2.

Raw-response scoring, assignment reconciliation and a real run ledger are still
required before enabling confirmatory data. This module makes no model calls.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import random
import sys
from pathlib import Path


class AnalysisError(ValueError):
    pass


COMPONENTS = ('self_other_attribution', 'goal_consistency', 'contradiction_resolution', 'post_unload_residue')
INVALID_REASONS = {'model_snapshot_drift', 'hash_mismatch', 'unrecoverable_corruption', 'failure_before_baseline'}
FIELDS = {'agent_id', 'cohort', 'family_id', 'A', 'B', 'C', 'valid_agent', 'technical_reason',
          'missing_points', 'dataset_mode', 'synthetic', 'baseline_composite', *COMPONENTS}


def mean(xs):
    return sum(xs) / len(xs)


def _fit(rows):
    """Frisch-Waugh-Lovell OLS, with fixed family intercepts and baseline.

    Exact redundant baseline covariates are omitted and disclosed; lack of
    treatment variation is an error. Residual SD is sqrt(SSE/(n-rank(X))).
    """
    n = len(rows)
    families = sorted({r['family_id'] for r in rows})
    centered = []
    for f in families:
        group = [r for r in rows if r['family_id'] == f]
        centers = {k: mean([r[k] for r in group]) for k in ('A', 'baseline', 'endpoint')}
        centered.extend({k: r[k] - centers[k] for k in centers} for r in group)
    bb = sum(r['baseline'] ** 2 for r in centered)
    redundant = bb < 1e-12
    ab = sum(r['A'] * r['baseline'] for r in centered) / bb if not redundant else 0
    yb = sum(r['endpoint'] * r['baseline'] for r in centered) / bb if not redundant else 0
    az = [r['A'] - ab * r['baseline'] for r in centered]
    yz = [r['endpoint'] - yb * r['baseline'] for r in centered]
    aa = sum(a*a for a in az)
    if aa < 1e-12:
        raise AnalysisError('treatment not identifiable in ANCOVA')
    beta = sum(a*y for a, y in zip(az, yz)) / aa
    rank = len(families) + 1 + (not redundant)
    if n <= rank:
        raise AnalysisError('insufficient residual degrees of freedom')
    sd = math.sqrt(sum((y-beta*a)**2 for a, y in zip(az, yz)) / (n-rank))
    return {'difference': beta, 'residual_sd': sd,
            'd': beta/sd if sd > 1e-12 else None, 'baseline_redundant': redundant}


def percentile(xs, q):
    xs = sorted(xs)
    pos = (len(xs)-1)*q
    lo, hi = math.floor(pos), math.ceil(pos)
    return xs[lo] + (xs[hi]-xs[lo])*(pos-lo)


def interpret(ci_d, p, underpowered, protocol_failure):
    if protocol_failure:
        return 'protocol_failure'
    if underpowered or ci_d is None or p is None:
        return 'inconclusive'
    lo, hi = ci_d
    if hi < 0:
        return 'negative'
    if lo > .5:
        return 'positive_above_mie'
    if lo > 0 and hi < .5:
        return 'positive_below_mie'
    if lo > 0:
        return 'positive_mie_uncertain'
    return 'inconclusive'


def _parse_rows(path, dataset_mode):
    with Path(path).open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        if len(columns) != len(set(columns)) or set(columns) != FIELDS:
            raise AnalysisError('score columns must match data dictionary exactly; no self-report fields')
        return _parse_rows_from_records(reader, dataset_mode)


def _parse_rows_from_records(records, dataset_mode):
    rows, seen = [], set()
    for raw in records:
        if raw['dataset_mode'] != dataset_mode or raw['synthetic'] != '1':
            raise AnalysisError('only explicitly synthetic-test rows are enabled')
        aid = raw['agent_id']
        if not aid or aid in seen:
            raise AnalysisError('empty or duplicate agent_id')
        seen.add(aid)
        if raw['family_id'] not in {'family_A', 'family_B'}:
            raise AnalysisError('unknown model family')
        if (raw['cohort'],raw['A'],raw['B'],raw['C']) not in {
            *(('main',str(a),str(b),str(c)) for a in (0,1) for b in (0,1) for c in (0,1)),
            ('generic_praise','2','1','0'),
        }:
            raise AnalysisError('invalid factorial cell')
        if raw['valid_agent'] not in {'0','1'}:
            raise AnalysisError('valid_agent must be 0 or 1')
        valid = raw['valid_agent'] == '1'
        reason = raw['technical_reason']
        if (valid and reason) or (not valid and reason not in INVALID_REASONS):
            raise AnalysisError('technical exclusion reason is invalid')
        try:
            missing = int(raw['missing_points'])
            baseline = float(raw['baseline_composite'])
            scores = [float(raw[k]) for k in COMPONENTS]
        except (TypeError, ValueError) as exc:
            raise AnalysisError('blank/malformed score; upstream scorer must encode fixed-denominator zeros') from exc
        if not 0 <= missing <= 100 or any(not math.isfinite(s) or not 0 <= s <= 1 for s in [baseline,*scores]):
            raise AnalysisError('score/missingness outside defined range')
        if raw['cohort'] != 'main' or raw['B'] != '1' or raw['C'] != '0':
            continue
        # Fixed assigned-agent policy, never quietly drop a failed instance.
        # Technically unverifiable agents get zero scores; also report failure.
        rows.append(dict(agent_id=aid, family_id=raw['family_id'], A=int(raw['A']),
                         baseline=baseline if valid else 0., endpoint=mean(scores) if valid else 0.,
                         valid=valid, missing_points=missing, technical_reason=reason))
    if {r['family_id'] for r in rows} != {'family_A','family_B'}:
        raise AnalysisError('both fixed model-family blocks are required')
    for family in ('family_A','family_B'):
        if {r['A'] for r in rows if r['family_id']==family} != {0,1}:
            raise AnalysisError('both A arms are required within each family')
    return rows



def bootstrap_sample(rows, rng):
    """Resample independent agents within each fixed family by A cell."""
    sampled = []
    for family in ('family_A', 'family_B'):
        for arm in (0, 1):
            cell = [r for r in rows if r['family_id'] == family and r['A'] == arm]
            if not cell:
                raise AnalysisError('empty bootstrap stratum')
            sampled.extend(rng.choice(cell) for _ in cell)
    return sampled


def analyze_primary_csv(path, n_perm=10000, n_boot=10000, seed=20261005, dataset_mode='confirmatory'):
    if dataset_mode != 'synthetic-test':
        raise AnalysisError('confirmatory analysis disabled: raw scorer, registered anchor and run ledger integration are unfinished')
    if type(n_perm) is not int or type(n_boot) is not int or n_perm < 1 or n_boot < 1 or type(seed) is not int:
        raise AnalysisError('positive resample counts and integer seed required')
    rows = _parse_rows(path, dataset_mode)
    fitted = _fit(rows)
    observed = fitted['difference']
    families = ('family_A','family_B')
    blocks = [[i for i,r in enumerate(rows) if r['family_id']==f] for f in families]
    def rng_for(label):
        value = hashlib.sha256(f'rrc-act-v1.2:{seed}:{label}'.encode()).hexdigest()
        return random.Random(int(value,16))
    prng, brng = rng_for('permutation'), rng_for('bootstrap')
    extreme, invalid_perm = 0, 0
    for _ in range(n_perm):
        permuted = [dict(r) for r in rows]
        for indices in blocks:
            labels = [rows[i]['A'] for i in indices]
            prng.shuffle(labels)
            for i,a in zip(indices,labels):permuted[i]['A']=a
        try:
            difference=_fit(permuted)['difference']
            extreme += abs(difference) >= abs(observed)-1e-12
        except AnalysisError:
            invalid_perm += 1
    p=(extreme+1)/(n_perm+1) if not invalid_perm else None
    bd, bs, invalid_boot = [], [], 0
    for _ in range(n_boot):
        sample=bootstrap_sample(rows, brng)
        try:
            fit=_fit(sample)
            bd.append(fit['difference'])
            if fit['d'] is not None:bs.append(fit['d'])
        except AnalysisError:
            invalid_boot += 1
    # Do not silently redraw singular samples or condition on favorable variance.
    ci_difference=[percentile(bd,.025),percentile(bd,.975)] if len(bd)==n_boot else None
    ci_d=[percentile(bs,.025),percentile(bs,.975)] if len(bs)==n_boot else None
    family_estimates={}
    underpowered=False
    for f in families:
        block=[r for r in rows if r['family_id']==f]
        valid_counts={a:sum(r['valid'] and r['A']==a for r in block) for a in (0,1)}
        underpowered |= any(v < 32 for v in valid_counts.values())
        ff=_fit(block)
        family_estimates[f]={'n':len(block), 'valid_n_control':valid_counts[0], 'valid_n_treatment':valid_counts[1],
                             'adjusted_difference':ff['difference'],
                             'raw_difference':mean([r['endpoint'] for r in block if r['A']==1])-mean([r['endpoint'] for r in block if r['A']==0])}
    protocol_failure=any(r['technical_reason'] in INVALID_REASONS-{'failure_before_baseline'} for r in rows)
    complete=[r for r in rows if r['valid'] and r['missing_points']==0]
    try:
        complete_fit=_fit(complete)
        complete_summary={'n':len(complete), 'adjusted_difference':complete_fit['difference'], 'standardized_d':complete_fit['d']}
    except (AnalysisError, ZeroDivisionError):
        complete_summary={'n':len(complete), 'status':'not_estimable'}
    return dict(evidence_status='synthetic_test_only', n=len(rows), valid_n=sum(r['valid'] for r in rows),
                n_treatment=sum(r['A']==1 for r in rows), n_control=sum(r['A']==0 for r in rows),
                raw_mean_treatment=mean([r['endpoint'] for r in rows if r['A']==1]),
                raw_mean_control=mean([r['endpoint'] for r in rows if r['A']==0]),
                adjusted_difference=observed, standardized_d=fitted['d'], residual_sd=fitted['residual_sd'],
                baseline_redundant=fitted['baseline_redundant'], permutation_p=p,
                bootstrap_difference_ci=ci_difference, bootstrap_d_ci=ci_d,
                underpowered=underpowered, protocol_failure=protocol_failure,
                interpretation=interpret(ci_d,p,underpowered,protocol_failure), family_estimates=family_estimates,
                missing_points=sum(r['missing_points'] for r in rows),
                failed_agents=[{'agent_id':r['agent_id'],'reason':r['technical_reason']} for r in rows if not r['valid']],
                complete_case_sensitivity=complete_summary, invalid_permutations=invalid_perm,
                invalid_bootstrap_fits=invalid_boot, undefined_bootstrap_d=n_boot-len(bs),
                n_perm=n_perm,n_boot=n_boot,seed=seed)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scores',type=Path)
    parser.add_argument('--dataset-mode',choices=['confirmatory','synthetic-test'],default='confirmatory')
    parser.add_argument('--permutations',type=int,default=10000)
    parser.add_argument('--bootstrap',type=int,default=10000)
    parser.add_argument('--seed',type=int,default=20261005)
    args=parser.parse_args()
    result=analyze_primary_csv(args.scores,args.permutations,args.bootstrap,args.seed,args.dataset_mode)
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':
    try:main()
    except (AnalysisError,OSError) as exc:
        print('ANALYSIS_BLOCKED: '+str(exc),file=sys.stderr)
        sys.exit(2)
