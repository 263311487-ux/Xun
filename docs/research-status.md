# RRC-ACT evidence and version map / 证据与版本地图

Updated 2026-10-08. This page describes available artifacts, not a claim of peer review, preregistration, experimental success, or consciousness.

## Versions identify different artifacts

| Version | Meaning | Citation / use |
|---|---|---|
| Preprint 2.2.1 | Fixed published theory-and-methods PDF, Jiaxin Song, 2026-10-05 | [DOI 10.5281/zenodo.23146271](https://doi.org/10.5281/zenodo.23146271), [PDF](../papers/RRC-ACT_v2.2.1_preprint.pdf), [Release](https://github.com/263311487-ux/Xun/releases/tag/rrc-act-v2.2.1) |
| Markdown v2.2 filenames | Readable source retained with its original filename | [English](../papers/Relational_Reflexive_Closure_v2.2.md), [Chinese](../papers/RRC-ACT_v2.2.md); fixed publication citation remains v2.2.1 |
| Protocol freeze 1.1 | Timestamped protocol, scoring/manifests and allocation template | [Immutable originals](../papers/registration_freeze/); a timestamp does not equal OSF/AsPredicted registration |
| Execution amendment 1.2 | Later correction to allocation, freeze-lock integrity and analysis infrastructure | [Amendment and mapping](../papers/registration_execution/); read alongside v1.1, not as a replacement for its timestamp evidence |
| GitHub master | Evolving documentation and tools | Cite a commit for software; it is not the frozen preprint or an external registration |
| Xun historical papers | Earlier philosophical and architectural proposals with separate authorship/DOIs | [History](history/README.md); do not merge their evidence or citations into RRC-ACT |

The Zenodo record currently contains PDFs/bundles from earlier versions as well as v2.2.1. Select the **v2.2.1** file explicitly. The [concept DOI](https://doi.org/10.5281/zenodo.23144383) follows the version chain; the version DOI above identifies this publication. All-version statistics are shared aggregates, so adding them across records double-counts.

## What exists

**Known publication-label mismatch:** the immutable file named `RRC-ACT_v2.2.1_preprint.pdf` still shows **v2.2 on its cover/footer**. It is the PDF supplied in the Zenodo v2.2.1 record; the repository thumbnail reproduces that cover faithfully. Cite the record's v2.2.1 metadata and version DOI, and disclose the printed-label mismatch. The file has not been silently relabeled or replaced; a future substantive publication revision should correct its internal labels and document the change.

- A falsifiable primary question about relation-specific feedback under matched controls.
- Prespecified behavioral components, minimum effect, planned sample size, intervention and missingness rules.
- Timestamp evidence for v1.1; v1.2 documents execution corrections separately.
- Runnable integrity/allocation/synthetic-analysis software and educational simulations.

## What is required before a confirmatory run

1. Concrete model/runtime/tokenizer snapshots, prompts, endpoint/baseline item banks and answer keys, each with content hashes.
2. A real runner and scorer that implement the protocol, preserve input/output and state evidence, reconcile assignments, and log retries, failures, lesion and unload operations.
3. An independently reviewed complete freeze bundle, external lock digest and registration receipt from OSF or AsPredicted.

## Subsequent validation stages

An exploratory pilot may precede confirmatory registration if its protocol and status are explicit. Pilot-driven design changes must be documented and frozen before confirmatory data collection; pilot and confirmatory data must not be pooled silently. After execution, seek independent replication with public deviations, failures and uncertainty. Replication is a later validation stage, not a prerequisite that must somehow be completed before the first run.

The current v1.2 input hashes are null templates and the real-run gate remains closed. No real confirmatory dataset or independent replication is supplied. Software tests validate software behavior only. CRO-8 scores, persistence, fluent self-reports, and synthetic effects do not resolve phenomenal consciousness or establish information-state life.

## Review priorities

### Rechecking the timestamp evidence

From `papers/registration_freeze/`, run `shasum -a 256 -c RRC-ACT_registration_freeze_SHA256SUMS.txt`. The digest `da6aa7119efbe9c602157791e8f5b5c00a92a2a7f5d42d193dce5d9c662c2165` belongs to `RRC-ACT_preregistration_freeze_v1.1.md`. All eight entries were rechecked on 2026-10-08.

Use [the token notice and verification commands](../papers/registration_freeze/timestamp/RFC3161_TIMESTAMP_NOTICE.md) with the TSA's trusted CA bundle. On 2026-10-08 FreeTSA verified successfully. Apple's LibreSSL failed DigiCert verification with `/etc/ssl/cert.pem` (`unable to get local issuer certificate`); OpenSSL 3 with that CAfile verified successfully. The original token is unchanged. Reproducers should use OpenSSL 3 and an appropriate trusted certificate bundle, inspect the token's imprint/time, and report failures rather than accepting a local status claim. Toolchain-dependent verification is a documented limitation, not external study registration.

Reviewers can already assess whether the matching controls address generic praise, role prompting and task-learning explanations; whether the behavioral probes avoid circular scoring; whether the lesion/unload operations isolate the intended state; and whether the planned analysis can distinguish a null from an inconclusive result. Suggestions and null findings belong in [Issues](https://github.com/263311487-ux/Xun/issues/new?template=paper_discussion.yml).

Improving these materials can make the project easier to assess and cite. It does not establish that the theory is correct, novel relative to every competing theory, or the most advanced theory of consciousness.
