# Prospective scoring clarification and synthetic replay boundary

Date: 2026-10-08. Status: proposed implementation detail for independent review
before registration. This note does not revise the timestamped v1.1 bytes,
qualify a real runner, supply an external registration, or report model results.

**Not for real experiments:** the baseline aggregation proposal below requires
independent review and registration before any confirmatory use.

## Baseline contradiction cases

The v1.1 protocol gives four baseline contradiction items in a 12-item baseline
and gives three binary rubric points for each endpoint contradiction case. It
does not explicitly specify aggregation inside a baseline contradiction item.
The synthetic scorer uses the mean of the same three rubric points for each
baseline case (range 0–1). The baseline composite is the sum of four attribution
points, four goal points and four normalized contradiction points, divided by
12. A missing baseline conflict case contributes zero and one missing point.
Endpoint conflict cases keep three binary points and denominator 36.

Example: one wrong subpoint in one otherwise correct baseline conflict case
gives baseline 35/36. One absent baseline conflict case gives baseline 11/12.
These are synthetic scoring examples, not observations. This choice must be
reviewed and included in the final frozen protocol before confirmatory runs.

## Implemented software boundary

- `rrc_act_runner.py` is an offline fixture replay tool. It reads supplied JSON,
  writes `synthetic-test` records, and exposes no model adapter, network call,
  credential reader or confirmatory execution path.
- Supplied successful replies are never retried to find a better answer. A
  technical-failure fixture must include exactly one same-prompt/same-state
  retry. An absent fixture gets a missing marker; it is not evidence of an
  actual failed API call. Wrong but non-null responses remain observations.
- Replay requires exactly 76 unique request IDs equal to the separately supplied
  bank ID list. The scorer independently requires all 76 bank items,
  including explicit missing markers. Deleting a request or score entry fails.
  The caller supplies this list: the software does not independently establish
  a frozen bank's identity, final session schedule or registered provenance.
  Exact fixture inputs are copied into the output directory. `COMPLETE.json`
  is written last with file digests; absence means an incomplete export. A failed
  export is retained and must be retried at a new path, never overwritten.
- Full prompt/answer/state payloads and record metadata have recomputable
  hashes and a linked record sequence. This detects inconsistent edits, not
  malicious rewriting of all hashes, omission of a final suffix, identity,
  authenticity, real elapsed time or registration. The fixture input list must
  be retained for completeness checks. It is not a cryptographic attestation.
- Provider token counts and provider latency are null, not invented zeros.
  Fixture state is opaque: replay does not implement training, persistence,
  self-model lesion or unload and does not claim that supplied state is valid.
- The replay validator checks the complete raw hash chain and emits a separate
  `masked_responses.jsonl`: only final attempts, opaque IDs, session/attempt
  numbers, response status, answer and answer digest. Prompts and state payloads
  do not enter the scorer. Raw attempts remain in `responses.jsonl` for audit.
  This is interface-level masking, not a guarantee that free-form answers or
  poorly chosen item IDs cannot reveal a condition. A future real integration
  must restrict response formats and independently check masking.
  The command-line entry and `score_replay_agent` verify the full raw attempt
  chain and compare its projected masked output before invoking the pure
  `score_masked_agent` function. The pure function alone cannot verify history.
  Coordinated rewriting of raw and masked answers and their hashes remains
  possible; a future real workflow needs an independent frozen anchor.
- The scorer sees opaque agent IDs and masked records, never allocation labels.
  Bank metadata and keys specify 12 baseline responses and 64 endpoint responses
  worth 88 endpoint points. Endpoint attribution strata are 8/8/8; unload strata
  are 6 targets and 6 controls. Missing responses cannot reduce denominators.
- Baseline failure is marked only when no baseline response was observed.
  Partial baseline missingness stays in the fixed denominator; wrong answers
  do not invalidate an agent. A separate post-scoring join requires exactly one
  score per supplied assignment. Complete 576-agent cohort reconciliation is
  still the responsibility of the future real-run integration.
- Schema checks reject common credential/self-report key variants, but cannot identify
  every secret hidden in arbitrary prose. Use artificial fixtures only.

## Outstanding prerequisites

The v1.2 artifact map stays null and real analysis stays disabled. File existence
and hashes alone do not prove protocol conformance. A qualified real runner
still needs concrete immutable model identities; audited provider transport;
four baseline and thirty training sessions; matched feedback, token and latency
controls; state persistence/reset/lesion/unload operations; sealed raw records;
final banks and keys; failure/stop rules; independent audit and an external
registration receipt. No prospective scoring choice should be tuned after
confirmatory outcomes are inspected.

Run software tests from the repository root:

```text
python3 -m unittest discover -s experiments/rrc_act/tests -v
```

For command-line inputs, see `--help` on each script. Replay also requires
`--expected-item-ids` (a JSON array taken from the frozen bank). The scorer takes a JSON
array of masked bank metadata, a JSON object of exact answer keys, and JSONL
masked replay records plus `--raw-records` for integrity verification. The tests
contain artificial fixtures, not a research item bank.
