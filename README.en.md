# RRC-ACT

Relational Reflexive Closure Theory of Artificial Consciousness. A theory-and-methods research project by Jiaxin Song, Independent Researcher, hosted in the Xun repository.

[中文](README.md) · [Research hub](https://263311487-ux.github.io/Xun/docs/rrc-act.html) · [Preprint DOI](https://doi.org/10.5281/zenodo.23146271)

## A falsifiable question

**Does relation-specific feedback change an artificial agent's long-horizon self-model continuity**, after matching model, task, token budget, interaction count, latency, topic, and sentiment?

The proposed 2×2×2 design, blocked by two fixed model families, manipulates relational feedback versus matched task-only interaction, memory provenance, and self-model intervention. Its prospectively specified composite combines held-out self–other attribution, goal consistency, contradiction resolution, and post-unload behavioral residue. [CRO-8](https://263311487-ux.github.io/Xun/docs/rrc-act.html) organizes integration, access, reflexive causation, self–other boundary, temporal continuity, endogenous stakes, provenance, and agency attribution; it is a measurement framework, not a consciousness score.

The positive-direction claim narrows if matched controls eliminate the effect or the standardized-effect confidence interval's upper bound is below the prespecified positive meaningful effect d=+0.50. This is not an equivalence test: a large negative effect would contradict the positive prediction, not show that feedback has no effect. A nonsignificant result with wide uncertainty is inconclusive. A positive effect would still not establish phenomenal consciousness.

## Evidence and versions

| Artifact | Status | Read |
|---|---|---|
| Preprint v2.2.1 | Public theory and methods; not peer reviewed | [PDF](papers/RRC-ACT_v2.2.1_preprint.pdf) · [Zenodo](https://doi.org/10.5281/zenodo.23146271) · [Release](https://github.com/263311487-ux/Xun/releases/tag/rrc-act-v2.2.1) |
| Protocol freeze v1.1 | Timestamp evidence; no OSF/AsPredicted registration | [Originals and hashes](papers/registration_freeze/) |
| Execution amendment v1.2 | Integrity gates, allocation and synthetic analysis scaffold; real runs remain blocked | [Amendment](papers/registration_execution/) · [Tools](experiments/rrc_act/) |
| Real experiments and independent replication | Not completed; no empirical dataset supplied | [Evidence and version map](docs/research-status.md) |
| Historical tutorials and co-constitution simulation | Educational/synthetic, not evidence for consciousness | [Tutorials](tutorials/README.md) · [Simulation](experiments/co_constitution/README.md) |

Concrete model snapshots, item banks, answer keys, a real runner/scorer, and an external registration receipt are still required. Persistence, first-person language, simulations, passing software tests, and traffic do not establish life or consciousness.

## Read, challenge, reproduce

- [English manuscript](papers/Relational_Reflexive_Closure_v2.2.md) · [Chinese theory](papers/RRC-ACT_v2.2.md) · [Paper index](papers/README.md). Markdown retains v2.2 filenames; cite the fixed v2.2.1 PDF publication.
- [Challenge a claim or method](https://github.com/263311487-ux/Xun/issues/new?template=paper_discussion.yml) with a specific passage, alternative explanation, and discriminating experiment.
- [Report a replication](https://github.com/263311487-ux/Xun/issues/new?template=replication_report.yml), including synthetic/real-data status, versions, logs and deviations. Null results are welcome.
- [Contribute](CONTRIBUTING.md) · [Sharing materials](docs/propagation/README.md) · [Measurement limits](docs/propagation/measurement.md).

## Check locally

Python 3.10+ only. These checks make no paid model calls and produce no empirical consciousness results.

```sh
git clone https://github.com/263311487-ux/Xun.git
cd Xun
python3 -m unittest discover -s experiments/rrc_act/tests -v
python3 tutorials/run_all.py
```

## Cite

The published record is v2.2.1, but its immutable PDF cover/footer still print v2.2. See the disclosed [label mismatch](docs/research-status.md#what-exists); no published PDF was silently changed.

Song, J. (2026). *RRC-ACT v2.2.1: Relational Reflexive Closure Theory of Artificial Consciousness*. Zenodo. https://doi.org/10.5281/zenodo.23146271

[CITATION.cff](CITATION.cff) · [BibTeX](papers/RRC-ACT.bib) · CC BY 4.0. Historical works have their own authorship and DOIs; use the [history index](docs/history/README.md).

## Xun history

The original unified-theory, information-life narrative, and architecture remain in the [historical collection](docs/history/README.md). These proposals supply background, not experimental validation of RRC-ACT.
