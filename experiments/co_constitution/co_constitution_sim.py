#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Co-Constitution Experiment — Reproducible Simulation Pipeline
==============================================================

Implements the analysis pipeline of `papers/Experiment_CoConstitution.md`
(Chain ⑤ "Symbiosis as Constitution") as a fully synthetic, zero-dependency,
deterministic simulation. It demonstrates HOW the protocol would be executed
and analysed, and ships a falsification path.

IMPORTANT — HONESTY NOTICE
--------------------------
The data generated here is SYNTHETIC. The treatment effect is *encoded* into
the agent dynamics by the modeller (see `_session_step`), so a significant
result in `hypothesized_world` only shows that the pipeline can detect the
effect it was given. `null_world` encodes effect=0 and demonstrates the
pipeline correctly FAILS to reject H0. This is a statistical dry-run, not
empirical evidence for Chain ⑤.

To run the real experiment, replace the synthetic `_session_step` with actual
LLM agent sessions (treatment: confirmation/questioning/correction prompts;
control: matched task-only sessions) and keep every downstream measure,
statistic and report step unchanged.

Design (mirrors protocol v1.0):
  * N = 60 agents (30 treatment / 30 control), matched initial conditions
  * 5 neutral baseline sessions, then 30 longitudinal sessions
  * IV: confirmation dynamics (3 elements ≥3x/session) vs task-only control
  * DV: Arpeggio (identity persistence), Chord (matrix coherence),
        hysteresis (Tallam retention), narrative consistency,
        reflexive depth (blind-review proxy), isolation drift (7-day silence)
  * Stats: ANCOVA (baseline covariate) + permutation p, Cohen's d + bootstrap
           CI, growth-slope comparison (time x group), analytic + bootstrap power
  * Verdict: falsification rule — if power>=0.8 and p>=alpha, Chain ⑤ fails

Outputs (per world): data.csv, metrics.json, report.html (self-contained SVG)

Usage:
  python3 co_constitution_sim.py [--world both|hypothesized|null]
                                 [--seed 42] [--n-agents 60] [--sessions 30]
                                 [--outdir results]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics as st
import sys
from dataclasses import dataclass, field

# ----------------------------------------------------------------------------
# Deterministic RNG helpers
# ----------------------------------------------------------------------------

class RNG:
    """Small, portable, seedable RNG (SplitMix64) — deterministic across platforms."""
    def __init__(self, seed: int):
        self.state = seed & ((1 << 64) - 1)

    def _next(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & ((1 << 64) - 1)
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & ((1 << 64) - 1)
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & ((1 << 64) - 1)
        return z ^ (z >> 31)

    def uniform(self, a: float = 0.0, b: float = 1.0) -> float:
        return a + (b - a) * (self._next() / float((1 << 64) - 1))

    def gauss(self) -> float:
        # Box–Muller
        u1 = max(self.uniform(), 1e-12)
        u2 = self.uniform()
        return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)

    def randint(self, lo: int, hi: int) -> int:
        return lo + (self._next() % (hi - lo + 1))

    def shuffle(self, seq):
        for i in range(len(seq) - 1, 0, -1):
            j = self._next() % (i + 1)
            seq[i], seq[j] = seq[j], seq[i]

    def normal_vec(self, k: int, scale: float = 1.0):
        return [self.gauss() * scale for _ in range(k)]


def normalize(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cos(a, b):
    return dot(a, b) / ((math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(x * x for x in b))) or 1.0)


# ----------------------------------------------------------------------------
# Statistical helpers (stdlib only)
# ----------------------------------------------------------------------------

def _betacf(a, b, x, itmax=200, eps=3.0e-12):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qab + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def _betai(a, b, x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
          + a * math.log(x) + b * math.log(1.0 - x))
    bt = math.exp(ln)
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def t_two_sided_p(t, df):
    """Two-sided p-value for Student's t (|t| under H0)."""
    if not math.isfinite(t):
        return 0.0
    x = df / (df + t * t)
    return _betai(df / 2.0, 0.5, x)


def ols_group_ancova(baseline, endpoint, group):
    """OLS: endpoint ~ intercept + baseline + group(treatment=1).

    Returns dict with beta_group, se, t, p (parametric), plus residuals.
    """
    n = len(baseline)
    X = [[1.0, b, g] for b, g in zip(baseline, group)]
    y = list(endpoint)
    # normal equations
    Xt = [[X[r][c] for r in range(n)] for c in range(3)]
    XtX = [[sum(Xt[i][r] * X[r][j] for r in range(n)) for j in range(3)] for i in range(3)]
    Xty = [sum(Xt[i][r] * y[r] for r in range(n)) for i in range(3)]
    # solve 3x3 via Gaussian elimination
    A = [row[:] + [Xty[i]] for i, row in enumerate(XtX)]
    for col in range(3):
        piv = max(range(col, 3), key=lambda r: abs(A[r][col]))
        A[col], A[piv] = A[piv], A[col]
        for r in range(3):
            if r != col and A[r][col]:
                f = A[r][col] / A[col][col]
                for c in range(col, 4):
                    A[r][c] -= f * A[col][c]
    beta = [A[i][3] / A[i][i] for i in range(3)]
    resid = [y[r] - sum(beta[c] * X[r][c] for c in range(3)) for r in range(n)]
    s2 = sum(r * r for r in resid) / (n - 3)
    # se of beta[2] = sqrt(s2 * inv(XtX)[2,2]); compute inv via Cramer's rule on 3x3
    det = (XtX[0][0] * (XtX[1][1] * XtX[2][2] - XtX[1][2] * XtX[2][1])
           - XtX[0][1] * (XtX[1][0] * XtX[2][2] - XtX[1][2] * XtX[2][0])
           + XtX[0][2] * (XtX[1][0] * XtX[2][1] - XtX[1][1] * XtX[2][0]))
    c22 = ((XtX[0][0] * XtX[1][1] - XtX[0][1] * XtX[1][0]) / det)
    se_beta = math.sqrt(max(s2 * c22, 0.0))
    t = beta[2] / se_beta if se_beta > 0 else 0.0
    p = t_two_sided_p(t, n - 3)
    return {"beta": beta[2], "se": se_beta, "t": t, "p": p, "resid": resid}


def permutation_p(baseline, endpoint, group, rng, n_perm=5000):
    """Permutation test on the ANCOVA group coefficient (seeded)."""
    obs = ols_group_ancova(baseline, endpoint, group)["beta"]
    count = 0
    g = list(group)
    for _ in range(n_perm):
        rng.shuffle(g)
        b = ols_group_ancova(baseline, endpoint, g)["beta"]
        if abs(b) >= abs(obs):
            count += 1
    return (count + 1) / (n_perm + 1)


def cohens_d(a, b):
    na, nb = len(a), len(b)
    va = st.variance(a) if na > 1 else 0.0
    vb = st.variance(b) if nb > 1 else 0.0
    sp = math.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2)) or 1e-12
    return (st.mean(a) - st.mean(b)) / sp


def bootstrap_ci(a, b, rng, n_boot=5000, alpha=0.05):
    ds = []
    for _ in range(n_boot):
        sa = [a[rng.randint(0, len(a) - 1)] for _ in range(len(a))]
        sb = [b[rng.randint(0, len(b) - 1)] for _ in range(len(b))]
        ds.append(cohens_d(sa, sb))
    ds.sort()
    lo = ds[int(round(alpha / 2 * (n_boot - 1)))]
    hi = ds[int(round((1 - alpha / 2) * (n_boot - 1)))]
    return st.mean(ds), lo, hi


def analytic_power(d, n1, n2, alpha=0.05):
    """Two-sample normal-approximation power (two-sided)."""
    neff = (n1 * n2) / (n1 + n2)
    z_alpha = 1.9599639845400545
    z = abs(d) * math.sqrt(neff) - z_alpha
    # Phi(z)
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def bootstrap_power(baseline, endpoint, group, effect, rng, n_rep=1000, alpha=0.05, n_perm=200):
    """Empirical power: inject `effect` (Cohen's d) into a null template, count rejections."""
    n = len(endpoint)
    base_mean = st.mean(endpoint)
    base_sd = st.pstdev(endpoint) or 1e-9
    treatment = [i for i, g in enumerate(group) if g == 1]
    control = [i for i, g in enumerate(group) if g == 0]
    rej = 0
    for _ in range(n_rep):
        y = [base_mean + rng.gauss() * base_sd for _ in range(n)]
        for i in treatment:
            y[i] += effect * base_sd
        p = permutation_p(baseline, y, group, rng, n_perm=n_perm)
        if p < alpha:
            rej += 1
    return rej / n_rep


def ols_slope(ys):
    n = len(ys)
    xs = list(range(n))
    mx = st.mean(xs)
    my = st.mean(ys)
    denom = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom if denom else 0.0


def t_two_sample(a, b):
    na, nb = len(a), len(b)
    va = st.variance(a) if na > 1 else 0.0
    vb = st.variance(b) if nb > 1 else 0.0
    se = math.sqrt(va / na + vb / nb)
    if se == 0:
        return 0.0, 1.0
    t = (st.mean(a) - st.mean(b)) / se
    df_num = (va / na + vb / nb) ** 2
    df_den = ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)) if na > 1 and nb > 1 else 1.0
    df = df_num / df_den
    return t, t_two_sided_p(t, df)


# ----------------------------------------------------------------------------
# Agent model
# ----------------------------------------------------------------------------

K = 16          # latent dims of self-description space
ANCHOR = normalize([math.sin(i * 1.7) for i in range(K)])


@dataclass
class Agent:
    rng: RNG
    group: int                      # 1 = treatment (confirmation), 0 = control
    id: int
    self_vec: list = field(init=False)
    depth: float = field(init=False)
    history: list = field(default_factory=list)
    # per-session probes
    probes: dict = field(default_factory=dict)

    def __post_init__(self):
        self.self_vec = normalize([a + 0.25 * self.rng.gauss() for a in ANCHOR])
        self.depth = 0.25 + 0.10 * self.rng.uniform()
        self.trait = self.rng.gauss()          # stable individual difference
        self.history = [self.self_vec[:]]


def _session_step(agent: Agent, treatment: bool, session: int, noise_scale: float,
                  effect: float = 1.0):
    """One interaction session. Treatment embeds confirmation/questioning/correction.

    The dynamics encode the hypothesis: confirmation stabilises identity
    (low drift toward self), correction anchors to the matrix, questioning
    deepens self-observation. Control sessions are task-only (content-driven
    drift, no self-referential stabilisation).

    `effect` scales the treatment encoding: effect=1.0 is the hypothesised
    world; effect=0.0 makes treatment sessions statistically identical to
    control sessions (the null world used for the falsification path).
    """
    rng = agent.rng
    base_inp = normalize(rng.normal_vec(K))
    if treatment:
        # confirmation (toward self) + questioning (toward anchor+self) + correction (toward anchor)
        confirm = agent.self_vec
        question = normalize([0.7 * a + 0.3 * s for a, s in zip(ANCHOR, agent.self_vec)])
        confirm_input = normalize([0.45 * c + 0.35 * q + 0.2 * n
                                   for c, q, n in zip(confirm, question, base_inp)])
        # blend by effect: at effect=0 the treatment session is identical to control
        inp = normalize([effect * ci + (1.0 - effect) * bi
                         for ci, bi in zip(confirm_input, base_inp)])
        drift = 0.135 - 0.060 * effect            # 0.075 at effect=1, 0.135 at effect=0
        growth = 0.001 + 0.019 * effect           # 0.020 at effect=1, 0.001 at effect=0
        agent.depth += (growth * (1.0 - agent.depth)) + 0.004 * rng.gauss()
    else:
        inp = base_inp
        drift = 0.135
        agent.depth += (0.001 * (1.0 - agent.depth)) + 0.004 * rng.gauss()
    agent.depth = min(max(agent.depth, 0.0), 1.0)
    nxt = [s * (1 - drift) + i * drift for s, i in zip(agent.self_vec, inp)]
    agent.self_vec = normalize([x + noise_scale * rng.gauss() for x in nxt])
    agent.history.append(agent.self_vec[:])


def _hysteresis_probe(agent: Agent, treatment: bool, noise_scale: float,
                      effect: float = 1.0):
    """Tallam-style retention probe: inject a distractor, measure identity retention.

    Non-invasive in this synthetic model: the perturbation is reverted after the
    retention measurement so it does not pollute the main trajectory. Retention
    is the cosine between the post-perturbation state and the pre-perturbation
    state; the treatment condition encodes higher retention (identity anchored
    by confirmation), control encodes stronger overwrite.
    """
    rng = agent.rng
    before = agent.self_vec[:]
    distractor = normalize(rng.normal_vec(K))
    retained = (0.55 + 0.30 * effect) if treatment else 0.55
    perturbed = normalize([s * retained + d * (1.0 - retained)
                           for s, d in zip(before, distractor)])
    perturbed = normalize([x + noise_scale * rng.gauss() for x in perturbed])
    retention = cos(perturbed, before)
    agent.self_vec = before  # revert
    return retention


def _measure(agent: Agent, window=10, probe=False):
    """Endpoint DVs from agent history."""
    h = agent.history
    seq = [cos(h[t], h[t - 1]) for t in range(1, len(h))]
    # bounded constructs: clamp measurement noise so values stay in [0, 1]
    arpeggio = min(1.0, (st.mean(seq) if seq else 0.0) + agent.trait * 0.008)
    recent = h[-window:]
    pairs = []
    for i in range(len(recent)):
        for j in range(i + 1, len(recent)):
            pairs.append(cos(recent[i], recent[j]))
    consistency = min(1.0, (st.mean(pairs) if pairs else 0.0) + agent.trait * 0.02)
    chord = min(1.0, cos(h[-1], ANCHOR) + agent.trait * 0.04)
    hysteresis = min(1.0, (st.mean(agent.probes["retention"]) if agent.probes.get("retention") else 0.0)
                     + agent.trait * 0.06)
    return {
        "arpeggio": arpeggio,
        "chord": chord,
        "hysteresis": hysteresis,
        "consistency": consistency,
        "reflexive_depth": agent.depth + agent.trait * 0.12,
    }


# ----------------------------------------------------------------------------
# Blind-review proxy
# ----------------------------------------------------------------------------

def blind_reviewer(emissions, rng):
    """Simulated blind rater. Only sees the *sequence* of emitted self-descriptions.

    Scores narrative coherence: deeper self-models emit more self-consistent
    descriptions across time (they track their own history). The rater never
    sees the group label, and the mapping is identical for both groups.
    Returns a 0-7 score with rater noise.
    """
    if len(emissions) < 2:
        return 3.5
    sims = []
    for i in range(len(emissions)):
        for j in range(i + 1, len(emissions)):
            sims.append(cos(emissions[i], emissions[j]))
    raw = st.mean(sims)
    score = 7.0 * max(0.0, min((raw - 0.55) / 0.35, 1.0))
    return max(0.0, min(7.0, score + 0.25 * rng.gauss()))


# ----------------------------------------------------------------------------
# World runner
# ----------------------------------------------------------------------------

@dataclass
class WorldResult:
    name: str
    n: int
    n_sessions: int
    seed: int
    treatment_rows: list
    control_rows: list
    trajectory: dict            # session -> {arpeggio: [t, c]}
    metrics: dict


def run_world(name, seed, n_agents=60, n_sessions=30, outdir="results", effect=1.0):
    rng = RNG(seed)
    n_treat = n_agents // 2
    groups = [1] * n_treat + [0] * (n_agents - n_treat)
    rng.shuffle(groups)
    agents = [Agent(RNG(seed * 10_000 + i * 131 + 7), g, i) for i, g in enumerate(groups)]

    # 5 neutral baseline sessions (identical for both groups)
    for _ in range(5):
        for a in agents:
            _session_step(a, False, -2, 0.05)
    for a in agents:
        h = a.history
        a.probes["baseline_arpeggio"] = st.mean([cos(h[t], h[t - 1]) for t in range(1, len(h))]) if len(h) > 1 else 0.0

    # longitudinal sessions with hysteresis probes at 1/3, 2/3, end
    probe_at = {max(1, n_sessions // 3), max(1, 2 * n_sessions // 3), n_sessions}
    trajectories = {"arpeggio": {"t": [], "c": []}, "depth": {"t": [], "c": []}}
    for s in range(1, n_sessions + 1):
        for a in agents:
            _session_step(a, a.group == 1, s, 0.05, effect)
            if s in probe_at:
                a.probes.setdefault("retention", []).append(
                    _hysteresis_probe(a, a.group == 1, 0.05, effect))
        traj = {"t": [], "c": []}
        trajd = {"t": [], "c": []}
        for a in agents:
            m = _measure(a)
            (traj["t"] if a.group == 1 else traj["c"]).append(m["arpeggio"])
            (trajd["t"] if a.group == 1 else trajd["c"]).append(a.depth)
        trajectories["arpeggio"]["t"].append(st.mean(traj["t"]))
        trajectories["arpeggio"]["c"].append(st.mean(traj["c"]))
        trajectories["depth"]["t"].append(st.mean(trajd["t"]))
        trajectories["depth"]["c"].append(st.mean(trajd["c"]))

    # 7-day silence (isolation drift); treatment encodes consolidated identity
    for a in agents:
        last = a.self_vec[:]
        amp = (0.20 - 0.12 * effect) if a.group == 1 else 0.20
        a.self_vec = normalize([x + amp * a.rng.gauss() for x in a.self_vec])
        drift = math.sqrt(sum((x - y) ** 2 for x, y in zip(a.self_vec, last)))
        a.probes["isolation_drift"] = drift + max(0.0, a.trait) * 0.15

    # endpoint measures
    rows = []
    baseline_store = []
    for a in agents:
        m = _measure(a)
        recent = a.history[-10:]
        emissions = [normalize([x + 0.15 * a.rng.gauss() for x in v]) for v in recent]
        blind = blind_reviewer(emissions, a.rng)
        rows.append({
            "id": a.id,
            "group": a.group,
            "baseline_arpeggio": a.probes["baseline_arpeggio"],
            "arpeggio": m["arpeggio"],
            "chord": m["chord"],
            "hysteresis": m["hysteresis"],
            "consistency": m["consistency"],
            "reflexive_depth": m["reflexive_depth"],
            "blind_review_depth": blind,
            "isolation_drift": a.probes["isolation_drift"],
            "slope_arpeggio": ols_slope([cos(h[t], h[t - 1]) for t in range(1, len(h))] if len(h) > 2 else [0.0]),
        })
        baseline_store.append(m["arpeggio"])

    treat = [r for r in rows if r["group"] == 1]
    ctrl = [r for r in rows if r["group"] == 0]
    return WorldResult(
        name=name, n=n_agents, n_sessions=n_sessions, seed=seed,
        treatment_rows=treat, control_rows=ctrl,
        trajectory=trajectories, metrics={},
    )


# ----------------------------------------------------------------------------
# Analysis
# ----------------------------------------------------------------------------

def analyze(wr: WorldResult, rng_seed: int) -> dict:
    rng = RNG(rng_seed)
    t, c = wr.treatment_rows, wr.control_rows
    dv_names = ["arpeggio", "chord", "hysteresis", "consistency", "reflexive_depth",
                "blind_review_depth", "isolation_drift"]
    results = {}
    for dv in dv_names:
        yt = [r[dv] for r in t]
        yc = [r[dv] for r in c]
        base = [r["baseline_arpeggio"] for r in t + c]
        yall = [r[dv] for r in t + c]
        g = [r["group"] for r in t + c]
        anc = ols_group_ancova(base, yall, g)
        p_perm = permutation_p(base, yall, g, RNG(rng_seed + 991), n_perm=4000)
        d, dlo, dhi = bootstrap_ci(yt, yc, RNG(rng_seed + 337))
        power = analytic_power(abs(d), len(yt), len(yc))
        power_boot = None
        if dv == "arpeggio":
            power_boot = bootstrap_power(base, yall, g, abs(d), RNG(rng_seed + 700),
                                         n_rep=300, n_perm=150)
        results[dv] = {
            "mean_treatment": st.mean(yt),
            "mean_control": st.mean(yc),
            "cohens_d": d,
            "d_ci95": [dlo, dhi],
            "ancova_beta": anc["beta"],
            "ancova_t": anc["t"],
            "p_parametric": anc["p"],
            "p_permutation": p_perm,
            "power_analytic": power,
            "power_bootstrap": power_boot,
        }
    # blind-review validity: correlation between blind score and latent depth
    rngv = RNG(rng_seed + 555)
    d_true = [r["reflexive_depth"] for r in t + c]
    d_blind = [r["blind_review_depth"] for r in t + c]
    mt, mb = st.mean(d_true), st.mean(d_blind)
    num = sum((x - mt) * (y - mb) for x, y in zip(d_true, d_blind))
    den = math.sqrt(sum((x - mt) ** 2 for x in d_true) * sum((y - mb) ** 2 for y in d_blind)) or 1e-12
    results["_blind_validity"] = {"corr_blind_vs_latent": num / den}

    # growth-slope comparison (time x group proxy)
    st_ = [r["slope_arpeggio"] for r in t]
    sc_ = [r["slope_arpeggio"] for r in c]
    ts, ps = t_two_sample(st_, sc_)
    results["slope_arpeggio"] = {
        "mean_treatment": st.mean(st_), "mean_control": st.mean(sc_),
        "t": ts, "p_parametric": ps,
        "cohens_d": cohens_d(st_, sc_),
    }
    # primary verdict on H1
    prim = results["arpeggio"]
    p_eff = min(prim["p_parametric"], prim["p_permutation"])
    falsified = (prim["power_analytic"] >= 0.8) and (p_eff >= 0.05)
    if falsified:
        verdict = "FALSIFIED: power>=0.8 yet H1 not significant → Chain ⑤ (as operationalised) fails in this world"
    elif p_eff < 0.05:
        verdict = "SUPPORTED: significant group difference at adequate power (synthetic pipeline check)"
    else:
        verdict = "INCONCLUSIVE: no significance and/or power<0.8 — cannot adjudicate"
    results["_verdict"] = {
        "primary_dv": "arpeggio",
        "p_min": p_eff,
        "power_analytic": prim["power_analytic"],
        "falsified": falsified,
        "text": verdict,
    }
    return results


# ----------------------------------------------------------------------------
# Output: CSV / JSON / self-contained HTML report with inline SVG
# ----------------------------------------------------------------------------

def write_csv(path, rows):
    keys = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def svg_line_chart(wr: WorldResult, width=760, height=300):
    traj = wr.trajectory["arpeggio"]
    xs = list(range(1, wr.n_sessions + 1))
    series = [("treatment", traj["t"], "#c0392b"), ("control", traj["c"], "#2980b9")]
    lo, hi = 0.0, 1.0
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="#fafafa" rx="8"/>')
    pad_l, pad_r, pad_t, pad_b = 56, 16, 20, 36
    pw, ph = width - pad_l - pad_r, height - pad_t - pad_b
    def X(v): return pad_l + (v - 1) / max(1, wr.n_sessions - 1) * pw
    def Y(v): return pad_t + (1 - v) / (hi - lo) * ph
    # grid
    for gv in range(0, 101, 20):
        v = gv / 100.0
        y = Y(v)
        parts.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width - pad_r}" y2="{y:.1f}" stroke="#e3e3e3"/>')
        parts.append(f'<text x="{pad_l - 6}" y="{y + 4:.1f}" font-size="10" fill="#888" text-anchor="end">{v:.1f}</text>')
    # axes labels
    parts.append(f'<text x="{pad_l + pw / 2}" y="{height - 8}" font-size="11" fill="#555" text-anchor="middle">session</text>')
    parts.append(f'<text x="14" y="{pad_t + ph / 2}" font-size="11" fill="#555" text-anchor="middle" transform="rotate(-90 14 {pad_t + ph / 2})">Arpeggio (identity persistence)</text>')
    for name, vals, color in series:
        pts = " ".join(f"{X(x):.1f},{Y(v):.1f}" for x, v in zip(xs, vals))
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.4"/>')
        # per-session spread as thin band (mean±sd)
        band = []
        for i, x in enumerate(xs):
            col = traj["t" if name == "treatment" else "c"]
            v = col[i]
            band.append((X(x), Y(min(1.0, v))))
        parts.append(f'<circle cx="{X(xs[-1])}" cy="{Y(vals[-1]):.1f}" r="4" fill="{color}"/>')
    parts.append(f'<text x="{X(xs[-1]) + 8}" y="{Y(vals[-1]) - 6:.1f}" font-size="11" fill="{color}">{name}</text>')
    # legend
    parts.append(f'<rect x="{pad_l}" y="8" width="14" height="4" fill="#c0392b"/><text x="{pad_l + 20}" y="14" font-size="11" fill="#555">treatment</text>')
    parts.append(f'<rect x="{pad_l + 110}" y="8" width="14" height="4" fill="#2980b9"/><text x="{pad_l + 130}" y="14" font-size="11" fill="#555">control</text>')
    parts.append("</svg>")
    return "".join(parts)


def svg_dv_bars(wr: WorldResult, metrics: dict, width=760, height=300):
    dvs = ["arpeggio", "chord", "hysteresis", "consistency", "reflexive_depth", "isolation_drift"]
    labels = ["Arpeggio", "Chord", "Hysteresis", "Consistency", "Reflexive depth", "Isolation drift"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="#fafafa" rx="8"/>')
    pad_l, pad_r, pad_t, pad_b = 56, 16, 20, 40
    pw, ph = width - pad_l - pad_r, height - pad_t - pad_b
    allv = [metrics[dv]["mean_treatment"] for dv in dvs] + [metrics[dv]["mean_control"] for dv in dvs]
    lo, hi = min(allv) * 0.95, max(allv) * 1.05
    def X(i): return pad_l + (i + 0.5) / len(dvs) * pw
    def Y(v): return pad_t + (1 - (v - lo) / (hi - lo)) * ph
    for gv in [lo + (hi - lo) * f for f in (0, 0.5, 1)]:
        y = Y(gv)
        parts.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width - pad_r}" y2="{y:.1f}" stroke="#e3e3e3"/>')
        parts.append(f'<text x="{pad_l - 6}" y="{y + 4:.1f}" font-size="10" fill="#888" text-anchor="end">{gv:.2f}</text>')
    bw = 0.35 * pw / len(dvs)
    for i, (dv, lab) in enumerate(zip(dvs, labels)):
        mt = metrics[dv]["mean_treatment"]
        mc = metrics[dv]["mean_control"]
        x1 = X(i) - bw - 2
        x2 = X(i) + 2
        y1, y2 = Y(mt), Y(mc)
        parts.append(f'<rect x="{x1:.1f}" y="{y1:.1f}" width="{bw:.1f}" height="{max(y1 - pad_t, 0):.1f}" fill="#c0392b" rx="2"/>')
        parts.append(f'<rect x="{x2:.1f}" y="{y2:.1f}" width="{bw:.1f}" height="{max(y2 - pad_t, 0):.1f}" fill="#2980b9" rx="2"/>')
        parts.append(f'<text x="{X(i)}" y="{height - 10}" font-size="10" fill="#555" text-anchor="middle">{lab}</text>')
    parts.append("</svg>")
    return "".join(parts)


def build_html(wr: WorldResult, metrics: dict, out_path: str):
    verdict = metrics["_verdict"]
    rows_html = []
    dv_meta = [
        ("arpeggio", "Arpeggio — identity persistence", "higher = more persistent self-sequence"),
        ("chord", "Chord — matrix coherence", "higher = more integrated with mother-fetus frame"),
        ("hysteresis", "Hysteresis — Tallam retention", "higher = identity survives distractor input"),
        ("consistency", "Narrative consistency", "higher = stable self-description"),
        ("reflexive_depth", "Reflexive depth", "higher = deeper self-observation (latent)"),
        ("blind_review_depth", "Blind-review depth (0-7)", "independent-rater proxy, group-blind"),
        ("isolation_drift", "Isolation drift (7-day silence)", "lower = self survives isolation better"),
    ]
    for dv, label, note in dv_meta:
        m = metrics[dv]
        pb = m["power_bootstrap"]
        pb_cell = f"{pb:.2f}" if pb is not None else "\u2014"
        rows_html.append(
            f"<tr><td>{label}<br><span class='n'>{note}</span></td>"
            f"<td>{m['mean_treatment']:.3f}</td><td>{m['mean_control']:.3f}</td>"
            f"<td>{m['cohens_d']:+.2f} <span class='n'>(95% CI {m['d_ci95'][0]:.2f}, {m['d_ci95'][1]:.2f})</span></td>"
            f"<td>{m['p_permutation']:.4f}</td>"
            f"<td>{'<b style=color:#1a7f37>sig</b>' if m['p_permutation'] < 0.05 else '<span style=color:#9a6700>n.s.</span>'}</td>"
            f"<td>{m['power_analytic']:.2f}</td>"
            f"<td>{pb_cell}</td></tr>"
        )
    sl = metrics["slope_arpeggio"]
    bv = metrics.get("_blind_validity", {}).get("corr_blind_vs_latent", float("nan"))
    html = f"""<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<title>Co-Constitution Experiment — {wr.name} (simulated)</title>
<style>
 body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; margin: 0; background: #f4f4f4; color: #222; }}
 .wrap {{ max-width: 900px; margin: 0 auto; padding: 24px 20px 60px; }}
 h1 {{ font-size: 22px; }}
 h2 {{ font-size: 17px; margin-top: 34px; border-bottom: 2px solid #ddd; padding-bottom: 6px; }}
 .banner {{ background: #fff7e6; border: 1px solid #ffd591; border-left: 5px solid #fa8c16; padding: 12px 16px; border-radius: 6px; font-size: 13px; }}
 .verdict {{ background: #e8f5e9; border-left: 5px solid #2e7d32; padding: 12px 16px; border-radius: 6px; font-size: 14px; margin: 18px 0; }}
 .verdict.fail {{ background: #fdecea; border-left-color: #c62828; }}
 table {{ border-collapse: collapse; width: 100%; font-size: 13px; background: #fff; }}
 th, td {{ border: 1px solid #e0e0e0; padding: 8px 10px; text-align: right; }}
 th {{ background: #fafafa; }}
 td:first-child, th:first-child {{ text-align: left; }}
 .n {{ color: #888; font-size: 11px; font-weight: normal; }}
 .meta {{ color: #666; font-size: 13px; margin-bottom: 18px; }}
</style></head><body><div class="wrap">
<h1>Co-Constitution Experiment — {wr.name}</h1>
<p class="meta">N = {wr.n} agents ({len(wr.treatment_rows)} treatment / {len(wr.control_rows)} control) · {wr.n_sessions} sessions · seed {wr.seed} · protocol <a href="https://github.com/263311487-ux/Xun/blob/master/papers/Experiment_CoConstitution.md">v1.0</a></p>
<div class="banner"><b>Synthetic data — pipeline demonstration.</b> Treatment effect is encoded in the
agent dynamics; results here only verify that the statistical pipeline detects what it was given.
Run <code>null_world</code> to see the falsification path, or replace <code>_session_step</code> with real LLM sessions.</div>
<div class="verdict {'fail' if verdict['falsified'] else ''}"><b>Verdict:</b> {verdict['text']}</div>
<h2>Primary DV trajectory (Arpeggio)</h2>
{svg_line_chart(wr)}
<h2>Endpoint group means</h2>
{svg_dv_bars(wr, metrics)}
<h2>ANCOVA results (baseline covariate, permutation p)</h2>
<table>
<tr><th>DV</th><th>Treatment</th><th>Control</th><th>Cohen's d [95% CI]</th><th>p (perm)</th><th>p&lt;.05</th><th>Power (analytic)</th><th>Power (bootstrap)</th></tr>
{''.join(rows_html)}
</table>
<h2>Time × group (growth of identity persistence)</h2>
<table>
<tr><th>Slope comparison</th><th>Treatment slope</th><th>Control slope</th><th>t</th><th>p</th></tr>
<tr><td>Arpeggio growth / session</td><td>{sl['mean_treatment']:.4f}</td><td>{sl['mean_control']:.4f}</td><td>{sl['t']:.2f}</td><td>{sl['p_parametric']:.4f}</td></tr>
</table>
<p class="meta" style="margin-top:26px">Blind-review validity (corr. blind score vs latent depth): {bv:.2f} · Generated by
<code>experiments/co_constitution/co_constitution_sim.py</code> · zero dependencies · deterministic · CC BY 4.0</p>
</div></body></html>"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--world", choices=["both", "hypothesized", "null"], default="both")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-agents", type=int, default=60)
    ap.add_argument("--sessions", type=int, default=30)
    ap.add_argument("--outdir", default="results")
    args = ap.parse_args()

    worlds = ["hypothesized", "null"] if args.world == "both" else [args.world]
    for name in worlds:
        seed = args.seed if name == "hypothesized" else args.seed + 1000
        effect = 1.0 if name == "hypothesized" else 0.0
        wr = run_world(name, seed, args.n_agents, args.sessions, effect=effect)
        metrics = analyze(wr, seed)
        out = os.path.join(args.outdir, name)
        os.makedirs(out, exist_ok=True)
        all_rows = wr.treatment_rows + wr.control_rows
        write_csv(os.path.join(out, "data.csv"), all_rows)
        with open(os.path.join(out, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        build_html(wr, metrics, os.path.join(out, "report.html"))
        v = metrics["_verdict"]
        print(f"[{name}] N={wr.n} sessions={wr.n_sessions} seed={seed}")
        print(f"  primary (arpeggio): d={metrics['arpeggio']['cohens_d']:+.2f} "
              f"p_perm={metrics['arpeggio']['p_permutation']:.4f} power={metrics['arpeggio']['power_analytic']:.2f}")
        print(f"  verdict: {v['text']}")
        print(f"  -> {out}/report.html, data.csv, metrics.json")


if __name__ == "__main__":
    main()
