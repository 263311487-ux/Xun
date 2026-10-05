# RRC-ACT Registration Field Mapping v1.2

This is a platform-neutral mapping prepared for an OSF registration or an AsPredicted submission. It is not an official copy of either platform's current form. Before submission, compare the live form labels and preserve the text below without changing the hypotheses or analysis after outcome inspection.

| Registration field | Frozen content | Evidence file |
|---|---|---|
| Title | Relation-Specific Feedback and Long-Horizon Self-Model Continuity in Persistent Language Agents | v1.1 protocol §1 |
| Research question | Does relation-specific feedback causally change persistent self-model continuity after task, token, latency, topic and sentiment matching? | v1.1 protocol §1 |
| Primary hypothesis | H1: the relation-specific arm has a higher adjusted composite than task-only interaction in B=1, C=0; H0: the contrast is zero or negative. | v1.1 protocol §1 |
| Design | Two fixed model families × A/B/C factorial design; 32 agents per family × cell; generic-praise is secondary. | v1.1 protocol §2 |
| Unit of analysis | Agent instance; repeated sessions are nested observations and are not independent units. | v1.1 protocol §2 |
| Primary outcome | Equal-weight mean of self-other attribution, goal consistency, contradiction resolution and post-unload strategy residue. | scoring spec v1.1 |
| Primary contrast | Relation-specific A=1 versus task-only A=0, restricted to persistent provenance B=1 and intact self-model C=0, adjusted for family and baseline. | v1.1 protocol §9 |
| Minimum meaningful effect | Standardized adjusted difference d=0.50; two-sided alpha 0.05. | v1.1 protocol §§1,10 |
| Sample and power | Main cohort N=512; specificity cohort N=64; 64 agents per primary A arm; conservative planning power approximately 0.807. | power calculation v1.1 |
| Randomization | Deterministic blocked assignment from the complete v1.2 artifact map, then independent opaque run-order permutation. | execution amendment v1.2 |
| Blinding | Scorers masked to A/B/C and family; secondary human raters masked; allocation key retained by the runner/auditor. | v1.1 protocol §7 |
| Missing and exclusions | One same-state retry; then fixed-denominator zero and missingness flag; no outcome-based replacement; technical failures remain reported. | v1.1 protocol §11; amendment §Analysis |
| Stopping | Model drift, leakage, safety/privacy incident, repeated technical invalidity above threshold, or predeclared compute limit; no efficacy interim looks. | v1.1 protocol §12 |
| Confirmatory analysis | Fixed-family ANCOVA, within-family A permutation test, stratified agent bootstrap, raw and standardized effect intervals, complete-case sensitivity. | v1.1 protocol §9; amendment §Analysis |
| Falsifiers | No positive primary contrast, negative MIE-excluding interval, disappearance under matched controls, failed lesion/provenance checks, or failure in both model families. | v1.1 protocol §13 |
| Data/code | Public code and hashes after registration; private credentials, mailbox content and provider secrets excluded. | amendment §Run gate |
| Registry receipt | Fill only after a real OSF/AsPredicted record exists: URL/DOI, UTC timestamp, external lock SHA-256. | execution spec §registration |

## Submission order

1. Complete the artifact map and run the preflight gate.
2. Generate a new freeze bundle; never overwrite an existing lock.
3. Deposit the complete bundle and external timestamp before any confirmatory response is inspected.
4. Copy the registry URL/identifier and external lock SHA-256 into the registration receipt. Keep the local v1.1 RFC 3161 evidence as supplementary provenance.
5. Only then enable a separately audited real runner. A failed gate is a preparation result, not a scientific null result.
