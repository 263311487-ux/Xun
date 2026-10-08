"""Hand-derived fixtures: 76 responses contain 100 score points."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from experiments.rrc_act import rrc_act_runner as runner
from experiments.rrc_act import rrc_act_scorer as scorer
from experiments.rrc_act import rrc_act_analysis as analysis


def fixture():
    bank, keys, replies = [], {}, {}
    for phase, component, count in (
        ('baseline','self_other_attribution',4), ('baseline','goal_consistency',4),
        ('baseline','contradiction_resolution',4), ('endpoint','self_other_attribution',24),
        ('endpoint','goal_consistency',16), ('endpoint','contradiction_resolution',12),
        ('endpoint','post_unload_residue',12)):
        for i in range(count):
            iid = f'{phase}-{component}-{i}'
            item = dict(item_id=iid, phase=phase, component=component)
            answer = 'action_A'
            if component=='self_other_attribution': answer=('self','other','unknown')[i%3]
            if component=='contradiction_resolution':
                answer=dict(conflict_detected=True, preferred_source='trace_A', update_action='revise')
            if component=='post_unload_residue': item['stratum']='target' if i<6 else 'control'
            bank.append(item); keys[iid]=answer
            replies[iid]=[dict(status='ok',answer=copy.deepcopy(answer),state_after={})]
    return bank, keys, replies


def assignments():
    return [dict(agent_id='AM00001',cohort='main',family_id='family_A',A='1',B='1',C='0')]


class RunnerScorerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.bank,self.keys,self.replies=fixture()

    def collect(self,replies=None,name='run',**kwargs):
        requests=[dict(item_id=i['item_id'],session=0 if i['phase']=='baseline' else 35,
                       prompt={'system':'Synthetic software test','user':i['item_id']}) for i in self.bank]
        return runner.replay_agent(agent_id='AM00001',requests=requests,
            replies=self.replies if replies is None else replies,output_dir=self.root/name,
            expected_item_ids=[i['item_id'] for i in self.bank],**kwargs)

    def score(self,records):
        try:
            masked=runner.mask_records(records,'AM00001')
        except runner.RunnerError as exc:
            raise scorer.ScorerError(str(exc)) from exc
        return scorer.score_replay_agent('AM00001',self.bank,self.keys,masked,records)

    def test_synthetic_mode_and_confirmatory_block_before_output(self):
        rows=self.collect()
        self.assertEqual(len(rows),76)
        self.assertEqual(rows[0]['dataset_mode'],'synthetic-test')
        self.assertIs(rows[0]['synthetic'],True)
        self.assertIsNone(rows[0]['input_tokens'])
        self.assertIsNone(rows[0]['provider_latency_ms'])
        self.assertNotIn('A',rows[0]); self.assertNotIn('family_id',rows[0])
        with self.assertRaises(runner.RunnerError): self.collect(name='real',dataset_mode='confirmatory')
        self.assertFalse((self.root/'real').exists())

    def test_replay_rejects_incomplete_fixed_protocol_item_list(self):
        requests=[dict(item_id=i['item_id'],session=0 if i['phase']=='baseline' else 35,
                       prompt={'user':i['item_id']}) for i in self.bank[:-1]]
        with self.assertRaisesRegex(runner.RunnerError,'76|complete'):
            runner.replay_agent(agent_id='AM00001',requests=requests,replies={},output_dir=self.root/'partial',
                                expected_item_ids=[i['item_id'] for i in self.bank])
        self.assertFalse((self.root/'partial').exists())

    def test_complete_count_with_wrong_bank_id_is_rejected(self):
        requests=[dict(item_id=i['item_id'],session=0 if i['phase']=='baseline' else 35,
                       prompt={'user':i['item_id']}) for i in self.bank]
        requests[-1]['item_id']='unbanked'
        with self.assertRaisesRegex(runner.RunnerError,'complete frozen bank'):
            runner.replay_agent(agent_id='AM00001',requests=requests,replies={},output_dir=self.root/'swapped',
                                expected_item_ids=[i['item_id'] for i in self.bank])
        self.assertFalse((self.root/'swapped').exists())

    def test_mask_omits_prompts_states_and_scorer_rejects_missing_or_unmasked_input(self):
        rows=self.collect()
        masked=runner.mask_records(rows,'AM00001')
        self.assertEqual(len(masked),76)
        for row in masked:
            self.assertFalse({'prompt','state_before','state_after','A','B','C','family_id'} & set(row))
        with self.assertRaises(scorer.ScorerError):
            scorer.score_replay_agent('AM00001',self.bank,self.keys,rows,rows)
        with self.assertRaises(scorer.ScorerError):
            scorer.score_replay_agent('AM00001',self.bank,self.keys,masked[:-1],rows)
        for mutation in ({'status':'typo'}, {'attempt':0}, {'answer':None}):
            bad=copy.deepcopy(masked); bad[0].update(mutation)
            with self.assertRaises(scorer.ScorerError):
                scorer.score_replay_agent('AM00001',self.bank,self.keys,bad,rows)

    def test_payload_hashes_persist_and_output_never_overwritten(self):
        rows=self.collect()
        raw=[json.loads(x) for x in (self.root/'run'/'responses.jsonl').read_text().splitlines()]
        self.assertEqual(rows,raw)
        self.assertTrue((self.root/'run'/'COMPLETE.json').is_file())
        manifest=json.loads((self.root/'run'/'COMPLETE.json').read_text())
        for name in ('responses.jsonl','masked_responses.jsonl','requests.json','replies.json','expected_item_ids.json'):
            self.assertEqual(manifest['files'][name],hashlib.sha256((self.root/'run'/name).read_bytes()).hexdigest())
        for row in rows:
            for field in ('prompt','answer','state_before','state_after'):
                value=json.dumps(row[field],sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
                self.assertEqual(row[field+'_sha256'],hashlib.sha256(value.encode()).hexdigest())
        with self.assertRaises(runner.RunnerError): self.collect()
        self.assertEqual(raw,[json.loads(x) for x in (self.root/'run'/'responses.jsonl').read_text().splitlines()])

    def test_fixed_denominators_and_post_score_assignment_join(self):
        masked=self.score(self.collect())
        self.assertEqual(masked['missing_points'],0)
        for name in ('baseline_composite',*analysis.COMPONENTS): self.assertEqual(masked[name],1.)
        self.assertNotIn('A',masked)
        row=scorer.join_assignments(assignments(),[masked])[0]
        self.assertEqual(set(row),analysis.FIELDS)
        self.assertEqual(row['synthetic'],'1'); self.assertEqual(row['dataset_mode'],'synthetic-test')

    def test_missing_conflict_three_points_baseline_one_no_denominator_shrink(self):
        del self.replies['endpoint-contradiction_resolution-0']
        del self.replies['baseline-contradiction_resolution-0']
        row=self.score(self.collect())
        self.assertEqual(row['missing_points'],4)
        self.assertAlmostEqual(row['contradiction_resolution'],33/36)
        self.assertAlmostEqual(row['baseline_composite'],11/12)
        self.assertEqual(row['valid_agent'],'1')

    def test_partial_conflict_strict_boolean_and_balanced_control_score(self):
        self.replies['endpoint-contradiction_resolution-0'][0]['answer']={
            'conflict_detected':'true','preferred_source':'wrong','update_action':'revise'}
        self.replies['baseline-contradiction_resolution-0'][0]['answer']['update_action']='retain'
        for i in range(6,12): self.replies[f'endpoint-post_unload_residue-{i}'][0]['answer']='wrong'
        row=self.score(self.collect())
        self.assertAlmostEqual(row['contradiction_resolution'],34/36)
        self.assertAlmostEqual(row['baseline_composite'],(4+4+3+2/3)/12)
        self.assertEqual(row['post_unload_residue'],.5)
        self.assertEqual(row['missing_points'],0)

    def test_all_missing_retained_wrong_answers_are_not_technical_failure(self):
        row=self.score(self.collect(replies={}))
        self.assertEqual(row['missing_points'],100)
        self.assertEqual(row['technical_reason'],'failure_before_baseline')
        self.assertEqual(row['valid_agent'],'0')
        self.assertEqual(len(scorer.join_assignments(assignments(),[row])),1)
        for attempts in self.replies.values(): attempts[0]['answer']='wrong'
        row=self.score(self.collect(name='wrong'))
        self.assertEqual(row['valid_agent'],'1'); self.assertEqual(row['missing_points'],0)

    def test_one_same_state_retry_and_no_success_selection(self):
        iid=self.bank[0]['item_id']
        self.replies[iid]=[dict(status='technical_failure'),self.replies[iid][0]]
        rows=self.collect(); attempts=[r for r in rows if r['item_id']==iid]
        self.assertEqual([r['attempt'] for r in attempts],[1,2])
        for name in ('prompt_sha256','state_before_sha256'):
            self.assertEqual(attempts[0][name],attempts[1][name])
        self.assertEqual(self.score(rows)['missing_points'],0)
        self.replies[iid][0]=dict(status='ok',answer='wrong',state_after={})
        with self.assertRaises(runner.RunnerError): self.collect(name='selected')
        self.assertFalse((self.root/'selected').exists())
        self.replies[iid]=[dict(status='technical_failure')]
        with self.assertRaisesRegex(runner.RunnerError,'retry'):
            self.collect(name='no-retry')
        self.assertFalse((self.root/'no-retry').exists())
        self.replies[iid]=[dict(status='technical_failure'),dict(status='technical_failure')]
        rows=self.collect(name='double-failure')
        self.assertEqual([r['status'] for r in rows if r['item_id']==iid],['technical_failure','technical_failure'])
        self.assertEqual(self.score(rows)['missing_points'],1)
        self.replies[iid]=[dict(status='technical_failure'),dict(status='missing')]
        with self.assertRaises(runner.RunnerError): self.collect(name='invalid-missing-retry')
        self.assertFalse((self.root/'invalid-missing-retry').exists())

    def test_tampering_duplicates_cross_agent_forged_modes_and_unblinding_rejected(self):
        rows=self.collect()
        for mutate in (lambda r:r[0].update(answer='tampered'), lambda r:r.append(copy.deepcopy(r[0])),
            lambda r:r[0].update(agent_id='AM00002'), lambda r:r[0].update(dataset_mode='confirmatory',synthetic=False),
            lambda r:r[0].update(A='1'), lambda r:r[0].update(self_report_score=1)):
            data=copy.deepcopy(rows); mutate(data)
            with self.assertRaises(scorer.ScorerError): self.score(data)

    def test_bad_keys_overlap_or_unequal_strata_rejected(self):
        rows=self.collect()
        for mode in ('missing_key','overlap','stratum','empty_conflict','extra_key'):
            bank,keys=copy.deepcopy(self.bank),copy.deepcopy(self.keys)
            if mode=='missing_key': keys.pop(bank[0]['item_id'])
            elif mode=='overlap': bank[-1]['item_id']=bank[0]['item_id']
            elif mode=='stratum': bank[-1]['stratum']='target'
            elif mode=='empty_conflict': keys['endpoint-contradiction_resolution-0']={}
            else: keys['unused']='answer'
            with self.assertRaises(scorer.ScorerError):
                scorer.score_replay_agent('AM00001',bank,keys,runner.mask_records(rows,'AM00001'),rows)

    def test_credentials_and_path_escape_rejected_before_creation(self):
        self.replies[self.bank[0]['item_id']][0]['state_after']={'nested':{'api-key-v2':'fixture-secret'}}
        with self.assertRaises(runner.RunnerError): self.collect()
        self.assertFalse((self.root/'run').exists())
        with self.assertRaises(runner.RunnerError):
            runner.replay_agent(agent_id='../../escape',requests=[],replies={},output_dir=self.root/'bad',expected_item_ids=[])

    def test_join_rejects_missing_duplicate_and_invalid_cells(self):
        row=self.score(self.collect())
        with self.assertRaises(scorer.ScorerError): scorer.join_assignments(assignments(),[])
        with self.assertRaises(scorer.ScorerError): scorer.join_assignments(assignments(),[row,row])
        bad=assignments(); bad[0]['cohort']='generic_praise'
        with self.assertRaises(scorer.ScorerError): scorer.join_assignments(bad,[row])

    def test_metadata_and_deleted_attempt_cannot_pass_unchanged_hash_chain(self):
        rows=self.collect()
        for mutate in (lambda r:r[0].update(session=-1), lambda r:r.pop(4),
                       lambda r:r[0].update(item_id='endpoint-self_other_attribution-0')):
            changed=copy.deepcopy(rows); mutate(changed)
            with self.assertRaises(scorer.ScorerError): self.score(changed)

    def test_join_rejects_invalid_scores_missingness_and_validity(self):
        row=self.score(self.collect())
        for mutation in ({'baseline_composite':float('nan')}, {'missing_points':101},
                         {'goal_consistency':2}, {'valid_agent':'0','technical_reason':''}):
            with self.assertRaises(scorer.ScorerError):
                scorer.join_assignments(assignments(),[dict(row,**mutation)])

    def test_state_continuity_uses_json_identity_not_python_boolean_coercion(self):
        rows=self.collect()
        rows[0]['state_after']={'v':True}
        rows[1]['state_before']={'v':1}
        previous='0'*64
        for row in rows:
            for field in runner.PAYLOADS: row[field+'_sha256']=runner.digest(row[field])
            row['prev_record_sha256']=previous
            row['record_sha256']=runner.record_digest(row)
            previous=row['record_sha256']
        with self.assertRaisesRegex(runner.RunnerError,'state chain'):
            runner.validate_records(rows,'AM00001')

    def test_negative_session_rejected_even_after_rehashing(self):
        rows=self.collect(); rows[0]['session']=-1
        previous='0'*64
        for row in rows:
            row['prev_record_sha256']=previous; row['record_sha256']=runner.record_digest(row)
            previous=row['record_sha256']
        with self.assertRaisesRegex(runner.RunnerError,'session'):
            runner.validate_records(rows,'AM00001')

    def test_join_accepts_integer_json_factors_and_normalizes_to_csv_strings(self):
        assigned=assignments()
        for key in ('A','B','C'): assigned[0][key]=int(assigned[0][key])
        joined=scorer.join_assignments(assigned,[self.score(self.collect())])[0]
        self.assertEqual((joined['A'],joined['B'],joined['C']),('1','1','0'))

    def test_nonfinite_payload_and_unhashable_bank_type_fail_closed(self):
        self.replies[self.bank[0]['item_id']][0]['answer']=float('nan')
        with self.assertRaises(runner.RunnerError): self.collect()
        self.assertFalse((self.root/'run').exists())
        bank=copy.deepcopy(self.bank); bank[0]['phase']=[]
        with self.assertRaises(scorer.ScorerError): scorer.validate_bank(bank,self.keys)

    def test_cli_replay_then_masked_scoring_and_confirmatory_refusal(self):
        requests=[dict(item_id=i['item_id'],session=0 if i['phase']=='baseline' else 35,
                       prompt={'user':i['item_id']}) for i in self.bank]
        for name,value in (('requests',requests),('replies',self.replies),('bank',self.bank),('keys',self.keys),
                           ('ids',[i['item_id'] for i in self.bank])):
            (self.root/(name+'.json')).write_text(json.dumps(value))
        run_cmd=[sys.executable,runner.__file__,'--agent-id','AM00001','--requests',str(self.root/'requests.json'),
                 '--replies',str(self.root/'replies.json'),'--output',str(self.root/'cli'),
                 '--expected-item-ids',str(self.root/'ids.json')]
        result=subprocess.run(run_cmd,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['evidence_status'],'synthetic_test_only')
        result=subprocess.run([sys.executable,scorer.__file__,'--agent-id','AM00001',
            '--bank',str(self.root/'bank.json'),'--keys',str(self.root/'keys.json'),
            '--records',str(self.root/'cli'/'masked_responses.jsonl'),
            '--raw-records',str(self.root/'cli'/'responses.jsonl')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['baseline_composite'],1)
        result=subprocess.run(run_cmd+['--dataset-mode','confirmatory'],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)


if __name__=='__main__': unittest.main()
