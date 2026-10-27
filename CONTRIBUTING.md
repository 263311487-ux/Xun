# Contributing to Xun / RRC-ACT

RRC-ACT is a theory-and-methods preprint with accompanying experimental infrastructure. Contributions fall into three categories.

## 1. Paper review and method critique

The most valuable contribution. Open an [issue using the paper discussion template](https://github.com/263311487-ux/Xun/issues/new?template=paper_discussion.yml) and:

- Point to a specific claim in the paper (section + quote)
- Provide an alternative explanation
- If possible, describe an experiment that would distinguish the two

Critique of the matching controls, behavioral probes, or analysis plan is especially welcome.

## 2. Replication reports

If you run the experimental tools (or an independent implementation) and obtain results:

- Use the [replication report template](https://github.com/263311487-ux/Xun/issues/new?template=replication_report.yml)
- State clearly whether you used real model snapshots or synthetic replay
- Include software version, run date, and any deviations from the protocol
- Negative results are equally welcome

## 3. Software contributions

The experiment tooling in `experiments/rrc_act/` and tutorials in `tutorials/` accept PRs:

```bash
git clone https://github.com/263311487-ux/Xun.git
cd Xun
python3 -m unittest discover -s experiments/rrc_act/tests -v
python3 tutorials/run_all.py
```

Software contributions must not require a paid model API. They must not claim to produce real experimental data when running the synthetic replay infrastructure.

## Important: epistemic standards

This repository applies the same falsification standards described in the research to its own contributions. Before opening an issue asserting that "X proves Y", check:
- Is the claim falsifiable?
- Have you considered at least one alternative explanation?
- Is the evidence you're citing diagnostic (it distinguishes your claim from alternatives)?
