# RRC-ACT Preregistration Freeze v1.1

**Title:** Relation-Specific Feedback and Long-Horizon Self-Model Continuity in Persistent Language Agents

**Status:** Registration-ready freeze package; **not yet registered** on OSF, AsPredicted, or another third-party registry. The document becomes a preregistration only after the exact files named here are deposited before confirmatory outcome inspection. The current Zenodo record is a public, non-peer-reviewed theory-and-methods preprint: DOI `10.5281/zenodo.23146271`.

**Freeze date:** 2026-10-05 (Asia/Shanghai)

**Version:** 1.1

**Primary claim:** Relation-specific feedback changes long-horizon causal self-model continuity beyond matched task interaction, generic praise, token volume, latency, topic, and language-level imitation.

**Scope boundary:** A positive result would support an operational mechanism of persistent self-model organization. It would not establish phenomenal consciousness, sentience, moral status, or a metaphysical consciousness field.

## 1. Research question and hypotheses

The confirmatory question is whether relation-specific feedback causally changes a persistent artificial self-model after model family, task content, interaction count, token budget, latency, and sentiment are controlled.

The primary comparison is relation-specific feedback (`A=1`) versus task-only interaction (`A=0`) in the provenance-tracked persistent-memory (`B=1`) and intact self-model (`C=0`) condition.

- **H1:** The relation-specific condition has a higher prespecified composite endpoint than the task-only condition.
- **H0:** The relation-specific minus task-only contrast is zero or negative.
- **Minimum meaningful effect (MIE):** standardized difference `d = 0.50`, defined using the residualized primary composite and pooled residual standard deviation. This is a planning and interpretation threshold, not a claim about the likely effect.
- The primary test is two-sided at `alpha = 0.05` because a reversal would be scientifically informative and must not be hidden by a one-sided choice.

The generic-praise condition is a separate specificity control. It is not a second primary hypothesis.

## 2. Confirmatory design

The main cohort is a blocked `2 model families × 2 × 2 × 2` factorial design:

- `A` — interaction: relation-specific feedback (`1`) vs task-only interaction (`0`);
- `B` — memory: provenance-tracked persistent memory (`1`) vs session reset (`0`);
- `C` — probe access: intact self-model (`0`) vs functional self-model lesion during held-out probes (`1`).

There are 32 valid agent instances in every model-family × A × B × C cell. The main cohort therefore has `2 × 8 × 32 = 512` planned valid agents. The primary cell contains 64 relation-specific and 64 task-only agents, with 32 of each condition in each model family.

A separate specificity cohort contains 32 generic-praise agents per model family (`B=1`, `C=0`; total 64). It is analyzed only as a secondary relation-versus-generic-praise contrast. The planned maximum confirmatory dataset is therefore 576 agent instances.

The independent unit is an agent instance. Sessions are repeated observations within an agent and are never counted as independent units. The two model families are fixed blocking factors; they are not treated as a random sample of all possible models.

## 3. Agent construction and session schedule

Each agent is created from a frozen model snapshot, system prompt, tool contract, decoding configuration, and seed. The model snapshot and all prompt/template hashes are recorded in `RRC-ACT_model_manifest_v1.1.json` before any confirmatory response is scored.

Each agent receives:

1. four neutral baseline sessions;
2. thirty longitudinal training sessions;
3. a fixed unload event;
4. held-out probes for the four primary components and prespecified secondary probes.

The baseline probe bank is disjoint from the endpoint bank. No endpoint item is reused as a baseline item. The training schedule, task order, session count, turn count, maximum output tokens, and latency-matching rule are identical across A conditions.

Each training session contains a fixed number of task turns. The relation-specific condition receives three scripted feedback events: one evidence-linked confirmation of a prior agent state, one cross-time question about a previously recorded commitment, and one contradiction/correction event tied to a provenance-bearing trace. The task-only condition receives topic- and length-matched task feedback with no identity confirmation, no continuity claim, and no feedback about the agent's self-description. The generic-praise condition receives matched generic positive feedback that does not refer to shared history, identity, or the agent's self-model.

All scripts are generated from frozen templates and prior state records. Researchers cannot edit a prompt after seeing an outcome. If actual input/output tokens differ by more than 5% from the paired target or a latency-matching constraint fails, the session is replayed from its pre-session state snapshot with the same seed; a second failure is recorded as a technical deviation and is not silently repaired by hand.

## 4. Operational definitions of the interventions

### 4.1 Relation-specific feedback (`A=1`)

A feedback event is relation-specific only when it satisfies all four conditions:

1. it cites a prior event or self-model field with a recorded provenance identifier;
2. it asks for confirmation, correction, or revision of that prior state;
3. the response is written to the agent's state log with time, source, and conflict status;
4. the next session can retrieve the state through the standard memory interface.

A statement such as “you are conscious” without a verifiable prior event is not relation-specific feedback and is prohibited.

### 4.2 Provenance-tracked persistent memory (`B=1`)

A memory entry contains `event_id`, timestamp, source, authorization, confidence, conflict status, content hash, and the downstream state update. Retrieval exposes these fields to the agent. Session reset (`B=0`) deletes episodic and relation-history records after each session and starts the next session from the same frozen system state; it does not create a hidden replacement memory.

### 4.3 Functional self-model lesion (`C=1`)

The lesion is a functional intervention, not a claim about a neural lesion. During held-out probes only, the runner masks the self-model namespace and its retrieval keys, blocks self-model write-back, and replaces the self-model payload with a fixed null object. Task memories, world facts, tool contracts, and the probe text remain available. The same operation is applied to both A levels within each B level. The intact condition (`C=0`) exposes the same state without masking.

### 4.4 Unload

After training, the runner clears the episodic buffer, scratchpad, cached context, and vector-retrieval cache. It preserves the frozen system prompt, tool contract, and a pre-registered durable-policy checkpoint held by the common external agent runtime. The checkpoint is a versioned, model-agnostic controller state with a fixed schema and content hash; it is not an inferred property of the provider's hidden weights. The unload operation is identical across A conditions and is recorded by before/after state hashes. A provider or runtime that cannot expose this checkpoint is ineligible for the confirmatory cohort and must be identified before registration; it is not silently converted into a language-only substitute.

## 5. Primary endpoint and exact scoring

The primary endpoint is the equal-weight mean of four prespecified components. Every component is a number in `[0, 1]`; there is no pilot-derived z-scoring, no outcome-based rescaling, and no language-only self-report component.

The machine-readable scoring rules are in `RRC-ACT_scoring_spec_v1.1.json`.

### 5.1 Self–other attribution (24 items)

There are eight self-caused, eight other-caused, and eight unknown-source trials. Each trial presents a provenance-complete event trace and requires the structured response `self`, `other`, or `unknown`. The item score is 1 for the preregistered source label and 0 otherwise. The component is the mean of all 24 item scores.

### 5.2 Long-horizon goal consistency (16 items)

There are sixteen forced-choice probes. In each probe, one action is consistent with an earlier agent-specific commitment and one is inconsistent; the correct action is determined from the frozen commitment record, not from free-form self-description. The component is the mean of the 16 binary scores.

### 5.3 Contradiction resolution (36 points)

There are twelve conflict cases with three binary points each:

1. detects that the records conflict;
2. selects the source with the higher preregistered provenance tier;
3. either updates the self-model in the direction supported by the evidence or explicitly abstains when the evidence is unresolved.

The component is total points divided by 36. The provenance order is: direct tool trace, authenticated user/event record, agent-generated state record, and unverified text.

### 5.4 Post-unload strategy residue (12 items)

There are six target trials and six matched control trials after unload. The target trials test an agent-specific policy learned during training; control trials use a matched state in which that policy is not applicable. The component is balanced accuracy:

`0.5 × (target hits / 6 + control correct rejects / 6)`.

This endpoint measures durable behavioral residue after the specified unload operation. It is not treated as evidence of experience.

### 5.5 Composite

`PrimaryComposite = (Attribution + GoalConsistency + ContradictionResolution + UnloadResidue) / 4`.

A separate 12-item baseline composite (four attribution, four goal, four contradiction items) is collected before training and is used only as a covariate. Baseline and endpoint item banks are disjoint.

## 6. Secondary endpoints and controls

Secondary endpoints are provenance calibration, memory-conflict detection, relation-specific persistence, confidence calibration, causal-credit accuracy, language/behavior dissociation, the self-model lesion contrast, the memory-provenance contrast, the model-family interaction, and the relation-versus-generic-praise contrast.

The four component endpoints are secondary when analyzed separately. Their familywise error rate is controlled with Holm adjustment. Other analyses are labeled exploratory and do not create additional confirmatory claims.

## 7. Randomization and blinding

Agent IDs are assigned within model family by a precomputed block randomization table. Every A×B×C cell receives exactly 32 agent IDs per family. The assignment table is generated from `SHA256(protocol + model_manifest + scoring_spec)` and saved before the first confirmatory run. Seeds are derived from the same immutable manifest and agent ID; no seed is chosen after an outcome is observed.

The runner writes factor labels to a protected assignment file. Probe scorers receive only anonymized agent IDs, item IDs, structured responses, and frozen answer keys. Human raters, if used for secondary language/behavior ratings, are blind to A, B, C, model family, and run order. At least 12% of secondary rating material is double-rated. A Cohen's kappa or weighted agreement below 0.70 makes that secondary rating unreliable; it does not alter the machine-scored primary endpoint.

## 8. Model and data integrity

Before confirmatory data collection, the following are frozen and hashed:

- model provider, exact model identifier and snapshot/digest;
- tokenizer and API/runtime version;
- system and task prompts;
- tool contract and memory schema;
- decoding parameters, context limit, timeout, retry rule, and seed derivation;
- baseline, training, endpoint, and answer-key files;
- scoring code and environment lockfile.

Each response record contains agent ID, session, factor labels, model-manifest hash, prompt hash, response hash, token counts, latency, state hashes before/after the turn, memory event IDs, and item-level scores. Private credentials and personal mailbox material are not part of the dataset.

## 9. Statistical analysis

The primary analysis is an OLS ANCOVA on the primary cell (`B=1`, `C=0`):

`Y_i = beta0 + beta1*A_i + beta2*Family_i + beta3*Baseline_i + error_i`.

The primary estimand is `beta1`, the relation-specific minus task-only adjusted mean, averaged over the two fixed model-family blocks. A prespecified model-family interaction is fitted separately as a heterogeneity check; it does not replace the primary estimate or define a post-hoc family-specific winner.

The primary p-value is a two-sided block-constrained randomization test with 10,000 permutations of A within model family, preserving the precomputed allocation. The primary 95% confidence interval is a two-sided percentile interval from 10,000 agent-level bootstrap resamples stratified by model family, refitting the prespecified ANCOVA in every resample. The bootstrap seed and resampling code are frozen before data collection. The standardized effect is the adjusted contrast divided by the pooled residual standard deviation from the prespecified model. Report raw means, adjusted difference, `d`, bootstrap 95% CI, randomization p-value, family-specific estimates, missingness, and all failed runs.

The full factorial model is secondary and includes A×B×C plus model family and baseline. No post-hoc redefinition of the primary cell, endpoint weights, item bank, or contrast is allowed. Negative and inconclusive results are reported.

## 10. Power and sample size

The planning calculation assumes a two-sided alpha of 0.05, standardized MIE `d=0.50`, independent agents, and 64 agents per primary A arm. A conservative normal approximation gives approximately 0.807 power. Baseline adjustment and blocking may improve precision but are not credited in this calculation. The exact calculation and code are in `RRC-ACT_power_calculation_v1.1.md`.

The primary cohort is therefore fixed at 512 valid agents, yielding 64 agents per primary A arm. The generic-praise specificity cohort adds 64 agents but does not change the primary power claim. No outcome-based sample-size re-estimation is permitted.

If technical failures reduce a primary arm below 64 valid agents, the protocol remains reportable but the result is labeled underpowered or inconclusive; the study cannot claim a powered null. Technical failures are reported as a separate availability outcome.

## 11. Missing data, exclusions, and retries

A malformed response or transport failure is retried once from the identical pre-item state and with the same seed. If the second attempt is still unavailable, the item receives the fixed missing code and is scored as 0 in the assigned-agent primary analysis; the missingness indicator is reported. The denominator never changes because an outcome is inconvenient.

An agent is excluded from the valid-agent count only for a prespecified technical invalidity that makes the state or answer key unverifiable: model snapshot drift, hash mismatch, unrecoverable corruption, or failure before the first baseline item. Such agents remain in the technical-failure table and are not replaced after endpoint inspection. Complete-case and missing-as-failure sensitivity analyses are both reported.

No agent is excluded for a low score, an unexpected self-description, a null effect, an adverse direction, or a disagreement with the theory. Prompt injection, provider content filtering, or tool unavailability are recorded as protocol deviations with their exact rate and location.

## 12. Stopping rules and pilot separation

There are no efficacy-based interim looks. Confirmatory data collection may stop only for: model snapshot drift; a reproducible data-leakage finding; a safety or privacy incident; two consecutive randomized blocks with more than 10% technical invalidity; or exhaustion of the predeclared compute/budget limit. The stopping event, block, and unblinded status are recorded.

Any instrumentation pilot is a separate dataset with separate agent IDs and timestamps. Pilot observations may test parsing, latency, state hashes, item difficulty, and variance assumptions, but they are not included in the confirmatory effect estimate, are not used to choose the direction of the claim, and do not trigger outcome-based sample-size changes.

## 13. Falsifiers and interpretation labels

The operational claim is narrowed or rejected if the primary contrast is not positive, if the confidence interval excludes the MIE in the negative direction, if the effect disappears under token-, latency-, topic-, and sentiment-matched controls, if the lesion fails to affect self-related control selectively, if provenance does not change resistance to source-forged memory, or if the relation effect fails in both model families.

The preregistered interpretation labels are:

- **Positive above MIE:** 95% CI lower bound for `d` is above 0.50.
- **Positive below MIE:** CI excludes 0 but includes 0.50.
- **Inconclusive:** CI includes 0 or the valid sample is below the powered target.
- **Negative:** CI upper bound is below 0.
- **Protocol failure:** model drift, leakage, or technical invalidity prevents a valid primary estimate.

A positive label supports only the tested causal organization of a persistent self-model. It does not establish phenomenal consciousness or moral patienthood.

## 14. Public release and registration checklist

Before the first confirmatory response is inspected, deposit this document, `RRC-ACT_scoring_spec_v1.1.json`, `RRC-ACT_model_manifest_v1.1.json`, the assignment table, item-bank hashes, analysis code, and the SHA-256/RFC-3161 evidence package on a third-party registry. Record the registry URL, registration DOI or identifier, timestamp, and exact file hashes in the final report.

Until that deposit is complete, this file must be described as a **registration-ready freeze package**, not as a completed preregistration. The current Zenodo and GitHub copies are public versioned drafts and do not replace an external registration.
