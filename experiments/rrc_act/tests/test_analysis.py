import csv
import tempfile
import unittest
from pathlib import Path
from experiments.rrc_act import rrc_act_analysis as analysis

COMPONENTS = ('self_other_attribution','goal_consistency','contradiction_resolution','post_unload_residue')


def fixture():
    rows = []
    for f in ('family_A','family_B'):
        for a in (0,1):
            for i in range(32):
                baseline = .3 + (i % 4) * .1
                score = .2 + .2*baseline + .08*a + (.02 if f == 'family_B' else 0) + (-.03 if i % 2 else .03)
                rows.append(dict(agent_id=f'AM{len(rows)+1:05d}',cohort='main',family_id=f,A=str(a),B='1',C='0',
                                 valid_agent='1',technical_reason='',missing_points='0',
                                 dataset_mode='synthetic-test',synthetic='1',baseline_composite=str(baseline),
                                 **{key: str(score) for key in COMPONENTS}))
    return rows


def write_rows(p, rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


class AnalysisTests(unittest.TestCase):
    def run_fixture(self, rows):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'scores.csv';write_rows(p,rows)
            return analysis.analyze_primary_csv(p,n_perm=99,n_boot=99,seed=7,dataset_mode='synthetic-test')

    def test_known_adjusted_effect_and_two_distinct_interval_scales(self):
        result=self.run_fixture(fixture())
        self.assertAlmostEqual(result['adjusted_difference'],.08,places=10)
        self.assertTrue(0 <= result['permutation_p'] <= 1)
        self.assertIn('bootstrap_difference_ci',result)
        self.assertIn('bootstrap_d_ci',result)
        self.assertGreater(result['bootstrap_d_ci'][0],result['bootstrap_difference_ci'][1])
        self.assertEqual(result['evidence_status'],'synthetic_test_only')

    def test_invalid_agent_retained_in_assigned_population(self):
        rows=fixture();rows[0]['valid_agent']='0';rows[0]['technical_reason']='failure_before_baseline'
        result=self.run_fixture(rows)
        self.assertEqual(result['n'],128)
        self.assertEqual(result['valid_n'],127)
        self.assertEqual(result['interpretation'],'inconclusive')
        self.assertTrue(result['underpowered'])

    def test_blank_score_rejected_never_silently_dropped(self):
        rows=fixture();rows[0]['goal_consistency']=''
        with self.assertRaises(analysis.AnalysisError):self.run_fixture(rows)

    def test_missing_point_bound_is_fixed(self):
        rows = fixture(); rows[0]['missing_points'] = '101'
        with self.assertRaises(analysis.AnalysisError): self.run_fixture(rows)

    def test_duplicate_or_unknown_family_rejected(self):
        for mutate in ('duplicate','family','nan'):
            rows=fixture()
            if mutate=='duplicate':rows[1]['agent_id']=rows[0]['agent_id']
            elif mutate=='family':rows[0]['family_id']='family_C'
            else:rows[0]['goal_consistency']='nan'
            with self.assertRaises(analysis.AnalysisError):self.run_fixture(rows)

    def test_default_confirmatory_entry_is_disabled_for_scaffold(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'scores.csv';write_rows(p,fixture())
            with self.assertRaisesRegex(analysis.AnalysisError,'confirmatory'):
                analysis.analyze_primary_csv(p)

    def test_mie_labels_cover_positive_interval_below_threshold(self):
        self.assertEqual(analysis.interpret([.1,.4],.01,False,False),'positive_below_mie')
        self.assertEqual(analysis.interpret([.1,.7],.01,False,False),'positive_mie_uncertain')
        self.assertEqual(analysis.interpret([.6,.9],.01,True,False),'inconclusive')
        self.assertEqual(analysis.interpret([-.9,-.6],.01,False,False),'negative')
        self.assertEqual(analysis.interpret([.1,.4],.99,False,False),'positive_below_mie')

    def test_bootstrap_resamples_within_family_and_arm(self):
        rows = analysis._parse_rows_from_records(fixture(), 'synthetic-test')
        rng = analysis.random.Random(3)
        for _ in range(20):
            sampled = analysis.bootstrap_sample(rows, rng)
            counts = {(f, a): sum(r['family_id'] == f and r['A'] == a for r in sampled)
                      for f in ('family_A', 'family_B') for a in (0, 1)}
            self.assertEqual(counts, {('family_A', 0): 32, ('family_A', 1): 32,
                                      ('family_B', 0): 32, ('family_B', 1): 32})

    def test_constant_baseline_and_zero_variance_are_explicit(self):
        rows=fixture()
        for row in rows:
            row['baseline_composite']='.5'
            for key in COMPONENTS:row[key]='.5'
        result=self.run_fixture(rows)
        self.assertIsNone(result['standardized_d'])
        self.assertIsNone(result['bootstrap_d_ci'])
        self.assertEqual(result['interpretation'],'inconclusive')
        self.assertTrue(result['baseline_redundant'])


if __name__ == '__main__':unittest.main()
