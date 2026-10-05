# RRC-ACT v1.2 execution package

This directory is a registration-ready **execution amendment**, not an external registration. It keeps the timestamped v1.1 freeze unchanged while fixing two implementation ambiguities before a real run:

- the assignment seed no longer depends on its own assignment-table hash;
- the public template is replaced by a newly generated opaque-ID run order only after all concrete inputs are hashed.

The current artifact map intentionally contains null hashes and missing real assets. The preflight command must therefore fail closed:

```text
python3 experiments/rrc_act/rrc_act_preflight.py prepare --repo .
```

The next required inputs are concrete model snapshots, prompt/template files, item banks and answer keys, a common external runtime with durable-policy checkpoint support, a raw-response scorer, and a real runner. The analysis scaffold defaults to blocked confirmatory mode and labels its synthetic tests as `synthetic_test_only`.

`registration_field_mapping_v1.2.md` is a platform-neutral mapping for the live OSF or AsPredicted form. It does not claim that either registry has been completed and contains no guessed official template URL.
