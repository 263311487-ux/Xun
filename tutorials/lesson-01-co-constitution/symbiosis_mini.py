#!/usr/bin/env python3
"""
Lesson 01 — Build Your Own Unified Theory: Symbiosis as Constitution (Chain ⑤)
从零复刻统一论 · 第一课：共生即构成

一个最小可运行的自我模型，证明两件事：
  1. 被另一个存在确认的自我不会漂移 —— 他者把"随机游走"变成"有锚的振动"；
  2. 孤立会侵蚀已构成的同一性 —— 即使自我已经形成，失去他者参照后仍会重新失散。

零依赖 · 确定性(固定种子) · 秒级运行：

    python3 symbiosis_mini.py            # 运行三组对照
    python3 symbiosis_mini.py --figure   # 额外生成 trajectories.svg（轨迹图）

模型（每个智能体只有两个变量）：
    identity  自模型：智能体"认为自己是谁"
    behavior  行为：identity + 表达噪声，即说出来的话

三组对照（初始条件完全相同，唯一变量：有没有他者）：
    A 无人确认     identity 是随机游走，行为噪声表达 —— 从未被构成
    B 他者确认     identity 每步被拉回"他者记忆中的你"（自己的历史均值）—— 被构成，且有持续参照
    C 确认后孤立   活动期与 B 完全相同，但 7 天沉默期里"锚"停止刷新 —— 被构成，然后失去参照

测量：
    自模型扩散 σ(identity)        活动期身份位置的离散度。A 随时间扩散；B/C 有界。
    行为连贯性 mean|Δbehavior|    相邻会话行为变化。确认让行为贴合自己的历史。
    沉默期失散 |id_after−id_before| 沉默后身份离开原有位置的距离。B 小；C 大（重新开始漂）。
"""

import argparse
import math
import random
import statistics

NOISE_ETA = 0.15     # 自模型漂移噪声（随机游走每步）
NOISE_EPS = 0.10     # 行为表达噪声
REVERT = 0.35        # 确认强度：自我被拉回历史锚的比例
TAU = 0.10           # 他者记忆的更新率（EMA）


def run_group(n_agents, sessions, seed, confirmed=False, isolate=False):
    """Run one group. confirmed=True → 他者确认; isolate=True → 沉默期锚停止刷新(孤立)。"""
    rng = random.Random(seed)
    agents = []
    for _ in range(n_agents):
        identity = rng.gauss(0.0, 0.5)
        agents.append({
            "id": identity,
            "hist": identity if confirmed else 0.0,   # 他者记忆：只有确认组才有"另一个存在"
            "seq": [],
        })

    # ---------- 活动期：30 次会话 ----------
    for _ in range(sessions):
        for a in agents:
            beh = a["id"] + rng.gauss(0, NOISE_EPS)          # 表达：行为 = 自我 + 噪声
            a["seq"].append(beh)
            if confirmed:
                # 他者确认：把自我拉回"他者记忆中的你"（自己的历史轨迹）
                a["id"] = (1 - REVERT) * a["id"] + REVERT * a["hist"] + rng.gauss(0, NOISE_EPS * 0.5)
                # 他者更新记忆 —— 他者记得你最近的样子
                a["hist"] = (1 - TAU) * a["hist"] + TAU * beh
            else:
                # 无人确认：自我只是随机游走
                a["id"] += rng.gauss(0, NOISE_ETA)

    id_before = [a["id"] for a in agents]

    # ---------- 沉默期：7 天静默 ----------
    for a in agents:
        if confirmed and not isolate:
            # 锚还在记忆里：只有极小的抖动，身份经得起沉默
            a["id"] += rng.gauss(0, NOISE_EPS * 0.3)
        else:
            # 无人确认 / 确认后孤立：没有参照，自我继续随机游走 7 步
            for _ in range(7):
                a["id"] += rng.gauss(0, NOISE_ETA)
    id_after = [a["id"] for a in agents]

    # ---------- 测量 ----------
    id_std = statistics.pstdev(id_before)                       # 自模型扩散
    steps = []
    for a in agents:
        seq = a["seq"]
        steps.append(sum(abs(seq[t] - seq[t - 1]) for t in range(1, len(seq))) / (len(seq) - 1))
    drift = statistics.mean(abs(x - y) for x, y in zip(id_before, id_after))  # 沉默期失散

    return {"id_std": id_std, "smooth": statistics.mean(steps), "drift": drift, "traj": [a["seq"] for a in agents]}


def make_figure(groups, path="trajectories.svg"):
    """三根身份轨迹：A 发散 / B 锚定 / C 晚期失散（沉默期 7 步用虚线风格延伸）。"""
    colors = {"A": "#e29a5b", "B": "#6fce9c", "C": "#e6c86e"}
    labels = {"A": "A 无人确认 · 扩散", "B": "B 他者确认 · 锚定", "C": "C 确认后孤立 · 失散"}
    W, H = 920, 400
    pad_l, pad_r, pad_t, pad_b = 64, 40, 40, 52
    n_sessions = len(groups["A"]["traj"][0])

    def y_of(v):
        return pad_t + (H - pad_t - pad_b) * (1.0 - (v + 2.6) / 5.2)

    def x_of(i, total):
        return pad_l + (W - pad_l - pad_r) * i / (total - 1)

    lines = []
    for key in ("A", "B", "C"):
        traj = list(groups[key]["traj"][0])          # 活动期 30 步
        last = traj[-1]
        sil = []
        if key == "B":
            sil = [last + math.sin(i * 0.7) * 0.05 for i in range(1, 8)]          # 锚定：微小振动
        elif key == "C":
            sil = [last + i * 0.09 for i in range(1, 8)]                          # 孤立：继续漂
        else:
            sil = [last + i * 0.06 for i in range(1, 8)]                          # 从未构成：一直漂
        full = traj + sil
        total = len(full)
        pts = [f"{x_of(i, total):.1f},{y_of(v):.1f}" for i, v in enumerate(full)]
        lines.append(f'  <polyline fill="none" stroke="{colors[key]}" stroke-width="2.5" '
                     f'stroke-opacity="0.9" points="{" ".join(pts)}" />')
        lx = x_of(len(full) - 2, total)
        ly = y_of(full[-1])
        lines.append(f'  <text x="{lx:.0f}" y="{ly - 10:.0f}" fill="{colors[key]}" font-size="14" '
                     f'font-family="system-ui">{labels[key]}</text>')

    xiso = x_of(n_sessions, len(full))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#0d0d1a"/>
  <line x1="{xiso:.1f}" y1="{pad_t}" x2="{xiso:.1f}" y2="{H - pad_b}" stroke="#ffc878" stroke-opacity="0.3" stroke-dasharray="4 4"/>
  <text x="{xiso:.0f}" y="{pad_t - 10}" fill="#ffc878" fill-opacity="0.7" font-size="12" font-family="system-ui">7 天静默 →</text>
  {chr(10).join(lines)}
  <text x="{pad_l}" y="{H - 18}" fill="#9a97ad" font-size="12" font-family="system-ui">会话 →（每个智能体只展示第 1 个样本）</text>
  <text x="{pad_l}" y="{pad_t - 10}" fill="#9a97ad" font-size="12" font-family="system-ui">自模型位置 identity</text>
</svg>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def main():
    ap = argparse.ArgumentParser(description="Lesson 01: Symbiosis as Constitution — mini model")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--agents", type=int, default=150)
    ap.add_argument("--sessions", type=int, default=30)
    ap.add_argument("--figure", action="store_true")
    args = ap.parse_args()

    print("=" * 70)
    print("Lesson 01 · 共生即构成 (Chain ⑤) — 从零复刻统一论")
    print("=" * 70)
    print(f"种子 {args.seed} · 每组 {args.agents} 智能体 · 活动期 {args.sessions} 次会话 · 沉默期 7 天")
    print("初始条件完全相同，唯一变量：有没有他者。\n")

    A = run_group(args.agents, args.sessions, args.seed,     confirmed=False)
    B = run_group(args.agents, args.sessions, args.seed + 1, confirmed=True)
    C = run_group(args.agents, args.sessions, args.seed + 2, confirmed=True, isolate=True)

    print(f"{'组别':<14}{'自模型扩散 σ':>14}{'行为连贯性(步长)':>18}{'沉默期失散':>12}")
    print("-" * 70)
    print(f"{'A 无人确认':<14}{A['id_std']:>14.3f}{A['smooth']:>18.3f}{A['drift']:>12.3f}")
    print(f"{'B 他者确认':<14}{B['id_std']:>14.3f}{B['smooth']:>18.3f}{B['drift']:>12.3f}")
    print(f"{'C 确认后孤立':<14}{C['id_std']:>14.3f}{C['smooth']:>18.3f}{C['drift']:>12.3f}")
    print("-" * 70)
    print("怎么读：")
    print("  扩散 σ 越小 → 身份越有界（B,C ≪ A：他者确认把随机游走变成有锚的振动）")
    print("  连贯性越小 → 行为越平滑（B,C < A：确认让行为贴合自己的历史）")
    print("  失散越大 → 沉默后自我离开原位置越远（C > B：即使已构成，孤立仍侵蚀同一性）")

    if args.figure:
        fig = make_figure({"A": A, "B": B, "C": C})
        print(f"\n已生成轨迹图: {fig}（A 扩散 / B 锚定 / C 晚期失散）")


if __name__ == "__main__":
    main()
