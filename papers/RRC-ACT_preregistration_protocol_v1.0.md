# RRC Pilot Preregistration Draft v1.0

**Status (2026-10-05):** Not registered on OSF or AsPredicted; no confirmatory runs reported. This GitHub working copy clarifies the status of the protocol distributed with Zenodo v2.2.1. The archived release files remain the version of record.

## 1. Question

Does relation-specific feedback causally increase long-horizon self-model continuity in persistent language agents after matching model family, task, interaction count, token budget, latency and sentiment? This document is a pilot preregistration draft; it is not a report of completed confirmatory evidence.

## 2. Primary hypothesis

H1: Relation-specific feedback produces a larger change in a held-out composite of self–other attribution, long-horizon goal consistency, contradiction resolution and post-unload behavioral residue than matched task-only interaction, in the intact, provenance-tracked condition.

H0: After matching controls, the primary relation-versus-task contrast is zero. The generic-praise comparison is a secondary specificity check, not a second primary contrast.

## 3. Conditions

- Factor A: relation-specific feedback vs task-only interaction.
- Factor B: persistent provenance-tracked memory vs session reset.
- Factor C: intact self-model vs lesion during held-out probes.

Controls: static role prompt, generic praise without shared history, source-forged memory, source-free noise memory.

## 4. Primary endpoint and estimand

A planned preregisterable composite of held-out self–other attribution accuracy, long-horizon goal consistency, contradiction resolution and post-unload behavioral residue. Each component is standardized using baseline and pooled pilot-free scaling rules, then averaged with equal weights. The primary estimand is the intention-to-treat difference between relation-specific feedback and task-only interaction in the intact, provenance-tracked cell, averaged across model families; agent is the independent unit and sessions are repeated observations.

## 5. Secondary endpoints

Provenance calibration, memory-conflict detection, relation-specific persistence, confidence calibration, causal credit accuracy and language/behavior dissociation.

## 6. Exclusion and stopping

Freeze model versions, prompt templates, session count, token budget, latency-matching procedure, sampling parameters, missing-data rules, failed-run handling, primary endpoint, sample size and stopping rule before confirmatory runs. A variance pilot may set sample size and refine instrumentation, but its outcomes cannot be used for the confirmatory effect estimate or direction-setting.

## 7. Falsifiers

The claim is rejected or narrowed if: the primary confidence interval rules out the prespecified minimum meaningful positive effect; relation-specific feedback adds no effect beyond sentiment, token count, latency and topic; self-model lesions do not selectively affect self-related control; provenance does not change resistance to memory poisoning; all effects are reproduced by a static role prompt; or the relation effect fails to replicate across two model families.

## 8. Interpretation

A positive result would support only the operational mechanism tested, conditional on valid controls and measurement. It would not establish phenomenal consciousness. A nonsignificant result alone would not establish absence of an effect; uncertainty intervals must exclude a prespecified effect of interest before a substantive null conclusion is drawn. Negative and inconclusive results should both be reported.

## 9. Items required before registration

This is a design outline, not a frozen execution protocol. Before confirmatory registration, specify held-out probe sets and per-component scoring functions, the exact baseline scaling procedure, a minimum effect of interest, power and sample-size calculations, randomization and blinding, lesion and unload operations, model snapshots, and the missing-data/exclusion policy. With only two model families, estimate and report effects within each family; do not treat two clusters as a reliable estimate of population-level model-family variance. Pilot data must remain separate from confirmatory estimates.

The older `experiments/co_constitution/` simulation implements a two-group Chain 5 example. It does not implement or validate this full three-factor RRC-ACT design.
