# Offline replay/scorer review · 2026-10-08

Scope: publish synthetic software tools for review, not approve a real experiment.
No model calls or real response collection were performed. The published
preprint and timestamped v1.1 files remain unchanged.

## Verification

- 21 new replay/scoring tests, including command-line replay → masked export →
  scoring, rejection of confirmatory mode, fixed denominators, partial scores,
  complete bank coverage, retries, missingness, overwrite prevention, payload
  and metadata edits, cross-agent rows, and assignment join validation.
- The existing 16 execution tests and 7 metrics tests also pass locally.
- All eight v1.1 stored file hashes match; the real preparation gate still
  exits 2 on null artifact hashes. None were filled merely to pass the gate.

## External model reviews and local adjudication

The official audit router was used three times, with separate independent reviews
and a separate judge. These are model-assisted code reviews, not human peer
review, scientific validation, or proof of evaluator independence.

First run: `audit_20261008_164614`. Only Gemini returned a substantive review;
the Astra endpoint reset and the Claude endpoint lacked a usable response. The
judge gave conditional approval. Its actionable completeness finding was
reproduced with a failing test and fixed: exactly 76 unique requested IDs must
match the separately supplied bank IDs, and the scorer requires explicit rows
for the full bank, including missing markers.

Second run: `audit_20261008_165353`. Astra and Gemini returned substantive
reviews; Claude failed. The judge returned **not approved**, combining retry
history/projection concerns and frozen-bank/real-experiment limitations. This
verdict is preserved; the dispositions below are local verification, not a
claim that the external judge approved the revision. Findings and dispositions:

| Finding | Disposition |
|---|---|
| Real collection, frozen model/bank identity and registration are unverified | Agreed; real execution remains disabled and is not approved by this publication |
| Caller can replace a bank and keys together | Agreed; these offline tools validate format/scoring, not an independent frozen-bank anchor |
| Masked response hashes do not authenticate retry history or provenance | Agreed; raw validation precedes projection, full raw attempts are retained, and the scorer alone cannot certify provenance |
| Prompt/state data might reveal condition | A separate masked output removes both before scoring; arbitrary answer prose and bad IDs still need a future independent masking review |
| Interrupted writes can leave partial directories | Exact fixture inputs are retained; COMPLETE.json is written last with file hashes; incomplete directories are not valid exports and are never overwritten |
| Hashes are not signatures/time attestations | Agreed and explicitly documented; no claim of tamper-proof real evidence |
| A second technical failure is rejected as “missing” | The proposed relaxation is not adopted: “missing” means no fixture existed. A second call failure must be technical_failure; tests cover both failures and rejection of the invalid mixed sequence |
| Baseline conflict scoring has an unstated aggregation detail | Separate prospective clarification proposes mean of three subpoints per one baseline point; immutable v1.1 remains untouched |
| The supplied assignment subset need not have 576 rows | Agreed; join checks one-to-one correspondence only, not complete confirmatory cohort qualification |
| JSON Boolean and CSV-style string synthetic flags differ | Intentional serialization boundary, tested explicitly; neither form accepts real data in these tools |

The review identifies unresolved prerequisites for a real study. Publication
of this synthetic reference implementation does not resolve those prerequisites
or convert model review into scientific evidence.

## Final scoped review and regression fixes

Third run: `audit_20261008_170042`. All three independent endpoints and the
separate judge returned. The judge gave **conditional approval limited to
offline synthetic developer tools**, requiring reproduction/fix of a reported
state-equality bug and verification of isolated findings. This does not replace
the earlier not-approved real-use assessment.

- Reproduced: Python treats `True` and `1` as equal inside dictionaries, but
  these are distinct JSON states. State continuity and failed-turn immutability
  now compare verified canonical hashes. Regression test failed before the fix.
- Reproduced: the raw validator accepted session -1; it now rejects negative
  sessions even with internally recomputed hashes. Regression test failed first.
- Reproduced: numeric JSON factors were rejected at the CSV-oriented assignment
  join. It now accepts valid integer or string factors and emits string columns.
- Reproduced: a non-string bank phase could raise TypeError. Explicit type
  validation now raises ScorerError; malformed data does not acquire a score.
- Verified: nonfinite payloads are already rejected by finite JSON encoding;
  an added test confirms no output directory is created for NaN.
- CLI input reads now specify UTF-8; hash self-exclusion is documented to avoid
  circularity. The prospective baseline-rule warning is explicit.
- CLI scoring now verifies original retry history and the exact masked
  projection before passing only masked data to the pure scoring function.
- Export writes to a temporary staging directory, reserves a new destination
  with exclusive creation, and moves COMPLETE.json last. An interrupted final
  transfer remains incomplete and cannot silently overwrite another run.

These fixes close the reproducible conditions for the explicitly limited
synthetic-tool publication. They do not enable real or confirmatory execution.
