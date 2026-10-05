# RRC-ACT execution tools

This directory contains preparation and analysis scaffolding for the RRC-ACT v1.2 execution amendment. It does not contain a real LLM runner, provider credentials, answer-key generator, or confirmatory data.

Run the local tests:

```text
python3 -m unittest discover -s experiments/rrc_act/tests -v
```

The preparation gate is expected to stop on the current template:

```text
python3 experiments/rrc_act/rrc_act_preflight.py prepare --repo .
```

`freeze` creates a new candidate bundle only after all concrete inputs pass. It refuses to overwrite an existing destination. `verify` requires the lock digest copied from the external registry deposit; a digest calculated from the local bundle is not an independent registration proof.

The primary analysis command intentionally defaults to blocked confirmatory mode. Supplying `--dataset-mode synthetic-test` is a pipeline test only and its result is labelled `synthetic_test_only`; it cannot be cited as evidence for artificial consciousness.
