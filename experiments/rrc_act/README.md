# RRC-ACT execution tools

This directory contains preparation and analysis scaffolding for the RRC-ACT v1.2 execution amendment. `rrc_act_runner.py` is an offline synthetic-replay recorder, not a real LLM runner; it has no provider adapter or network path. `rrc_act_scorer.py` applies fixed scoring denominators to a frozen masked item bank, but is enabled only for explicitly synthetic replay data. No provider credentials, concrete answer bank, or confirmatory data are included.

Run the local tests:

```text
python3 -m unittest discover -s experiments/rrc_act/tests -v
```

The preparation gate is expected to stop on the current template:

```text
python3 experiments/rrc_act/rrc_act_preflight.py prepare --repo .
```

`freeze` creates a new candidate bundle only after all concrete inputs pass. It refuses to overwrite an existing destination. `verify` requires the lock digest copied from the external registry deposit; a digest calculated from the local bundle is not an independent registration proof.

Replay command inputs are synthetic fixtures (`requests.json`, `replies.json`) plus a separate frozen 76-item ID list; the output folder must not already exist. Replay records are hash-chained, have explicit null provider token/latency fields, and are always labelled `synthetic-test`. Full attempts go into `responses.jsonl`; after verification a separate `masked_responses.jsonl` removes prompts and state payloads and retains only final responses. The scorer accepts only this masked schema, including explicit missing markers for every absent item; `join_assignments` adds labels only after scoring. Missing responses stay in the fixed denominators, while wrong answers remain valid observations.

The primary analysis command intentionally defaults to blocked confirmatory mode. These replay/score tools cannot be cited as empirical evidence or used to enable the real-run gate. Before confirmatory data collection, the real runner, model snapshots, provider terms, durable-state adapter, prompt/item banks and answer keys, retry semantics, and third-party registration receipt must be complete and independently audited. Runner development and explicitly exploratory pilot design can precede registration. Real calls may incur provider charges and are not executed by this software.

**Prospective scoring note:** the v1.1 protocol defines four baseline contradiction cases inside a 12-item baseline composite but does not spell out their within-case aggregation. This scorer gives each case one point equal to the mean of its three frozen binary rubric points (baseline denominator 12). This is a proposed clarification; disclose it in v1.2 and freeze/externally register it before any confirmatory response is inspected. The v1.1 timestamped files remain unchanged.

See the [detailed boundary and scoring note](../../papers/registration_execution/synthetic_scoring_note_20261008.md), including what hashes do not establish and which real-runtime operations are still missing.

Command-line scoring additionally requires `--raw-records responses.jsonl` to verify original retry history and compare the exact masked projection before scoring. See the [review record](../../papers/registration_execution/replay_review_20261008.md) for external review limitations and reproduced fixes. Pure `score_masked_agent` is the scoring core, not a provenance verifier.
