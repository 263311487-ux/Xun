# RRC-ACT v1.2 Execution Amendment

**Status:** prospective execution amendment; not registered. It does not replace or alter the byte-level v1.1 freeze or its RFC 3161 tokens. It becomes operative only when this amendment, the completed artifact map, the model snapshots, the item banks, the scoring code, the analysis code, and the freeze lock are deposited together before confirmatory output is inspected.

## Why this amendment exists

The v1.1 protocol describes an assignment seed that includes the model manifest, while that manifest also contains the assignment-table hash. That is a circular dependency. The v1.1 CSV also presents condition blocks in public row order, which is unsuitable as the final blinded run order. The v1.2 execution path fixes both issues without rewriting the public v1.1 record.

## Hash and assignment order

`execution_spec_v1.2.json` is the single upstream artifact map. Every listed file has a relative path and SHA-256. The map itself is canonicalized with sorted JSON keys:

```text
input_root_sha256 = SHA256(canonical_json(artifact_path_and_hash_map))
assignment_seed_sha256 = SHA256(
  "rrc-act-allocation-v1.2\n" + input_root_sha256 + "\n" + SHA256(execution_spec_v1.2.json)
)
```

The assignment table is generated only after this seed exists. Its hash is written into a new freeze lock and is never used to generate itself. The lock is compared with the digest deposited at the external registry; a local lock alone is version control, not registration.

IDs are opaque, 576 rows are balanced across 18 cells, and global run order is independently permuted. The runner receives the allocation key. Scorers receive masked IDs, item IDs, structured responses, and frozen answer keys. The allocation key is not disclosed to scorers until scoring closes.

## Analysis clarifications

- The raw ANCOVA contrast is measured in composite score points from 0 to 1. The minimum meaningful effect `d = 0.50` is standardized. Interpretation labels compare the standardized bootstrap interval with zero and 0.50; they never compare a raw score-point interval directly with `0.50`.
- Bootstrap draws resample whole agents within model-family by treatment arm and refit the prespecified ANCOVA. Invalid or zero-variance fits are counted. They are not silently redrawn or discarded; an incomplete interval is inconclusive.
- A technical failure remains in the assigned-agent table and is scored with the fixed denominator. Complete-case sensitivity is reported separately. A failure before baseline is marked explicitly; assigning a fixed baseline for an ITT calculation is a conservative analysis convention, not evidence that a baseline was observed.
- Two fixed model families are blocking factors, not a population sample of all models. Family-specific estimates are mandatory and no general claim over model families is permitted.

## Run gate

Before a confirmatory run, the gate must see concrete model provider and snapshot identifiers, tokenizer/runtime versions, prompts, task templates, baseline and endpoint banks, answer keys, tool and memory schemas, durable-policy checkpoint support, a real runner, a raw-response scorer, analysis code, an environment lock, and a registry receipt. Missing hashes, `latest` model labels, null item-bank fields, snapshot drift, state-hash mismatch, provider filtering, or privacy leakage fail closed. The old synthetic simulator remains a statistical dry-run and cannot satisfy this gate.
