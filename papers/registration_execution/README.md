# RRC-ACT v1.2 execution package

This directory contains a prospective **execution amendment**, not a completed registration package or external registration. It keeps the timestamped v1.1 freeze unchanged while fixing two implementation ambiguities before a real run:

- the assignment seed no longer depends on its own assignment-table hash;
- the public template is replaced by a newly generated opaque-ID run order only after all concrete inputs are hashed.

The current artifact map intentionally contains null hashes and missing real assets. The preflight command must therefore fail closed:

```text
python3 experiments/rrc_act/rrc_act_preflight.py prepare --repo .
```

The next required inputs are concrete model snapshots, prompt/template files, item banks and answer keys, a common external runtime with durable-policy checkpoint support, and a real provider-backed runner. `experiments/rrc_act/rrc_act_runner.py` currently records offline synthetic fixtures only; `rrc_act_scorer.py` scores masked synthetic replay only. They are software pipeline checks, not a real runner/scorer qualification or evidence. The analysis scaffold defaults to blocked confirmatory mode and labels its synthetic tests as `synthetic_test_only`.

`registration_field_mapping_v1.2.md` is a platform-neutral mapping for the live OSF or AsPredicted form. It does not claim that either registry has been completed and contains no guessed official template URL.

The [synthetic scoring note](synthetic_scoring_note_20261008.md) documents a proposed baseline aggregation clarification and the exact boundary of the new offline tools. Include the reviewed clarification in a future complete freeze; it has not been externally registered.
