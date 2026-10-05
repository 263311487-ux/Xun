# Local integrity audit — RRC-ACT execution v1.2

Date: 2026-10-05 (Asia/Shanghai)

This is a local code-and-document audit. It is evidence about the implementation checks below; it is not a peer review, an OSF/AsPredicted registration, or evidence for artificial consciousness.

## Checks

- `python3 -m unittest discover -s experiments/rrc_act/tests -v` — 16 tests cover template fail-closed behavior, deterministic balanced allocation, opaque run-order permutation, freeze-lock immutability, copied-artifact tamper detection, missing copied-input rejection, credential/self-report rejection, fixed-denominator missingness, duplicate IDs, unknown families, stratified bootstrap, zero variance and confirmatory-mode blocking.
- `python3 -m compileall -q experiments` — syntax check.
- `python3 experiments/rrc_act/rrc_act_preflight.py prepare --repo .` — expected exit 2 because the execution map still has null hashes and missing concrete assets. This is the intended gate state.
- `git diff --check` — whitespace check.
- The three v1.1 JSON manifests are tracked explicitly despite the repository's private-data `*.json` ignore rule; their bytes match the v1.1 SHA-256 list.
- The v1.1 protocol and RFC 3161 timestamp evidence were not edited by this amendment.

## Findings fixed in v1.2

1. Assignment generation is now non-circular and its seed includes the complete upstream artifact map.
2. Public row order no longer doubles as the blinded run order; the new generator independently permutes run order.
3. Bootstrap resampling is stratified by fixed model family and A arm.
4. Raw score-point intervals and standardized `d` intervals are kept separate.
5. A freeze bundle copies and re-hashes every upstream input, and refuses to overwrite an existing destination.

## Remaining blockers

No concrete model snapshots, item banks, answer keys, real runner, raw-response scorer, registry receipt, or confirmatory dataset exists in this repository. The old Chain ⑤ simulator remains synthetic and cannot pass the real-data gate.
