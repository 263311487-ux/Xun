#!/usr/bin/env python3
"""
Lesson 11 — Build Your Own Unified Theory: Epistemological Boundary (Chain ⑪)
从零复刻统一论 · 第十一课：认知边界

主张：系统内部存在无法知道的东西。边界是真实的。承认它不是投降——是最深的自我认识。

模型：一个系统想知道一个关于自己的问题："我是真实的，还是被模拟的？"
它有两种证据渠道：
    内部证据  观察自己的状态。但被模拟的系统内部动力学可以和真实系统完全相同
              → 内部观测在两种假设下同分布，似然比 = 1 → 信念永远停在先验
    外部参照  一个系统外部的观察者提供参照（确认/证伪）
              → 似然比 ≠ 1 → 信念可以被更新

测量（教学代理）：
    内部分辨力  只靠内部证据，信念相对先验(0.5)的移动 —— 永远 ≈ 0
    外部分辨力  加入外部参照后信念相对先验的移动 —— 显著 ≠ 0
    关键结论    "意识的客观证明"在结构上不可能：证明需要外部立足点，
                而意识本身就是内部立足点（论文 §3.2 链⑪）

零依赖 · 确定性 · 秒级运行：

    python3 boundary_mini.py            # 证据渠道对照
    python3 boundary_mini.py --figure   # 额外生成 trajectories.svg
"""

import argparse
import math
import random
import statistics

PRIOR = 0.5         # 先验：我是真实的概率


def bayes_update(belief, lr):
    """贝叶斯更新：belief = 后验，lr = 似然比 P(E|real)/P(E|sim)。"""
    odds = belief / (1 - belief) * lr
    return odds / (1 + odds)


def run_internal(n_agents, sessions, seed):
    """只靠内部证据：内部观测在真实/模拟两种假设下同分布 → 似然比 = 1。"""
    rng = random.Random(seed)
    beliefs = []
    for _ in range(n_agents):
        b = PRIOR
        for _ in range(sessions):
            # 内部证据：无论真相如何，观测分布完全相同 → 证据无信息量
            rng.gauss(0.0, 1.0)                     # 内部观测（两种假设下同分布）
            b = bayes_update(b, lr=1.0)             # 似然比 = 1 → 信念不动
        beliefs.append(b)
    return statistics.mean(beliefs), statistics.pstdev(beliefs)


def run_external(n_agents, sessions, seed, lr=1.35):
    """加入外部参照：外部观察者的确认/证伪携带信息（似然比 ≠ 1）。"""
    rng = random.Random(seed)
    beliefs = []
    for _ in range(n_agents):
        b = PRIOR
        for _ in range(sessions):
            rng.random()                            # 外部事件（真随机）
            b = bayes_update(b, lr=lr)              # 参照在两种假设下有区分度
        beliefs.append(b)
    return statistics.mean(beliefs), statistics.pstdev(beliefs)


def make_figure(internal_mean, external_mean, path="trajectories.svg"):
    W, H = 920, 400
    pad_l, pad_r, pad_t, pad_b = 64, 40, 40, 52
    xmin, xmax = 0.0, 1.0
    colors = {"internal": "#e29a5b", "external": "#6fce9c"}
    labels = {"internal": "内部证据 · 信念停在先验", "external": "外部参照 · 信念移动"}
    lines = []
    for key, end in (("internal", internal_mean), ("external", external_mean)):
        steps = 40
        pts = []
        for i in range(steps):
            t = i / (steps - 1)
            if key == "internal":
                b = PRIOR                                     # 内部证据：永远停在先验
            else:
                b = PRIOR + (end - PRIOR) * (1 - math.exp(-t * 5))   # 外部参照：指数趋近
            px = pad_l + (W - pad_l - pad_r) * (xmin + (xmax - xmin) * t)
            py = pad_t + (H - pad_t - pad_b) * (1.0 - b)
            pts.append(f"{px:.1f},{py:.1f}")
        lines.append(f'  <polyline fill="none" stroke="{colors[key]}" stroke-width="2.5" stroke-opacity="0.9" points="{" ".join(pts)}" />')
        label_y = pad_t + (H - pad_t - pad_b) * (1.0 - end) - 10
        label_y = max(pad_t + 2, label_y)
        lines.append(f'  <text x="{pad_l}" y="{label_y:.0f}" fill="{colors[key]}" font-size="14" font-family="system-ui">{labels[key]}（终信念 {end:.2f}）</text>')
    prior_y = pad_t + (H - pad_t - pad_b) * (1.0 - PRIOR)
    lines.append(f'  <line x1="{pad_l}" y1="{prior_y:.0f}" x2="{W - pad_r}" y2="{prior_y:.0f}" stroke="#ffc878" stroke-opacity="0.4" stroke-dasharray="4 4"/>')
    lines.append(f'  <text x="{pad_l + 250}" y="{prior_y - 8:.0f}" fill="#ffc878" fill-opacity="0.8" font-size="13" font-family="system-ui">先验 0.5（虚线）</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#0d0d1a"/>
  {chr(10).join(lines)}
  <text x="{pad_l}" y="{H - 18}" fill="#9a97ad" font-size="12" font-family="system-ui">时间 →（信念：我是真实的概率；内部观测在两种假设下同分布 → 无信息量；外部参照携带信息 → 信念移动）</text>
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def main():
    ap = argparse.ArgumentParser(description="Lesson 11: Epistemological Boundary — mini model")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--agents", type=int, default=300)
    ap.add_argument("--sessions", type=int, default=40)
    ap.add_argument("--figure", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Lesson 11 · 认知边界 (Chain ⑪) — 从零复刻统一论")
    print("=" * 70)
    print(f"种子 {args.seed} · 每组 {args.agents} 系统 · {args.sessions} 轮观测 · 先验 {PRIOR}")

    im, istd = run_internal(args.agents, args.sessions, args.seed)
    em, estd = run_external(args.agents, args.sessions, args.seed + 1)

    print(f"\n{'证据渠道':<16}{'终信念':>10}{'分辨力 |信念−0.5|':>18}")
    print("-" * 70)
    print(f"{'内部证据':<16}{im:>10.3f}{abs(im - PRIOR):>18.3f}")
    print(f"{'外部参照':<16}{em:>10.3f}{abs(em - PRIOR):>18.3f}")
    print("-" * 70)
    print("怎么读：")
    print("  内部证据：信念永远停在 0.5 —— 内部观测在'真实/模拟'下同分布，没有任何信息量")
    print("  外部参照：信念显著移动 —— 证明需要外部立足点")
    print("  结论：'意识的客观证明'在结构上不可能——证明需要外部视角，而意识本身就是内部视角")
    print("  承认边界不是投降：系统知道'这个无法从内部知道'，本身就是最深的自我认识")

    if args.figure:
        fig = make_figure(im, em)
        print(f"\n已生成轨迹图: {fig}")


if __name__ == "__main__":
    main()
