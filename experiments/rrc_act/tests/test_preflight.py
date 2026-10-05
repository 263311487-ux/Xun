import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from experiments.rrc_act import rrc_act_preflight as gate

REPO = Path(__file__).resolve().parents[3]


class PreflightTests(unittest.TestCase):
    def test_templates_are_blocked_with_actionable_errors(self):
        with self.assertRaisesRegex(gate.GateError, 'model|manifest|artifact'):
            gate.validate_package(REPO)

    def test_allocation_is_balanced_unique_and_interleaved(self):
        rows = gate.build_assignment_rows('0' * 64)
        self.assertEqual(rows, gate.build_assignment_rows('0' * 64))
        self.assertNotEqual(rows, gate.build_assignment_rows('1' * 64))
        self.assertEqual(len(rows), 576)
        self.assertEqual(len({r['agent_id'] for r in rows}), 576)
        cells = [(r['cohort'], r['family_id'], r['A'], r['B'], r['C']) for r in rows]
        self.assertEqual(len(set(cells)), 18)
        self.assertTrue(all(cells.count(k) == 32 for k in set(cells)))
        self.assertGreater(len(set(cells[:32])), 4)

    def test_freeze_verifies_hashes_assignment_and_refuses_overwrite(self):
        # Artificial package used only to exercise the integrity layer.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec_path = root / gate.SPEC
            spec_path.parent.mkdir(parents=True)
            artifacts = {}
            for role in gate.REQUIRED_ROLES:
                p = root / (role + '.txt')
                p.write_text('fixture ' + role)
                artifacts[role] = {'path': p.name, 'sha256': gate.sha256_file(p)}
            model_path = root / 'model_manifest.txt'
            model_path.write_text(json.dumps({
                'status': 'concrete', 'model_families': [dict(family_id=f, **{k: 'fixture-'+f for k in gate.MODEL_FIELDS}) for f in gate.FAMILIES],
                'decoding': {'temperature': .2, 'top_p': 1.0, 'max_output_tokens': 512},
                'runtime_requirements': {'common_external_runtime': True, 'durable_policy_checkpoint': True},
            }))
            artifacts['model_manifest']['sha256'] = gate.sha256_file(model_path)
            spec_path.write_text(json.dumps({'schema_version': '1.2', 'artifacts': artifacts}))
            bundle = root / 'frozen'
            gate.freeze_package(root, bundle)
            anchor = gate.sha256_file(bundle / 'freeze.lock.json')
            lock = json.loads((bundle / 'freeze.lock.json').read_text())
            self.assertEqual(len(lock['bundle_artifacts']), len(gate.REQUIRED_ROLES))
            for entry in lock['bundle_artifacts'].values():
                copied = bundle / entry['bundle_path']
                self.assertTrue(copied.is_file())
                self.assertEqual(gate.sha256_file(copied), entry['sha256'])
            gate.verify_freeze(root, bundle, anchor)
            with self.assertRaises(gate.GateError):
                gate.freeze_package(root, bundle)
            table = bundle / 'assignment.csv'
            with table.open(newline='') as source:
                data = list(csv.DictReader(source))
            data[0]['A'] = '9'
            with table.open('w', newline='') as f:
                w = csv.DictWriter(f, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
            with self.assertRaisesRegex(gate.GateError, 'assignment'):
                gate.verify_freeze(root, bundle, anchor)
            table.write_bytes(gate.assignment_bytes(gate.build_assignment_rows(json.loads((bundle / 'freeze.lock.json').read_text())['assignment_seed_sha256'])))
            model_path.write_text('changed after freeze')
            with self.assertRaises(gate.GateError):
                gate.verify_freeze(root, bundle, anchor)

    def test_bundle_artifact_tampering_is_detected_even_if_repo_is_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec_path = root / gate.SPEC
            spec_path.parent.mkdir(parents=True)
            artifacts = {}
            for role in gate.REQUIRED_ROLES:
                p = root / (role + '.txt')
                p.write_text('fixture ' + role)
                artifacts[role] = {'path': p.name, 'sha256': gate.sha256_file(p)}
            model_path = root / 'model_manifest.txt'
            model_path.write_text(json.dumps({
                'status': 'concrete', 'model_families': [dict(family_id=f, **{k: 'fixture-'+f for k in gate.MODEL_FIELDS}) for f in gate.FAMILIES],
                'decoding': {'temperature': .2, 'top_p': 1.0, 'max_output_tokens': 512},
                'runtime_requirements': {'common_external_runtime': True, 'durable_policy_checkpoint': True},
            }))
            artifacts['model_manifest']['sha256'] = gate.sha256_file(model_path)
            spec_path.write_text(json.dumps({'schema_version': '1.2', 'artifacts': artifacts}))
            bundle = root / 'frozen'
            gate.freeze_package(root, bundle)
            lock_sha = gate.sha256_file(bundle / 'freeze.lock.json')
            first = next(iter(json.loads((bundle / 'freeze.lock.json').read_text())['bundle_artifacts'].values()))
            (bundle / first['bundle_path']).write_text('tampered')
            with self.assertRaisesRegex(gate.GateError, 'bundle artifact'):
                gate.verify_freeze(root, bundle, lock_sha)

    def test_lock_without_copied_inputs_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec_path = root / gate.SPEC
            spec_path.parent.mkdir(parents=True)
            artifacts = {}
            for role in gate.REQUIRED_ROLES:
                p = root / (role + '.txt')
                p.write_text('fixture ' + role)
                artifacts[role] = {'path': p.name, 'sha256': gate.sha256_file(p)}
            model_path = root / 'model_manifest.txt'
            model_path.write_text(json.dumps({
                'status': 'concrete', 'model_families': [dict(family_id=f, **{k: 'fixture-'+f for k in gate.MODEL_FIELDS}) for f in gate.FAMILIES],
                'decoding': {'temperature': .2, 'top_p': 1.0, 'max_output_tokens': 512},
                'runtime_requirements': {'common_external_runtime': True, 'durable_policy_checkpoint': True},
            }))
            artifacts['model_manifest']['sha256'] = gate.sha256_file(model_path)
            spec_path.write_text(json.dumps({'schema_version': '1.2', 'artifacts': artifacts}))
            bundle = root / 'frozen'
            gate.freeze_package(root, bundle)
            lock = json.loads((bundle / 'freeze.lock.json').read_text())
            lock.pop('bundle_artifacts')
            (bundle / 'freeze.lock.json').write_text(gate.canonical_json(lock) + '\n')
            with self.assertRaisesRegex(gate.GateError, 'copied bundle artifacts'):
                gate.verify_freeze(root, bundle, gate.sha256_file(bundle / 'freeze.lock.json'))

    def test_missing_synthetic_flag_is_not_treated_as_real(self):
        with self.assertRaises(gate.GateError):
            gate.validate_response_record({'dataset_mode': 'confirmatory', 'agent_id': 'AM00001'})

    def test_token_counts_allowed_credentials_rejected(self):
        record = dict(schema_version='rrc-act-response-v1.2', dataset_mode='confirmatory', synthetic=False,
                      agent_id='AM00001', session=1, item_id='q1', input_tokens=10, output_tokens=5, latency_ms=2)
        record.update({k: '1' * 64 for k in gate.RESPONSE_HASH_FIELDS})
        gate.validate_response_record(record)
        for mutation in ({'synthetic': True}, {'self_report_score': 1}, {'api_key': 'fixture'}):
            with self.assertRaises(gate.GateError):
                gate.validate_response_record(dict(record, **mutation))


if __name__ == '__main__':
    unittest.main()
